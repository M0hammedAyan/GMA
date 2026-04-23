#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

struct FramePacket {
    uint64_t frame_id = 0;
    int64_t timestamp_ns = 0;
    int width = 0;
    int height = 0;
    int stride_bytes = 0;
    bool valid = false;
    std::vector<uint8_t> payload;

    FramePacket() = default;

    explicit FramePacket(size_t payload_bytes)
        : payload(payload_bytes, 0) {}
};
