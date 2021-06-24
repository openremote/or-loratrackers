#ifndef wackySerialHelpers_h
#define wackySerialHelpers_h

#include <Arduino.h>

class WackySerialHelpers
{
public:
    static void printHex(unsigned char *buf, int buf_len);
};

#endif