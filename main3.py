# !/usr/local/bin/python3
# -*- coding : utf-8 -*-
# ver 1.3.0
import pymysql.cursors
import tkinter
import tkinter.ttk
from tkinter import *
import PIL.Image
from PIL import ImageTk
import platform
import threading
import time
import sys
import subprocess
import os
from collections import OrderedDict
import base64
import BillClass as b, CardClass as c, RFIDClass as r, AnimatedGif as animate, CommonClass as com, SoundClass as s, Config as config
from smartcard.CardMonitoring import CardMonitor


class Main:
    DEBUG = False  # 디버그 모드
    # MYSQL_HOST = "192.168.0.223"
    MYSQL_HOST = "glstest.iptime.org"
    MYSQL_PORT = 30001
    if 'Linux' in platform.system():
        MYSQL_HOST = "localhost"
        MYSQL_PORT = 3306

    CARD_INIT_FLAG = False
    CHARGE_INIT_FLAG = False
    ISSUED_INIT_FLAG = False
    LOOKUP_INIT_FLAG = False

    _rf_thread = ""
    MAIN_USE = False
    MAIN_SECOND = 0
    MAIN_SOUND = False

    CARD_TYPE = 2       # 기본 구형
    input_money = 0     # 사용된 금액
    temp_money = 0      # 실제 투입금액
    input_cash = 0      # 사용중인 금액 (디스플레이용)
    bonus = 0           # 보너스
    use_bonus = 0       # 사용된 보너스
    count = 0           # 관리자페이지 진입 카운트

    CARD_MIN_MONEY = 1000  # 카드발급 최소금액

    charge_phase1_thread = ""
    charge_phase1_second = 0  # 지폐를 투입하여 주세요 쓰레드에서 사용하는 초
    charge_phase1_state = False  # 충전 페이즈1 상태

    charge_phase2_thread = ""
    charge_phase2_second = 0  # 세차카드를 터치하여주세요 쓰레드에서 사용하는 초
    charge_phase2_state = False  # 충전 페이즈2 상태

    issued_phase1_thread = ""
    issued_phase1_second = 0  # 지폐를 투입하여 주세요 쓰레드에서 사용하는 초
    issued_phase1_state = False  # 충전 페이즈1 상태

    lookup_phase1_thread = ""
    lookup_phase1_second = 0  # 세차카드를 터치하여주세요 쓰레드에서 사용하는 초
    lookup_phase1_state = False  # 잔액조회

    # 지폐인식기, 카드배출기, 음성, 데이터베이스 객체생성
    bill = b.Bill()
    card = c.Card()
    sound = s.Sound()
    my = com.Common()
    config = config.Config()

    rf_class = ""
    window = ""

    main_frame = ""
    main_input = ""     # 메인 뷰금액
    charge_frame = ""
    charge1_frame = ""
    charge2_frame = ""
    charge3_frame = ""

    issued_frame = ""
    issued1_frame = ""

    lookup_frame = ""
    admin_frame = ""
    admin_login_frame = ""  # 로그인 페이지
    master_frame = ""
    card_init_frame = ""

    init_card_label = ""
    init_shop_id_label = ""
    init_start_btn_ = ""
    init_start_enable_btn = ""
    admin_pass_entry = ""

    # 관리자 기입창
    entry_1 = ""
    entry_2 = ""
    entry_3 = ""
    entry_4 = ""
    entry_5 = ""
    entry_6 = ""
    entry_7 = ""
    entry_8 = ""
    entry_9 = ""
    entry_10 = ""

    card_price_entry = ""
    shop_title_entry = ""
    shop_id_entry = ""
    admin_password_entry = ""
    min_card_price_entry = ""

    # 마스터 기입창
    master_entry_1 = ""
    master_entry_2 = ""
    master_entry_3 = ""
    master_entry_4 = ""
    master_entry_5 = ""
    master_entry_6 = ""
    master_entry_7 = ""
    master_entry_8 = ""
    master_entry_9 = ""
    master_entry_10 = ""
    rf_title = ""
    manager_combobox = ""
    binary_combobox = ""
    binary_title = ""

    master_card_price_entry = ""
    master_shop_title_entry = ""
    master_shop_id_entry = ""
    master_admin_password_entry = ""
    master_min_card_price_entry = ""

    charge_btn = ""
    issued_btn = ""
    lookup_btn = ""
    lookup_back = ""
    lookup_back_btn = ""
    charge_next_btn = ""
    charge_next_btn1 = ""
    charge_next_btn_pi = ""
    charge_back_btn = ""
    charge_back_btn1 = ""
    issued_next_btn = ""

    main_back = ""
    main_label = ""
    main_use_label = ""
    main_use_label_pi = ""
    charge_back = ""
    charge_input = ""

    issued_back = ""
    issued_input = ""
    issued_card = ""

    charge1_back = ""
    charge1_input = ""
    charge1_bonus_input = ""
    charge2_back = ""
    charge2_input = ""

    charge_btn_img = ""
    issued_btn_img = ""
    lookup_btn_img = ""

    charge_next_gif = ""
    issued_next_gif = ""
    p = ""

    lookup_member_class_label = ""
    debug_main_label = ""
    debug_charge_label = ""
    debug_charge1_label = ""
    debug_lookup_label = ""
    debug_issued_label = ""

    # 프레임 화면 전환
    def raise_frame(self, frame):
        frame.tkraise()

    # 충전 시작
    def charge_init(self):
        # 메인 버튼 사용불가
        self.charge_btn.config(state="disabled")
        self.issued_btn.config(state="disabled")
        self.lookup_btn.config(state="disabled")

        # 음성 재생중일때
        if self.sound.get_busy():
            self.sound.stop_sound()  # 중지
        self.sound.play_sound("./msgs/msg005.wav")  # 카드 충전을 선택하셨습니다

        # 각종 플래그변경
        self.rf_class.CHARGE_FLAG = True    # RFID 충전플래그 ON
        self.rf_class.LOOKUP_FLAG = False   # RFID 조회플래그 OFF
        self.rf_class.ISSUED_FLAG = True    # RFID 발급플래그 ON
        self.CHARGE_INIT_FLAG = True     # 뷰 충전 플래그 ON

        self.charge_phase1_state = False  # 충전 페이지1 음성 쓰레드 플래그 ON
        self.charge_phase1_second = 0     # 충전 페이지1 음성 쓰레드 시간 초기화
        self.charge_phase2_state = False  # 충전 페이지2 음성 쓰레드 플래그 ON
        self.charge_phase2_second = 0     # 충전 페이지2 음성 쓰레드 시간 초기화

        self.raise_frame(self.charge_frame)
        self.charge_phase1(0, 3)  # 충전 페이지1 음성스레드 시작 (횟수, 시간)

    # 지폐를 투입하여주세요 음성 스레드
    def charge_phase1(self, i=0, second=3.0):
        if self.charge_phase1_state:
            return

        # 음성 재생중이 아니라면
        if not self.sound.get_busy():
            # 돈을 넣었다면
            if self.input_money > 0:
                self.sound.play_sound("./msgs/msg009.wav")  # 지폐를 더투입하거나 다음버튼을 눌러주세요
            else:
                self.sound.play_sound("./msgs/msg008.wav")  # 지폐를 투입하여 주세요

        i += 1
        # 재생횟수 1회 증가
        self.charge_phase1_second += 1

        # 음성 재생 20회 이후
        if self.charge_phase1_second >= 20:
            # 충전 페이지1 음성 스레드 플래그 OFF
            self.charge_phase1_state = True
            # 음성 재생중이라면
            if self.sound.get_busy():
                self.sound.stop_sound()

            # 일정시간동안 지폐를 투입하지 않아 메인화면으로 이동합니다.
            self.sound.play_sound("./msgs/msg020.wav")
            # 메인 이동
            self.raise_frame(self.main_frame)
            # 메인 버튼활성화
            self.charge_btn.config(state="active")
            self.issued_btn.config(state="active")
            self.lookup_btn.config(state="active")

            self.rf_class.CHARGE_FLAG = False   # RFID 충전 플래그 OFF
            self.rf_class.LOOKUP_FLAG = True    # RFID 잔액조회 플래그 ON
            self.rf_class.ISSUED_FLAG = False   # RFID 하단 충전 플래그 ON
            self.charge_phase1_thread.cancel()  # 충전 페이지1 음성 스레드 취소

        self.charge_phase1_thread = threading.Timer(second, self.charge_phase1, [i])
        self.charge_phase1_thread.daemon = True
        self.charge_phase1_thread.start()

    # 카드 충전 : 지폐투입 다음버튼
    def charge_next(self):
        # 음성 재생중이면
        if self.sound.get_busy():
            self.sound.stop_sound()

        # 음성 재생횟수 초기화
        self.charge_phase1_second = 0
        # 페이지1 음성플래그 OFF
        self.charge_phase1_state = True

        # 만약 충전 페이지1 스레드가 살아있다면
        if self.charge_phase1_thread:
            # 스레드 취소
            self.charge_phase1_thread.cancel()

        self.raise_frame(self.charge1_frame)
        self.charge_phase2(0, 3)  # 충전 페이지2 음성스레드 시작

    # 카드 터치 음성 재생 스레드
    def charge_phase2(self, i=0, second=3.0):
        if self.charge_phase2_state:
            return

        if not self.sound.get_busy():
            self.sound.play_sound("./msgs/msg010.wav")  # 세차카드를 터치하여 주세요

        i += 1
        self.charge_phase2_second += 1

        if self.charge_phase2_second >= 20:
            # 카드 터치 음성 스레드 플래그 OFF
            self.charge_phase2_state = True

            if self.sound.get_busy():
                self.sound.stop_sound()

            self.sound.play_sound("./msgs/msg021.wav")  # 일정시간 동안 다음 단계를 진행하지 않아 메인화면으로 이동합니다
            # 메인화면 이동 후 버튼 활성화
            self.raise_frame(self.main_frame)
            self.charge_btn.config(state="active")
            self.issued_btn.config(state="active")
            self.lookup_btn.config(state="active")
            self.rf_class.LOOKUP_FLAG = True    # RFID 조회 플래그 ON
            self.rf_class.CHARGE_FLAG = False   # RFID 충전 플래그 OFF
            self.rf_class.ISSUED_FLAG = False   # RFID 하단 충전 플래그 ON
            self.charge_phase2_thread.cancel()

        self.charge_phase2_thread = threading.Timer(second, self.charge_phase2, [i])
        self.charge_phase2_thread.daemon = True
        self.charge_phase2_thread.start()

    # 충전 종료
    def quit_charge(self, frame):
        self.charge_btn.config(state="active")
        self.issued_btn.config(state="active")
        self.lookup_btn.config(state="active")
        self.rf_class.CHARGE_FLAG = False   # 충전 OFF
        self.rf_class.ISSUED_FLAG = False   # 발급 OFF
        self.rf_class.LOOKUP_FLAG = True    # 조회 ON

        self.CHARGE_INIT_FLAG = False       # 메인 충전 OFF
        self.charge_phase1_state = True     # 스레드 종료

        if self.sound.get_busy():
            self.sound.stop_sound()
        self.raise_frame(self.main_frame)

        if self.charge_phase1_thread:
            self.charge_phase1_thread.cancel()
        if self.charge_phase2_thread:
            self.charge_phase2_thread.cancel()

    # 발급 시작
    def issued_init(self):
        # 카드 1장 막기
        if not self.rf_class.ISSUED_ENABLE:
            if self.sound.get_busy():
                self.sound.stop_sound()
            self.sound.play_sound("./msgs/msg024.wav")
            return

        if self.sound.get_busy():
            self.sound.stop_sound()
        self.sound.play_sound("./msgs/msg006.wav")  # 카드 발급 선택

        self.charge_btn.config(state="disabled")
        self.issued_btn.config(state="disabled")
        self.lookup_btn.config(state="disabled")

        self.issued_card.config(text="{} 원".format(str(self.CARD_MIN_MONEY)))
        self.raise_frame(self.issued_frame)

        self.ISSUED_INIT_FLAG = True       # 메인 발급 ON
        self.rf_class.CHARGE_FLAG = False  # 리더기 충전 OFF
        self.rf_class.LOOKUP_FLAG = False  # 리더기 조회 OFF

        self.charge_phase1_state = False  # 충전 페이지1 음성 스레드 플래그 ON
        self.charge_phase1_second = 0

        self.charge_phase1(0, 3.5)

    # 발급
    def issued(self):
        self.charge_phase1_second = 0
        self.charge_phase1_state = True
        self.issued_next_gif.config(state="disable")
        self.issued_next_btn_animate_stop()

        if self.charge_phase1_thread:
            self.charge_phase1_thread.cancel()

        if not self.card.CARD_CONNECT:
            print("배출기가 연결퇴지 않아 연결합니다.")
            self.card.sendData("hi")

        if self.card.CARD_CONNECT:
            self.card.sendData("enable")
            if self.card.CARD_STATE:
                self.card.sendData("output")
                self.raise_frame(self.main_frame)
                res = self.card.sendData("state")

                if res == 2:
                    self.sound.play_sound("./msgs/msg014.wav")
                elif res == 5:
                    self.sound.play_sound("./msgs/msg017.wav")
                    self.charge_btn.config(state="active")
                    self.issued_btn.config(state="active")
                    self.lookup_btn.config(state="active")
                    self.ISSUED_INIT_FLAG = False
                    self.rf_class.LOOKUP_FLAG = True
                    self.rf_class.CHARGE_FLAG = False
                    self.raise_frame(self.main_frame)
                    return
                else:
                    self.sound.play_sound("./msgs/msg017.wav")
                    self.charge_btn.config(state="active")
                    self.issued_btn.config(state="active")
                    self.lookup_btn.config(state="active")
                    self.card.sendData("init")
                    self.ISSUED_INIT_FLAG = False
                    self.rf_class.LOOKUP_FLAG = True
                    self.rf_class.CHARGE_FLAG = False
                    self.raise_frame(self.main_frame)
                    return

                try:
                    res = self.card.sendData("state")
                    if res == 4 or res == 5 or res == 2:
                        self.bonus = 0
                        self.rf_class.bonus = 0

                        card_price = int(self.CARD_MIN_MONEY)
                        temp = card_price - self.bonus
                        total_use = 0

                        if int(temp) > 0:  # 카드가격이 남았다면
                            print("카드 가격 남음")
                            input_money = self.input_money - temp
                            self.use_bonus = self.bonus
                            self.input_money -= temp
                            self.rf_class.input_money -= temp
                            self.rf_class.bonus = 0
                            self.bonus = 0
                        else:
                            print("카드 가격 안남음")
                            self.bonus -= card_price
                            self.use_bonus = card_price
                            self.rf_class.bonus -= card_price
                            input_money = self.input_money

                        self.card.sendData("disable")
                        self.charge_btn.config(state="active")
                        self.issued_btn.config(state="active")
                        self.lookup_btn.config(state="active")

                        total_view_mny = self.input_money + self.bonus

                        total_view_mny = self.my.number_format(total_view_mny)
                        input_money = self.my.number_format(input_money)

                        self.change_money(total_view_mny, input_money, self.my.number_format(self.bonus), "발급")
                        if self.rf_class.input_money > 0:
                            self.rf_class.ISSUED_FLAG = True
                            self.rf_class.ISSUED_ENABLE = False
                        else:
                            self.rf_class.ISSUED_FLAG = False
                            self.rf_class.ISSUED_ENABLE = True
                            self.rf_class.LOOKUP_FLAG = True

                        self.ISSUED_INIT_FLAG = False

                    else:
                        self.sound.play_sound("./msgs/msg017.wav")
                        self.charge_btn.config(state="active")
                        self.issued_btn.config(state="active")
                        self.lookup_btn.config(state="active")
                        self.card.sendData("init")
                        self.raise_frame(self.main_frame)
                        return

                except Exception as e:
                    print("issued err >> " + str(e))
            else:
                self.sound.play_sound("./msgs/msg017.wav")
                self.charge_btn.config(state="active")
                self.issued_btn.config(state="active")
                self.lookup_btn.config(state="active")
                self.ISSUED_INIT_FLAG = False
                self.raise_frame(self.main_frame)
                return

    # 발급 종료
    def quit_issued(self, frame):
        self.charge_btn.config(state="active")
        self.issued_btn.config(state="active")
        self.lookup_btn.config(state="active")
        self.rf_class.LOOKUP_FLAG = True
        self.rf_class.CHARGE_FLAG = False
        self.rf_class.ISSUED_FLAG = False
        self.ISSUED_INIT_FLAG = False

        if self.sound.get_busy():
            self.sound.stop_sound()
        self.raise_frame(frame)

        if self.charge_phase1_thread:
            self.charge_phase1_thread.cancel()

    # 잔액조회 시작
    def lookup_init(self):
        self.charge_btn.config(state="disabled")
        self.issued_btn.config(state="disabled")
        self.lookup_btn.config(state="disabled")
        self.raise_frame(self.lookup_frame)
        self.lookup_back_btn.config(state="active")

        if self.sound.get_busy():
            self.sound.stop_sound()

        self.sound.play_sound("./msgs/msg007.wav")  # 잔액 조회를 시작합니다
        if not self.sound.get_busy():
            self.sound.play_sound("./msgs/msg010.wav")  # 세차 카드를 터치하여 주세요

        self.rf_class.LOOKUP_FLAG = True
        self.LOOKUP_INIT_FLAG = True

        self.lookup_phase1_state = False
        self.lookup_phase1_second = 0

        self.lookup_thread(0, 3)

    # 잔액조회 음성 스레드
    def lookup_thread(self, i=0, second=3.0):
        if self.lookup_phase1_state:
            return

        if not self.sound.get_busy():
            self.sound.play_sound("./msgs/msg010.wav")

        i += 1
        self.lookup_phase1_second += 1

        if self.lookup_phase1_second >= 20:
            self.lookup_phase1_state = True

            if self.sound.get_busy():
                self.sound.stop_sound()
            self.sound.play_sound("./msgs/msg021.wav")  # 일정시간 동안 다음 단계를 진행하지 않아서 메인화면으로 이동합니다.
            self.raise_frame(self.main_frame)
            self.charge_btn.config(state="active")  # 메인 충전버튼 활성화
            self.issued_btn.config(state="active")  # 메인 발급버튼 활성화
            self.lookup_btn.config(state="active")  # 메인 조회버튼 활성화
            self.lookup_phase1_thread.cancel()  # 잔액조회 음성 쓰레드 취소

        self.lookup_phase1_thread = threading.Timer(second, self.lookup_thread, [i])
        self.lookup_phase1_thread.daemon = True
        self.lookup_phase1_thread.start()

    # 잔액조회 종료
    def quit_lookup(self):
        self.lookup_input.config(text="0 원")
        self.charge_btn.config(state="active")
        self.issued_btn.config(state="active")
        self.lookup_btn.config(state="active")
        self.raise_frame(self.main_frame)
        self.rf_class.CHARGE_FLAG = False
        self.rf_class.ISSUED_FLAG = False
        self.rf_class.LOOKUP_FLAG = True
        self.LOOKUP_INIT_FLAG = False

        self.lookup_phase1_state = True
        self.lookup_phase1_second = 0

        if self.sound.get_busy():
            self.sound.stop_sound()

        if self.lookup_phase1_thread:
            self.lookup_phase1_thread.cancel()

    # 메인 페이지 돌아가기
    def phase_end(self):
        self.charge_btn.config(state="active")
        self.issued_btn.config(state="active")
        self.lookup_btn.config(state="active")
        self.raise_frame(self.main_frame)
        self.rf_class.CHARGE_FLAG = False
        self.rf_class.ISSUED_FLAG = False
        self.rf_class.LOOKUP_FLAG = True

    # 매장 ID 종료
    def quit_card_money(self):
        self.rf_class.INIT_FLAG = False
        self.init_card_start_enable_btn.place_forget()
        self.init_card_start_btn.place(x=250, y=233)
        self.raise_frame(self.main_frame)

    # 충전 다음 버튼 움직이기
    def next_btn_animate(self):
        self.charge_next_gif.place(x=770, y=625)
        self.charge_next_gif.stop = False
        self.charge_next_gif.start()

    # 충점 다음 버튼 멈추기
    def next_btn_animate_stop(self):
        self.charge_next_gif.stop = True
        self.charge_next_gif.place_forget()

    # 충전 다음 버튼 움직이는지 확인하기
    def is_next_btn_animate(self):
        return self.charge_next_gif.stop

    # 발급 다음 버튼 움직이기
    def issued_next_btn_animate(self):
        self.issued_next_gif.place(x=770, y=625)
        self.issued_next_gif.stop = False
        self.issued_next_gif.start()

    # 발급 다음 버튼 멈추기
    def issued_next_btn_animate_stop(self):
        self.issued_next_gif.stop = True
        self.issued_next_gif.place_forget()

    # 발급 다음 버튼 움직이는지 확인
    def is_issued_next_btn_animate(self):
        return self.issued_next_gif.stop

    # 메인 background 이미지 가져오기
    def getBackgroundImage(self, flag):
        # 카드충전
        if flag == 1:
            self.bill.sendData("hi")
            if self.bill.BILL_CONNECT:
                background_image = "./images/charge_on_btn.png"
            else:
                background_image = "./images/charge_off_btn.png"
        # 카드발급
        elif flag == 2:
            self.card.sendData("hi")
            if self.card.CARD_CONNECT:
                background_image = "./images/issued_on_btn.png"
            else:
                background_image = "./images/issued_off_btn.png"
        # 잔액조회
        elif flag == 3:
            background_image = "./images/lookup_on_btn.png"

        # 다음버튼
        elif flag == 4:
            if self.bill.get_Inputmoney() > 0:
                background_image = "./images/next_btn_on.png"
            else:
                background_image = "./images/next_btn_off.png"

        res = PIL.Image.open(background_image)
        return res

    # 메인 라벨 움직이게 하기
    def main_use_label_init(self, second=1.0):
        if self.MAIN_USE:
            return

        self.my.toggle(self.main_use_label, self.main_use_label_pi)
        th = threading.Timer(second, self.main_use_label_init)

        if self.input_money > 0 and not self.CHARGE_INIT_FLAG and not self.ISSUED_INIT_FLAG and not self.LOOKUP_INIT_FLAG:
            if not self.sound.get_busy():
                self.sound.play_sound("./msgs/msg025.wav")  # 재생중이지 않으면 투입금액이 잇다 재생
        th.daemon = True
        th.start()

    # 메인 프레임으로 돌아가기
    def main_frame_raise(self):
        if not self.DEBUG:
            if 'Linux' in platform.system():
                self.window.attributes('-fullscreen', True)

        self.p.kill()
        # p = subprocess.Popen(['florence hide'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        #                      universal_newlines=True)
        # if not "" == self.p.stderr.readline():
        #     subprocess.Popen(['florence'], shell=True)

        self.config.load_config()
        self.raise_frame(self.main_frame)

    # 로그인
    def login(self, pw):
        if pw == self.config.get_config("password"):
            self.raise_frame(self.admin_frame)
        elif pw == self.config.get_config("gil_password"):
            self.raise_frame(self.admin_frame)
        elif pw == self.config.get_config("master_password"):
            self.raise_frame(self.master_frame)
        else:
            self.my.show_msg("잘못된 비밀번호입니다.")

    # 관리자 페이지 데이터 저장
    def set_all_data(self):
        res = self.my.show_msg_ys("저장하시겠습니까?")
        if res:
            file_data = OrderedDict()
            file_data["man"] = int(self.entry_1.get().replace(",", ""))
            file_data["2man"] = int(self.entry_2.get().replace(",", ""))
            file_data["3man"] = int(self.entry_3.get().replace(",", ""))
            file_data["4man"] = int(self.entry_4.get().replace(",", ""))
            file_data["5man"] = int(self.entry_5.get().replace(",", ""))
            file_data["6man"] = int(self.entry_6.get().replace(",", ""))
            file_data["7man"] = int(self.entry_7.get().replace(",", ""))
            file_data["8man"] = int(self.entry_8.get().replace(",", ""))
            file_data["9man"] = int(self.entry_9.get().replace(",", ""))
            file_data["10man"] = int(self.entry_10.get().replace(",", ""))
            file_data["card_price"] = int(self.card_price_entry.get().replace(",", ""))
            file_data["min_card_price"] = int(self.min_card_price_entry.get().replace(",", ""))
            file_data["id"] = self.shop_id_entry.get()
            file_data["admin_password"] = self.admin_password_entry.get()

            self.config.set_all_data(file_data)

            if not self.DEBUG:
                if 'Linux' in platform.system():
                    self.window.attributes('-fullscreen', True)

            self.p.kill()

            self.config.load_config()
            self.raise_frame(self.main_frame)

    # 마스터 페이지 데이터 저장
    def set_master_all_data(self):
        res = self.my.show_msg_ys("저장하시겠습니까?")
        if res:
            file_data = OrderedDict()
            file_data["man"] = int(self.master_entry_1.get().replace(",", ""))
            file_data["2man"] = int(self.master_entry_2.get().replace(",", ""))
            file_data["3man"] = int(self.master_entry_3.get().replace(",", ""))
            file_data["4man"] = int(self.master_entry_4.get().replace(",", ""))
            file_data["5man"] = int(self.master_entry_5.get().replace(",", ""))
            file_data["6man"] = int(self.master_entry_6.get().replace(",", ""))
            file_data["7man"] = int(self.master_entry_7.get().replace(",", ""))
            file_data["8man"] = int(self.master_entry_8.get().replace(",", ""))
            file_data["9man"] = int(self.master_entry_9.get().replace(",", ""))
            file_data["10man"] = int(self.master_entry_10.get().replace(",", ""))
            file_data["card_price"] = int(self.master_card_price_entry.get().replace(",", ""))
            file_data["min_card_price"] = int(self.master_min_card_price_entry.get().replace(",", ""))
            file_data["id"] = self.master_shop_id_entry.get()
            file_data["admin_password"] = self.master_admin_password_entry.get()
            file_data["manager_name"] = self.manager_combobox.get()
            file_data["binary_type"] = self.binary_combobox.get()

            self.config.set_all_data_master(file_data)

            if not self.DEBUG:
                if 'Linux' in platform.system():
                    self.window.attributes('-fullscreen', True)

            self.p.kill()

            self.config.load_config()
            self.raise_frame(self.main_frame)

    # 프로그램 종료
    def power_off(self):
        self.MAIN_USE = True
        self.MAIN_SOUND = True
        sys.exit()

    # 저희 셀프세차장 음성 재생
    def init_main_sound(self, event):
        if not self.sound.get_busy():
            self.sound.play_sound("./msgs/msg003.wav")

    # 데이터베이스 초기화 (마스터)
    def init_database(self):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user='pi', password='1234', charset='utf8mb4', db='glstech')

        try:
            with conn.cursor() as cursor:
                query = "DELETE FROM card"  # 카드테이블 초기화
                cursor.execute(query)

                query = "INSERT INTO total (`no`, `total`, `charge`, `bonus`, `card`, `card_count`) VALUE (1, '0', '0', '0', '0', '0') " \
                        "ON DUPLICATE KEY UPDATE total = '0', charge = '0', bonus = '0', card = '0', card_count = '0'"  # 토탈 테이블 초기화
                cursor.execute(query)

                init_pass = '1234'
                admin_pass = init_pass.encode("utf-8")
                temp = base64.b64encode(admin_pass)
                admin_pass = temp.decode("utf-8")

                query = "UPDATE config SET admin_password = %s, `device_addr` = '01', card_price = 1000, bonus1 = '1000', bonus2 = '3000', bonus3 = '5000', bonus4 = '7000', bonus5 = '10000', bonus6 = '11000', bonus7 = '13000', bonus8 = '15000'," \
                        "bonus9 = '17000', bonus10 = '20000', id = '0000', shop_name = 'abcd' WHERE no = 1"  # 설정 초기화
                cursor.execute(query, (admin_pass))
            conn.commit()
        finally:
            conn.close()

        if not self.DEBUG:
            if 'Linux' in platform.system():
                self.window.attributes('-fullscreen', True)

        self.config.load_config()
        self.raise_frame(self.main_frame)

    # 데이터베이스 초기화 체크 (마스터)
    def check_database(self):
        total_mny = 0
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user='pi', password='1234', charset='utf8mb4', db='glstech')

        # Connection 으로부터 Dictoionary Cursor 생성
        curs = conn.cursor(pymysql.cursors.DictCursor)

        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM card"  # 카드테이블 초기화
                curs.execute(query)

                rows = curs.fetchall()
                card_length = len(rows)
                if int(card_length) > 0:
                    self.my.show_msg("카드테이블이 초기화 되지 않았습니다.")
                    return False

                query = "SELECT * FROM total"  # 토탈 테이블 초기화
                curs.execute(query)
                rows = curs.fetchall()
                for row in rows:
                    total_mny += int(row['total'])

                if total_mny > 0:
                    self.my.show_msg("토탈테이블이 초기화 되지 않았습니다.")
                    return False
            conn.commit()
        finally:
            conn.close()
        self.my.show_msg("초기화상태입니다.")
        return True

    # 전체 금액 초기화
    def init_money(self, use_input_mny):
        self.input_money -= use_input_mny
        self.temp_money -= use_input_mny
        self.input_cash = 0
        self.bonus = 0
        self.use_bonus = 0

        self.rf_class.input_cash = self.input_cash
        self.rf_class.input_money = self.input_money
        self.rf_class.bonus = self.bonus
        self.rf_class.use_bonus = 0

        total_mny = self.input_money + self.bonus
        total_mny = self.my.number_format(total_mny)
        self.change_money(total_mny, self.my.number_format(self.input_money), self.my.number_format(self.bonus), "금액초기화")

    # 뷰의 금액 변경
    def change_money(self, total_mny, mny, bonus, temp_str="지폐인식기"):
        try:
            self.charge_input.config(text="{} 원".format(str(total_mny)))
            self.charge1_input.config(text="{} 원".format(str(mny)))
            self.charge1_bonus_input.config(text="{} 원".format(str(bonus)))
            self.issued_input.config(text="{} 원".format(str(total_mny)))

            if total_mny == "0" or total_mny == 0:
                color = "black"
            else:
                color = "red"
            self.main_input.config(text=" 투입금액       {} 원".format(str(total_mny)), fg=color)
        except Exception as e:
            print("View money err >> " + e)

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

    # 관리자 페이지 열기
    def show_admin(self, event):
        self.config.load_config()
        self.count += 1
        if self.count >= 3:
            self.admin_pass_entry.delete(0, END)
            self.raise_frame(self.admin_login_frame)
            self.window.attributes('-fullscreen', False)
            self.entry_1.delete(0, 100)
            self.entry_2.delete(0, 100)
            self.entry_3.delete(0, 100)
            self.entry_4.delete(0, 100)
            self.entry_5.delete(0, 100)
            self.entry_6.delete(0, 100)
            self.entry_7.delete(0, 100)
            self.entry_8.delete(0, 100)
            self.entry_9.delete(0, 100)
            self.entry_10.delete(0, 100)

            self.shop_id_entry.delete(0, 100)
            self.card_price_entry.delete(0, 100)
            self.admin_password_entry.delete(0, 100)
            self.min_card_price_entry.delete(0, 100)

            self.entry_1.insert(0, self.my.number_format(self.config.get_config(10000)))
            self.entry_2.insert(0, self.my.number_format(self.config.get_config(20000)))
            self.entry_3.insert(0, self.my.number_format(self.config.get_config(30000)))
            self.entry_4.insert(0, self.my.number_format(self.config.get_config(40000)))
            self.entry_5.insert(0, self.my.number_format(self.config.get_config(50000)))
            self.entry_6.insert(0, self.my.number_format(self.config.get_config(60000)))
            self.entry_7.insert(0, self.my.number_format(self.config.get_config(70000)))
            self.entry_8.insert(0, self.my.number_format(self.config.get_config(80000)))
            self.entry_9.insert(0, self.my.number_format(self.config.get_config(90000)))
            self.entry_10.insert(0, self.my.number_format(self.config.get_config(100000)))

            self.card_price_entry.insert(0, self.my.number_format(self.config.get_config("card_price")))
            self.min_card_price_entry.insert(0, self.my.number_format(self.config.get_config("min_card_price")))
            # self.shop_title_entry.insert(0, self.config.get_config("shop_name"))
            self.shop_id_entry.insert(0, self.config.get_config("id"))
            self.admin_password_entry.insert(0, self.config.get_config("password"))

            self.master_entry_1.delete(0, 100)
            self.master_entry_2.delete(0, 100)
            self.master_entry_3.delete(0, 100)
            self.master_entry_4.delete(0, 100)
            self.master_entry_5.delete(0, 100)
            self.master_entry_6.delete(0, 100)
            self.master_entry_7.delete(0, 100)
            self.master_entry_8.delete(0, 100)
            self.master_entry_9.delete(0, 100)
            self.master_entry_10.delete(0, 100)

            # self.shop_title_entry.delete(0, 100)
            self.master_shop_id_entry.delete(0, 100)
            self.master_card_price_entry.delete(0, 100)
            self.master_admin_password_entry.delete(0, 100)
            self.master_min_card_price_entry.delete(0, END)

            self.master_entry_1.insert(0, self.my.number_format(self.config.get_config(10000)))
            self.master_entry_2.insert(0, self.my.number_format(self.config.get_config(20000)))
            self.master_entry_3.insert(0, self.my.number_format(self.config.get_config(30000)))
            self.master_entry_4.insert(0, self.my.number_format(self.config.get_config(40000)))
            self.master_entry_5.insert(0, self.my.number_format(self.config.get_config(50000)))
            self.master_entry_6.insert(0, self.my.number_format(self.config.get_config(60000)))
            self.master_entry_7.insert(0, self.my.number_format(self.config.get_config(70000)))
            self.master_entry_8.insert(0, self.my.number_format(self.config.get_config(80000)))
            self.master_entry_9.insert(0, self.my.number_format(self.config.get_config(90000)))
            self.master_entry_10.insert(0, self.my.number_format(self.config.get_config(100000)))

            self.master_card_price_entry.insert(0, self.my.number_format(self.config.get_config("card_price")))
            self.master_min_card_price_entry.insert(0, self.my.number_format(self.config.get_config("min_card_price")))
            # self.shop_title_entry.insert(0, self.config.get_config("shop_name"))
            self.master_shop_id_entry.insert(0, self.config.get_config("id"))
            self.master_admin_password_entry.insert(0, self.config.get_config("password"))

            manager_title = self.config.get_config("manager_name")
            self.rf_title.config(text="현재 업체 상태 : " + manager_title)

            binary_title = self.config.get_config("rf_reader_type")
            self.binary_title.config(text="현재 저장 번지 : " + binary_title)

            self.p = subprocess.Popen(['florence show'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if not "" == self.p.stderr.readline():
                self.p = subprocess.Popen(['florence'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            self.count = 0
            return

    # 카드 금액 초기화
    def init_card_money(self):
        if not self.DEBUG:
            if 'Linux' in platform.system():
                self.window.attributes('-fullscreen', True)
        self.init_shop_id_label.config(text="저장될 매장 ID : " + self.config.get_config("id"))
        self.init_card_start_enable_btn.place_forget()
        self.raise_frame(self.card_init_frame)

    # 매장 ID 입력 시작
    def init_card_money_start(self):
        self.rf_class.INIT_FLAG = True
        self.init_card_start_btn.place_forget()
        self.init_card_start_enable_btn.place(x=250, y=233)
        self.my.show_msg("카드 초기화모드를 시작합니다. 전면 리더기에 카드를 터치해주세요.")

    # 메인 UI 제어 스레드
    def init_view_thread(self, second=1.0):
        if self.rf_class.INIT_FLAG:
            if self.rf_class.init_state == "1":
                self.init_card_label.config(text="매장 ID 입력 상태 : 성공", fg="blue")
            else:
                self.init_card_label.config(text="매장 ID 입력 상태 : 실패", fg="red")

        if self.rf_class.charge_state == "1":
            print("충전 상태 ON")
            self.rf_class.CHARGE_FLAG = False
            self.rf_class.ISSUED_FLAG = False
            self.CHARGE_INIT_FLAG = False
            self.rf_class.charge_state = "0"

            # 금액 화면에 뷰
            self.charge2_input.config(text="{} 원".format(self.my.number_format(str(self.rf_class.total_money))))
            self.init_money(self.rf_class.use_money)

            # 충전 완료 화면으로 이동
            self.raise_frame(self.charge2_frame)

            if self.sound.get_busy():
                self.sound.stop_sound()
            self.sound.play_sound("./msgs/msg013.wav")  # 충전이 완료되었습니다 감사합니다.

            self.charge_phase1_state = True  # 충전 페이지1 음성 OFF

            if self.charge_phase1_thread:
                self.charge_phase1_thread.cancel()
            if self.charge_phase2_thread:
                self.charge_phase2_thread.cancel()

            time.sleep(2.5)
            self.rf_class.ISSUED_ENABLE = True
            self.phase_end()

        if self.rf_class.lookup_state == "1":
            print("조회 상태 ON")
            # 잔액조회 화면의 금액 변경
            self.lookup_input.config(text="{} 원".format(self.my.number_format(self.rf_class.card_remain_money)))
            self.rf_class.LOOKUP_FLAG = False

            # 잔액조회 화면으로 변경
            self.raise_frame(self.lookup_frame)

            if self.sound.get_busy():
                self.sound.stop_sound()

            self.sound.play_sound("./msgs/msg018.wav")  # 잔액조회가 완료되었습니다 감사합니다
            self.rf_class.lookup_state = "0"

            if self.lookup_phase1_thread:
                self.lookup_phase1_thread.cancel()
            if self.config.get_config("data_collect_state") == "1":
                self.lookup_member_class_label.config(text="회원등급 : " + str(self.rf_class.member_class))
                self.lookup_member_class_label.place(x=710, y=650)

            time.sleep(2.5)
            self.quit_lookup()

        rf_thread = threading.Timer(second, self.init_view_thread)
        rf_thread.daemon = True
        rf_thread.start()

    # 지폐인식기 스레드함수
    def bill_thread(self, second=1.0):
        state = self.bill.sendData("getActiveStatus")
        bill_data = ""
        if state == 1 or state == 11:
            bill_data = self.bill.sendData("billData")

            if type(bill_data) == int:
                # 투입금액
                if bill_data > 0:
                    self.input_money += bill_data
                    self.input_cash += bill_data
                    self.rf_class.input_money += bill_data
                    self.rf_class.current_money = self.input_cash

                    bonus = 0
                    self.rf_class.current_bonus = 0

                    self.rf_class.bonus = int(bonus)    # 리더기에 사용할 변수에 투입금액에 대한 보너스 주입
                    self.rf_class.current_bonus = int(self.input_money)  # 리더기에 사용할 변수에 투입금액에 대한 보너스 주입

                    total_view_mny = self.input_money + bonus  # 최종금액 = 투입금액 + 보너스
                    total_view_mny = self.my.number_format(total_view_mny)  # 최종 금액에 number format 작업
                    mny = self.my.number_format(self.input_money)  # 투입금액에 number format 작업

                    if bill_data:
                        if self.sound.get_busy():
                            self.sound.stop_sound()
                        self.sound.play_sound("./msgs/msg022.wav")

                    self.change_money(total_view_mny, mny, self.my.number_format(bonus))
                    self.bill.sendData("insertE")

        t = threading.Timer(second, self.bill_thread)
        t.daemon = True  # 메인함수가 종료될때 같이 종료됨
        t.start()

    # 지폐인식기 UI 스레드
    def bill_ui_thread(self, second=0.3):
        try:
            if int(self.input_money) > 0:
                self.charge_next_gif.config(state="active")
                if self.is_next_btn_animate():
                    self.next_btn_animate()

                if self.input_money >= self.CARD_MIN_MONEY:
                    if self.is_issued_next_btn_animate():
                        self.issued_next_btn_animate()
                        self.issued_next_gif.config(state="active")
            else:
                if not self.is_issued_next_btn_animate():
                    self.issued_next_btn_animate_stop()

                if not self.is_next_btn_animate():
                    self.next_btn_animate_stop()
                self.change_money(0, 0, 0)

        except Exception as e:
            print("bill_ui_thread_err : " + str(e))

        th = threading.Timer(second, self.bill_ui_thread)
        th.daemon = True
        th.start()

    def initialize(self):
        print("프로그램 시작")

        # 리더기 감시 시작
        cardmonitor = CardMonitor()
        self.rf_class = r.transmitobserver()
        cardmonitor.addObserver(self.rf_class)
        self.rf_class.LOOKUP_FLAG = True

        # 지폐인식기 쓰레드 시작
        # if not 'Windows' in platform.system():
        self.bill.sendData("insertE")
        self.bill_thread(1.0)
        self.bill_ui_thread(0.5)

        # UI 제어 시작
        self.init_view_thread(1.0)

    # UI 초기화
    def __init__(self):
        self.window = Tk()

        if not self.DEBUG:
            if 'Linux' in platform.system():
                self.window.attributes('-fullscreen', True)

        self.window.title("Charger")
        self.window.geometry("1024x768+0+0")
        self.window.resizable(False, False)

        # 프레임화면
        self.main_frame = Frame(self.window)
        self.charge_frame = Frame(self.window)   # 카드충전
        self.charge1_frame = Frame(self.window)  # 카드터치
        self.charge2_frame = Frame(self.window)
        self.issued_frame = Frame(self.window)   # 발급
        self.lookup_frame = Frame(self.window)   # 조회

        # 관리자, 마스터, 카드 초기화 페이지
        self.admin_frame = Frame(self.window)
        self.admin_login_frame = Frame(self.window)
        self.master_frame = Frame(self.window)
        self.card_init_frame = Frame(self.window)

        self.admin_pass_entry = Entry(self.admin_login_frame, show="*")
        self.admin_pass_entry.grid(row=1, column=1, padx=5)

        admin_pass_btn = Button(self.admin_login_frame, text="확인", command=lambda: self.login(self.admin_pass_entry.get()))
        admin_pass_btn.grid(row=1, column=2, padx=5)

        admin_pass_btn = Button(self.admin_login_frame, text="취소", command=lambda: self.main_frame_raise())
        admin_pass_btn.grid(row=1, column=3)

        self.admin_login_frame.grid_rowconfigure(0, weight=1)
        self.admin_login_frame.grid_rowconfigure(3, weight=1)
        self.admin_login_frame.grid_columnconfigure(0, weight=1)
        self.admin_login_frame.grid_columnconfigure(4, weight=1)

        # 관리자페이지 시작
        title_label = Label(self.admin_frame, text="관리자 환경설정", font=("", 40, 'bold'), anchor="e")
        title_label.place(x=290, y=40)

        title_label = Label(self.admin_frame, text="버전 : " + str(self.config.get_config("version")), font=("", 20, 'bold'), anchor="e")
        title_label.place(x=750, y=50)

        title_1 = Label(self.admin_frame, text="10,000원 보너스금액", font=("", 12, "bold"))
        title_1.place(x=50, y=160)
        self.entry_1 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_1.place(x=240, y=150)

        title_2 = Label(self.admin_frame, text="20,000원 보너스금액", font=("", 12, "bold"))
        title_2.place(x=50, y=210)
        self.entry_2 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_2.place(x=240, y=200)

        title_3 = Label(self.admin_frame, text="30,000원 보너스금액", font=("", 12, "bold"))
        title_3.place(x=50, y=260)
        self.entry_3 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_3.place(x=240, y=250)

        title_4 = Label(self.admin_frame, text="40,000원 보너스금액", font=("", 12, "bold"))
        title_4.place(x=50, y=310)
        self.entry_4 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_4.place(x=240, y=300)

        title_5 = Label(self.admin_frame, text="50,000원 보너스금액", font=("", 12, "bold"))
        title_5.place(x=50, y=360)
        self.entry_5 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_5.place(x=240, y=350)

        title_6 = Label(self.admin_frame, text="60,000원 보너스금액", font=("", 12, "bold"))
        title_6.place(x=50, y=410)
        self.entry_6 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_6.place(x=240, y=400)

        title_7 = Label(self.admin_frame, text="70,000원 보너스금액", font=("", 12, "bold"))
        title_7.place(x=50, y=460)
        self.entry_7 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_7.place(x=240, y=450)

        title_8 = Label(self.admin_frame, text="80,000원 보너스금액", font=("", 12, "bold"))
        title_8.place(x=50, y=510)
        self.entry_8 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_8.place(x=240, y=500)

        title_9 = Label(self.admin_frame, text="90,000원 보너스금액", font=("", 12, "bold"))
        title_9.place(x=50, y=560)
        self.entry_9 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_9.place(x=240, y=550)

        title_10 = Label(self.admin_frame, text="100,000원 보너스금액", font=("", 12, "bold"))
        title_10.place(x=50, y=610)
        self.entry_10 = Entry(self.admin_frame, width=7, font=("", 25))
        self.entry_10.place(x=240, y=600)

        admin_pass = Label(self.admin_frame, text="관리자비밀번호", font=("", 12, "bold"))
        admin_pass.place(x=500, y=160)
        self.admin_password_entry = Entry(self.admin_frame, width=13, font=("", 25))
        self.admin_password_entry.place(x=700, y=150)

        card_price = Label(self.admin_frame, text="카드 발급 금액", font=("", 12, "bold"))
        card_price.place(x=500, y=260)
        self.card_price_entry = Entry(self.admin_frame, width=10, font=("", 25))
        self.card_price_entry.place(x=700, y=250)

        min_card_price = Label(self.admin_frame, text="카드 발급 최소 투입금액", font=("", 12, "bold"))
        min_card_price.place(x=500, y=360)
        self.min_card_price_entry = Entry(self.admin_frame, width=10, font=("", 25))
        self.min_card_price_entry.place(x=700, y=350)

        shop_id = Label(self.admin_frame, text="매장 번호", font=("", 12, "bold"))
        shop_id.place(x=500, y=460)
        self.shop_id_entry = Entry(self.admin_frame, width=10, font=("", 25))
        self.shop_id_entry.place(x=700, y=450)

        card_init_btn = Button(self.admin_frame, text="매장 ID 등록 모드 진입", activebackground="blue", width=20, height=2, font=("", 13, "bold"), command=lambda: self.init_card_money())
        card_init_btn.place(x=700, y=550)

        admin_save_btn = Button(self.admin_frame, text="저    장", width=20, height=2, font=("", 15, "bold"), command=lambda: self.set_all_data())
        admin_save_btn.place(x=250, y=650)
        admin_back_btn = Button(self.admin_frame, text="취    소", width=20, height=2, font=("", 15, "bold"), command=lambda: self.main_frame_raise())
        admin_back_btn.place(x=510, y=650)

        power_off = Button(self.admin_frame, text="프로그램\n종료", width=10, height=2, font=("", 15, "bold"), command=lambda: self.power_off())
        power_off.place(x=850, y=650)

        # 마스터페이지 시작
        title_label = Label(self.master_frame, text="마스터 환경설정", font=("", 40, 'bold'), anchor="e")
        title_label.place(x=290, y=40)

        master_title_1 = Label(self.master_frame, text="10,000원 보너스금액", font=("", 12, "bold"))
        master_title_1.place(x=50, y=160)
        self.master_entry_1 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_1.place(x=240, y=150)

        master_title_2 = Label(self.master_frame, text="20,000원 보너스금액", font=("", 12, "bold"))
        master_title_2.place(x=50, y=210)
        self.master_entry_2 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_2.place(x=240, y=200)

        master_title_3 = Label(self.master_frame, text="30,000원 보너스금액", font=("", 12, "bold"))
        master_title_3.place(x=50, y=260)
        self.master_entry_3 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_3.place(x=240, y=250)

        master_title_4 = Label(self.master_frame, text="40,000원 보너스금액", font=("", 12, "bold"))
        master_title_4.place(x=50, y=310)
        self.master_entry_4 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_4.place(x=240, y=300)

        master_title_5 = Label(self.master_frame, text="50,000원 보너스금액", font=("", 12, "bold"))
        master_title_5.place(x=50, y=360)
        self.master_entry_5 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_5.place(x=240, y=350)

        master_title_6 = Label(self.master_frame, text="60,000원 보너스금액", font=("", 12, "bold"))
        master_title_6.place(x=50, y=410)
        self.master_entry_6 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_6.place(x=240, y=400)

        master_title_7 = Label(self.master_frame, text="70,000원 보너스금액", font=("", 12, "bold"))
        master_title_7.place(x=50, y=460)
        self.master_entry_7 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_7.place(x=240, y=450)

        master_title_8 = Label(self.master_frame, text="80,000원 보너스금액", font=("", 12, "bold"))
        master_title_8.place(x=50, y=510)
        self.master_entry_8 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_8.place(x=240, y=500)

        master_title_9 = Label(self.master_frame, text="90,000원 보너스금액", font=("", 12, "bold"))
        master_title_9.place(x=50, y=560)
        self.master_entry_9 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_9.place(x=240, y=550)

        master_title_10 = Label(self.master_frame, text="100,000원 보너스금액", font=("", 12, "bold"))
        master_title_10.place(x=50, y=610)
        self.master_entry_10 = Entry(self.master_frame, width=7, font=("", 25))
        self.master_entry_10.place(x=240, y=600)

        master_admin_pass = Label(self.master_frame, text="관리자비밀번호", font=("", 12, "bold"))
        master_admin_pass.place(x=500, y=160)
        self.master_admin_password_entry = Entry(self.master_frame, width=13, font=("", 25))
        self.master_admin_password_entry.place(x=660, y=150)

        master_card_price = Label(self.master_frame, text="카드 발급 금액", font=("", 12, "bold"))
        master_card_price.place(x=500, y=210)
        self.master_card_price_entry = Entry(self.master_frame, width=10, font=("", 25))
        self.master_card_price_entry.place(x=660, y=200)

        master_min_card_price = Label(self.master_frame, text="카드 발급 최소 투입금액", font=("", 12, "bold"))
        master_min_card_price.place(x=500, y=260)
        self.master_min_card_price_entry = Entry(self.master_frame, width=10, font=("", 25))
        self.master_min_card_price_entry.place(x=660, y=250)

        master_shop_id = Label(self.master_frame, text="매장 번호", font=("", 12, "bold"))
        master_shop_id.place(x=500, y=310)
        self.master_shop_id_entry = Entry(self.master_frame, width=10, font=("", 25))
        self.master_shop_id_entry.place(x=660, y=300)

        master_admin_save_btn = Button(self.master_frame, text="저    장", width=20, height=2, font=("", 15, "bold"), command=lambda: self.set_master_all_data())
        master_admin_save_btn.place(x=250, y=650)
        master_admin_back_btn = Button(self.master_frame, text="취    소", width=20, height=2, font=("", 15, "bold"), command=lambda: self.main_frame_raise())
        master_admin_back_btn.place(x=510, y=650)

        master_power_off = Button(self.master_frame, text="프로그램\n종료", width=10, height=2, font=("", 15, "bold"), command=lambda: self.power_off())
        master_power_off.place(x=850, y=650)

        database_init_btn = Button(self.master_frame, text="데이터베이스 초기화", activebackground="blue", command=lambda: self.init_database())
        database_init_btn.place(x=850, y=550)

        database_check_btn = Button(self.master_frame, text="데이터베이스 초기화 확인", activebackground="blue", command=lambda: self.check_database())
        database_check_btn.place(x=850, y=600)

        # 업체 선택 셀렉트
        manager_title = self.config.get_config("manager_name")

        # 카드 저장 번지
        card_binary_title = self.config.get_config("rf_reader_type")

        self.rf_title = Label(self.master_frame, text="현재 업체 상태 : " + manager_title, font=("", 15, "bold"), anchor="e")
        self.rf_title.place(x=550, y=360)

        self.binary_title = Label(self.master_frame, text="현재 저장 번지 :" + card_binary_title, font=("", 15, 'bold'), anchor="e")
        self.binary_title.place(x=550, y=450)

        manager_list = self.config.get_manager_list()
        values = []
        binary_values = []
        for mg in manager_list:
            values.append(mg["manager_name"])

        binary_values.append("1")
        binary_values.append("2")

        self.manager_combobox = tkinter.ttk.Combobox(self.master_frame, height=15, values=values, font=("", 15, 'bold'))
        self.manager_combobox.place(x=550, y=410)
        self.manager_combobox.set(self.config.get_config("manager_name"))  # 현재 정보 셀렉트

        self.binary_combobox = tkinter.ttk.Combobox(self.master_frame, height=15, values=binary_values, font=("", 15, 'bold'))
        self.binary_combobox.place(x=550, y=500)
        self.binary_combobox.set(self.config.get_config("rf_reader_type"))

        frame_array = [self.main_frame, self.charge_frame, self.charge1_frame, self.charge2_frame, self.issued_frame,
                       self.lookup_frame, self.admin_login_frame, self.admin_frame, self.master_frame, self.card_init_frame]

        # 프레임 셋팅
        for frame in frame_array:
            frame.grid(row=0, column=0, sticky='news')

        # 메인 배경
        # main_back_image = PIL.Image.open("./images/test_back.png") # 디자인 수정용
        main_back_image = PIL.Image.open("./images/main_back.png")
        main_back_image = ImageTk.PhotoImage(main_back_image)
        self.main_back = Label(self.main_frame, image=main_back_image, bg="#a8c4b9")
        self.main_back.bind("<Button-1>", self.init_main_sound)  # 버튼 클릭시 음성재생
        self.main_back.pack()

        # 카드 초기화 배경
        card_init_back_image = PIL.Image.open("./images/main_back.png")
        card_init_back_image = ImageTk.PhotoImage(card_init_back_image)
        card_init_back = Label(self.card_init_frame, image=card_init_back_image, bg="#a8c4b9")
        card_init_back.pack()

        # 관리자기능
        admin_input_label = Label(self.main_frame, bg="#a8c4b9", width=30, height=5)
        admin_input_label.bind('<Button-1>', self.show_admin)
        admin_input_label.place(x=20, y=0)

        # 메인 사용라벨
        main_use_image = PIL.Image.open("./images/main_use_label.png")
        main_use_image = ImageTk.PhotoImage(main_use_image)
        self.main_use_label = Label(self.main_frame, image=main_use_image, bd=0)
        self.main_use_label.visible = True
        self.main_use_label.place(x=281, y=535)
        self.main_use_label_pi = self.main_use_label.place_info()

        # 카드충전 배경 (현금투입)
        charge_back_image = PIL.Image.open("./images/new_charge_back.png")
        charge_back_image = ImageTk.PhotoImage(charge_back_image)
        self.charge_back = Label(self.charge_frame, image=charge_back_image, bg="#a8c4b9").pack()

        charge_gif = animate.AnimatedGif(self.charge_frame, './images/bill-1.gif', 0.7)
        charge_gif.config(bg="#a8c4b9")
        charge_gif.place(x=360, y=360)
        charge_gif.start()

        # 카드충전배경 (카드터치)
        charge1_back_image = PIL.Image.open("./images/charge1_back.png")
        charge1_back_image = ImageTk.PhotoImage(charge1_back_image)
        self.charge1_back = Label(self.charge1_frame, image=charge1_back_image).pack()

        # 카드충전배경 (카드잔액)
        charge2_back_image = PIL.Image.open("./images/charge2_back.png")
        charge2_back_image = ImageTk.PhotoImage(charge2_back_image)
        self.charge2_back = Label(self.charge2_frame, image=charge2_back_image).pack()

        # 카드발급 배경 (현금투입)
        issued_back_image = PIL.Image.open("./images/new_issued_back.png")
        issued_back_image = ImageTk.PhotoImage(issued_back_image)
        self.issued_back = Label(self.issued_frame, image=issued_back_image, bg="#a8c4b9").pack()

        issued_gif = animate.AnimatedGif(self.issued_frame, './images/bill-1.gif', 0.7)
        issued_gif.config(bg="#a8c4b9")
        issued_gif.place(x=360, y=360)
        issued_gif.start()

        # 잔액조회배경
        lookup_back_image = PIL.Image.open("./images/lookup_back.png")
        lookup_back_image = ImageTk.PhotoImage(lookup_back_image)
        self.lookup_back = Label(self.lookup_frame, image=lookup_back_image, bg="#a8c4b9").pack()

        # 메인 남은금액
        self.main_input = Label(self.main_frame, text="투입금액     0원", fg="black", bg="#a8c4b9", width=27, font=("Corier", 29, "bold"), anchor="e")
        self.main_input.place(x=0, y=700)

        # 카드 초기화 상태
        self.init_card_label = Label(self.card_init_frame, text="매장 ID 입력 상태 : X", fg="black", bg="#a8c4b9", width=30, font=("Corier", 29, "bold"), anchor="e")
        self.init_card_label.place(x=0, y=50)

        self.init_shop_id_label = Label(self.card_init_frame, text="저장될 매장 ID : 0000", fg="black", bg="#a8c4b9", width=30, font=("Corier", 29, "bold"), anchor="e")
        self.init_shop_id_label.place(x=0, y=160)
        # 카드충전 투입금액
        self.charge_input = Label(self.charge_frame, text="0 원", fg="#34fccb", bg="#454f49", width=11, font=("Corier", 40), anchor="e")
        self.charge_input.place(x=490, y=215)

        # 카드충전1 투입금액
        self.charge1_input = Label(self.charge1_frame, text="0 원", fg="#34fccb", bg="#454f49", width=11, font=("Corier", 40), anchor="e")
        self.charge1_input.place(x=490, y=215)

        # 카드충전1 보너스 금액
        self.charge1_bonus_input = Label(self.charge1_frame, text="0 원", fg="#fefefe", bg="#464646", width=8, font=("Corier", 12), anchor="e")
        self.charge1_bonus_input.place(x=744, y=295)

        # 카드충전2 투입금액
        self.charge2_input = Label(self.charge2_frame, text="0 원", fg="#34fccb", bg="#454f49", width=11, font=("Corier", 40), anchor="e")
        self.charge2_input.place(x=490, y=215)

        # 카드 발급 투입금액
        self.issued_input = Label(self.issued_frame, text="0 원", fg="#34fccb", bg="#454f49", width=11, font=("Corier", 40), anchor="e")
        self.issued_input.place(x=490, y=215)

        # 카드발급 카드금액
        self.issued_card = Label(self.issued_frame, text=self.my.number_format(self.config.get_config("card_price")) + " 원", fg="#fefefe", bg="#464646", width=8, font=("Corier", 12), anchor="e")
        self.issued_card.place(x=744, y=295)

        # 잔액조회 잔액
        self.lookup_input = Label(self.lookup_frame, text="0 원", fg="#34fecc", bg="#444f49", width=11, font=("Corier", 40), anchor="e")
        self.lookup_input.place(x=490, y=215)

        # 메인 제목
        self.main_label = Label(self.main_frame, text="저희 세차장을 이용해주셔서 감사합니다", font=("Corier", 20), bg="#a8c4b9")
        self.main_label.place(x=60, y=70)

        # 메인 버튼 3개 모듈 연결 여부검사 후 이미지변경
        charge_btn_img = self.getBackgroundImage(1)
        charge_btn_back = ImageTk.PhotoImage(charge_btn_img)
        issued_btn_img = self.getBackgroundImage(2)
        issued_btn_back = ImageTk.PhotoImage(issued_btn_img)
        lookup_btn_img = self.getBackgroundImage(3)
        lookup_btn_back = ImageTk.PhotoImage(lookup_btn_img)

        # 카드충전 다음 버튼 잔액검사 후 이미지변경
        charge_next_btn_img = PIL.Image.open("./images/next_btn_off.png")
        issued_next_btn_img = PIL.Image.open("./images/next_btn_off.png")
        charge_next_btn = ImageTk.PhotoImage(charge_next_btn_img)
        issued_next_btn = ImageTk.PhotoImage(issued_next_btn_img)

        # 카드충전 버튼 이미지 변경
        charge_back_btn_img = PIL.Image.open("./images/back_btn.png")
        charge_back_btn = ImageTk.PhotoImage(charge_back_btn_img)

        # 카드발급 버튼 이미지 변경
        issued_back_btn_img = PIL.Image.open("./images/back_btn.png")
        issued_back_btn = ImageTk.PhotoImage(issued_back_btn_img)

        # 잔액조회 버튼 이미지 변경
        lookup_back_btn_img = PIL.Image.open("./images/back_btn.png")
        lookup_back_btn = ImageTk.PhotoImage(lookup_back_btn_img)

        # 초기화 시작 버튼 이미지 연결
        init_btn_back = PIL.Image.open("./images/init_start_btn.png")
        init_btn_back = ImageTk.PhotoImage(init_btn_back)

        # 초기화 동작 중 버튼 이미지 연결
        init_btn_enable_back = PIL.Image.open("./images/init_start_btn_enable.png")
        init_btn_enable_back = ImageTk.PhotoImage(init_btn_enable_back)

        # 초기화 종료 버튼 이미지 연결
        init_btn_quit_back = PIL.Image.open("./images/init_quit_btn.png")
        init_quit_btn_back = ImageTk.PhotoImage(init_btn_quit_back)

        # 메인 충전, 발급, 조회 버튼 객체 생성
        self.charge_btn = Button(self.main_frame, image=charge_btn_back, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", width="250")
        self.issued_btn = Button(self.main_frame, image=issued_btn_back, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")
        self.lookup_btn = Button(self.main_frame, image=lookup_btn_back, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", width="250")

        self.init_card_start_btn = Button(self.card_init_frame, image=init_btn_back, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")
        self.init_card_start_btn.config(command=lambda: self.init_card_money_start())
        self.init_card_start_btn.place(x=250, y=233)

        self.init_card_start_enable_btn = Button(self.card_init_frame, image=init_btn_enable_back, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")
        self.init_card_start_enable_btn.place(x=250, y=233)

        quit_card_init_btn = Button(self.card_init_frame, image=init_quit_btn_back, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")
        quit_card_init_btn.config(command=lambda: self.quit_card_money())
        quit_card_init_btn.place(x=550, y=233)

        # 버튼 상태 변경
        if self.bill.BILL_CONNECT:
            self.charge_btn.config(command=lambda: self.charge_init())
        else:
            self.charge_btn.config(command=lambda: self.my.show_msg("모듈을 연결해주세요"))

        if self.card.CARD_CONNECT:
            self.issued_btn.config(command=lambda: self.issued_init())
        else:
            self.charge_btn.config(command=lambda: self.my.show_msg("모듈을 연결해주세요"))

        self.lookup_btn.config(command=lambda: self.lookup_init())

        self.charge_btn.place(x=84, y=233)
        self.issued_btn.place(x=385, y=233)
        self.lookup_btn.place(x=686, y=233)

        # 카드충전 버튼 객체생성
        self.charge_next_btn = Button(self.charge_frame, image=charge_next_btn, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", width="155", state="disabled")
        self.charge_back_btn = Button(self.charge_frame, image=charge_back_btn, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", command=lambda: self.quit_charge(self.main_frame), width="155")
        self.charge_back_btn1 = Button(self.charge1_frame, image=charge_back_btn, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", width="155", command=lambda: self.quit_charge(self.main_frame))
        self.charge_back_btn.place(x=50, y=650)
        self.charge_back_btn1.place(x=50, y=650)

        self.charge_next_gif = animate.AnimatedButtonGif(self.charge_frame, "./images/next_btn_ani2.gif", 0.7)
        self.charge_next_gif.config(bg="#a8c4b9", command=lambda: self.charge_next(), relief="solid", bd="0", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")

        # 카드발급 버튼 객체생성 -> 다음버튼 핸들링
        self.issued_next_btn = Button(self.issued_frame, image=issued_next_btn, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", width="155", state="disable")
        self.issued_back_btn = Button(self.issued_frame, image=issued_back_btn, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", width="155", command=lambda: self.quit_issued(self.main_frame))
        self.issued_back_btn.place(x=50, y=650)

        self.issued_next_gif = animate.AnimatedButtonGif(self.issued_frame, './images/next_btn_ani2.gif', 0.7)
        self.issued_next_gif.config(bg="#a8c4b9", command=lambda: self.issued(), relief="solid", bd="0", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9")

        # 잔액조회 버튼 객체생성
        self.lookup_back_btn = Button(self.lookup_frame, image=lookup_back_btn, relief="solid", bd="0", bg="#a8c4b9", activebackground="#a8c4b9", highlightthickness=4, highlightcolor="#a8c4b9", anchor="center", highlightbackground="#a8c4b9", width="155", command=lambda: self.quit_lookup())
        self.lookup_back_btn.place(x=50, y=650)

        # 잔액조회 회원등급 라벨 객체 생성
        member_class_title = Label(self.lookup_frame, text="회원등급 : ", bg="#a8c4b9", font=("Corier", 20, "bold"))
        self.lookup_member_class_label = Label(self.lookup_frame, text="회원등급 : ", bg="#a8c4b9", font=("Corier", 20, "bold"))

        self.charge_next_btn.visible = True
        self.issued_next_btn.visible = True
        self.charge_next_btn.place(x=825, y=650)  # 충전 초기 다음버튼
        self.charge_next_btn_pi = self.charge_next_btn.place_info()
        self.issued_next_btn.place(x=825, y=650)  # 발급 초기 다음 버튼
        self.issued_next_btn_pi = self.issued_next_btn.place_info()

        self.main_use_label_init(4)
        self.raise_frame(self.main_frame)

        self.initialize()  # 생성자는 UI 설정후 맨뒤에
        self.window.mainloop()


if __name__ == "__main__":
    app = Main()