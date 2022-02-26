# Builds the MAVSDK code using the present CMakeLists.txt file.

cmake -Bbuild -H.
cmake --build build -j4