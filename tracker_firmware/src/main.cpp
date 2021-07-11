#include "utilities.h"
#include "wackyServer.h"
#include "flexbuffers.h"
#include "wackySerialHelpers.h"
#include "wackyZlib.h"
#include "wackyGps.h"

#if DEVICE_TYPE == 1
#include "Button2.h"
#define CONFIG_BUTTON 38
int selectedMode = -1;
Button2 configButton = Button2(CONFIG_BUTTON);
void configDoubleClick(Button2 &btn)
{
  digitalWrite(BOARD_LED, LED_ON);
  selectedMode = 2; // fake gps
}
void configClick(Button2 &btn)
{
  digitalWrite(BOARD_LED, LED_OFF);
  selectedMode = 1; // real gps
}
#endif

#ifdef USE_SERVER
WackyServer *server = WackyServer::getInstance();
#endif

#ifdef USE_GPS
WackyGps *gps = WackyGps::getInstance();
#endif
WackyZlib *zlib = WackyZlib::getInstance();

uint8_t recv_buf[RH_MESH_MAX_MESSAGE_LEN];
uint8_t recv_len = sizeof(recv_buf);
uint8_t recv_from;

/**
 * @brief Setup the board power settings and optionally the server (LoRa modem)
 */
void setup()
{
  initBoard();

  /* They wait to get LoRa/GPS up */
  delay(1500);

#if DEVICE_TYPE == 1
  configButton.setDoubleClickHandler(configDoubleClick);
  configButton.setClickHandler(configClick);
#endif

#ifdef USE_SERVER
  server->init();
#endif
}

/**
 * @brief Main code loop, gets gps data and optionally sends it via LoRa
 */
void loop()
{
  configButton.loop();
#ifdef USE_GPS

  /* Obtain current GPS data */
  WackyGps::GpsData currentData = gps->obtainCurrentData();

  if (selectedMode == 2)
  {
    currentData = {0};
    currentData.valid = true;
    currentData.altitude = 0.0f;
    currentData.datetime = 1;
    currentData.lt = 2.0f;
    currentData.lg = 3.0f;
    currentData.speed = 4;
    currentData.course = 5.0f;
  }
#else
  WackyGps::GpsData currentData = {0};
  currentData.valid = true;
  currentData.altitude = 0.0f;
  currentData.datetime = 1;
  currentData.lt = 2.0f;
  currentData.lg = 3.0f;
  currentData.speed = 4;
  currentData.course = 5.0f;
#endif

  /* If location is invalid, return NULL */
  if (currentData.valid)
  {
    /* Print obtained gps data */
    Serial.printf("Alt: %f Dt: %d lt: %f lg: %f speed: %f course: %f\n",
                  currentData.altitude, currentData.datetime, currentData.lt, currentData.lg, currentData.speed, currentData.course);

    /* Generate flexbuffer with our data */
    flexbuffers::Builder fbb;
    fbb.Map([&]()
            {
              fbb.Int("dt", currentData.datetime);
              fbb.Double("lt", currentData.lt);
              fbb.Double("lg", currentData.lg);
              fbb.Double("sp", currentData.speed);
              fbb.Double("al", currentData.altitude);
              fbb.Double("cs", currentData.course);
            });
    fbb.Finish();

    /* Get the buffer of our flexbuffer */
    const std::vector<uint8_t> flexOut = fbb.GetBuffer();

    /* Compress and append the checksum and the header */
    unsigned char *zlibOut;
    uint64_t zlibSize = zlib->compressWithHeaderAndChecksum(&zlibOut, flexOut.data(), flexOut.size());

    /* Print compressed data ready to send */
    WackySerialHelpers::printHex(zlibOut, zlibSize);
#ifdef USE_SERVER
    uint8_t ret = server->sendPacket(zlibOut, zlibSize, EDGE_DEVICE_ID);

    Serial.printf("sendPacket: %d\n", ret);
#endif

    /* Free the zlib data we created for the next loop cycle */
    free(zlibOut);
  }
  else
  {

    for (int i = 0; i < gps->getSatellites(); i++)
    {
      digitalWrite(BOARD_LED, LED_ON);
      delay(500);
      digitalWrite(BOARD_LED, LED_OFF);
      delay(500);
    }
    Serial.printf("Waiting for GPS fix... Sat:%d GPS time: %lld\n", gps->getSatellites(), (long long)gps->getUnixTime());
  }

  Serial.printf("Listening for packets while waiting...");
  /* Custom delay function to not fully halt the code execution, when it delays our code it still is processing the gps serial data */
  customDelayLoRaGps(server,
                     recv_buf, &recv_len, &recv_from,
#ifdef USE_GPS
                     gps,
#else
                     NULL,
#endif
#if DEVICE_TYPE == 1
                     &configButton,
#else
                     NULL,
#endif
                     5000);
  Serial.printf("OK\n");
}