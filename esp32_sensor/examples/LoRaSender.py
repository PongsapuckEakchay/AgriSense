from time import sleep

# Function to send data through LoRa
def send(lora, data):
    """
    Send data via LoRa.
    
    :param lora: SX127x LoRa object
    :param data: String data to be sent
    """
    print("LoRa Sender")
    print('TX: {}'.format(data))  # Display the data being sent
    lora.println(data)            # Send data via LoRa
