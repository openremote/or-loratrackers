#ifndef wackyZlib_h
#define wackyZlib_h

#include <Arduino.h>
#include "uzlib.h"

#define CMF 0x78
#define FLG 0x9c
#define ZLIB_MAGIC_LEN 2

class WackyZlib
{
private:
    static WackyZlib *instance;
    WackyZlib();
    ~WackyZlib();
    struct uzlib_comp comp
    {
    };
    int32_t compress(uint8_t **out, const uint8_t *src, uint32_t len);
    

public:
    static WackyZlib *getInstance();
    uint64_t compressWithHeaderAndChecksum(uint8_t **out, const uint8_t *src, uint32_t len);
    static uint32_t generateChecksum(const uint8_t *src, uint32_t len);
    static uint64_t appendMagicAndChecksum(uint8_t **out, uint32_t checksum, const uint8_t *src, uint32_t len);
};

#endif