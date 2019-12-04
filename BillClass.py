import serial
import platform
import threading
import Config


class Bill:
    BILL_STATE = False           # 지폐인식기 상태
    BILL_CONNECT = False         # 지폐인식기 컨넥션
    PORT = "COM5"  # 윈도우

    if 'Linux' in platform.system():
        # PORT = "/dev/ttyUSB1"    # 리눅스 ver 1.3.0 미만
        PORT = "/dev/serial0"  # 리눅스 ver 1.3.0
    BAUD = "9600"
    ser = ""
    INPUT_MONEY = 0     # 투입금액
    END = False
    global_second = 0
    config = Config.Config()

    def sendData(self, temp_str):
        req = ""  # bytearray
        res = ""  # 바이트 읽어오기

        try:
            self.ser = serial.Serial(self.PORT, self.BAUD, timeout=1)  # 시리얼연결

            if temp_str == "hi":  # connection
                checksum = 0x48 + 0x69 + 0x3f
                req = bytearray([0x24, 0x48, 0x69, 0x3f, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))

                if res:
                    temp = "".join(map(chr, res))

                    if "$me!" in temp:
                        self.BILL_CONNECT = True
                        checksum = 0x65 + 0x73 + 0x0D
                        req = bytearray([0x24, 0x65, 0x73, 0x0D, checksum])
                        res = self.ser.readline(self.ser.write(bytes(req)))
                        print(res)
                    else :
                        self.BILL_CONNECT = False

            elif temp_str == "state": # config 읽기
                checksum = 0x47 + 0x43 + 0x3f
                req = bytearray([0x24, 0x47, 0x43, 0x3f, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                print(res)

            elif temp_str == "insertE":  # 입수가능설정
                checksum = 0x53 + 0x41 + 0x0D
                req = bytearray([0x24, 0x53, 0x41, 0x0D, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))

                if res:
                    temp = "".join(map(chr, res))

                    if "$OKa" in temp:
                        self.BILL_STATE = True
                        checksum = 0x65 + 0x73 + 0x0D
                        req = bytearray([0x24, 0x65, 0x73, 0x0D, checksum])
                        res = self.ser.readline(self.ser.write(bytes(req)))
                    else :
                        self.BILL_STATE = False
                else :
                    self.BILL_STATE = False

            elif temp_str == "get_config": # 설정불러오기
                checksum = 0x47 + 0x43 + 0x3f
                req = bytearray([0x24, 0x47, 0x43, 0x3f, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))

                temp = "".join(map(chr, res))
                search_idx = temp.find("$gc")
                start_idx = search_idx + 4

                if len(res):
                    res = res[start_idx]
                print(res)

            elif temp_str == "set_config": # 설정 저장
                checksum = 0x53 + 0x43 + 0x1f
                req = bytearray([0x24, 0x53, 0x43, 0x1f, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))

                temp = "".join(map(chr, res))
                search_idx = temp.find("$gc")
                start_idx = search_idx + 4

                if len(res):
                    res = res[start_idx]
                print(res)

            elif temp_str == "insertD": # 입수금지설정
                checksum = 0x53 + 0x41 + 0x0E
                req = bytearray([0x24, 0x53, 0x41, 0x0E, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                print(res)

                if res:
                    if len(res) >= 5:
                        response = res[1] + res[2] + res[3]
                        response = response % 256
                        checksum1 = res[4]
                        if response == checksum1:
                            self.BILL_STATE = False
                            checksum = 0x65 + 0x73 + 0x0E
                            req = bytearray([0x24, 0x65, 0x73, 0x0E, checksum])
                            res = self.ser.readline(self.ser.write(bytes(req)))
                        else:
                            self.BILL_STATE = True
                else:
                    self.BILL_STATE = True

            elif temp_str == "billData": # 지폐권종파악
                checksum = 0x47 + 0x42 + 0x3f
                req = bytearray([0x24, 0x47, 0x42, 0x3f, checksum])
                res1 = self.ser.readline(self.ser.write(bytes(req)))
                temp = list()
                for c in res1:
                    temp.append(hex(c)[2:])
                print(temp)

                if res1:
                    if len(res1) >= 4:
                        temp = "".join(map(chr, res1))
                        search_idx = temp.find("$gb")
                        start_idx = search_idx + 3

                        if search_idx >= 0:
                            if res1[start_idx] == 1:
                                res = 1000
                            elif res1[start_idx] == 5:
                                res = 5000
                            elif res1[start_idx] == 10:
                                res = 10000
                            elif res1[start_idx] == 50:
                                res = 50000
                            else:
                                res = 0
                        else:
                            res = 0

                    event_tx_idx = temp.find("$ES")

                    if event_tx_idx >= 0:
                        checksum = 0x65 + 0x73 + res1[event_tx_idx + 3]
                        req = bytearray([0x24, 0x65, 0x73, res1[event_tx_idx + 3], checksum])
                        self.ser.readline(self.ser.write(bytes(req)))
                else:
                    res = 0

            elif temp_str == "checkStatus":
                checksum = 0x53 + 0x41 + 0x0E
                req = bytearray([0x24, 0x53, 0x41, 0x0E, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                res = res[:4].decode()
                print(res)

            elif temp_str == "return_bill": # 지폐 반환하기
                checksum = 0x53 + 0x41 + 0x06
                req = bytearray([0x24, 0x53, 0x41, 0x06, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))
                temp = "".join(map(chr, res))
                print(res)

            elif temp_str == "getActiveStatus":
                checksum = 0x47 + 0x41 + 0x3f
                req = bytearray([0x24, 0x47, 0x41, 0x3f, checksum])
                res = self.ser.readline(self.ser.write(bytes(req)))

                if res:
                    temp = "".join(map(chr, res))
                    search_idx = temp.find("$ga")
                    start_idx = search_idx + 3

                    if search_idx >= 0:
                        if len(res):
                            res = res[start_idx]

                    event_tx_idx = temp.find("$ES")  # 보내줘야 더이상 안보냄

                    if event_tx_idx >= 0:
                        checksum = 0x65 + 0x73 + res[event_tx_idx + 3]
                        req = bytearray([0x24, 0x65, 0x73, res[event_tx_idx + 3], checksum])
                        self.ser.readline(self.ser.write(bytes(req)))

            # print(type(res))
            self.disconnect()
            return res

        except UnboundLocalError as ex:
            print("액세스 거부", ex)
            self.BILL_CONNECT = False
        except FileNotFoundError as ex:
            print("지정된 포트를 찾을 수 없습니다. ", ex)
            self.BILL_CONNECT = False
        except UnicodeDecodeError as ex:
            print("디코딩 오류", ex)
            self.BILL_CONNECT = False
        except serial.serialutil.SerialException as ex:
            print("오류 명령어 >> " + temp_str)
            print("시리얼 오류", ex)
            self.BILL_CONNECT = False
        except Exception as ex:
            print("오류 명령어 >>" + temp_str)
            print('오류를 알 수 없습니다.', ex)
            self.config.error_log(str(ex), "지폐인식기 에러")
            print(str(ex))
            self.BILL_CONNECT = False

    def checkBillData(self, second=1.0):
        if self.END:
            return
        # 지폐인식기의 투입상태 검사 후 금지면 활성화하는 로직 추가
        state = self.sendData('getActiveStatus')

        if state == 1 or state == 11:
            res = self.sendData("billData")
            self.INPUT_MONEY += res
            self.sendData('insertE')

        self.global_second += 1

        if self.global_second > 15:
            self.sendData('insertD')
            self.END = True

        threading.Timer(second, self.checkBillData).start()

    def connectSerial(self):
        try:
            self.ser = serial.Serial(self.PORT, self.BAUD, timeout=1)
        except Exception as e:
            print(e)

    def disconnect(self):
        if self.ser:
            if self.ser.isOpen():
                self.ser.close()

    def get_billstate(self):
        return self.BILL_STATE

    def get_billconnect(self):
        return self.BILL_CONNECT

    def get_Inputmoney(self):
        return self.INPUT_MONEY

    def get_Activestatus(self, num):
        if num == 0:
            return "리셋 후 초기화 동작중"
        elif num == 1:
            return "초기화 후 대기중"
        elif num == 2:
            return "입수가능"
        elif num == 3:
            return "인식작업 중 오류로 인한 반환 작업 중"
        elif num == 4:
            return "인식작업 중"
        elif num == 5:
            return "인식작업 완료 후 대기 중(입수금지상태)"
        elif num == 7:
            return "반환동작 중"
        elif num == 8:
            return "반환동작 완료 후 대기 중(입수 금지상태)"
        elif num == 10:
            return "stack 동작 중"
        elif num == 11:
            return "stack 동작 완료 후 대기 중 (입수금지상태)"
        elif num == 12:
            return "동작 Error로 인한 대기중"
        elif num == 16:
            return "stack이 open된 상태(입수금지상태)"
        elif num == 17:
            return "강제 입수 동작 중"
        elif num == 18:
            return "강제 입수 완료 후 대기중"
        else:
            return num


if __name__ == '__main__':
    app = Bill()
    app.sendData("insertE")
    #app.sendData("insertD")
    #app.sendData("billData")


