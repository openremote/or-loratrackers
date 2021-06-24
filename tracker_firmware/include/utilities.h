#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include "boards.h"
#include "wackyGps.h"
#include "wackyServer.h"
#include "wackySerialHelpers.h"
#include "Button2.h"

#if defined(TBeam_V1_1)
#include <axp20x.h>

AXP20X_Class pmu;

/**
 * @brief Custom function provided by the developers of the TTGO T Beam
 * It is initializing the PMU by settings the voltages for the subchips (GPS, LoRA)
 */
bool initPMU()
{
    if (pmu.begin(Wire, AXP192_SLAVE_ADDRESS) == AXP_FAIL)
    {
        return false;
    }

    pmu.setPowerOutPut(AXP192_DCDC1, 0);
    pmu.setPowerOutPut(AXP192_DCDC2, 0);
    pmu.setPowerOutPut(AXP192_LDO2, 0);
    pmu.setPowerOutPut(AXP192_LDO3, 0);
    pmu.setPowerOutPut(AXP192_EXTEN, 0);

    pmu.setLDO2Voltage(3300);  //LoRa VDD
    pmu.setLDO3Voltage(3300);  //GPS VDD
    pmu.setDCDC1Voltage(3300); //3.3v pin near IO21 and 22

    pmu.setPowerOutPut(AXP192_DCDC1, AXP202_ON);
    pmu.setPowerOutPut(AXP192_LDO2, AXP202_ON);
#ifdef USE_GPS
    pmu.setPowerOutPut(AXP192_LDO3, AXP202_ON);
#endif

    pinMode(PMU_IRQ, INPUT_PULLUP);
    attachInterrupt(
        PMU_IRQ, [] {

        },
        FALLING);

    pmu.adc1Enable(AXP202_VBUS_VOL_ADC1 |
                       AXP202_VBUS_CUR_ADC1 |
                       AXP202_BATT_CUR_ADC1 |
                       AXP202_BATT_VOL_ADC1,
                   AXP202_ON);

    pmu.enableIRQ(AXP202_VBUS_REMOVED_IRQ |
                      AXP202_VBUS_CONNECT_IRQ |
                      AXP202_BATT_REMOVED_IRQ |
                      AXP202_BATT_CONNECT_IRQ,
                  AXP202_ON);
    pmu.clearIRQ();
    return true;
}

void disablePeripherals()
{
    pmu.setPowerOutPut(AXP192_DCDC1, AXP202_OFF);
    pmu.setPowerOutPut(AXP192_LDO2, AXP202_OFF);
    pmu.setPowerOutPut(AXP192_LDO3, AXP202_OFF);
}
#endif

void turnBoardLed(bool state)
{
    digitalWrite(BOARD_LED, !state);
}

/**
 * @brief Custom delay function which works on encoding data and forwarding packets while user wants the program to delay
 */
void customDelayLoRaGps(WackyServer *wackyServer, uint8_t *lora_buf, uint8_t *lora_len, uint8_t *lora_source, WackyGps *wackyGps, Button2 *configButton, unsigned long ms)
{
    unsigned long start = millis();
    do
    {
#ifdef USE_GPS
        while (Serial1.available())
        {
            wackyGps->encodeGpsData();
        }
#endif
#ifdef USE_SERVER
        bool success = wackyServer->receiveOrForwardPacket(lora_buf, lora_len, lora_source);
        if (success)
        {
            Serial.printf("Received or forwarding packet!\n");
        }
#endif
#if DEVICE_TYPE == 1
        configButton->loop();
#endif

    } while (millis() - start < ms);
}

void initBoard()
{
    pinMode(BOARD_LED, OUTPUT);
    Serial.begin(SERIAL_BDRATE);
    Serial.println(F("InitBoard"));

#ifdef USE_SERVER
    SPI.begin(RADIO_SCLK_PIN, RADIO_MISO_PIN, RADIO_MOSI_PIN);
#endif

#ifdef TBeam_V1_1
    Wire.begin(I2C_SDA, I2C_SCL);
    initPMU();
#endif

#ifdef USE_GPS
    Serial1.begin(GPS_BAUD_RATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
#endif
}