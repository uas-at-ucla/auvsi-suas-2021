cmake_minimum_required(VERSION 3.10.2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project(ugv)

add_executable(ugv
    ugv.cpp
)

find_package(MAVSDK REQUIRED)

target_link_libraries(ugv
    MAVSDK::mavsdk
    MAVSDK::mavsdk_action
    MAVSDK::mavsdk_telemetry
    MAVSDK::mavsdk_mission
)

if(NOT MSVC)
    add_compile_options(ugv PRIVATE -Wall -Wextra)
else()
    add_compile_options(ugv PRIVATE -WX -W2)
endif()
