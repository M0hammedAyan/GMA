#pragma once

#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <mutex>
#include <vector>

// Fixed-capacity, overwrite-on-full ring buffer for deterministic capture pipelines.
template <typename T>
class RingBuffer {
public:
    explicit RingBuffer(size_t capacity)
        : capacity_(capacity), slots_(capacity) {}

    size_t capacity() const { return capacity_; }

    // Overwrites the oldest element when full.
    void push(T&& item) {
        std::unique_lock<std::mutex> lock(mu_);
        if (size_ == capacity_) {
            // Drop oldest entry to keep the newest data.
            tail_ = (tail_ + 1) % capacity_;
            --size_;
            ++overflows_;
        }

        slots_[head_] = std::move(item);
        head_ = (head_ + 1) % capacity_;
        ++size_;
        lock.unlock();
        cv_.notify_one();
    }

    bool pop(T& out, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mu_);
        if (!cv_.wait_for(lock, timeout, [&] { return size_ > 0 || stopped_; })) {
            return false;
        }
        if (size_ == 0) {
            return false;
        }

        out = std::move(slots_[tail_]);
        tail_ = (tail_ + 1) % capacity_;
        --size_;
        return true;
    }

    void stop() {
        std::lock_guard<std::mutex> lock(mu_);
        stopped_ = true;
        cv_.notify_all();
    }

    size_t overflows() const {
        std::lock_guard<std::mutex> lock(mu_);
        return overflows_;
    }

private:
    size_t capacity_ = 0;
    std::vector<T> slots_;
    size_t head_ = 0;
    size_t tail_ = 0;
    size_t size_ = 0;
    size_t overflows_ = 0;
    bool stopped_ = false;

    mutable std::mutex mu_;
    std::condition_variable cv_;
};
