from machine import Pin, I2C, SPI, time_pulse_us
from time import sleep
from dht20 import DHT20
from sx127x import SX127x
from examples import LoRaSender

# ----- DHT20 Configuration -----
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # I2C pins for DHT20
dht = DHT20(i2c)

# ----- HC-SR04 Configuration -----
TRIG_PIN = 4  # GPIO13
ECHO_PIN = 0  # GPIO12
trigger = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# ----- LoRa Configuration -----
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

def measure_distance_cm():
    """
    Measure distance using HC-SR04 sensor
    Returns distance in centimeters
    """
    try:
        # Ensure trigger starts low
        trigger.value(0)
        sleep(0.1)  # 100ms delay between measurements
        
        # Send trigger pulse
        trigger.value(1)
        sleep(0.00001)  # 10 microseconds delay
        trigger.value(0)
        
        # Wait for echo with timeout
        duration = time_pulse_us(echo, 1, 30000)
        
        # Check if duration is valid
        if duration < 0:
            return None
            
        # Calculate distance in centimeters
        distance_cm = (duration * 0.0343) / 2
        
        # Validate reading (typical range 2cm to 400cm)
        if 2 <= distance_cm <= 400:
            return round(distance_cm)
        return None
        
    except Exception as e:
        print("Measurement error:", e)
        return None

def read_dht():
    """
    Read temperature and humidity from DHT20
    Returns tuple of (temperature, humidity) or (None, None) on error
    """
    try:
        dht.measure()
        temperature = dht.temperature
        humidity = dht.humidity
        return temperature, humidity
    except Exception as e:
        print("DHT20 error:", e)
        return None, None

def main():
    print("LoRa Multi-sensor Sender")
    print("Sending DHT20 and HC-SR04 measurements...")
    
    while True:
        try:
            # Read DHT20
            temperature, humidity = read_dht()
            
            # Read HC-SR04
            distance = measure_distance_cm()
            
            # Create message if readings are valid
            if temperature is not None and humidity is not None and distance is not None:
                message = f"Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%, Level: {distance}cm"
                
                # Send via LoRa
                print("TX:", message)
                LoRaSender.send(lora, message)
            else:
                print("Invalid sensor readings")
                
            # Wait before next reading
            sleep(5)
            
        except Exception as e:
            print("Error in main loop:", e)
            sleep(5)

if __name__ == '__main__':
    main()