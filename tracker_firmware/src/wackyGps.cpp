#include "wackyGps.h"

WackyGps *WackyGps::instance = NULL;
WackyGps::WackyGps() {}

WackyGps *WackyGps::getInstance()
{
    if (instance == NULL)
        instance = new WackyGps();
    return instance;
}

void WackyGps::removeInstance()
{
    delete instance;
    instance = NULL;
}

/**
 * @brief Get current location
 * @returns TinyGPSLocation struct
 */
TinyGPSLocation WackyGps::getLocation()
{
    return gps.location;
}

/**
 * @brief Get current course
 * @returns Raw value, divide by 100 to get degrees
 */
int WackyGps::getCourse()
{
    return gps.course.value();
}

/**
 * @brief Get current speed
 * @returns speed in kmph
 */
double WackyGps::getSpeed()
{
    return gps.speed.kmph();
}

/**
 * @brief Get altitude
 * @returns altitude in meters
 */
double WackyGps::getAltitude()
{
    return gps.altitude.meters();
}

/**
 * @brief Get the amount of satellites connected right now.
 * @returns amount of satellites 
 */
uint32_t WackyGps::getSatellites()
{
    return gps.satellites.value();
}

/**
 * @brief Get the unix timestamp from current date&time from GPS
 * @returns Unix time in time_t format
 */
time_t WackyGps::getUnixTime()
{
    /* Define tm struct */
    struct tm timeinfo = {0};

    timeinfo.tm_year = gps.date.year() - 1900; /* I don't really know why I need to do that...*/
    timeinfo.tm_mon = gps.date.month() - 1;    /* Jan = 0 */
    timeinfo.tm_mday = gps.date.day();
    timeinfo.tm_hour = gps.time.hour();
    timeinfo.tm_min = gps.time.minute();
    timeinfo.tm_sec = gps.time.second();
    return mktime(&timeinfo);
}

/**
 * @brief Custom non-halting delay (it's processing gps data when it waits)
 */
void WackyGps::gpsDelay(unsigned long ms)
{
    unsigned long start = millis();
    do
    {
        while (Serial1.available())
            gps.encode(Serial1.read());
    } while (millis() - start < ms);
}

/**
 * @brief Expose encode data for the custom delay function
 */
bool WackyGps::encodeGpsData()
{
    return gps.encode(Serial1.read());
}

/**
 * @brief Gets our GPS data and returns it.
 * @returns if valid is true, all of the fields are filled, otherwise only valid is filled.
 */
WackyGps::GpsData WackyGps::obtainCurrentData()
{
    /* Define GpsData to return */
    WackyGps::GpsData toReturn = {0};

    /* Get the location first, to check if it's valid */
    TinyGPSLocation location = getLocation();

    /* If the location is not valid (Waiting for GPS FIX), mark GpsData as not valid and return it. */
    if (!location.isValid())
    {
        toReturn.valid = false;
        return toReturn;
    }

    /* Fill GpsData with our current GPS values */
    toReturn.altitude = getAltitude();
    toReturn.datetime = getUnixTime();

    toReturn.lt = location.lat();
    toReturn.lg = location.lng();
    toReturn.speed = getSpeed();
    toReturn.course = getCourse() / 100; // BUG: Adding .0 like in the implementation of getCourse().deg() returns -17816834.000000 as the course

    /* Mark it as valid */
    toReturn.valid = true;

    return toReturn;
}