import serial
import time

class Pixy2(object):
    PIXY_DEFAULT_ARGVAL                  = 0x80000000
    PIXY_BUFFERSIZE                      = 0x104
    PIXY_CHECKSUM_SYNC                   = 0xc1af
    PIXY_NO_CHECKSUM_SYNC                = 0xc1ae
    PIXY_SEND_HEADER_SIZE                = 4
    PIXY_MAX_PROGNAME                    = 33
    PIXY_TYPE_REQUEST_CHANGE_PROG        = 0x02
    PIXY_TYPE_REQUEST_RESOLUTION         = 0x0c
    PIXY_TYPE_RESPONSE_RESOLUTION        = 0x0d
    PIXY_TYPE_REQUEST_VERSION            = 0x0e
    PIXY_TYPE_RESPONSE_VERSION           = 0x0f
    PIXY_TYPE_RESPONSE_RESULT            = 0x01
    PIXY_TYPE_RESPONSE_ERROR             = 0x03
    PIXY_TYPE_REQUEST_BRIGHTNESS         = 0x10
    PIXY_TYPE_REQUEST_SERVO              = 0x12
    PIXY_TYPE_REQUEST_LED                = 0x14
    PIXY_TYPE_REQUEST_LAMP               = 0x16
    PIXY_TYPE_REQUEST_FPS                = 0x18
    PIXY_TYPE_REQUEST_CCC                = 0x20
    PIXY_TYPE_REQUEST_MAIN_FEATURES      = 0x30
    PIXY_TYPE_REQUEST_MODE               = 0x36
    PIXY_TYPE_REQUEST_NEXT_TURN          = 0x3a
    PIXY_TYPE_REQUEST_DEFAULT_TURN       = 0x3c
    PIXY_TYPE_REQUEST_VECTOR             = 0x38
    PIXY_TYPE_REQUEST_REVERSE_VECTOR     = 0x3e
    PIXY_TYPE_REQUEST_VIDEO              = 0x70
    PIXY_RESULT_OK                       = 0
    PIXY_RESULT_ERROR                    = -1
    PIXY_RESULT_BUSY                     = -2
    PIXY_RESULT_CHECKSUM_ERROR           = -3
    PIXY_RESULT_TIMEOUT                  = -4
    PIXY_RESULT_BUTTON_OVERRIDE          = -5
    PIXY_RESULT_PROG_CHANGING            = -6
    PIXY_RCS_MIN_POS                     = 0
    PIXY_RCS_MAX_POS                     = 1000
    PIXY_RCS_CENTER_POS                  = ((PIXY_RCS_MAX_POS-PIXY_RCS_MIN_POS)/2)
    def __init__(self):
        self.serial = serial.Serial()
        self.serial.port = "COM6"
        self.serial.baudrate = 19200
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.timeout = 1
        self.send_msg = ""
        self.recv_msg = ""

    def open(self):
        try:
            if not self.serial.isOpen():
                self.serial.open()
        except:
            print("except : open")

    def close(self):
        try:
            if self.serial.isOpen():
                self.serial.close()
        except:
            print("except : close")

    def send_packet(self, _type, _data:bytes=[]):
        try:
            self.open()
            buffer = bytearray()
            header = Pixy2.PIXY_NO_CHECKSUM_SYNC.to_bytes(2, 'little')
            buffer.append(header[0])
            buffer.append(header[1])
            buffer.append(int(_type))
            buffer.append(len(_data) & 0xff)
            for byte in _data:
                buffer.append(byte)
            print(buffer)
            self.serial.write(buffer)
        except Exception as e:
            print("except : write " + str(e))

    def read(self, timeout=5):
        timer = time.time()
        try:
            buffer = bytearray()
            data = bytearray()
            start = False
            while True:
                if time.time() - timer > timeout:
                    break
                if self.serial.readable:
                    recv = self.serial.read()
                    if len(recv) == 0:
                        break
                    if start == False and recv[0] == 0xaf:
                        start = True
                    if start == True:
                        buffer.append(recv[0])
                        if len(buffer) > 4:
                            if int.from_bytes(buffer[0:2], byteorder='little') == Pixy2.PIXY_CHECKSUM_SYNC:
                                length = buffer[3]
                                if len(buffer) >= length + 6:
                                    checksum = int.from_bytes(buffer[4:6], byteorder='little')
                                    datasum = 0
                                    for i in range(6, 6 + length):
                                        datasum += buffer[i]
                                        data.append(buffer[i])
                                    if checksum == datasum:
                                        print(buffer)
                                        return True, data
                                    break
                else:
                    break
                # time.sleep(0.00001)
            return False, []
        except Exception as e:
            print(e)
            return False, []
    
    def cmd(self, _type, _data:bytes=[]):
        self.send_packet(_type, _data)
        return self.read()

    def change_prog(self, prog:str = ""):
        data = prog.encode()
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_CHANGE_PROG, data)

    def get_version(self):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_VERSION)

    def get_resolution(self):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_RESOLUTION)

    def get_frame_width(self, data_array):
        if len(data_array) < 2:
            return None
        return int.from_bytes(data_array[0:2], byteorder='little')

    def get_frame_height(self, data_array):
        if len(data_array) < 4:
            return None
        return int.from_bytes(data_array[2:4], byteorder='little')

    def set_camera_brightness(self, brightness):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_BRIGHTNESS, [brightness])

    def set_led(self, r, g, b):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_LED, [r, g, b])

    def set_lamp(self, upper, lower):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_LAMP, [upper, lower])

    def get_fps(self):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_FPS)

    # CCC 0-255, 0-255
    def get_blocks(self, sigmap, max_blocks):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_CCC, [sigmap, max_blocks])

    def get_color_code(self, blocks_array):
        if len(blocks_array) < 2:
            return None
        return int.from_bytes(blocks_array[0:2], byteorder='little')

    def get_x_center(self, blocks_array):
        if len(blocks_array) < 4:
            return None
        return int.from_bytes(blocks_array[2:4], byteorder='little')

    def get_y_center(self, blocks_array):
        if len(blocks_array) < 6:
            return None
        return int.from_bytes(blocks_array[4:6], byteorder='little')
    
    def get_width(self, blocks_array):
        if len(blocks_array) < 8:
            return None
        return int.from_bytes(blocks_array[6:8], byteorder='little')

    def get_height(self, blocks_array):
        if len(blocks_array) < 10:
            return None
        return int.from_bytes(blocks_array[8:10], byteorder='little')

    def get_angle(self, blocks_array):
        if len(blocks_array) < 12:
            return None
        return int.from_bytes(blocks_array[10:12], byteorder='little')

    def get_index(self, blocks_array):
        if len(blocks_array) < 13:
            return None
        return int.from_bytes(blocks_array[12:13], byteorder='little')

    def get_age(self, blocks_array):
        if len(blocks_array) < 14:
            return None
        return int.from_bytes(blocks_array[13:14], byteorder='little')

    # Video 0-315, 0-207, 0-1
    def get_rgb(self, x, y, saturate):
        x_bytes = x.to_bytes(2, 'little')
        y_bytes = y.to_bytes(2, 'little')
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_VIDEO, [x_bytes[0], x_bytes[1], y_bytes[0], y_bytes[1], saturate])

    # Line 0 Main -1 All, 1 vector ,2 intersection ,4 barcode
    def get_main_features(self, req_type, features):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_MAIN_FEATURES, [req_type, features])

    def set_mode(self, mode):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_MODE, [mode])

    def set_next_turn(self, angle):
        angle_bytes = angle.to_bytes(2, 'little')
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_NEXT_TURN, [angle_bytes[0], angle_bytes[1]])

    def set_default_turn(self, angle):
        angle_bytes = angle.to_bytes(2, 'little')
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_DEFAULT_TURN, [angle_bytes[0], angle_bytes[1]])

    def set_vector(self, index):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_VECTOR, [index])

    def reverse_vector(self):
        return self.cmd(Pixy2.PIXY_TYPE_REQUEST_REVERSE_VECTOR)

if __name__ == '__main__':
    print("start")
    pixy2 = Pixy2()
    # pixy2.get_version()
    # pixy2.get_resolution()
    # pixy2.get_fps()
    # pixy2.change_prog("Raspi")
    result, data = pixy2.get_blocks(1, 1)
    if result :
        color = pixy2.get_color_code(data)
        print(color)
        x = pixy2.get_x_center(data)
        print(x)
        y = pixy2.get_y_center(data)
        print(y)
        width = pixy2.get_width(data)
        print(width)
        height = pixy2.get_height(data)
        print(height)
        angle = pixy2.get_angle(data)
        print(angle)
        idx = pixy2.get_index(data)
        print(idx)
        age = pixy2.get_age(data)
        print(age)
    # pixy2.get_rgb(0, 0, 0)
