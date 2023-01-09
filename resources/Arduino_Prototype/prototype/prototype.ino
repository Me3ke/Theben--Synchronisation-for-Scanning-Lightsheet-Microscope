#include <SPI.h>
#ifdef __AVR_ATmega2560__
  const byte CLOCKOUT = 11;  // Mega 2560
#else
  const byte CLOCKOUT = 9;   // Uno, Duemilanove, etc.
#endif
int baudrate = 9600;

void send(int channel, int V) {
  digitalWrite(SS, LOW);
  byte commandb1 = 0x03;
  byte commandb2 = (channel << 4) | ((V & 0x0F00) >> 8);
  byte commandb3 = V & 0x0FF;
  byte commandb4 = 0x00;
  SPI.transfer(commandb1);
  SPI.transfer(commandb2);
  SPI.transfer(commandb3);
  SPI.transfer(commandb4);
  digitalWrite(SS, HIGH);

  //Serial.println(commandb2, DEC);
  //Serial.println(commandb3, DEC);
}

void useInternalRefVoltage() {
  digitalWrite(SS, LOW);
  byte commandb1 = 0x08;
  byte commandb2 = 0x00;
  byte commandb3 = 0x01;
  SPI.transfer(commandb1);
  SPI.transfer(commandb2);
  SPI.transfer(commandb2);
  SPI.transfer(commandb3);
  digitalWrite(SS, HIGH);
}

void clearVoltages() {
  send(0x0F, 0x000);
}

void setup() {
  Serial.begin(baudrate);
  Serial.println("hello");
  SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  SPI.setDataMode(SPI_MODE1);
  delay(1000);
  useInternalRefVoltage();
  clearVoltages();
  Serial.println("finished setup");
}

void triggerCam() {
  pinMode (2, OUTPUT);
  digitalWrite(2, HIGH);
  digitalWrite(2, LOW);
}

float slopeValues[] = {0.0000,  0.00230, 0.00470, 0.00567, 0.01056, 0.01389, 0.02120, 0.02944, 0.03732, 0.05063, 0.06488, 0.08400, 0.10367, 0.12682, 0.15291, 0.18212, 0.21451, 0.25225, 0.29008, 0.33306, 0.37855, 0.42789, 0.48126, 0.53757, 0.59711, 0.65829, 0.71645, 0.77882, 0.84167, 0.90096, 0.95912, 1.02536, 1.08954, 1.14092, 1.19670, 1.25124, 1.30274, 1.34852, 1.39325, 1.42950, 1.46376, 1.49178, 1.51156, 1.53039, 1.54400, 1.54837, 1.54444, 1.53274, 1.51709, 1.49353, 1.46680, 1.42992, 1.38684, 1.34005, 1.28784, 1.23249, 1.16617, 1.10937, 1.03202, 0.95563, 0.87502, 0.80487, 0.72248, 0.64366, 0.55386, 0.47008, 0.37947, 0.29656, 0.21059, 0.13184, 0.05721, -0.01622, -0.08361, -0.15035, -0.21094, -0.26502, -0.31623, -0.36233, -0.40302, -0.43849, -0.46762, -0.48788, -0.50282, -0.51582, -0.51884, -0.50951, -0.49633, -0.48009, -0.45763, -0.42999, -0.39824, -0.36064, -0.31386, -0.26798, -0.21726, -0.16527, -0.10561, -0.04676, 0.01186, 0.07330, 0.13024, 0.19185, 0.25440, 0.31042, 0.37269, 0.42807, 0.48426, 0.54119, 0.58734, 0.64046, 0.68464, 0.72661, 0.76553, 0.79940, 0.82910, 0.85855, 0.88487, 0.90454, 0.92142, 0.93929, 0.95344, 0.96473, 0.97289, 0.98068, 0.98592, 0.99071, 1};
byte incomingByte;
byte number = 0;
long inputValues[] = {1024, 1034, 1044, 1054, 1064, 1074, 1084, 1094, 1104, 1114, 1124, 1134, 1144, 1154, 1164, 1174, 1184, 1194, 1204, 1214, 1224, 1234, 1244, 1254, 1264, 1274, 1284, 1294, 1304, 1314, 1324, 1334, 1344, 1354, 1364, 1374, 1384, 1394, 1404, 1414, 1424, 1434, 1444, 1454, 1464, 1474, 1484, 1494, 1504, 1514, 1524, 1534, 1544, 1554, 1564, 1574, 1584, 1594, 1604, 1614, 1624, 1634, 1644, 1654, 1664, 1674, 1684, 1694, 1704, 1714, 1724, 1734, 1744, 1754, 1764, 1774, 1784, 1794, 1804, 1814, 1824, 1834, 1844, 1854, 1864, 1874, 1884, 1894, 1904, 1914, 1924, 1934, 1944, 1954, 1964, 1974, 1984, 1994, 2004, 2014, 2024, 2034, 2044, 2054, 2064, 2074, 2084, 2094, 2104, 2114, 2124, 2134, 2144, 2154, 2164, 2174, 2184, 2194, 2204, 2214, 2224, 2234, 2244, 2254, 2264, 2274, 2284, 2294, 2304, 2314, 2324, 2334, 2344, 2354, 2364, 2374, 2384, 2394, 2404, 2414, 2424, 2434, 2444, 2454, 2464, 2474, 2484, 2494, 2504, 2514, 2524, 2534, 2544, 2554, 2564, 2574, 2584, 2594, 2604, 2614, 2624, 2634, 2644, 2654, 2664, 2674, 2684, 2694, 2704, 2714, 2724, 2734, 2744, 2754, 2764, 2774, 2784, 2794, 2804, 2814, 2824, 2834, 2844, 2854, 2864, 2874, 2884, 2894, 2904, 2914, 2924, 2934, 2944, 2954, 2964, 2974, 2984, 2994, 3004, 3014};



void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    number = incomingByte - 48;
    Serial.print("read: ");
    Serial.println(number, DEC);
    if (number == 1) {
      int byteNumber = 0;
      long value_n = 0;
      byte valueInput[4];
      Serial.println("Type in voltage value (0000..4095):");
      while (Serial.available() == 0) {}
      Serial.readBytes(valueInput, 4);
      int size = sizeof(valueInput)/sizeof(valueInput[0]);
      Serial.print("size:");
      Serial.println(size, DEC);
      for (int i = 0; i < size; i++) {
        value_n = value_n * 10 + valueInput[i] - 48;
        Serial.println("value now: ");
        Serial.println(value_n, DEC);
      }
      Serial.println("finished");
      send(0, value_n);
    }
    if (number == 2) {
      Serial.println("Clearing Voltages");
      clearVoltages();
    }
    if (number == 3) {
      Serial.println("looping though all values");
      int size = sizeof(inputValues)/sizeof(inputValues[0]);        //!!!!!
      Serial.println(size);
      for (int i = 0; i < 410; i++) {
        send(0, inputValues[i]);
        delay(10);
      }
      Serial.println("finished");
      delay(5000);
      clearVoltages();
    }
    if (number == 5) {
      triggerCam();
    }
    if (number == 9) {
      SPI.end();
    }
  }
}