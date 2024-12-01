# AgriSense IoT - Smart Rice Field Management System

ระบบ IoT สำหรับการจัดการน้ำในนาข้าวอัจฉริยะ เพื่อลดการปล่อยก๊าซเรือนกระจกและสร้างรายได้จากคาร์บอนเครดิต

## 🛠 Technical Components

### Hardware
- ESP32 Microcontroller
- DHT20 Temperature & Humidity Sensor
- HC-SR04 Ultrasonic Water Level Sensor
- LoRa SX127x Module
- Methane (CH4) Gas Sensor
- Water Flow Sensor
- Relay Module for Water Gate Control
- Raspberry Pi (Gateway)

### Network Architecture
- Device Layer: ESP32 with sensors
- Communication: LoRa (433MHz) for sensor data transmission
- Gateway: Raspberry Pi with LoRa receiver
- Cloud: AWS IoT Core

### Communication Protocols
- LoRa Parameters:
  - Frequency: 433MHz
  - Bandwidth: 125kHz
  - Spreading Factor: 9
  - Coding Rate: 5
  - TX Power: 14dBm
- UART (9600 baud) between ESP32s
- MQTT for cloud communication

## 📡 Data Flow
1. Sensor data collection (ESP32 + Sensors)
2. LoRa transmission to gateway
3. Gateway processes and formats data
4. Data uploaded to AWS IoT Core via MQTT
5. Cloud processing and storage
6. Web application display and control

## 📦 Project Structure
```
/
├── esp32_GW/               # ESP32 Gateway node code
│   ├── examples/           # LoRa examples
│   ├── boot.py            # Boot configuration
│   ├── main.py            # Gateway main code
│   └── sx127x.py          # LoRa module library
│
├── esp32_sensor/          # ESP32 Sensor node code
│   ├── examples/          # LoRa examples
│   ├── boot.py            # Boot configuration
│   ├── dht20.py          # DHT20 sensor library
│   ├── main.py           # Sensor node main code
│   └── sx127x.py         # LoRa module library
│
├── README.md             # Project documentation
└── raspi_gateway.py      # Raspberry Pi AWS connector
```

## 🔌 Pin Configuration

### Sensor Node (ESP32)
```python
# DHT20
SCL = Pin(22)
SDA = Pin(21)

# HC-SR04
TRIG_PIN = Pin(4)
ECHO_PIN = Pin(0)

# LoRa
dio_0 = Pin(26)
ss = Pin(18)
reset = Pin(16)
sck = Pin(5)
miso = Pin(19)
mosi = Pin(27)
```

### Gateway Node (ESP32)
```python
# UART
TX = Pin(22)
RX = Pin(21)

# LoRa (Same as sensor node)
dio_0 = Pin(26)
ss = Pin(18)
reset = Pin(16)
sck = Pin(5)
miso = Pin(19)
mosi = Pin(27)
```

## 🔧 Installation & Setup

1. Flash ESP32 Firmware:
```bash
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 firmware.bin
```

2. Install Required Libraries:
```bash
pip install AWSIoTPythonSDK
pip install RPi.GPIO
```

3. Configure AWS IoT:
   - Create IoT thing
   - Generate and download certificates
   - Update certificate paths in `raspi_gateway.py`

4. Update MQTT Topics:
```python
TOPIC_STATUS = "devices/D-101/telemetry"
TOPIC_ENVIRONMENT = "devices/D-101/environment"
TOPIC_WATER_FLOW = "devices/D-101/water_flow"
```

## 📊 Data Format

### Sensor Payload (JSON)
```json
{
  "ch4": 0.15,
  "temp": 30.2,
  "humidity": 60.5,
  "sunlight": 1300.0,
  "level": 4.5,
  "flow_rate": 12.5,
  "direction": "OUT",
  "pump_status": "ON",
  "latitude": 12.7563,
  "longitude": 100.5018,
  "battery": 90.0,
  "name": "pump-01"
}
```

## 🔒 Security
- AWS IoT device authentication using X.509 certificates
- MQTT over TLS
- Secure storage of credentials on Raspberry Pi

## 🚀 Future Improvements
- Implement OTA updates
- Add battery monitoring
- Enhance error handling
- Implement data backup mechanism
- Add support for multiple gateways
