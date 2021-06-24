// Define the board name (Only one for now.)
#if DEVICE_TYPE == 1
#define TBeam_V1_1
#define USE_GPS
#elif DEVICE_TYPE == 2
#define NODE_DEVICE_GENERIC
#endif

#define USE_SERVER

#define SERIAL_BDRATE 115200
#define LORA_FREQUENCY 868.0
#define LORA_TX_POWER 13
#define LORA_CAD 0 // Listen before talk timeout in ms

#define EDGE_DEVICE_ID 1

// Dont change me.
#define UNUSE_PIN (0)

// Add more boards here:

#if defined(TBeam_V1_1)
#define GPS_RX_PIN 34
#define GPS_TX_PIN 12
#define BUTTON_PIN 38
#define BUTTON_PIN_MASK GPIO_SEL_38
#define I2C_SDA 21
#define I2C_SCL 22
#define PMU_IRQ 35

#define RADIO_SCLK_PIN 5
#define RADIO_MISO_PIN 19
#define RADIO_MOSI_PIN 27
#define RADIO_CS_PIN 18
#define RADIO_DI0_PIN 26
#define RADIO_RST_PIN 23
#define RADIO_DIO1_PIN 33
#define RADIO_BUSY_PIN 32

#define BOARD_LED 4
#define LED_ON LOW
#define LED_OFF HIGH
#define GPS_BAUD_RATE 9600
#elif defined(NODE_DEVICE_GENERIC)
/**
 * NAME /   ESP -   LILYGO
 * ************************
 * SCLK /   5   -   IO5     =
 * MISO /   19  -   IO19    =
 * MOSI /   27  -   IO27    =
 * CS   /   18  -   IO18    =
 * RST  /   14  -   IO23    !
 * DI0  /   26  -   IO14    !
 */


#define RADIO_SCLK_PIN 5
#define RADIO_MISO_PIN 19
#define RADIO_MOSI_PIN 27
#define RADIO_CS_PIN 18
#define RADIO_RST_PIN 14
#define RADIO_DI0_PIN 26

//#define RADIO_DIO1_PIN              33
//#define RADIO_BUSY_PIN              32
#define BOARD_LED 4
#define LED_ON LOW
#define LED_OFF HIGH
#else
#error "Please define DEVICE_TYPE in build flags."
#endif