#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "frame_packet.hpp"

class DualCameraRecorder {
public:
    struct Config {
        int width = 640;
        int height = 480;
        int fps = 30;
        int max_frame_age_ms = 120;
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
        std::atomic<uint64_t> rs_skipped_empty{0};
        std::atomic<uint64_t> wc_skipped_empty{0};
        std::atomic<uint64_t> rs_skipped_stale{0};
        std::atomic<uint64_t> wc_skipped_stale{0};
        std::atomic<uint64_t> rs_push_failures{0};
        std::atomic<uint64_t> wc_push_failures{0};
        std::atomic<uint64_t> writer_ticks{0};
        std::atomic<uint64_t> paired_written{0};
        std::atomic<uint64_t> pair_skipped_empty{0};
        std::atomic<uint64_t> pair_skipped_stale{0};
        std::atomic<uint64_t> pair_skipped_age{0};
    };

    struct FrameSnapshot {
        uint64_t generation = 0;
        FramePacket packet;
    };

    class LatestFrameBuffer {
    public:
        explicit LatestFrameBuffer(size_t payload_bytes);

        void store(int64_t capture_timestamp_ns,
                   int width,
                   int height,
                   int stride_bytes,
                   const uint8_t* data,
                   size_t size);

        bool snapshot(FrameSnapshot& out) const;

    private:
        size_t payload_bytes_ = 0;
        mutable std::mutex mu_;
        FrameSnapshot latest_;
    };

    bool init_realsense();
    bool init_webcam_v4l2();
    bool init_writers();
    bool push_frame(void* appsrc, const FramePacket& packet, int64_t pts_ns, int64_t duration_ns);
    void close_webcam_v4l2();
    void close_writers();

    void realsense_capture_loop();
    void webcam_capture_loop();
    void sync_writer_loop();
    void metrics_loop();
    void print_validation_summary() const;

    int64_t now_monotonic_ns() const;

    Config cfg_;
    std::atomic<bool> running_{false};

    int64_t recording_start_ns_ = 0;
    int64_t recording_stop_ns_ = 0;
    int64_t writer_interval_ns_ = 0;
    int64_t max_frame_age_ns_ = 0;

    size_t rs_frame_bytes_ = 0;
    size_t wc_frame_bytes_ = 0;

    LatestFrameBuffer rs_latest_;
    LatestFrameBuffer wc_latest_;

    uint64_t rs_last_written_generation_ = 0;
    uint64_t wc_last_written_generation_ = 0;

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
