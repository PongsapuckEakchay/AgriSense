from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
import time
import json
import serial  # For reading data from ESP32

# GPIO setup
GPIO.setmode(GPIO.BCM)
RELAY_PIN = 27  # GPIO27
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Initially turn off relay

# Initialize UART for communication with ESP32
uart = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

# AWS IoT connection settings
CLIENT_ID = ""
HOST = "a1s12v1c4f03nn-ats.iot.ap-southeast-2.amazonaws.com"
PORT = 8883
ROOT_CA = "/home/AgriSense/AgriSense_cert/AmazonRootCA1.pem"
PRIVATE_KEY = "/home/AgriSense/AgriSense_cert/ea872fddbf625d0b8bbd7527f5a4c35898976752a224991394d173009d95bcbc-private.pem.key"
CERTIFICATE = "/home/AgriSense/AgriSense_cert/ea872fddbf625d0b8bbd7527f5a4c35898976752a224991394d173009d95bcbc-certificate.pem.crt"

# MQTT Topics (unchanged)
TOPIC_STATUS = "devices/D-101/telemetry"
TOPIC_ENVIRONMENT = "devices/D-101/environment"
TOPIC_WATER_FLOW = "devices/D-101/water_flow"
TOPIC_PUMP_STATUS = "devices/D-101/water_flow"

# Initial pump status
pump_status = "OFF"

# Create an MQTT client
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(HOST, PORT)
mqtt_client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERTIFICATE)

# Configure MQTT client settings
mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline queueing
mqtt_client.configureDrainingFrequency(2)  # Drains 2 messages per second when offline
mqtt_client.configureConnectDisconnectTimeout(10)  # Connection timeout in seconds
mqtt_client.configureMQTTOperationTimeout(5)  # Operation timeout in seconds

# Callback function for pump status update
def pump_status_callback(client, userdata, message):
    global pump_status
    try:
        # Decode the message payload
        payload = json.loads(message.payload.decode("utf-8"))

        # ตรวจสอบว่ามี key 'pump_status' ใน payload หรือไม่
        if "pump_status" in payload:
            new_status = payload["pump_status"].upper()  # Ensure it's uppercase for consistency

            # Update global pump_status and control relay
            if new_status == "ON":
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                print("Relay turned ON (from MQTT)")
            elif new_status == "OFF":
                GPIO.output(RELAY_PIN, GPIO.LOW)
                print("Relay turned OFF (from MQTT)")
            else:
                print(f"Unknown pump_status value: {new_status}")

            # Update global pump_status
            pump_status = new_status
        else:
            # ไม่มี key 'pump_status' ใน payload
            print("No 'pump_status' key found in received payload. Relay state unchanged.")
    except json.JSONDecodeError:
        print("Invalid JSON received for pump_status")

# Connect to AWS IoT Core
print("Connecting to AWS IoT Core...")
mqtt_client.connect()
print("Connected to AWS IoT Core!")

# Subscribe to pump status topic
mqtt_client.subscribe(TOPIC_PUMP_STATUS, 1, pump_status_callback)
print(f"Subscribed to topic: {TOPIC_PUMP_STATUS}")

try:
    while True:
        # Read data from ESP32
        if uart.in_waiting > 0:
            received_data = uart.readline().decode().strip()
            try:
                # Parse the received data as JSON
                json_data = json.loads(received_data)
                
                # Separate payloads and publish to respective topics
                environment_payload = {
                    "ch4": json_data.get("ch4", 0.0),
                    "temp": json_data.get("temp", 0.0),
                    "humidity": json_data.get("humidity", 0.0),
                    "sunlight": json_data.get("sunlight", 0.0),
                    "level": json_data.get("level", 0.0)
                }
                mqtt_client.publish(TOPIC_ENVIRONMENT, json.dumps(environment_payload), 1)
                print(f"Published to {TOPIC_ENVIRONMENT}: {environment_payload}")

                water_flow_payload = {
                    "flow_rate": json_data.get("flow_rate", 0.0),
                    "direction": json_data.get("direction", "IN")
                }
                mqtt_client.publish(TOPIC_WATER_FLOW, json.dumps(water_flow_payload), 1)
                print(f"Published to {TOPIC_WATER_FLOW}: {water_flow_payload}")
                
                telemetry_payload = {
                    "name": json_data.get("name", "unknown_device"),
                    "battery": json_data.get("battery", 0.0),
                    "latitude": json_data.get("latitude", 0.0),
                    "longitude": json_data.get("longitude", 0.0)
                }
                #mqtt_client.publish(TOPIC_STATUS, json.dumps(telemetry_payload), 1)
                #print(f"Published to {TOPIC_STATUS}: {telemetry_payload}")

            except json.JSONDecodeError:
                print("Invalid JSON received from ESP32:", received_data)

        time.sleep(1)

except KeyboardInterrupt:
    print("Disconnecting from AWS IoT Core...")
    mqtt_client.disconnect()
    GPIO.cleanup()
    print("Disconnected!")

