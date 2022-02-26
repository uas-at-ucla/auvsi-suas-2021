//
// Demonstrates how to add and fly Waypoint missions using the MAVSDK.
//

#include <mavsdk/mavsdk.h>
#include <mavsdk/plugins/action/action.h>
#include <mavsdk/plugins/mission/mission.h>
#include <mavsdk/plugins/telemetry/telemetry.h>

#include <chrono>
#include <functional>
#include <future>
#include <iostream>
#include <thread>
#include <string>

using namespace mavsdk;
using std::chrono::seconds;
using std::this_thread::sleep_for;

/**
*
* Create a MissionItem object with the following information
*   1. Latitude and Longitude coordinates to go to.
*   2. Altitude to achieve
*   3. Speed to move at (in m/s)
*   4. "is_fly_through" -> True means touch waypoint and keep going. False means stop at waypoint.
*   5. gimbal_pitch_deg and gimbal_yaw_deg is for gimbal component; UGV WILL NOT HAVE GIMBAL!
*   6. "camera_action" is for if UGV has a camera; UGV WILL NOT HAVE CAMERA!
*
*
* A "MissionItem" is essentially a fancy version of a coordinate pair to have UGV to go to.
*
* DON'T TOUCH!
*
*/
Mission::MissionItem make_mission_item(
    double latitude_deg,
    double longitude_deg,
    float relative_altitude_m,
    float speed_m_s,
    bool is_fly_through,
    float gimbal_pitch_deg,
    float gimbal_yaw_deg,
    Mission::MissionItem::CameraAction camera_action)
{
    Mission::MissionItem new_item{};
    new_item.latitude_deg = latitude_deg;
    new_item.longitude_deg = longitude_deg;
    new_item.relative_altitude_m = relative_altitude_m;
    new_item.speed_m_s = speed_m_s;
    new_item.is_fly_through = is_fly_through;
    new_item.gimbal_pitch_deg = gimbal_pitch_deg;
    new_item.gimbal_yaw_deg = gimbal_yaw_deg;
    new_item.camera_action = camera_action;
    return new_item;
}

/*
*
* Setups up the "System" object that will be used to interface
* with autopilot computer on UGV
*
* DON'T TOUCH
*
*/
std::shared_ptr<System> get_system(Mavsdk& mavsdk)
{
    std::cout << "Waiting to discover system...\n";
    auto prom = std::promise<std::shared_ptr<System>>{};
    auto fut = prom.get_future();

    // We wait for new systems to be discovered, once we find one that has an
    // autopilot, we decide to use it.
    mavsdk.subscribe_on_new_system([&mavsdk, &prom]() {
        auto system = mavsdk.systems().back();

        if (system->has_autopilot()) {
            std::cout << "Discovered autopilot\n";

            // Unsubscribe again as we only want to find one system.
            mavsdk.subscribe_on_new_system(nullptr);
            prom.set_value(system);
        }
    });

    // We usually receive heartbeats at 1Hz, therefore we should find a
    // system after around 3 seconds max, surely.
    if (fut.wait_for(seconds(3)) == std::future_status::timeout) {
        std::cerr << "No autopilot found.\n";
        return {};
    }

    // Get discovered system now.
    return fut.get();
}

int main(int argc, char** argv)
{
    // The URL to use to connect to the UGV.
    // Currently set to connect to simulator.
    std::string ugv_url = "udp://:14540";

    // Initialize our MAVSDK interface by connecting to the UGV.
    Mavsdk mavsdk;
    ConnectionResult connection_result = mavsdk.add_any_connection(ugv_url);

    if (connection_result != ConnectionResult::Success) {
        std::cerr << "Connection failed: " << connection_result << '\n';
        return 1;
    }

    // Initialize our system object
    auto system = get_system(mavsdk);
    if (!system) {
        return 1;
    }

    // Initialize our action, mission, and telemetry objects.
    // "action" is used to send commands to the UGV (e.g. arm, start, stop, go-to location)
    // "mission" is used to send mission 

    /*
    * Initialize our Action, Mission, and Telemetry objects.
    * 
    * "action" is used to send commands to UGV (e.g. arm, start, stop, go-to location)
    *   -> Object Type: mavsdk::Action
    *   -> Documentation: https://mavsdk.mavlink.io/main/en/cpp/api_reference/classmavsdk_1_1_action.html
    *
    * "mission" is used to manage "waypoint missions", which essentially are missions about going to waypoints.
    *   -> Object Type: mavsdk::Mision
    *   -> Documentation: https://mavsdk.mavlink.io/main/en/cpp/api_reference/classmavsdk_1_1_mission.html
    *   -> Consists of "MissionItem" objects: https://mavsdk.mavlink.io/main/en/cpp/api_reference/structmavsdk_1_1_mission_1_1_mission_item.html
    *
    *  "telemetry" is used to get UGV telemetry data: state, mode, GPS, altitude, etc.
    *   -> Object Type: mavsdk::Telemetry
    *   -> Documentation: https://mavsdk.mavlink.io/main/en/cpp/guide/telemetry.html
    *
    */
    auto action = Action{system};
    auto mission = Mission{system};
    auto telemetry = Telemetry{system};

    
    // Check that all systems are good to go!
    while (!telemetry.health_all_ok()) {
        std::cout << "Waiting for system to be ready\n";
        sleep_for(seconds(1));
    }

    std::cout << "System ready\n";
    std::cout << "Creating and uploading mission\n";

    // Initialize a vector of MissionItems to be passed into our
    // Mission object.
    // 
    // MissionItem Documation: https://mavsdk.mavlink.io/main/en/cpp/api_reference/structmavsdk_1_1_mission_1_1_mission_item.html
    std::vector<Mission::MissionItem> mission_items;

    mission_items.push_back(make_mission_item(
        47.398170327054473,
        8.5456490218639658,
        0.0f,
        5.0f,
        false,
        0.0f,
        0.0f,
        Mission::MissionItem::CameraAction::None));

    mission_items.push_back(make_mission_item(
        47.398241338125118,
        8.5455360114574432,
        0.0f,
        5.0f,
        false,
        0.0f,
        0.0f,
        Mission::MissionItem::CameraAction::None));

    mission_items.push_back(make_mission_item(
        47.398139363821485,
        8.5453846156597137,
        0.0f,
        5.0f,
        false,
        0.0f,
        0.0f,
        Mission::MissionItem::CameraAction::None));

    /*
    *
    * Upload our mission data to the UGV autopilot computer
    *
    * Mission::MissionPlan contains the mission plan, which will be made up of the MissionItems
    *
    */
    std::cout << "Uploading mission...\n";
    Mission::MissionPlan mission_plan{};
    mission_plan.mission_items = mission_items;
    const Mission::Result upload_result = mission.upload_mission(mission_plan);

    if (upload_result != Mission::Result::Success) {
        std::cerr << "Mission upload failed: " << upload_result << ", exiting.\n";
        return 1;
    }
    
    /*
    *
    * Arm the UGV
    *
    * This is done with our "action" object.
    *
    */
    std::cout << "Arming...\n";
    const Action::Result arm_result = action.arm();
    if (arm_result != Action::Result::Success) {
        std::cerr << "Arming failed: " << arm_result << '\n';
        return 1;
    }
    std::cout << "Armed.\n";

    std::atomic<bool> want_to_pause{false};
    // Before starting the mission, we want to be sure to subscribe to the mission progress.
    mission.subscribe_mission_progress([&want_to_pause](Mission::MissionProgress mission_progress) {
        std::cout << "Mission status update: " << mission_progress.current << " / "
                  << mission_progress.total << '\n';

        if (mission_progress.current >= 2) {
            // We can only set a flag here. If we do more request inside the callback,
            // we risk blocking the system.
            want_to_pause = true;
        }
    });

    /*
    *
    * From here, we execute the mission!
    *
    */

    // Start the mission
    Mission::Result start_mission_result = mission.start_mission();
    if (start_mission_result != Mission::Result::Success) {
        std::cerr << "Starting mission failed: " << start_mission_result << '\n';
        return 1;
    }

    // While we don't want to pause the mission, do nothing for a second.
    while (!want_to_pause) {
        sleep_for(seconds(1));
    }

    // Pauses the mission
    std::cout << "Pausing mission...\n";
    const Mission::Result pause_mission_result = mission.pause_mission();

    // Pauses the mission: check to see if Mission pause was successful.
    if (pause_mission_result != Mission::Result::Success) {
        std::cerr << "Failed to pause mission:" << pause_mission_result << '\n';
    }
    std::cout << "Mission paused.\n";

    // Pause for 5 seconds.
    sleep_for(seconds(5));

    // Then continue.
    Mission::Result start_mission_again_result = mission.start_mission();
    if (start_mission_again_result != Mission::Result::Success) {
        std::cerr << "Starting mission again failed: " << start_mission_again_result << '\n';
        return 1;
    }

    // Keep doing the mission until it is finished.
    while (!mission.is_mission_finished().second) {
        sleep_for(seconds(1));
    }

    // We need to wait a bit, otherwise the armed state might not be correct yet.
    sleep_for(seconds(2));

    while (telemetry.armed()) {
        // Wait until we're done.
        sleep_for(seconds(1));
    }
    std::cout << "Disarmed, exiting.\n";
}
