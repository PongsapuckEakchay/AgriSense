from machine import Pin, SPI, UART
from sx127x import SX127x
import json

# Initialize UART1 with TX on Pin 22 and RX on Pin 21
uart1 = UART(1, baudrate=9600, tx=Pin(22), rx=Pin(21))

# Sensor data to be updated from LoRa
sensor_data = {
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

# LoRa Configuration
lora_default = {
    'frequency': 433000000,
    'frequency_offset': 0,
    'tx_power_level': 14,
    'signal_bandwidth': 125e3,
    'spreading_factor': 9,
    'coding_rate': 5,
    'preamble_length': 8,
    'implicitHeader': False,
    'sync_word': 0x12,
    'enable_CRC': True,
    'invert_IQ': False,
    'debug': False,
}

lora_pins = {
    'dio_0': 26,
    'ss': 18,
    'reset': 16,
    'sck': 5,
    'miso': 19,
    'mosi': 27,
}

# Initialize SPI for LoRa
lora_spi = SPI(
    baudrate=10000000, polarity=0, phase=0,
    bits=8, firstbit=SPI.MSB,
    sck=Pin(lora_pins['sck'], Pin.OUT, Pin.PULL_DOWN),
    mosi=Pin(lora_pins['mosi'], Pin.OUT, Pin.PULL_UP),
    miso=Pin(lora_pins['miso'], Pin.IN, Pin.PULL_UP),
)

# Initialize LoRa
lora = SX127x(lora_spi, pins=lora_pins, parameters=lora_default)

def parse_sensor_data(payload):
    """Parse the sensor data from the LoRa payload"""
    try:
        # Extract temperature
        if "Temperature:" in payload:
            temp_str = payload.split("Temperature: ")[1].split("°C,")[0]
            sensor_data["temp"] = float(temp_str)
            print("Updated temperature:", temp_str)
            
        # Extract humidity
        if "Humidity:" in payload:
            hum_str = payload.split("Humidity: ")[1].split("%")[0]
            sensor_data["humidity"] = float(hum_str)
            print("Updated humidity:", hum_str)
            
        # Extract level
        if "Level:" in payload:
            level_str = payload.split("Level: ")[1].split("cm")[0]
            # Convert cm to m
            sensor_data["level"] = float(level_str) 
            print("Updated level:", level_str, "cm")
            
        return True
        
    except Exception as e:
        print("Error parsing sensor data:", e)
        return False

def receive(lora):
    """
    Receive data from LoRa and forward via UART
    """
    print("LoRa Receiver with UART Forwarding")
    print("Waiting for incoming messages...")

    while True:
        if lora.receivedPacket():
            try:
                # Read LoRa payload
                payload = lora.readPayload().decode()
                rssi = lora.packetRssi()
                
                # Print received data to console
                print("LoRa RX: {} | RSSI: {}".format(payload, rssi))
                
                # Parse and update sensor data
                if parse_sensor_data(payload):
                    # Send complete sensor_data via UART
                    json_payload = json.dumps(sensor_data)
                    uart1.write(json_payload + "\n")
                    print("UART TX:", json_payload)
                
            except Exception as e:
                print("Error processing message:", e)

if __name__ == '__main__':
    receive(lora)