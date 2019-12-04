# ver 1.2.5
import sys
from smartcard.scard import *
import Config as con
import platform
import time
from collections import OrderedDict
from smartcard.System import readers
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import *
import requests
import json
import os


class transmitobserver(CardObserver):
    config = con.Config()
    init_state = "0"
    charge_state = "0"
    lookup_state = "0"
    CHARGE_FLAG = False
    ISSUED_FLAG = False
    INIT_FLAG = False
    LOOKUP_FLAG = False
    ISSUED_ENABLE = True

    input_money = 0
    bonus = 0
    use_bonus = 0
    input_cash = 0
    card_remain_money = 0
    total_money = 0

    use_money = 0

    current_money = 0
    current_bonus = 0

    buzzer_reader = ""
    member_class = ""
    mb_level = ""

    UID_BYTE = [0xFF, 0xCA, 0x00, 0x00, 0x04]  # 시리얼 번호 바이트
    LOAD_KEY_SELECT = [0xFF, 0x82, 0x00, 0x00, 0x06]  # 로드 키 셀렉트

    AUTH_SELECT = [0xFF, 0x86, 0x00, 0x00, 0x05]  # 인증 셀렉트
    AUTH_DF = [0x01, 0x00, 0x00, 0x60, 0x00]  # 인증 데이터

    READ_BINARY_SELECT = [0xFF, 0xB0, 0x00, 0x01, 0x10]  # 1번 바이너리 블록 셀렉트
    READ_BINARY_SELECT_2 = [0xFF, 0xB0, 0x00, 0x02, 0x10]  # 2번 바이너리 블록 셀렉트

    UPDATE_BINARY_SELECT = [0xFF, 0xD6, 0x00, 0x01, 0x10]  # 1번 업데이트 바이너리 블록 셀렉트
    UPDATE_BINARY_SELECT_2 = [0xFF, 0xD6, 0x00, 0x02, 0x10]  # 2번 업데이트 바이너리 블록 셀렉트

    BUZZER_BYTE = [0xE0, 0x00, 0x00, 0x28, 0x01, 0x0A]  # 부저 바이트

    """A card observer that is notified when cards are inserted/removed
    from the system, connects to cards and SELECT DF_TELECOM """

    # get xor byte
    def get_xor_hex(self, code):
        a = code
        b = 0xFF
        c = a ^ b
        res = hex(c).upper()

        return res

    # get init update binary block byte
    def get_req_byte(self, serial_number, master_byte1, master_byte2):
        self.config.load_config()
        shop_id = self.config.get_config("id")
        compare_master_byte = self.get_master_card_crc(serial_number)
        mny = 0
        if self.config.get_config("encrypt") == "1":
            temp = hex(mny)[2:].rjust(8, '0')  # 정수로 들어옴
            temp = temp.upper()
            shop_id = format(int(shop_id), 'x').rjust(4, "0").upper()

            compare_result = int(int(temp, 16) / 1000)
            total = compare_result + int(serial_number, 16)
            temp_namuji = (total % 100)

            arg1 = int(temp[4:6], 16)
            arg2 = int(temp[6:8], 16)
            arg3 = int(temp[2:4], 16)
            arg4 = int(temp[0:2], 16)
            arg5 = int(self.config.crc[temp_namuji], 16)
            shop_total = int(serial_number, 16) + int(shop_id, 16)
            shop_namnuji = (shop_total % 100)
            shop1 = int(shop_id[0:2], 16)
            shop2 = int(shop_id[2:4], 16)
            arg10 = int(self.config.crc[shop_namnuji], 16)
            manager_no = int(self.config.get_config("manager_no"))

            if master_byte1 == 11 and master_byte2 == compare_master_byte:
                arg1 = 0
                arg2 = 0
                arg3 = 0
                arg4 = 0
                arg5 = 0

            req_byte = [arg1, arg2, arg3, arg4, arg5, 0x00, 0x00, 0x00, 0x00, 0x00, manager_no, master_byte1,
                        master_byte2, arg10, shop1, shop2]  # 신버전

        else:
            temp = hex(mny)[2:].rjust(8, '0')  # 정수로 들어옴
            shop_id = format(int(shop_id), 'x').rjust(4, "0").upper()
            temp = temp.upper()
            arg1 = int(temp[4:6], 16)
            arg2 = int(temp[6:8], 16)
            arg3 = int(temp[2:4], 16)
            arg4 = int(temp[0:2], 16)

            arg1_reverse = self.get_xor_hex(arg1)
            arg2_reverse = self.get_xor_hex(arg2)
            arg3_reverse = self.get_xor_hex(arg3)
            arg4_reverse = self.get_xor_hex(arg4)

            arg5 = int(arg1_reverse, 16)
            arg6 = int(arg2_reverse, 16)
            arg7 = int(arg3_reverse, 16)
            arg8 = int(arg4_reverse, 16)

            shop1 = int(shop_id[0:2], 16)
            shop2 = int(shop_id[2:4], 16)

            shop1_reverse = self.get_xor_hex(shop1)
            shop2_reverse = self.get_xor_hex(shop2)

            arg9 = int(shop1_reverse, 16)
            arg10 = int(shop2_reverse, 16)

            req_byte = [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 0xAA, 0x55, 0x00, 0x00, arg9, arg10, shop1,
                        shop2]  # 구버전

        return req_byte

    # 카드 시리얼 번호 변환
    def change_serial(self, serial):
        res = hex(serial[3])[2:].rjust(2, "0")
        res += hex(serial[2])[2:].rjust(2, "0")
        res += hex(serial[1])[2:].rjust(2, "0")
        res += hex(serial[0])[2:].rjust(2, "0")
        res = res.upper()
        return res

    # 신버전 체크섬 구하기
    def get_check_sum(self, serial_number, money, shop_id, key1, key2):
        if self.config.get_config("encrypt") == 1:
            compare_result = int(int(money, 16) / 1000)
            compare_money = compare_result + int(serial_number, 16)

            compare_money_index = (compare_money % 100)
            compare_money_crc = int(self.config.crc[compare_money_index], 16)

            '''
            shop_num = int(shop1, 16) + int(shop2, 16)
            shop_total = int(serial_number, 16) + shop_num

            '''''
            shop_total = int(serial_number, 16) + int(shop_id, 16)

            compare_shop_id_index = (shop_total % 100)
            compare_shop_id_crc = int(self.config.crc[compare_shop_id_index], 16)

            # print("비교 money_crc >>" + str(compare_money_crc))
            # print("비교 shop_id_crc >>" + str(compare_shop_id_crc))
            # print("key1 >> " + str(key1))
            # print("key2 >> " + str(key2))

            if key1 == compare_money_crc and key2 == compare_shop_id_crc:
                return True
            else:
                return False
        else:
            return True

    # get update binary block byte
    def get_set_money_byte(self, serial_number, mny, shop_id):
        self.config.load_config()

        if self.config.get_config("encrypt") == "1":
            temp = hex(mny)[2:].rjust(8, '0')  # 정수로 들어옴
            temp = temp.upper()
            # if 'Windows' in platform.system():
            #     shop_id = format(int(shop_id), 'x').rjust(4, "0").upper()

            compare_result = int(int(temp, 16) / 1000)
            total = compare_result + int(serial_number, 16)
            temp_namuji = (total % 100)

            arg1 = int(temp[4:6], 16)
            arg2 = int(temp[6:8], 16)
            arg3 = int(temp[2:4], 16)
            arg4 = int(temp[0:2], 16)
            arg5 = int(self.config.crc[temp_namuji], 16)
            shop1 = int(shop_id[0:2], 16)
            shop2 = int(shop_id[2:4], 16)

            shop_total = int(serial_number, 16) + int(shop_id, 16)
            shop_namnuji = (shop_total % 100)
            arg10 = int(self.config.crc[shop_namnuji], 16)

            manager_no = int(self.config.get_config("manager_no"))

            # set_money_byte = [0xFF, 0xD6, 0x0, 0x01, 0x10, arg1, arg2, arg3, arg4, arg5, 0x00, 0x00, 0x00, 0xAA, 0x55, 0x00, 0x00, 0x00, arg10, shop1, shop2]  # 신버전
            set_money_byte = [arg1, arg2, arg3, arg4, arg5, 0x00, 0x00, 0x00, 0xAA, 0x55, manager_no, 0x00, 0x00, arg10, shop1, shop2]  # 신버전

        else:
            temp = hex(mny)[2:].rjust(8, '0')  # 정수로 들어옴
            temp = temp.upper()
            arg1 = int(temp[4:6], 16)
            arg2 = int(temp[6:8], 16)
            arg3 = int(temp[2:4], 16)
            arg4 = int(temp[0:2], 16)

            arg1_reverse = self.get_xor_hex(arg1)
            arg2_reverse = self.get_xor_hex(arg2)
            arg3_reverse = self.get_xor_hex(arg3)
            arg4_reverse = self.get_xor_hex(arg4)

            arg5 = int(arg1_reverse, 16)
            arg6 = int(arg2_reverse, 16)
            arg7 = int(arg3_reverse, 16)
            arg8 = int(arg4_reverse, 16)

            shop1 = int(shop_id[0:2], 16)
            shop2 = int(shop_id[2:4], 16)

            shop1_reverse = self.get_xor_hex(shop1)
            shop2_reverse = self.get_xor_hex(shop2)

            arg9 = int(shop1_reverse, 16)
            arg10 = int(shop2_reverse, 16)

            # set_money_byte = [0xFF, 0xD6, 0x0, 0x01, 0x10, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 0xAA, 0x55, 0x00, 0x00, arg9, arg10, shop1, shop2]  # 구버전
            set_money_byte = [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 0xAA, 0x55, 0x00, 0x00, arg9, arg10, shop1, shop2]  # 구버전

        return set_money_byte

    # 부저 1회 울리기
    def buzzer(self, reader_name):
        req_byte = [0xE0, 0x00, 0x00, 0x28, 0x01, 0x0A]
        try:
            hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_SYSTEM)
            try:
                hresult, readers = SCardListReaders(hcontext, [])
                if hresult == SCARD_S_SUCCESS:
                    if hresult == SCARD_S_SUCCESS:
                        try:
                            hresult, hcard, dwActiveProtocol = SCardConnect(
                                hcontext, reader_name, SCARD_SHARE_DIRECT, 0)
                            if hresult == SCARD_S_SUCCESS:
                                try:
                                    hresult, response = SCardControl(hcard, SCARD_CTL_CODE(3500), req_byte)
                                    if hresult == 0:
                                        return response
                                finally:
                                    hresult = SCardDisconnect(hcard, SCARD_UNPOWER_CARD)
                                    if hresult != SCARD_S_SUCCESS:
                                        print('Failed to disconnect: ' + SCardGetErrorMessage(hresult))
                        except error as e:
                            print(e)

            finally:
                hresult = SCardReleaseContext(hcontext)
                if hresult != SCARD_S_SUCCESS:
                    print('Failed to release context: ' + SCardGetErrorMessage(hresult))
        except error as e:
            print(e)

    # 부저 2회 울리기
    def buzzer_double(self, reader_name):
        req_byte = [0xE0, 0x00, 0x00, 0x28, 0x01, 0x0A]
        try:
            hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_SYSTEM)
            try:
                hresult, readers = SCardListReaders(hcontext, [])
                if hresult == SCARD_S_SUCCESS:
                    if hresult == SCARD_S_SUCCESS:
                        try:
                            hresult, hcard, dwActiveProtocol = SCardConnect(
                                hcontext, reader_name, SCARD_SHARE_DIRECT, 0)
                            if hresult == SCARD_S_SUCCESS:
                                try:
                                    hresult, response = SCardControl(hcard, SCARD_CTL_CODE(3500), req_byte)
                                    hresult, response = SCardControl(hcard, SCARD_CTL_CODE(3500), req_byte)
                                    if hresult == 0:
                                        return response
                                finally:
                                    hresult = SCardDisconnect(hcard, SCARD_UNPOWER_CARD)
                                    if hresult != SCARD_S_SUCCESS:
                                        print('Failed to disconnect: ' + SCardGetErrorMessage(hresult))
                        except error as e:
                            print(e)

            finally:
                hresult = SCardReleaseContext(hcontext)
                if hresult != SCARD_S_SUCCESS:
                    print('Failed to release context: ' + SCardGetErrorMessage(hresult))
        except error as e:
            print(e)

    # 보너스 가져오기
    def get_bonus(self, input_mny):
        temp_money = input_mny
        bonus = 0

        if temp_money >= 100000:
            while temp_money >= 100000:
                bonus += int(self.config.get_config(100000))
                temp_money -= 100000

        if temp_money >= 90000:
            while temp_money >= 90000:
                bonus += int(self.config.get_config(90000))
                temp_money -= 90000

        if temp_money >= 80000:
            while temp_money >= 80000:
                bonus += int(self.config.get_config(80000))
                temp_money -= 80000

        if temp_money >= 70000:
            while temp_money >= 70000:
                bonus += int(self.config.get_config(70000))
                temp_money -= 70000

        if temp_money >= 60000:
            while temp_money >= 60000:
                bonus += int(self.config.get_config(60000))
                temp_money -= 60000

        if temp_money >= 50000:
            while temp_money >= 50000:
                bonus += int(self.config.get_config(50000))
                temp_money -= 50000

        if temp_money >= 40000:
            while temp_money >= 40000:
                bonus += int(self.config.get_config(40000))
                temp_money -= 40000

        if temp_money >= 30000:
            while temp_money >= 30000:
                bonus += int(self.config.get_config(30000))
                temp_money -= 30000

        if temp_money >= 20000:
            while temp_money >= 20000:
                bonus += int(self.config.get_config(20000))
                temp_money -= 20000

        if temp_money >= 10000:
            while temp_money >= 10000:
                bonus += int(self.config.get_config(10000))
                temp_money -= 10000

        if temp_money > 0:
            res = self.config.get_config(temp_money)
            bonus += int(res)

        return bonus

    # 마스터카드 CRC 가져오기
    def get_master_card_crc(self, serial_number):
        idx = (int(serial_number, 16) + 0x0b) % 100
        res = self.config.crc[idx]
        return int(res, 16)

    def __init__(self):
        self.cards = []

    def update(self, observable, actions):
        self.config.load_config()
        key = self.config.get_config("shop_id")
        arg1 = int(key[0:2], 16)
        arg2 = int(key[2:4], 16)
        arg3 = int(key[4:6], 16)
        arg4 = int(key[6:8], 16)
        arg5 = int(key[8:10], 16)
        arg6 = int(key[10:12], 16)

        LOAD_KEY_DF = [arg1, arg2, arg3, arg4, arg5, arg6]  # 로드 키 데이터
        # LOAD_KEY_DF = [0x00, 0x00, 0x40, 0xBC, 0x84, 0x0C]  # 로드 키 데이터

        (addedcards, removedcards) = actions

        for card in addedcards:
            if card not in self.cards:
                self.cards += [card]

                try:
                    r = readers()

                    if str(card.reader) == str(r[0]):
                        card.connection = card.createConnection()
                        card.connection.connect()
                        serial_number, sw1, sw2 = card.connection.transmit(self.UID_BYTE)

                        if serial_number and len(serial_number) > 2:
                            response, is_load_key, sw2 = card.connection.transmit(self.LOAD_KEY_SELECT + LOAD_KEY_DF)  # LOAD KEY

                            # LOAD KEY 성공
                            if is_load_key == 144:
                                response, is_authentication, sw2 = card.connection.transmit(self.AUTH_SELECT + self.AUTH_DF)  # AUTHENTICATION

                                # AUTHENTICATION 성공
                                if is_authentication == 144:
                                    # TODO : 07.08 2번지 읽기로 변경됨 -> 07.16 데이터베이스에서 설정할 수 있도록 변경됨 -> 08.07 2번지가 비어있을 때 1번지의 값을 쓰도록 변경
                                    binary_block = []
                                    binary_block_1 = []

                                    if self.config.get_config("rf_reader_type") == "1":
                                        binary_block, sw1, sw2 = card.connection.transmit(self.READ_BINARY_SELECT)  # 1번 바이너리 블록 읽기
                                        print("1번지 바이너리 블록 >>" + str(binary_block))
                                        binary_block_1, sw1, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_2)  # 2번 바이너리 블록 읽기
                                        print("2번지 바이너리 블록 >>" + str(binary_block_1))
                                    elif self.config.get_config("rf_reader_type") == "2":
                                        binary_block, sw1, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_2)  # 2번 바이너리 블록 읽기
                                        print("2번지 바이너리 블록 >>" + str(binary_block))
                                        binary_block_1, sw1, sw2 = card.connection.transmit(self.READ_BINARY_SELECT)  # 1번 바이너리 블록 읽기
                                        print("1번지 바이너리 블록 >>" + str(binary_block_1))

                                    if binary_block and len(binary_block) > 2:
                                        # 카드 잔액
                                        remain_money = hex(binary_block[3])[2:].rjust(2, "0") \
                                                       + hex(binary_block[2])[2:].rjust(2, "0") + hex(binary_block[0])[2:].rjust(2, "0") + hex(binary_block[1])[2:].rjust(2, "0")
                                        remain_money_bak = hex(binary_block_1[3])[2:].rjust(2, "0") + hex(
                                            binary_block_1[2])[2:].rjust(2, "0") + hex(binary_block_1[0])[2:].rjust(2,"0") \
                                                           + hex(binary_block_1[1])[2:].rjust(2, "0")
                                        print("카드잔액 >>" + str(remain_money))

                                        # 상점 번호
                                        shop_id = hex(binary_block[14])[2:].rjust(2, "0") + hex(binary_block[15])[2:].rjust(2, "0")
                                        shop_id_bak = hex(binary_block_1[14])[2:].rjust(2, "0") + hex(binary_block_1[15])[2:].rjust(2, "0")

                                        # 마스터 여부
                                        master_byte1 = binary_block[11]
                                        master_byte2 = binary_block[12]

                                        # 마스터 여부
                                        master_byte1_bak = binary_block_1[11]
                                        master_byte2_bak = binary_block_1[12]

                                        # UID
                                        serial_number = self.change_serial(serial_number)
                                        data = {'card_num': serial_number}

                                        if self.config.get_config("data_collect_state") == "1":
                                            try:
                                                member_info = requests.post("http://192.168.0.200:5000/get_vip_bonus", json=[], data=data)
                                                # member_info = requests.post("http://glstest.iptime.org:50000/get_vip_bonus", json=[], data=data)
                                                member_info = member_info.json()
                                                if member_info:
                                                    for x in member_info:
                                                        member_level = x['level_name']
                                                        # 보너스 재설정
                                                        self.mb_level = str(x['level'])
                                                        self.config.get_member_bonus_config(str(x['level']))
                                                    self.member_class = member_level
                                                else:
                                                    self.config.init_member_bonus()
                                                    self.config.load_config()
                                                    self.member_class = "비회원"
                                            except Exception as e:
                                                self.config.error_log(str(e), "회원보너스 에러")
                                                print(e)

                                        # CRC 검증 로직
                                        check_sum = self.get_check_sum(serial_number, remain_money, shop_id,binary_block[4], binary_block[13])

                                        if not check_sum:
                                            remain_money = remain_money_bak
                                            shop_id = shop_id_bak
                                            master_byte1 = master_byte1_bak
                                            master_byte2 = master_byte2_bak

                                            check_sum = self.get_check_sum(serial_number, remain_money, shop_id, binary_block_1[4], binary_block_1[13])

                                            compare_master_byte = self.get_master_card_crc(serial_number)
                                            if master_byte1 == 11 and master_byte2 == compare_master_byte:
                                                check_sum = True
                                                print("마스터카드 임")

                                        # Windows 면 검증 통과
                                        if "Windows" in platform.system():
                                            check_sum = True

                                        if check_sum:
                                            # 카드 잔액 대문자 변경
                                            remain_money = remain_money.upper()

                                            # 상점 번호 대문자 변경
                                            shop_id = shop_id.upper()

                                            # 금액 10진수로 변환
                                            mny = int(remain_money, 16)

                                            # DB에서 상점 번호 겟
                                            config_shop_id = self.config.get_config("id")

                                            # 16진수로 변경하면서 4자리로 변경
                                            config_shop_id = hex(int(config_shop_id))[2:].rjust(4, "0")

                                            # 대문자 변경
                                            config_shop_id = config_shop_id.upper()

                                            # 초기화 플래그
                                            if self.INIT_FLAG:
                                                set_req_byte = self.get_req_byte(serial_number, master_byte1, master_byte2)  # CRC 적용된 초기 바이너리 바이트
                                                # TODO : 07.08 2번지 읽기로 변경됨 -> 07.16 데이터베이스 설정값으로 변경됨
                                                set1 = ""
                                                time.sleep(0.25)
                                                if self.config.get_config("rf_reader_type") == "1":
                                                    response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT + set_req_byte)  # 1번지 바이너리 블럭 업데이트
                                                elif self.config.get_config("rf_reader_type") == "2":
                                                    response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_2 + set_req_byte)  # 2번지 바이너리 블럭 업데이트

                                                if set1 == 144:
                                                    time.sleep(0.25)
                                                    if self.config.get_config("rf_reader_type") == "1":
                                                        response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_2 + set_req_byte)  # 2번지 바이너리 블럭 업데이트 (백업)
                                                    elif self.config.get_config("rf_reader_type") == "2":
                                                        response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT + set_req_byte)  # 1번지 바이너리 블럭 업데이트 (백업)

                                                    if set1 == 144:
                                                        print("백업 업데이트 성공!!")
                                                        self.init_state = "1"  # 성공 플래그
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    else:
                                                        self.init_state = "0"  # 실패 플래그
                                                        print("백업 업데이트 실패##")
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                else:
                                                    self.init_state = "0"  # 실패 플래그
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                            else:
                                                if shop_id == config_shop_id:
                                                    # 잔액 조회 또는 충전 로직
                                                    if self.CHARGE_FLAG:
                                                        self.LOOKUP_FLAG = False
                                                        self.ISSUED_FLAG = False

                                                        if self.input_money > 0:
                                                            self.LOOKUP_FLAG = False

                                                            # 충전 해야될 금액 구하기
                                                            self.total_money = self.input_money + self.bonus + int(mny)
                                                            self.use_money = self.input_money
                                                            bonus = self.bonus

                                                            charge_money = self.input_money + self.bonus

                                                            if self.config.get_config("data_collect_state") == "1":
                                                                try:
                                                                    # 회원 보너스 구하기
                                                                    mb_bonus = self.config.get_member_bonus(self.input_money)

                                                                    if mb_bonus:
                                                                        self.total_money = self.total_money + int(mb_bonus) - self.bonus
                                                                        self.current_bonus = int(mb_bonus)
                                                                        charge_money = self.input_money + int(mb_bonus)

                                                                except Exception as e:
                                                                    self.config.error_log(str(e), "회원보너스 에러")
                                                                    print(e)

                                                            set_req_byte = self.get_set_money_byte(serial_number, self.total_money, shop_id)

                                                            # TODO : 07.08 2번지 읽기로 변경됨 -> 07.16 데이터베이스 설정값으로 변경됨
                                                            set1 = ""
                                                            time.sleep(0.25)
                                                            if self.config.get_config("rf_reader_type") == "1":
                                                                response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT + set_req_byte)  # 1번지 바이너리 블럭 업데이트
                                                            elif self.config.get_config("rf_reader_type") == "2":
                                                                response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_2 + set_req_byte)  # 2번지 바이너리 블럭 업데이트

                                                            if set1 == 144:
                                                                self.CHARGE_FLAG = False

                                                                time.sleep(0.25)
                                                                if self.config.get_config("rf_reader_type") == "1":
                                                                    response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_2 + set_req_byte)  # 2번 바이너리 블럭 업데이트 (백업)
                                                                elif self.config.get_config("rf_reader_type") == "2":
                                                                    response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT + set_req_byte)  # 1번 바이너리 블럭 업데이트 (백업)

                                                                dic = OrderedDict()
                                                                dic['card_num'] = str(serial_number)
                                                                dic['total_mny'] = str(self.total_money)
                                                                dic['current_mny'] = str(self.current_money)
                                                                dic['current_bonus'] = str(self.get_bonus(self.current_money))
                                                                dic['before_mny'] = str(int(mny))
                                                                dic['charge_money'] = str(int(charge_money))
                                                                dic['card_price'] = "0"
                                                                dic['reader_type'] = "1"

                                                                self.config.set_card_table(dic)

                                                                dic1 = OrderedDict()

                                                                dic1['total_mny'] = str(int(self.use_money + bonus))
                                                                dic1['charge_mny'] = str(self.use_money)
                                                                dic1['bonus_mny'] = str(bonus)
                                                                dic1['card_count'] = "0"
                                                                dic1['card_price'] = "0"

                                                                self.config.set_total_table(dic1)
                                                                self.charge_state = "1"  # 성공 플래그
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                                            else:
                                                                self.charge_state = "0"  # 실패 플래그
                                                                self.config.error_log(str(set_req_byte), "1번 리더기 충전 실패함")
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                                    # 잔액 조회
                                                    elif self.LOOKUP_FLAG:
                                                        check_sum = self.get_check_sum(serial_number, remain_money, shop_id, binary_block[4], binary_block[13])

                                                        if not check_sum:
                                                            time.sleep(0.25)
                                                            set_req_byte = self.get_set_money_byte(serial_number, int(mny), shop_id)
                                                            response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_2 + set_req_byte)  # 2번 바이너리 블럭 업데이트

                                                            if set1 == 144:
                                                                if remain_money:
                                                                    self.lookup_state = "1"
                                                                else:
                                                                    self.lookup_state = "0"
                                                                self.card_remain_money = mny
                                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        else:
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                                            if remain_money:
                                                                self.lookup_state = "1"
                                                            else:
                                                                self.lookup_state = "0"

                                                            self.card_remain_money = mny
                                                else:
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                        else:
                                            self.init_state = "0"  # 실패 플래그
                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                    else:
                                        self.init_state = "0"  # 실패 플래그
                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                else:
                                    self.init_state = "0"  # 실패 플래그
                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                            else:
                                self.init_state = "0"  # 실패 플래그
                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                    elif str(card.reader) == str(r[1]):
                        if self.ISSUED_FLAG:
                            card.connection = card.createConnection()
                            card.connection.connect()
                            serial_number, sw1, sw2 = card.connection.transmit(self.UID_BYTE)

                            if serial_number and len(serial_number) > 2:
                                response, is_load_key, sw2 = card.connection.transmit(self.LOAD_KEY_SELECT + LOAD_KEY_DF)  # LOAD KEY

                                # LOAD KEY 성공
                                if is_load_key == 144:
                                    response, is_authentication, sw2 = card.connection.transmit(self.AUTH_SELECT + self.AUTH_DF)  # AUTHENTICATION

                                    # AUTHENTICATION 성공
                                    if is_authentication == 144:
                                        # TODO : 07.08 2번지 읽기로 변경됨 -> 07.16 데이터베이스 설정값으로 변경됨
                                        binary_block = []
                                        if self.config.get_config("rf_reader_type") == "1":
                                            binary_block, sw1, sw2 = card.connection.transmit(self.READ_BINARY_SELECT)  # 1번 바이너리 블록 읽기
                                            print("1번지 바이너리 블록 >>" + str(binary_block))
                                        elif self.config.get_config("rf_reader_type") == "2":
                                            binary_block, sw1, sw2 = card.connection.transmit(self.READ_BINARY_SELECT_2)  # 2번 바이너리 블록 읽기
                                            print("2번지 바이너리 블록 >>" + str(binary_block))

                                        if binary_block and len(binary_block) > 2:
                                            # 카드 잔액
                                            remain_money = hex(binary_block[3])[2:].rjust(2, "0") + hex(binary_block[2])[2:].rjust(2, "0") + hex(binary_block[0])[2:].rjust(2,"0") + hex(binary_block[1])[2:].rjust(2, "0")
                                            print("카드잔액 >>" + str(remain_money))

                                            # 상점 번호
                                            shop_id = hex(binary_block[14])[2:].rjust(2, "0") + hex(binary_block[15])[2:].rjust(2, "0")
                                            serial_number = self.change_serial(serial_number)

                                            # CRC 검증 로직
                                            check_sum = self.get_check_sum(serial_number, remain_money, shop_id, binary_block[4], binary_block[13])

                                            # Windows 면 검증 통과
                                            if "Windows" in platform.system():
                                                check_sum = True

                                            if check_sum:
                                                # 카드 잔액 대문자 변경
                                                remain_money = remain_money.upper()

                                                # 상점 번호 대문자 변경
                                                shop_id = shop_id.upper()

                                                # 금액 10진수로 변환
                                                mny = int(remain_money, 16)

                                                # DB에서 상점 번호 겟
                                                config_shop_id = self.config.get_config("id")

                                                # 16진수로 변경하면서 4자리로 변경
                                                config_shop_id = hex(int(config_shop_id))[2:].rjust(4, "0")

                                                # 대문자 변경
                                                config_shop_id = config_shop_id.upper()

                                                if shop_id == config_shop_id:
                                                    self.CHARGE_FLAG = False
                                                    # 충전 로직
                                                    if self.input_money > 0:
                                                        self.LOOKUP_FLAG = False

                                                        # 충전 해야될 금액 구하기
                                                        self.total_money = self.input_money + self.bonus + int(mny)
                                                        self.use_money = self.input_money
                                                        bonus = self.bonus

                                                        charge_money = self.input_money + self.bonus

                                                        set_req_byte = self.get_set_money_byte(serial_number, self.total_money, shop_id)

                                                        # TODO : 07.08 2번지 읽기로 변경됨 -> 07.16 데이터베이스 설정값으로 변경됨
                                                        set1 = ""
                                                        time.sleep(0.25)
                                                        if self.config.get_config("rf_reader_type") == "1":
                                                            response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT + set_req_byte)  # 1번지 바이너리 블럭 업데이트
                                                            self.ISSUED_FLAG = False
                                                            self.CHARGE_FLAG = False
                                                        elif self.config.get_config("rf_reader_type") == "2":
                                                            response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_2 + set_req_byte)  # 2번지 바이너리 블럭 업데이트

                                                        if set1 == 144:
                                                            time.sleep(0.25)
                                                            if self.config.get_config("rf_reader_type") == "1":
                                                                response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT_2 + set_req_byte)  # 2번지 바이너리 블럭 업데이트
                                                            elif self.config.get_config("rf_reader_type") == "2":
                                                                response, set1, set2 = card.connection.transmit(self.UPDATE_BINARY_SELECT + set_req_byte)  # 1번지 바이너리 블럭 업데이트

                                                            self.charge_state = "1"  # 성공 플래그

                                                            dic = OrderedDict()
                                                            dic['card_num'] = str(serial_number)
                                                            dic['total_mny'] = str(self.total_money)
                                                            dic['current_mny'] = str(self.current_money)
                                                            dic['current_bonus'] = str(self.get_bonus(self.current_money))
                                                            dic['before_mny'] = str(int(mny))
                                                            dic['charge_money'] = str(int(charge_money))
                                                            dic['card_price'] = "0"
                                                            dic['reader_type'] = "1"

                                                            self.config.set_card_table(dic)

                                                            dic1 = OrderedDict()
                                                            dic1['total_mny'] = str(int(self.use_money + bonus))
                                                            dic1['charge_mny'] = str(self.use_money)
                                                            dic1['bonus_mny'] = str(bonus)
                                                            dic1['card_count'] = "0"
                                                            dic1['card_price'] = "0"

                                                            self.config.set_total_table(dic1)
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)

                                                        else:
                                                            self.config.error_log(str(set_req_byte), "2번 리더기 충전 실패함")
                                                            self.charge_state = "0"  # 실패 플래그
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                        # self.LOOKUP_FLAG = True
                                                    else:
                                                        self.LOOKUP_FLAG = True
                                                        self.ISSUED_FLAG = False
                                                        self.CHARGE_FLAG = False
                                                        self.ISSUED_ENABLE = True
                                                else:
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                            else:
                                                self.init_state = "0"  # 실패 플래그
                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                                card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                        else:
                                            print("어디서 나는 걸까")
                                            self.init_state = "0"  # 실패 플래그
                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                            card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                    else:
                                        print("어디서 나는 걸까 짜증")
                                        self.init_state = "0"  # 실패 플래그
                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                        card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                else:
                                    print("어디서 나는 걸까 짜증난다")
                                    self.init_state = "0"  # 실패 플래그
                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                                    card.connection.control(SCARD_CTL_CODE(3500), self.BUZZER_BYTE)
                            else:
                                pass
                except Exception as e:
                    self.config.error_log(str(e), "RF리더기 쓰레드 에러")
                    print("전체 트라이 >> " + str(e))
                finally:
                    card.connection.disconnect()

        for card in removedcards:
            print("- Removed card: ", toHexString(card.atr))
            if card in self.cards:
                self.cards.remove(card)
                self.buzzer_reader = ""


if __name__ == "__main__":
    print()