#pragma once

#include <atomic>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <thread>
#include <vector>

#include "frame_packet.hpp"
#include "ring_buffer.hpp"

class DualCameraRecorder {
public:
    struct Config {
        int width = 640;
        int height = 480;
        int fps = 15;
        int sync_tolerance_ms = 15;
        int buffer_seconds = 10;
        std::string webcam_device = "/dev/video0";
        std::string output_dir = "recordings/native";
    };

    explicit DualCameraRecorder(Config cfg);
    ~DualCameraRecorder();

    bool start();
    void stop();

private:
    struct Metrics {
        std::atomic<uint64_t> rs_captured{0};
        std::atomic<uint64_t> wc_captured{0};
        std::atomic<uint64_t> rs_written{0};
        std::atomic<uint64_t> wc_written{0};
        std::atomic<uint64_t> rs_dropped_unmatched{0};
        std::atomic<uint64_t> wc_dropped_unmatched{0};
        std::atomic<uint64_t> sync_mismatch{0};
    };

    bool init_realsense();
    bool init_webcam_v4l2();
    bool init_writers();
    void close_webcam_v4l2();
    void close_writers();

    void realsense_capture_loop();
    void webcam_capture_loop();
    void sync_writer_loop();
    void metrics_loop();

    int64_t now_monotonic_ns() const;

    Config cfg_;
    std::atomic<bool> running_{false};

    int64_t webcam_offset_ns_ = 0;

    size_t rs_frame_bytes_ = 0;
    size_t wc_frame_bytes_ = 0;

    RingBuffer<FramePacket> rs_ring_;
    RingBuffer<FramePacket> wc_ring_;

    Metrics metrics_;

    std::thread rs_thread_;
    std::thread wc_thread_;
    std::thread writer_thread_;
    std::thread metrics_thread_;

    // Opaque handles kept as void* here to keep headers lightweight.
    void* rs_pipeline_ = nullptr;
    void* gst_rs_pipeline_ = nullptr;
    void* gst_wc_pipeline_ = nullptr;
    void* gst_rs_appsrc_ = nullptr;
    void* gst_wc_appsrc_ = nullptr;

    int wc_fd_ = -1;

    struct V4L2MappedBuffer {
        void* start = nullptr;
        size_t length = 0;
    };
    std::vector<V4L2MappedBuffer> wc_buffers_;
};
