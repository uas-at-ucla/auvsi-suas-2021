#ifndef GROUND_CLIENT_CLASSES
#define GROUND_CLIENT_CLASSES
class Telemetry{
    public:
     Telemetry(int latitude, int longitude, int altitude, int heading){
         m_lat = latitude;
         m_long = longitude;
         m_alt = altitude;
         m_head = heading;
     }

    private:
     int m_lat;
     int m_long;
     int m_alt;
     int m_head;  
};
#endif