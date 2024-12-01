import time
import struct

class DHT20:
    def __init__(self, i2c, address=0x38):
        self.i2c = i2c
        self.address = address
        self._initialize()

    def _initialize(self):
        # เขียนค่าเริ่มต้นให้เซ็นเซอร์
        self.i2c.writeto(self.address, b'\xAC\x33\x00')
        time.sleep(0.1)

    def measure(self):
        # ส่งคำสั่งให้เซ็นเซอร์เริ่มอ่านค่า
        self.i2c.writeto(self.address, b'\xAC\x33\x00')
        time.sleep(0.1)
        # อ่านค่าข้อมูล 7 ไบต์จากเซ็นเซอร์
        data = self.i2c.readfrom(self.address, 7)

        if data[0] & 0x80:
            raise Exception("Sensor not ready")

        # คำนวณความชื้นและอุณหภูมิ
        self.humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / 1048576
        self.temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) * 200 / 1048576 - 50

    def temperature(self):
        return self.temperature

    def humidity(self):
        return self.humidity
