#include "wackyZlib.h"

WackyZlib *WackyZlib::instance = nullptr;

WackyZlib::WackyZlib()
{
    this->comp = {.out = {.outbuf = nullptr}};

    // Tweakable compress settings.
    // TODO: parameterize or add defines
    this->comp.dict_size = 32768;
    this->comp.hash_bits = 12;

    // Calculate hash size to allocate the hash table.
    size_t hash_size = sizeof(uzlib_hash_entry_t) * (1 << this->comp.hash_bits);

    // Allocate the hash table.
    this->comp.hash_table = (uzlib_hash_entry_t *)malloc(hash_size);

    // Initialize the hash table.
    memset(this->comp.hash_table, 0, hash_size);
}

/**
 * @brief frees hash table and deletes the current instance.
 * @note To create a new one, call getInstance()
 */
WackyZlib::~WackyZlib()
{
    free(this->comp.hash_table);
    free(this->comp.out.outbuf);
    delete instance;
    instance = nullptr;
}

/**
 * @brief Return already existing instance of Zlib or create a new one.
 * @note The init function gets called, the object is always ready to use.
 * @returns Returns pointer to current instance
 */
WackyZlib *WackyZlib::getInstance()
{
    if (instance == nullptr)
        instance = new WackyZlib();
    return instance;
}

/**
 * @brief compresses data using zlib
 * @note Pass the out buffer as address (&data)
 * @returns the size of the out buffer
 */
int32_t WackyZlib::compress(uint8_t **out, const uint8_t *src, uint32_t len)
{
    // Reset out from (possible) previous compressions
    // TODO: Will the prev out be reset too?
    this->comp.out = {nullptr};

    // Create a start block
    zlib_start_block(&this->comp.out);

    // Compress our data into block
    uzlib_compress(&this->comp, src, len);

    // Close the block
    zlib_finish_block(&this->comp.out);

    // out is a pointer-to-pointer of output buffer
    *out = this->comp.out.outbuf;

    // Return the length of current output buffer
    return this->comp.out.outlen;
}

/**
 * @brief generates adler_32 checksum of raw (non-compressed) data
 * @returns Generated checksum
 */
uint32_t WackyZlib::generateChecksum(const uint8_t *src, uint32_t len)
{
    // Call the adler32 function to obtain checksum
    return uzlib_adler32(src, len, 1);
}

/**
 * @brief Append header and checksum
 * @note Pass the out buffer as address (&data)
 * @returns the size of the end buffer
 */
uint64_t WackyZlib::appendMagicAndChecksum(uint8_t **out, uint32_t checksum, const uint8_t *src, uint32_t len)
{
    // Calculate the length of final buffer
    uint64_t finalLen = ZLIB_MAGIC_LEN + len + sizeof(uint32_t);

    // Create a final buffer with magic, data and the checksum
    auto *_out = new uint8_t[finalLen];

    // Insert magic data (first two bytes)
    _out[0] = CMF;
    _out[1] = FLG;

    // Copy the compressed data after the magic data
    memcpy(&_out[2], src, len);

    // Copy the checksum after the compressed data
    for (int i = 0; i < 4; i++)
        _out[ZLIB_MAGIC_LEN + len + i] = checksum >> (24 - (8 * i)); // Reverse the checksum order MSB (Network order)

    // out is a pointer-to-pointer of output buffer
    *out = _out;

    // Return the length of out buffer
    return finalLen;
}

/**
 * @brief compresses data using zlib and appends checksum & header to it
 * @note Pass the out buffer as address (&data)
 * @returns the size of the out buffer
 */
uint64_t WackyZlib::compressWithHeaderAndChecksum(uint8_t **out, const uint8_t *src, uint32_t len)
{
    uint32_t checksum = WackyZlib::generateChecksum(src, len);
    unsigned char *zlibOut;
    uint8_t compressSize = this->compress(&zlibOut, src, len);
    return WackyZlib::appendMagicAndChecksum(out, checksum, zlibOut, compressSize);
}