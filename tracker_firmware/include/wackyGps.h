#ifndef wackyGps_h
#define wackyGps_h

#include <Arduino.h>
#include <TinyGPS++.h>
#include <time.h>

#include "boards.h"

class WackyGps
{
private:
    static WackyGps *instance;
    WackyGps();
    TinyGPSPlus gps;

public:
    void gpsDelay(unsigned long ms);
    static WackyGps *getInstance();
    static void removeInstance();
    TinyGPSLocation getLocation();
    int getCourse();
    double getSpeed();
    double getAltitude();
    time_t getUnixTime();
    uint32_t getSatellites();
    bool encodeGpsData();

    struct GpsData
    {
        uint64_t datetime;
        double lt;
        double lg;
        double speed;
        double altitude;
        double course;
        bool valid;
    };
    GpsData obtainCurrentData();
};

#endif