#include "wackyServer.h"

WackyServer *WackyServer::instance = NULL;
WackyServer::WackyServer() {}

WackyServer *WackyServer::getInstance()
{
    if (instance == NULL)
        instance = new WackyServer();
    return instance;
}

void WackyServer::removeInstance()
{
    delete instance;
    instance = NULL;
}

/**
 * @brief Initialize LoRa and the mesh manager
 */
void WackyServer::init()
{
    zlib = WackyZlib::getInstance();
    rf = new RH_RF95(RADIO_CS_PIN, RADIO_DI0_PIN);
    manager = new RHMesh(*rf, THIS_DEVICE_ID);
    if (!manager->init())
    {
        Serial.println("Init failed!");
    }
    rf->setFrequency(LORA_FREQUENCY);
    rf->setTxPower(LORA_TX_POWER, false);

    Serial.printf("LoRa frequency is: %0.1f\n", LORA_FREQUENCY);
    Serial.printf("LoRa Tx power is: %d\n", LORA_TX_POWER);
    Serial.printf("LoRa CAD (Listen before talk) timeout is: %dms\n", LORA_CAD);
}

/**
 * @brief Sends the packet to the destination and waits for the response
 * @returns result
 */
uint8_t WackyServer::sendPacket(unsigned char *data, uint8_t size, uint8_t destination)
{
    return manager->sendtoWait(data, size, destination);
}

bool WackyServer::receiveOrForwardPacket(uint8_t *buf, uint8_t *len, uint8_t *source)
{
    return manager->recvfromAck(buf, len, source);
}

