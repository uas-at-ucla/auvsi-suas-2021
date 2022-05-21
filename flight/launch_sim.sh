cd $PX4_PATH
export PX4_HOME_LAT=34.17381230160001
export PX4_HOME_LON=-118.48154453362903

if [ ${HEADLESS+1} ]
then
    make px4_sitl gazebo HEADLESS=1
else
    make px4_sitl gazebo
fi