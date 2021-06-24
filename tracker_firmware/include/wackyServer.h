#ifndef wackyServer_h
#define wackyServer_h

#include <Arduino.h>
#include <RH_RF95.h>
#include <RHMesh.h>
#include "flexbuffers.h"
#include "wackySerialHelpers.h"
#include "wackyZlib.h"

#include "boards.h"

class WackyServer
{
private:
    static WackyServer *instance;
    WackyServer();
    RH_RF95 *rf;
    RHMesh *manager;
    WackyZlib *zlib;
    uint8_t buf[RH_MESH_MAX_MESSAGE_LEN];

public:
    static WackyServer *getInstance();
    static void removeInstance();
    void init();
    uint8_t sendPacket(unsigned char *data, uint8_t size, uint8_t destination);
    bool receiveOrForwardPacket(uint8_t *buf, uint8_t *len, uint8_t *source);
};

#endif