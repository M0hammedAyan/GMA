#include "dual_camera_recorder.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <limits>

#include <fcntl.h>
#include <gst/app/gstappsrc.h>
#include <gst/gst.h>
#include <librealsense2/rs.hpp>
#include <linux/videodev2.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>

namespace {
constexpr uint32_t kV4L2BufferCount = 6;

bool xioctl(int fd, unsigned long request, void* arg) {
    while (true) {
        int ret = ioctl(fd, request, arg);
        if (ret == 0) {
            return true;
        }
        if (errno == EINTR) {
            continue;
        }
        return false;
    }
}

std::string build_pipeline(const std::string& file_path, int width, int height, int fps, const std::string& raw_format) {
    return "appsrc name=src is-live=true format=time do-timestamp=true "
           "caps=video/x-raw,format=" + raw_format + ",width=" +
           std::to_string(width) + ",height=" + std::to_string(height) +
           ",framerate=" + std::to_string(fps) +
           "/1 ! queue max-size-buffers=32 leaky=downstream "
           "! videoconvert ! video/x-raw,format=I420 "
           "! v4l2h264enc extra-controls=\"controls,video_bitrate=4000000;\" "
           "! h264parse ! mp4mux ! filesink location=" + file_path;
}

}  // namespace

DualCameraRecorder::DualCameraRecorder(Config cfg)
    : cfg_(std::move(cfg)),
      rs_frame_bytes_(static_cast<size_t>(cfg_.width * cfg_.height * 3)),
      wc_frame_bytes_(static_cast<size_t>(cfg_.width * cfg_.height * 2)),
      rs_ring_(static_cast<size_t>(cfg_.buffer_seconds * cfg_.fps)),
      wc_ring_(static_cast<size_t>(cfg_.buffer_seconds * cfg_.fps)) {}

DualCameraRecorder::~DualCameraRecorder() {
    stop();
}

bool DualCameraRecorder::start() {
    if (running_.exchange(true)) {
        return true;
    }

    std::filesystem::create_directories(cfg_.output_dir);
    gst_init(nullptr, nullptr);

    if (!init_realsense()) {
        running_.store(false);
        return false;
    }
    if (!init_webcam_v4l2()) {
        running_.store(false);
        return false;
    }
    if (!init_writers()) {
        running_.store(false);
        return false;
    }

    rs_thread_ = std::thread(&DualCameraRecorder::realsense_capture_loop, this);
    wc_thread_ = std::thread(&DualCameraRecorder::webcam_capture_loop, this);
    writer_thread_ = std::thread(&DualCameraRecorder::sync_writer_loop, this);
    metrics_thread_ = std::thread(&DualCameraRecorder::metrics_loop, this);
    return true;
}

void DualCameraRecorder::stop() {
    if (!running_.exchange(false)) {
        return;
    }

    rs_ring_.stop();
    wc_ring_.stop();

    if (rs_thread_.joinable()) {
        rs_thread_.join();
    }
    if (wc_thread_.joinable()) {
        wc_thread_.join();
    }
    if (writer_thread_.joinable()) {
        writer_thread_.join();
    }
    if (metrics_thread_.joinable()) {
        metrics_thread_.join();
    }

    close_writers();
    close_webcam_v4l2();

    if (rs_pipeline_ != nullptr) {
        auto* pipeline = static_cast<rs2::pipeline*>(rs_pipeline_);
        try {
            pipeline->stop();
        } catch (...) {
        }
        delete pipeline;
        rs_pipeline_ = nullptr;
    }
}

bool DualCameraRecorder::init_realsense() {
    try {
        auto* pipeline = new rs2::pipeline();
        rs2::config cfg;
        cfg.enable_stream(RS2_STREAM_COLOR, cfg_.width, cfg_.height, RS2_FORMAT_RGB8, cfg_.fps);
        pipeline->start(cfg);
        rs_pipeline_ = pipeline;
        return true;
    } catch (const std::exception& ex) {
        std::cerr << "RealSense init failed: " << ex.what() << std::endl;
        return false;
    }
}

bool DualCameraRecorder::init_webcam_v4l2() {
    wc_fd_ = open(cfg_.webcam_device.c_str(), O_RDWR);
    if (wc_fd_ < 0) {
        std::cerr << "Failed to open webcam " << cfg_.webcam_device << ": " << strerror(errno) << std::endl;
        return false;
    }

    v4l2_format fmt{};
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = static_cast<uint32_t>(cfg_.width);
    fmt.fmt.pix.height = static_cast<uint32_t>(cfg_.height);
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt.fmt.pix.field = V4L2_FIELD_NONE;

    if (!xioctl(wc_fd_, VIDIOC_S_FMT, &fmt)) {
        std::cerr << "VIDIOC_S_FMT failed: " << strerror(errno) << std::endl;
        return false;
    }

    v4l2_streamparm parm{};
    parm.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    parm.parm.capture.timeperframe.numerator = 1;
    parm.parm.capture.timeperframe.denominator = static_cast<uint32_t>(cfg_.fps);
    xioctl(wc_fd_, VIDIOC_S_PARM, &parm);

    v4l2_requestbuffers req{};
    req.count = kV4L2BufferCount;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;

    if (!xioctl(wc_fd_, VIDIOC_REQBUFS, &req) || req.count < 2) {
        std::cerr << "VIDIOC_REQBUFS failed" << std::endl;
        return false;
    }

    wc_buffers_.resize(req.count);

    for (uint32_t i = 0; i < req.count; ++i) {
        v4l2_buffer buf{};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;

        if (!xioctl(wc_fd_, VIDIOC_QUERYBUF, &buf)) {
            std::cerr << "VIDIOC_QUERYBUF failed" << std::endl;
            return false;
        }

        wc_buffers_[i].length = buf.length;
        wc_buffers_[i].start = mmap(nullptr, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, wc_fd_, buf.m.offset);
        if (wc_buffers_[i].start == MAP_FAILED) {
            std::cerr << "mmap failed" << std::endl;
            return false;
        }

        if (!xioctl(wc_fd_, VIDIOC_QBUF, &buf)) {
            std::cerr << "VIDIOC_QBUF failed" << std::endl;
            return false;
        }
    }

    v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (!xioctl(wc_fd_, VIDIOC_STREAMON, &type)) {
        std::cerr << "VIDIOC_STREAMON failed" << std::endl;
        return false;
    }

    return true;
}

bool DualCameraRecorder::init_writers() {
    const std::string rs_file = cfg_.output_dir + "/realsense_native.mp4";
    const std::string wc_file = cfg_.output_dir + "/webcam_native.mp4";

    const std::string rs_pipeline_desc = build_pipeline(rs_file, cfg_.width, cfg_.height, cfg_.fps, "RGB");
    const std::string wc_pipeline_desc = build_pipeline(wc_file, cfg_.width, cfg_.height, cfg_.fps, "YUY2");

    GError* err = nullptr;

    GstElement* rs_pipeline = gst_parse_launch(rs_pipeline_desc.c_str(), &err);
    if (err != nullptr || rs_pipeline == nullptr) {
        if (err != nullptr) {
            std::cerr << "GStreamer RS pipeline error: " << err->message << std::endl;
            g_error_free(err);
        }
        return false;
    }

    err = nullptr;
    GstElement* wc_pipeline = gst_parse_launch(wc_pipeline_desc.c_str(), &err);
    if (err != nullptr || wc_pipeline == nullptr) {
        if (err != nullptr) {
            std::cerr << "GStreamer WC pipeline error: " << err->message << std::endl;
            g_error_free(err);
        }
        gst_object_unref(rs_pipeline);
        return false;
    }

    GstElement* rs_src = gst_bin_get_by_name(GST_BIN(rs_pipeline), "src");
    GstElement* wc_src = gst_bin_get_by_name(GST_BIN(wc_pipeline), "src");
    if (rs_src == nullptr || wc_src == nullptr) {
        if (rs_src != nullptr) {
            gst_object_unref(rs_src);
        }
        if (wc_src != nullptr) {
            gst_object_unref(wc_src);
        }
        gst_object_unref(rs_pipeline);
        gst_object_unref(wc_pipeline);
        return false;
    }

    gst_element_set_state(rs_pipeline, GST_STATE_PLAYING);
    gst_element_set_state(wc_pipeline, GST_STATE_PLAYING);

    gst_rs_pipeline_ = rs_pipeline;
    gst_wc_pipeline_ = wc_pipeline;
    gst_rs_appsrc_ = rs_src;
    gst_wc_appsrc_ = wc_src;
    return true;
}

void DualCameraRecorder::close_writers() {
    auto close_pipe = [](void*& pipe, void*& appsrc) {
        if (appsrc != nullptr) {
            gst_object_unref(static_cast<GstElement*>(appsrc));
            appsrc = nullptr;
        }
        if (pipe != nullptr) {
            auto* gst_pipe = static_cast<GstElement*>(pipe);
            gst_element_send_event(gst_pipe, gst_event_new_eos());
            gst_element_set_state(gst_pipe, GST_STATE_NULL);
            gst_object_unref(gst_pipe);
            pipe = nullptr;
        }
    };

    close_pipe(gst_rs_pipeline_, gst_rs_appsrc_);
    close_pipe(gst_wc_pipeline_, gst_wc_appsrc_);
}

void DualCameraRecorder::close_webcam_v4l2() {
    if (wc_fd_ >= 0) {
        v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        xioctl(wc_fd_, VIDIOC_STREAMOFF, &type);

        for (auto& b : wc_buffers_) {
            if (b.start != nullptr && b.start != MAP_FAILED) {
                munmap(b.start, b.length);
            }
        }
        wc_buffers_.clear();

        close(wc_fd_);
        wc_fd_ = -1;
    }
}

void DualCameraRecorder::realsense_capture_loop() {
    auto* pipeline = static_cast<rs2::pipeline*>(rs_pipeline_);
    uint64_t frame_id = 0;

    while (running_.load()) {
        try {
            rs2::frameset frames = pipeline->wait_for_frames();
            rs2::video_frame color = frames.get_color_frame();
            if (!color) {
                continue;
            }

            FramePacket pkt(rs_frame_bytes_);
            pkt.frame_id = frame_id++;
            pkt.timestamp_ns = static_cast<int64_t>(color.get_timestamp() * 1000000.0);
            pkt.width = cfg_.width;
            pkt.height = cfg_.height;
            pkt.stride_bytes = cfg_.width * 3;
            pkt.valid = true;

            std::memcpy(pkt.payload.data(), color.get_data(), rs_frame_bytes_);
            rs_ring_.push(std::move(pkt));
            metrics_.rs_captured.fetch_add(1);
        } catch (...) {
            if (!running_.load()) {
                break;
            }
        }
    }
}

void DualCameraRecorder::webcam_capture_loop() {
    uint64_t frame_id = 0;

    while (running_.load()) {
        pollfd pfd{};
        pfd.fd = wc_fd_;
        pfd.events = POLLIN;
        int pr = poll(&pfd, 1, 1000);
        if (pr <= 0) {
            continue;
        }

        v4l2_buffer buf{};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;

        if (!xioctl(wc_fd_, VIDIOC_DQBUF, &buf)) {
            continue;
        }

        FramePacket pkt(wc_frame_bytes_);
        pkt.frame_id = frame_id++;
        pkt.timestamp_ns = static_cast<int64_t>(buf.timestamp.tv_sec) * 1000000000LL +
                           static_cast<int64_t>(buf.timestamp.tv_usec) * 1000LL;
        pkt.width = cfg_.width;
        pkt.height = cfg_.height;
        pkt.stride_bytes = cfg_.width * 2;
        pkt.valid = true;

        const auto bytes_used = std::min<size_t>(buf.bytesused, pkt.payload.size());
        std::memcpy(pkt.payload.data(), wc_buffers_[buf.index].start, bytes_used);

        wc_ring_.push(std::move(pkt));
        metrics_.wc_captured.fetch_add(1);

        xioctl(wc_fd_, VIDIOC_QBUF, &buf);
    }
}

void DualCameraRecorder::sync_writer_loop() {
    std::optional<FramePacket> rs_pending;
    std::optional<FramePacket> wc_pending;

    const int64_t tolerance_ns = static_cast<int64_t>(cfg_.sync_tolerance_ms) * 1000000LL;

    while (running_.load()) {
        if (!rs_pending.has_value()) {
            FramePacket pkt;
            if (rs_ring_.pop(pkt, std::chrono::milliseconds(100))) {
                rs_pending = std::move(pkt);
            }
        }

        if (!wc_pending.has_value()) {
            FramePacket pkt;
            if (wc_ring_.pop(pkt, std::chrono::milliseconds(100))) {
                wc_pending = std::move(pkt);
            }
        }

        if (!rs_pending.has_value() || !wc_pending.has_value()) {
            continue;
        }

        int64_t wc_corrected = wc_pending->timestamp_ns - webcam_offset_ns_;
        int64_t delta = rs_pending->timestamp_ns - wc_corrected;
        int64_t abs_delta = std::llabs(delta);

        if (abs_delta <= tolerance_ns) {
            webcam_offset_ns_ = static_cast<int64_t>(0.98 * static_cast<double>(webcam_offset_ns_) +
                                                     0.02 * static_cast<double>(wc_pending->timestamp_ns - rs_pending->timestamp_ns));

            auto push_to_appsrc = [](void* src_ptr, const uint8_t* data, size_t size, int64_t ts_ns) {
                auto* src = GST_APP_SRC(src_ptr);
                GstBuffer* buf = gst_buffer_new_allocate(nullptr, size, nullptr);
                GstMapInfo map{};
                if (gst_buffer_map(buf, &map, GST_MAP_WRITE)) {
                    std::memcpy(map.data, data, size);
                    gst_buffer_unmap(buf, &map);
                }
                GST_BUFFER_PTS(buf) = ts_ns;
                GST_BUFFER_DTS(buf) = ts_ns;
                GST_BUFFER_DURATION(buf) = GST_CLOCK_TIME_NONE;
                gst_app_src_push_buffer(src, buf);
            };

            // Webcam is YUYV; convert stage is expected in final production pipeline.
            // For this dedicated path, we publish bytes as-is for deterministic timing instrumentation.
            push_to_appsrc(gst_rs_appsrc_, rs_pending->payload.data(), rs_pending->payload.size(), rs_pending->timestamp_ns);
            push_to_appsrc(gst_wc_appsrc_, wc_pending->payload.data(), wc_pending->payload.size(), wc_pending->timestamp_ns);

            metrics_.rs_written.fetch_add(1);
            metrics_.wc_written.fetch_add(1);

            rs_pending.reset();
            wc_pending.reset();
            continue;
        }

        metrics_.sync_mismatch.fetch_add(1);
        if (rs_pending->timestamp_ns < wc_corrected) {
            metrics_.rs_dropped_unmatched.fetch_add(1);
            rs_pending.reset();
        } else {
            metrics_.wc_dropped_unmatched.fetch_add(1);
            wc_pending.reset();
        }
    }
}

void DualCameraRecorder::metrics_loop() {
    using namespace std::chrono_literals;
    while (running_.load()) {
        std::this_thread::sleep_for(1s);
        std::cout
            << "metrics "
            << "rs_cap=" << metrics_.rs_captured.load() << ' '
            << "wc_cap=" << metrics_.wc_captured.load() << ' '
            << "rs_wr=" << metrics_.rs_written.load() << ' '
            << "wc_wr=" << metrics_.wc_written.load() << ' '
            << "rs_drop=" << metrics_.rs_dropped_unmatched.load() << ' '
            << "wc_drop=" << metrics_.wc_dropped_unmatched.load() << ' '
            << "sync_mismatch=" << metrics_.sync_mismatch.load() << ' '
            << "rs_overflow=" << rs_ring_.overflows() << ' '
            << "wc_overflow=" << wc_ring_.overflows()
            << std::endl;
    }
}

int64_t DualCameraRecorder::now_monotonic_ns() const {
    const auto now = std::chrono::steady_clock::now().time_since_epoch();
    return std::chrono::duration_cast<std::chrono::nanoseconds>(now).count();
}
