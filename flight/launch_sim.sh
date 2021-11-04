cd $PX4_PATH
export PX4_HOME_LAT=38.144478
export PX4_HOME_LON=-76.42942

if [ ${HEADLESS+1} ]
then
    make px4_sitl gazebo HEADLESS=1
else
    make px4_sitl gazebo
fi