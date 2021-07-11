# GPS Update Message Protocol

## Introduction

In our LoRa mesh network, our trackers will be obtaining their location via GPS every couple of seconds and then using the LoRa mesh system to send the resulting data to the edge device, which can then upload the data to the OpenRemote IoT platform.

In this document we will describe the data our GPS tracker system is going to use and how we are planning on encoding it, keeping the requirements in mind.

## Data Payload

The GPS trackers in our LoRa mesh network are going to be using their on-board GPS to obtain information on their position (longitude & latitude), altitude, course/heading & ground speed. Due to the way GPS works, which is based on synchronized atomic timing1, we will also be able to get the current date & time, which could be handy for us as the LoRa mesh network might add some delay between the measurement and the receiving of the message at the edge of the mesh network.

This brings the final payload to contain the following datapoints:

|Abbreviation|Name|Data Type|Description|
|---|---|---|---|
|`DT`|Date & Time|Signed 32-bit integer|UTC Timestamp in seconds|
|`LT `|Latitude|64-bit floating point|Latitude in degrees|
|`LG`|Longitude|64-bit floating point|Longitude in degrees|
|`SP`|Speed|64-bit floating point|Ground speed (km/h)|
|`AL`|Altitude|64-bit floating point|Altitude in meters|
|`CS`|Course|64-bit floating point|Course over the ground (Degrees offset from true north)|

## Encoding Requirements

First and foremost, we are looking for an encoding format which allows us to easily encode the data we want to transmit into raw bytes. Because we are using an ESP32 w/ Arduino for our hardware, this encoding format will need to have a portable C++ library which we can easily include into our ESP32 project. On the receiving-side of the transmission, we will also require a python library which is able to decode the bytes back into Python datatypes.

Because LoRa is not fast, with a maximum data rate of 27kbit/s in the most optimal conditions, the system would benefit if the encoding would make these messages as small as possible. For instance, simply sending JSON via the LoRa network would be a big waste as we don’t require the data packets to be human readable. The size requirement is further enforced by a limitation of the transmission library we are using, called RadioHead. RadioHead defines a maximum payload size of 245 bytes for any message routed over a mesh network, which means the encoded message data has a maximum size of 245 bytes. Another factor to the size limitation is the regulatory requirement set by the government, which states one can only be actively transmitting 1% of the time.

Furthermore, OpenRemote has asked us to make our system adaptable to other use-cases. This means the encoding will need to be dynamic enough to be able to handle different messages than the ones we are going to be using for our GPS tracker system.

## Flatbuffers

Flatbuffers is a data serialization library made by Google, which is very efficient and cross-platform. It allows you to specify the format of your message in a Flatbuffer schema file, which can then be fed into the Flatbuffer compiler to generate serialization/deserialization code for various programming languages like C, C++, Java, Python, Go and more. The generated code takes a data structure (class, struct, dictionary, etc. depending on the language) and turns it into a buffer of bytes, which can then be saved to disk or sent over a network connection. 

Flat Buffers advertises itself as a solution for high-performance scenarios like games, as Flatbuffers are simple and fast to serialize and deserialize. It is also memory efficient as it does not require any extra allocations: the only allocation required is the resulting buffer of bytes.

## Downsides of a pre-defined format

One large downside to using Flatbuffers in our situation is that it is not schema-less, otherwise known as self-describing. Both sides of the system, the GPS trackers and the edge device, will need to have the code needed to serialize & deserialize these messages. This also means that the edge device will not be able to handle other messages than for the ones we define, which would not allow others to use the same LoRa system as we would like them to be able to. 

One alternative we considered was to allow users to specify the Flatbuffer format of a message using configuration options in OpenRemote. With this option, users would be able to use custom messages, although it would take a lot of technical knowledge to make it work. Another unknown is that this would require parsing the Flatbuffer schema and using it to dynamically parse the incoming data packets, which is not supported by Flatbuffer itself.

## Flexbuffers

As a part of Flatbuffers, there is another type of encoding which is meant for dynamic data. This is data for which the schema is not known before-hand and thus this data needs to be self-describing for programs to be able to parse it correctly. 

This encoding, called Flexbuffers, is based on the datatypes used by Flatbuffers but includes a couple of bytes at the end of the data buffer describing the structure & datatypes of the data. This means that both the encoder & decoder can encode/decode messages without knowing the format of the message beforehand. Flexbuffers were made to be used for dynamic parts of Flatbuffers, but are also usable as a general encoding format.

Just like Flatbuffers, Flexbuffers are cross-platform and there are implementations available for most major languages, including C++ and Python, which are the two languages we are going to be using. The C++ library is also made to be portable and usable on Arduino-based microcontroller

For our use-case, Flexbuffers allow us to make OpenRemote be able to decode any type of Flexbuffer-encoded LoRa message into a JSON-structure, which would allow us to meet the requirement from OpenRemote in making the system flexible enough for other LoRa data messages.

## Making the payload smaller

With a payload which follows the format described above encoded using the Flexbuffer encoding, the resulting payload size of our GPS tracker payload is 113 bytes. While this fits in our payload budget of 245 bytes, getting the payload smaller should make the message faster to send at the slow data rate that we get with the LoRa protocol. And when following the regulatory radio transmission requirements, we would only be able to send such a 113-byte message every 30 seconds. 

Looking at the resulting bytes in hexadecimal shows us that the data is not very densely packed. There are lots of bytes which are zeros and there are also duplicate bytes.

```
00000000: 01100100 01110100 00000000 01101100 01110100 00000000
00000006: 01101100 01100111 00000000 01110011 01110000 00000000
0000000c: 01100001 01101100 00000000 01100011 01110011 00000000
00000012: 00000110 00000111 00000101 00010101 00010000 00010100
00000018: 00001111 00000000 00000000 00000000 00000000 00000000
0000001e: 00000000 00000000 00001101 00000000 00000000 00000000
00000024: 00000000 00000000 00000000 00000000 00000001 00000000
0000002a: 00000000 00000000 00000000 00000000 00000000 00000000
00000030: 00000110 00000000 00000000 00000000 00000000 00000000
00000036: 00000000 00000000 11001000 00000000 00000000 00000000
0000003c: 00000000 00000000 00000000 00000000 00011110 00000000
00000042: 00000000 00000000 00000000 00000000 00000000 00000000
00000048: 11101101 00010010 01111000 01100000 00000000 00000000
0000004e: 00000000 00000000 11001000 10100000 11001001 00101100
00000054: 01111001 10010100 00010111 01000000 10100001 10000101
0000005a: 10110100 00001011 10100001 11100000 01001001 01000000
00000060: 00011110 00000000 00000000 00000000 00000000 00000000
00000066: 00000000 00000000 00000111 00000111 00000111 00001111
0000006c: 00001111 00000111 00110110 00100111 00000001
```

To make the data smaller, we opted to use compression to compress the data.
There are various compression methods which are all have different trade-offs & benefits. One important detail to note is the difference between lossy & loss-less compression formats:
Lossless compression formats compress without losing any data. For example, a hypothetical lossless text compression format could compress “hahahaha” to “ha*4”: The compressed output data is a lot smaller than the input, yet the input data can easily be calculated based on the compressed output and no data is lost.

Lossy compression formats in in contrary do allow losing data but try to do so without losing information. Examples include JPG, H.264 (Usually contained in MP4) and MPEG-2 (usually contained in MP3). After running these compression algorithms, the file should still hold the same information (A song, a video, or a picture), while (usually) smaller in size. For an image for instance, this can mean reducing the number of colors used in the picture so large areas which use the same color can then be compressed just like a lossless format. Lossy compression is all about removing data without losing quality and is (practically) only used for digital media.

Because we want to compress our Flexbuffer-encoded data messages in which all bytes are important, we must use lossless compression to compress our messages. While there are many losless compression formats, there are only a few meant for generic data. Most lossless compression formats have smart algorithms that depend on the structure of the data it is used on, like audio or images.

This brought us to the generic data lossless compression format we are are planning on using, which is zlib. Zlib is originally the name of a library used for compression, based around the DEFLATE compression algorithm. Zlib adds a wrapper around DEFLATE which allows users to decompress data without knowing the compression parameters beforehand, as the compression parameters are built into 2 header bytes in front of the compressed data and an ADLER-32 checksum3 of the original uncompressed data is added to the end of the compressed data.

By using zlib to compress our 113 byte-long messages, we get a resulting compressed size of 80 bytes, which is a reduction of about 30%:

```
00000000: 01111000 10011100 01001011 00101001 01100001 11001000
00000006: 00000001 10100010 01110100 10000110 11100010 00000010
0000000c: 10000110 11000100 00011100 10000110 11100100 01100010
00000012: 00000110 00110110 01110110 01010110 01010001 00000001
00000018: 00010001 01111110 00000110 00001000 11100000 10000101
0000001e: 11010010 10001100 01010000 10011010 00001101 01001010
00000024: 10011111 10000000 11010010 01110010 01010000 11111010
0000002a: 10101101 01010000 01000101 00000010 01011000 01111100
00000030: 11000001 01001001 10011101 11001010 00101001 11100010
00000036: 00001110 00001011 01011011 10110111 01110000 00101111
0000003c: 01111100 11100000 11101001 00000000 10010011 01100111
00000042: 01100111 01100111 11100111 11100111 01100111 00110111
00000048: 01010011 01100111 00000100 00000000 10000010 11000101
0000004e: 00010000 10100011
```

## Transport Security

Transport Security
Our GPS trackers are going to be transmitting their GPS location via LoRa every couple of seconds to send the data to the edge device. Because of the nature of radio technology, this means anyone can easily record, replay, or block the transmitted radio waves for malicious purposes. These techniques can be used to obtain the GPS location of the trackers, to block a location update to reach the edge device or to impersonate one of the trackers.

In most networks, like the IP-based networks we use to connect to the internet, transport security is utilized to mitigate these issues. By making use of public key cryptography and a Diffie-Hellman key exchange, both parties can create an encrypted communication channel to ensure that the data being sent isn’t being snooped on by others and that the data received has not been altered.
In our case, we opted not to go for any of these security measures for a couple of reasons. 
First, adding encryption to the protocol would require a lot of set up for the user. For instance, the user would have to distribute a key to every hardware tracker device so that they can use it for encrypting the data.

Second is that we don’t think the location data is very sensitive in the context in which the system is designed. If you want to eavesdrop on the location data, you will need to be close by in which case you already know where the GPS tracker is.