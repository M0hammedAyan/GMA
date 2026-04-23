#include "dual_camera_recorder.hpp"

#include <algorithm>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <mutex>
#include <thread>
#include <utility>

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
constexpr auto kCapturePollTimeout = std::chrono::milliseconds(100);
constexpr auto kWriterSleepQuantum = std::chrono::microseconds(2000);
constexpr auto kBusDrainTimeout = 2 * GST_SECOND;

bool xioctl(int fd, unsigned long request, void* arg) {
    while (true) {
        const int ret = ioctl(fd, request, arg);
        if (ret == 0) {
            return true;
        }
        if (errno == EINTR) {
            continue;
        }
        return false;
    }
}

std::string build_pipeline(const std::string& file_path,
                           int width,
                           int height,
                           int fps,
                           const std::string& raw_format) {
    return "appsrc name=src is-live=true format=time block=false do-timestamp=false "
           "caps=video/x-raw,format=" + raw_format + ",width=" +
           std::to_string(width) + ",height=" + std::to_string(height) +
           ",framerate=" + std::to_string(fps) +
           "/1 ! queue max-size-buffers=2 leaky=downstream "
           "! videoconvert ! video/x-raw,format=I420 "
           "! v4l2h264enc extra-controls=\"controls,video_bitrate=4000000;\" "
           "! h264parse ! mp4mux ! filesink location=" + file_path;
}

void reset_metric(std::atomic<uint64_t>& metric) {
    metric.store(0, std::memory_order_relaxed);
}

}  // namespace

DualCameraRecorder::LatestFrameBuffer::LatestFrameBuffer(size_t payload_bytes)
    : payload_bytes_(payload_bytes), latest_{0, FramePacket(payload_bytes)} {}

void DualCameraRecorder::LatestFrameBuffer::store(int64_t capture_timestamp_ns,
                                                  int width,
                                                  int height,
                                                  int stride_bytes,
                                                  const uint8_t* data,
                                                  size_t size) {
    std::lock_guard<std::mutex> lock(mu_);
    if (latest_.packet.payload.size() != payload_bytes_) {
        latest_.packet.payload.resize(payload_bytes_);
    }

    const size_t copy_size = std::min(payload_bytes_, size);
    std::memcpy(latest_.packet.payload.data(), data, copy_size);
    latest_.packet.frame_id = latest_.generation + 1;
    latest_.packet.timestamp_ns = capture_timestamp_ns;
    latest_.packet.width = width;
    latest_.packet.height = height;
    latest_.packet.stride_bytes = stride_bytes;
    latest_.packet.valid = true;
    ++latest_.generation;
}

bool DualCameraRecorder::LatestFrameBuffer::snapshot(FrameSnapshot& out) const {
    std::lock_guard<std::mutex> lock(mu_);
    if (!latest_.packet.valid) {
        return false;
    }
    out = latest_;
    return true;
}

DualCameraRecorder::DualCameraRecorder(Config cfg)
    : cfg_(std::move(cfg)),
      rs_frame_bytes_(static_cast<size_t>(cfg_.width * cfg_.height * 3)),
      wc_frame_bytes_(static_cast<size_t>(cfg_.width * cfg_.height * 2)),
      rs_latest_(rs_frame_bytes_),
      wc_latest_(wc_frame_bytes_) {
    if (cfg_.fps < 1) {
        cfg_.fps = 30;
    }
    writer_interval_ns_ = 1000000000LL / static_cast<int64_t>(cfg_.fps);
        max_frame_age_ns_ = std::max<int64_t>(writer_interval_ns_ * 3, static_cast<int64_t>(cfg_.max_frame_age_ms) * 1000000LL);
}

DualCameraRecorder::~DualCameraRecorder() {
    stop();
}

bool DualCameraRecorder::start() {
    if (running_.exchange(true)) {
        return true;
    }

    reset_metric(metrics_.rs_captured);
    reset_metric(metrics_.wc_captured);
    reset_metric(metrics_.rs_written);
    reset_metric(metrics_.wc_written);
    reset_metric(metrics_.rs_skipped_empty);
    reset_metric(metrics_.wc_skipped_empty);
    reset_metric(metrics_.rs_skipped_stale);
    reset_metric(metrics_.wc_skipped_stale);
    reset_metric(metrics_.rs_push_failures);
    reset_metric(metrics_.wc_push_failures);
    reset_metric(metrics_.writer_ticks);
    reset_metric(metrics_.paired_written);
    reset_metric(metrics_.pair_skipped_empty);
    reset_metric(metrics_.pair_skipped_stale);
    reset_metric(metrics_.pair_skipped_age);
    rs_last_written_generation_ = 0;
    wc_last_written_generation_ = 0;
    recording_start_ns_ = now_monotonic_ns();
    recording_stop_ns_ = 0;

    std::filesystem::create_directories(cfg_.output_dir);
    gst_init(nullptr, nullptr);

    auto cleanup_failed_start = [&]() {
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
        running_.store(false);
    };

    if (!init_realsense()) {
        cleanup_failed_start();
        return false;
    }
    if (!init_webcam_v4l2()) {
        cleanup_failed_start();
        return false;
    }
    if (!init_writers()) {
        cleanup_failed_start();
        return false;
    }

    try {
        rs_thread_ = std::thread(&DualCameraRecorder::realsense_capture_loop, this);
        wc_thread_ = std::thread(&DualCameraRecorder::webcam_capture_loop, this);
        writer_thread_ = std::thread(&DualCameraRecorder::sync_writer_loop, this);
        metrics_thread_ = std::thread(&DualCameraRecorder::metrics_loop, this);
    } catch (...) {
        running_.store(false);
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
        cleanup_failed_start();
        return false;
    }

    return true;
}

void DualCameraRecorder::stop() {
    if (!running_.exchange(false)) {
        return;
    }

    recording_stop_ns_ = now_monotonic_ns();

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

    print_validation_summary();
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

    g_object_set(rs_src, "is-live", TRUE, "format", GST_FORMAT_TIME, "do-timestamp", FALSE, "block", FALSE, nullptr);
    g_object_set(wc_src, "is-live", TRUE, "format", GST_FORMAT_TIME, "do-timestamp", FALSE, "block", FALSE, nullptr);

    gst_element_set_state(rs_pipeline, GST_STATE_PLAYING);
    gst_element_set_state(wc_pipeline, GST_STATE_PLAYING);

    gst_rs_pipeline_ = rs_pipeline;
    gst_wc_pipeline_ = wc_pipeline;
    gst_rs_appsrc_ = rs_src;
    gst_wc_appsrc_ = wc_src;
    return true;
}

bool DualCameraRecorder::push_frame(void* appsrc, const FramePacket& packet, int64_t pts_ns, int64_t duration_ns) {
    if (appsrc == nullptr || !packet.valid) {
        return false;
    }

    GstBuffer* buf = gst_buffer_new_allocate(nullptr, packet.payload.size(), nullptr);
    if (buf == nullptr) {
        return false;
    }

    GstMapInfo map{};
    if (!gst_buffer_map(buf, &map, GST_MAP_WRITE)) {
        gst_buffer_unref(buf);
        return false;
    }

    std::memcpy(map.data, packet.payload.data(), packet.payload.size());
    gst_buffer_unmap(buf, &map);

    GST_BUFFER_PTS(buf) = static_cast<GstClockTime>(std::max<int64_t>(0, pts_ns));
    GST_BUFFER_DTS(buf) = static_cast<GstClockTime>(std::max<int64_t>(0, pts_ns));
    GST_BUFFER_DURATION(buf) = static_cast<GstClockTime>(std::max<int64_t>(0, duration_ns));

    const GstFlowReturn flow = gst_app_src_push_buffer(GST_APP_SRC(appsrc), buf);
    if (flow != GST_FLOW_OK) {
        std::cerr << "gst_app_src_push_buffer failed with flow=" << flow << std::endl;
        return false;
    }

    return true;
}

void DualCameraRecorder::close_writers() {
    auto close_pipe = [](void*& pipe_ptr, void*& appsrc_ptr) {
        auto* pipe = static_cast<GstElement*>(pipe_ptr);
        auto* appsrc = static_cast<GstElement*>(appsrc_ptr);

        if (pipe == nullptr) {
            if (appsrc != nullptr) {
                gst_object_unref(appsrc);
                appsrc_ptr = nullptr;
            }
            return;
        }

        if (appsrc != nullptr) {
            gst_app_src_end_of_stream(GST_APP_SRC(appsrc));
        }

        GstBus* bus = gst_element_get_bus(pipe);
        if (bus != nullptr) {
            GstMessage* message = gst_bus_timed_pop_filtered(bus, kBusDrainTimeout, static_cast<GstMessageType>(GST_MESSAGE_EOS | GST_MESSAGE_ERROR));
            if (message != nullptr) {
                if (GST_MESSAGE_TYPE(message) == GST_MESSAGE_ERROR) {
                    GError* error = nullptr;
                    gchar* debug = nullptr;
                    gst_message_parse_error(message, &error, &debug);
                    std::cerr << "GStreamer finalization error: " << (error != nullptr ? error->message : "unknown") << std::endl;
                    if (error != nullptr) {
                        g_error_free(error);
                    }
                    g_free(debug);
                }
                gst_message_unref(message);
            }
            gst_object_unref(bus);
        }

        gst_element_set_state(pipe, GST_STATE_NULL);

        if (appsrc != nullptr) {
            gst_object_unref(appsrc);
            appsrc_ptr = nullptr;
        }

        gst_object_unref(pipe);
        pipe_ptr = nullptr;
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

    while (running_.load(std::memory_order_relaxed)) {
        try {
            rs2::frameset frames;
            if (!pipeline->poll_for_frames(&frames)) {
                std::this_thread::sleep_for(kCapturePollTimeout);
                continue;
            }

            rs2::video_frame color = frames.get_color_frame();
            if (!color) {
                continue;
            }

            rs_latest_.store(now_monotonic_ns(),
                             cfg_.width,
                             cfg_.height,
                             cfg_.width * 3,
                             static_cast<const uint8_t*>(color.get_data()),
                             rs_frame_bytes_);
            metrics_.rs_captured.fetch_add(1, std::memory_order_relaxed);
        } catch (const std::exception&) {
            if (!running_.load(std::memory_order_relaxed)) {
                break;
            }
            std::this_thread::sleep_for(kCapturePollTimeout);
        } catch (...) {
            if (!running_.load(std::memory_order_relaxed)) {
                break;
            }
            std::this_thread::sleep_for(kCapturePollTimeout);
        }
    }
}

void DualCameraRecorder::webcam_capture_loop() {
    while (running_.load(std::memory_order_relaxed)) {
        pollfd pfd{};
        pfd.fd = wc_fd_;
        pfd.events = POLLIN;

        const int pr = poll(&pfd, 1, static_cast<int>(kCapturePollTimeout.count()));
        if (pr < 0) {
            if (errno == EINTR) {
                continue;
            }
            continue;
        }
        if (pr == 0) {
            continue;
        }

        v4l2_buffer buf{};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;

        if (!xioctl(wc_fd_, VIDIOC_DQBUF, &buf)) {
            continue;
        }

        if (buf.index >= wc_buffers_.size() || wc_buffers_[buf.index].start == nullptr) {
            xioctl(wc_fd_, VIDIOC_QBUF, &buf);
            continue;
        }

        const int64_t timestamp_ns = static_cast<int64_t>(buf.timestamp.tv_sec) * 1000000000LL +
                                     static_cast<int64_t>(buf.timestamp.tv_usec) * 1000LL;
        const size_t bytes_used = std::min<size_t>(buf.bytesused, wc_frame_bytes_);

        (void)timestamp_ns;
        wc_latest_.store(now_monotonic_ns(),
                         cfg_.width,
                         cfg_.height,
                         cfg_.width * 2,
                         static_cast<const uint8_t*>(wc_buffers_[buf.index].start),
                         bytes_used);
        metrics_.wc_captured.fetch_add(1, std::memory_order_relaxed);

        xioctl(wc_fd_, VIDIOC_QBUF, &buf);
    }
}

void DualCameraRecorder::sync_writer_loop() {
    const int64_t interval_ns = std::max<int64_t>(1, writer_interval_ns_);
    int64_t next_tick_ns = now_monotonic_ns();

    while (running_.load(std::memory_order_relaxed)) {
        const int64_t now_ns = now_monotonic_ns();
        if (now_ns < next_tick_ns) {
            const int64_t sleep_ns = std::min<int64_t>(next_tick_ns - now_ns, std::chrono::duration_cast<std::chrono::nanoseconds>(kWriterSleepQuantum).count());
            std::this_thread::sleep_for(std::chrono::nanoseconds(sleep_ns));
            continue;
        }

        const int64_t pts_ns = std::max<int64_t>(0, next_tick_ns - recording_start_ns_);
        const int64_t tick_now_ns = now_monotonic_ns();

        FrameSnapshot rs_snapshot;
        FrameSnapshot wc_snapshot;

        const bool rs_ready = rs_latest_.snapshot(rs_snapshot);
        const bool wc_ready = wc_latest_.snapshot(wc_snapshot);

        if (!rs_ready || !wc_ready) {
            metrics_.pair_skipped_empty.fetch_add(1, std::memory_order_relaxed);
            if (!rs_ready) {
                metrics_.rs_skipped_empty.fetch_add(1, std::memory_order_relaxed);
            }
            if (!wc_ready) {
                metrics_.wc_skipped_empty.fetch_add(1, std::memory_order_relaxed);
            }
        } else if (rs_snapshot.generation == rs_last_written_generation_ ||
                   wc_snapshot.generation == wc_last_written_generation_) {
            metrics_.pair_skipped_stale.fetch_add(1, std::memory_order_relaxed);
            if (rs_snapshot.generation == rs_last_written_generation_) {
                metrics_.rs_skipped_stale.fetch_add(1, std::memory_order_relaxed);
            }
            if (wc_snapshot.generation == wc_last_written_generation_) {
                metrics_.wc_skipped_stale.fetch_add(1, std::memory_order_relaxed);
            }
        } else if ((tick_now_ns - rs_snapshot.packet.timestamp_ns) > max_frame_age_ns_ ||
                   (tick_now_ns - wc_snapshot.packet.timestamp_ns) > max_frame_age_ns_) {
            metrics_.pair_skipped_age.fetch_add(1, std::memory_order_relaxed);
        } else {
            const bool rs_ok = push_frame(gst_rs_appsrc_, rs_snapshot.packet, pts_ns, interval_ns);
            const bool wc_ok = push_frame(gst_wc_appsrc_, wc_snapshot.packet, pts_ns, interval_ns);

            if (rs_ok && wc_ok) {
                rs_last_written_generation_ = rs_snapshot.generation;
                wc_last_written_generation_ = wc_snapshot.generation;
                metrics_.rs_written.fetch_add(1, std::memory_order_relaxed);
                metrics_.wc_written.fetch_add(1, std::memory_order_relaxed);
                metrics_.paired_written.fetch_add(1, std::memory_order_relaxed);
            } else {
                if (!rs_ok) {
                    metrics_.rs_push_failures.fetch_add(1, std::memory_order_relaxed);
                }
                if (!wc_ok) {
                    metrics_.wc_push_failures.fetch_add(1, std::memory_order_relaxed);
                }
            }
        }

        metrics_.writer_ticks.fetch_add(1, std::memory_order_relaxed);

        next_tick_ns += interval_ns;
        const int64_t lateness_ns = now_monotonic_ns() - next_tick_ns;
        if (lateness_ns > interval_ns) {
            next_tick_ns = now_monotonic_ns() + interval_ns;
        }
    }
}

void DualCameraRecorder::metrics_loop() {
    using namespace std::chrono_literals;
    while (running_.load(std::memory_order_relaxed)) {
        std::this_thread::sleep_for(1s);
        std::cout
            << "metrics "
            << "rs_cap=" << metrics_.rs_captured.load(std::memory_order_relaxed) << ' '
            << "wc_cap=" << metrics_.wc_captured.load(std::memory_order_relaxed) << ' '
            << "rs_wr=" << metrics_.rs_written.load(std::memory_order_relaxed) << ' '
            << "wc_wr=" << metrics_.wc_written.load(std::memory_order_relaxed) << ' '
            << "rs_empty=" << metrics_.rs_skipped_empty.load(std::memory_order_relaxed) << ' '
            << "wc_empty=" << metrics_.wc_skipped_empty.load(std::memory_order_relaxed) << ' '
            << "rs_stale=" << metrics_.rs_skipped_stale.load(std::memory_order_relaxed) << ' '
            << "wc_stale=" << metrics_.wc_skipped_stale.load(std::memory_order_relaxed) << ' '
            << "pair_wr=" << metrics_.paired_written.load(std::memory_order_relaxed) << ' '
            << "pair_empty=" << metrics_.pair_skipped_empty.load(std::memory_order_relaxed) << ' '
            << "pair_stale=" << metrics_.pair_skipped_stale.load(std::memory_order_relaxed) << ' '
            << "pair_age=" << metrics_.pair_skipped_age.load(std::memory_order_relaxed) << ' '
            << "rs_push_fail=" << metrics_.rs_push_failures.load(std::memory_order_relaxed) << ' '
            << "wc_push_fail=" << metrics_.wc_push_failures.load(std::memory_order_relaxed) << ' '
            << "ticks=" << metrics_.writer_ticks.load(std::memory_order_relaxed)
            << std::endl;
    }
}

void DualCameraRecorder::print_validation_summary() const {
    const int64_t stop_ns = recording_stop_ns_ > 0 ? recording_stop_ns_ : now_monotonic_ns();
    const int64_t elapsed_ns = std::max<int64_t>(1, stop_ns - recording_start_ns_);
    const double elapsed_sec = static_cast<double>(elapsed_ns) / 1000000000.0;
    const double rs_fps = static_cast<double>(metrics_.rs_written.load(std::memory_order_relaxed)) / elapsed_sec;
    const double wc_fps = static_cast<double>(metrics_.wc_written.load(std::memory_order_relaxed)) / elapsed_sec;
    const double paired_fps = static_cast<double>(metrics_.paired_written.load(std::memory_order_relaxed)) / elapsed_sec;

    std::cout
        << "final "
        << "elapsed_s=" << elapsed_sec << ' '
        << "rs_written=" << metrics_.rs_written.load(std::memory_order_relaxed) << ' '
        << "wc_written=" << metrics_.wc_written.load(std::memory_order_relaxed) << ' '
        << "rs_fps=" << rs_fps << ' '
        << "wc_fps=" << wc_fps << ' '
        << "pair_written=" << metrics_.paired_written.load(std::memory_order_relaxed) << ' '
        << "pair_fps=" << paired_fps << ' '
        << "pair_empty=" << metrics_.pair_skipped_empty.load(std::memory_order_relaxed) << ' '
        << "pair_stale=" << metrics_.pair_skipped_stale.load(std::memory_order_relaxed) << ' '
        << "pair_age=" << metrics_.pair_skipped_age.load(std::memory_order_relaxed) << ' '
        << "rs_empty=" << metrics_.rs_skipped_empty.load(std::memory_order_relaxed) << ' '
        << "wc_empty=" << metrics_.wc_skipped_empty.load(std::memory_order_relaxed) << ' '
        << "rs_stale=" << metrics_.rs_skipped_stale.load(std::memory_order_relaxed) << ' '
        << "wc_stale=" << metrics_.wc_skipped_stale.load(std::memory_order_relaxed) << ' '
        << "rs_push_fail=" << metrics_.rs_push_failures.load(std::memory_order_relaxed) << ' '
        << "wc_push_fail=" << metrics_.wc_push_failures.load(std::memory_order_relaxed)
        << std::endl;
}

int64_t DualCameraRecorder::now_monotonic_ns() const {
    const auto now = std::chrono::steady_clock::now().time_since_epoch();
    return std::chrono::duration_cast<std::chrono::nanoseconds>(now).count();
}
