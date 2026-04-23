#include <csignal>
#include <iostream>
#include <thread>

#include "dual_camera_recorder.hpp"

namespace {
std::atomic<bool> g_stop{false};

void on_sigint(int) {
    g_stop.store(true);
}
}  // namespace

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;

    std::signal(SIGINT, on_sigint);

    DualCameraRecorder::Config cfg;
    cfg.width = 640;
    cfg.height = 480;
    cfg.fps = 30;

    DualCameraRecorder recorder(cfg);
    if (!recorder.start()) {
        std::cerr << "Failed to start native dual-camera recorder" << std::endl;
        return 1;
    }

    std::cout << "Native recorder running. Press Ctrl+C to stop." << std::endl;
    while (!g_stop.load()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    recorder.stop();
    return 0;
}
