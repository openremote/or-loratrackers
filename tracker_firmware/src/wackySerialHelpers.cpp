#include "wackySerialHelpers.h"

/**
 * @brief print buf in format like 010203 ([1,2,3])
 */
void WackySerialHelpers::printHex(unsigned char *buf, int buf_len)
{
    Serial.print("HEX: ");
    for (int i = 0; i < buf_len; i++)
    {
        Serial.printf("%02X", buf[i]);
    }
    Serial.println();
}