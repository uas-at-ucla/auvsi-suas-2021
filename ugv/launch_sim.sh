cd $PX4_PATH
#export PX4_HOME_LAT=38.144478
#export PX4_HOME_LON=-76.42942
#export PX4_HOME_ALT=0.0

if [ ${HEADLESS+1} ]
then
    make px4_sitl gazebo_r1_rover HEADLESS=1
else
    make px4_sitl gazebo_r1_rover
fi