import platform
import serial


class Card:
    CARD_STATE = False
    CARD_INIT = False
    CARD_CONNECT = False
    PORT = "COM6"  # 윈도우
    # PORT = "/dev/ttyUSB0"  # 리눅스
    if 'Linux' in platform.system():
        PORT = "/dev/ttyUSB1"  # 리눅스
    BAUD = "9600"
    ser = ""

    def sendData(self, temp_str):
        req = ""
        res = ""

        try:
            self.ser = serial.Serial(self.PORT, self.BAUD, timeout=1)

            if temp_str == "hi":  # 연결
                checksum = 0x48 + 0x49 + 0x3f
                req = bytearray([0x24, 0x48, 0x49, 0x3f, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                temp = "".join(map(chr, res))

                if "$me!" in temp:
                    self.CARD_CONNECT = True
                else:
                    self.CARD_CONNECT = False

            elif temp_str == "init":  # 초기화
                checksum = 0x49 + 0x00 + 0x00
                req = bytearray([0x24, 0x49, 0x00, 0x00, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                response = res[1] + res[2] + res[3]
                checksum = res[4]
                print(res)

                if response == checksum:
                    self.CARD_INIT = True
                else:
                    self.CARD_INIT = False

            elif temp_str == "enable":  # 동작
                checksum = 0x48 + 0x43 + 0x3f
                req = bytearray([0x24, 0x48, 0x43, 0x3f, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                temp = "".join(map(chr, res))

                if "$hc!" in temp:
                    self.CARD_STATE = True
                else:
                    self.CARD_STATE = False

            elif temp_str == "disable":  # 동작 금지
                checksum = 0x48 + 0x00 + 0x00
                req = bytearray([0x24, 0x48, 0x00, 0x00, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                response = res[1] + res[2] + res[3]
                checksum = res[4]

                if response == checksum:
                    self.CARD_STATE = False
                else:
                    self.CARD_STATE = True

            elif temp_str == "output":  # 배출
                checksum = 0x44 + 0x01 + 0x53
                req = bytearray([0x24, 0x44, 0x01, 0x53, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                print(res)

            elif temp_str == "state":  # 배출기 상태파악
                checksum = 0x53 + 0x00 + 0x00
                req = bytearray([0x24, 0x53, 0x00, 0x00, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                print(res)

                if res == b'$stb':
                    res = 1  # "대기상태"
                elif res == b'$sonP':
                    res = 2  # "배출 동작중"
                elif res == b'$sth!':
                    res = 3  # "방출기 동작 금지 상태"
                elif res == b'$s\x01o\xe3':
                    res = 4  # "1장 배출 후 정상종료 상태"
                elif res == b'$s\x01n\xe2':
                    res = 5  # "1장 배출 후 비정상종료 상태 or 카드 없음"
                elif res == b'$s\x01n\xe8':
                    res = 6  # "1장 배출 후 도둑 감지상태"
                else:
                    res = 7  # "알수없는 오류"

            elif temp_str == "getErr":
                checksum = 0x53 + 0x45 + 0x52
                req = bytearray([0x24, 0x53, 0x45, 0x52, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))

            self.disconnect()
            return res

        except UnboundLocalError as ex:
            print("액세스 거부", ex)
        except FileNotFoundError as ex:
            print("지정된 포트를 찾을 수 없습니다", ex)
        except Exception as ex:
            print("오류 명령어 >> " + temp_str)
            print("오류를 알 수 없습니다", ex)

    def connectSerial(self):
        try:
            self.ser = serial.Serial(self.PORT, self.BAUD)
        except Exception as e:
            print(e)

    def getCardConnect(self):
        return self.CARD_CONNECT

    def disconnect(self):
        if self.ser:
            if self.ser.isOpen():
                self.ser.close()


if __name__ == "__main__":
    app = Card()
    #app.sendData("enable")
    app.sendData("init")
    #app.sendData("output")
    #app.sendData("disable")