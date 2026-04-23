cmake_minimum_required(VERSION 3.16)
project(gma_dualcam_recorder LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED gstreamer-1.0 gstreamer-app-1.0)
find_package(realsense2 REQUIRED)

add_executable(gma_dualcam_recorder
    src/main.cpp
    src/dual_camera_recorder.cpp
)

target_include_directories(gma_dualcam_recorder PRIVATE
    include
    ${GSTREAMER_INCLUDE_DIRS}
)

target_link_directories(gma_dualcam_recorder PRIVATE
    ${GSTREAMER_LIBRARY_DIRS}
)

target_link_libraries(gma_dualcam_recorder PRIVATE
    realsense2::realsense2
    ${GSTREAMER_LIBRARIES}
    pthread
)

target_compile_options(gma_dualcam_recorder PRIVATE
    ${GSTREAMER_CFLAGS_OTHER}
    -Wall
    -Wextra
    -Wpedantic
)
