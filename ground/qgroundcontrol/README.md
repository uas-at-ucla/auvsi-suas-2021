# UAS @ UCLA Custom QGroundControl Build

As part of the ground station software suite, we will be using a custom build of QGroundControl.

QGroundControl comes with the following visuals we need to show to judges during the AUVSI SUAS 2021 competition:
1. Satellite view of airfield
2. Drone position
3. Drone speed in KIAS, or ground speed in knots
4. Drone MSL altitude in feet

However, some features we will need to add to QGroundControl via custom elements are:
1. Flight boundaries
2. Stationary objects
3. Assigned waypoints for drone to fly through
4. Airdrop point
5. Airdrop boundary (area UGV will drive in)
6. RTH/RTL location (nice to have, not required)

# Development Guide (WIP)
QGroundControl is implemented using the Qt Framework. That being said, it is required to setup Qt and Qt Creator. Here is a link to a guide on how to setup the QGroundControl development environment:

https://docs.google.com/document/d/1BeYNTWl3izGJc2LJ7haU5wiB8R_NWzDI/edit

The UI elements of QGroundControl are implemented using a mix of C++ classes and Qt QML elements.
* The C++ classes implements the backend logic for the UI elements.
* Qt QML implements the frontend UI elements.

When making a custom Qt QML element, you will be working with the following files:
1. **main.cc** - This file contains the main() function that starts the program. Within the main() function, you will be registering your custom Qt QML element for use using:
`qmlRegisterType<C++_Class_Name>("QGroundControl.CustomPlugins.C++_Class_Name", Major_Version_Number, Minor_Version_Number, "Name for Custom Qt QML Element");`
![image](https://user-images.githubusercontent.com/25020111/141656403-c06c32cf-48ce-4ca3-aa20-fd34600fda8f.png)
2. **The C++ source and header files that implement your custom QML element** - For organization, be sure to save all source and header files you create in the **src/CustomPlugins** directory. You create new C++ classes by going to **File -> New File or Project...** and follow the dialog menus below:
![image](https://user-images.githubusercontent.com/25020111/141656485-d9359408-fc07-49ad-8a26-695fc4e83e1f.png)
![image](https://user-images.githubusercontent.com/25020111/141656501-edc5b06e-d08b-4dea-af4f-ef48941fc41f.png)
3. **FlyViewCustomLayer.qml** - This Qt QML file is where we will place our custom Qt QML UI elements. Assuming the custom Qt QML is registered correctly in the **main.cc** file, you import your custom Qt QML element as follows: 
`import QGroundControl.CustomPlugins.C++_Class_Name Major_Version_Number.Minor_Version_Number`
![image](https://user-images.githubusercontent.com/25020111/141656567-c5352a56-598d-4248-92ad-073ae7479033.png)
![image](https://user-images.githubusercontent.com/25020111/141656580-25ccd313-d69d-4437-ac81-ca66a29ebb23.png)


# Key Links 
* [Website](http://qgroundcontrol.com) (qgroundcontrol.com)
* [User Manual](https://docs.qgroundcontrol.com/en/)
* [Developer Guide](https://dev.qgroundcontrol.com/en/)
* [Discussion/Support](https://docs.qgroundcontrol.com/en/Support/Support.html)
* [Contributing](https://dev.qgroundcontrol.com/en/contribute/)
* [License](https://github.com/mavlink/qgroundcontrol/blob/master/COPYING.md)
