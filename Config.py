import pymysql
import platform
import base64
from collections import OrderedDict


class Config:
    UPDATE_VERSION = "1.3.0"
    man = ""
    man2 = ""
    man3 = ""
    man4 = ""
    man5 = ""
    man6 = ""
    man7 = ""
    man8 = ""
    man9 = ""
    man10 = ""

    mb_bonus1 = ""
    mb_bonus2 = ""
    mb_bonus3 = ""
    mb_bonus4 = ""
    mb_bonus5 = ""
    mb_bonus6 = ""
    mb_bonus7 = ""
    mb_bonus8 = ""
    mb_bonus9 = ""
    mb_bonus10 = ""

    crc = [] * 100

    card_price = ""
    shop_name = ""
    id = ""
    shop_id = ""
    admin_password = ""
    gil_password = ""
    master_password = ""
    rf_reader_type = ""
    version = ""

    manager_no = ""
    manager_id = ""
    manager_name = ""
    encrypt = ""
    data_collect_state = ""

    MYSQL_HOST = "glstest.iptime.org"
    MYSQL_PORT = 30001
    if 'Linux' in platform.system():
        MYSQL_HOST = "localhost"
        MYSQL_PORT = 3306

    # 데이터베이스 연걸 초기화
    def __init__(self):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user='pi', password='1234', charset='utf8', db='glstech')

        # Connection 으로부터 Dictionary Cursor 생성
        curs = conn.cursor(pymysql.cursors.DictCursor)

        try:
            with conn.cursor() as cursor:
                sql = 'SELECT ' \
                      '`con`.`bonus1`, ' \
                      '`con`.`bonus2`, ' \
                      '`con`.`bonus3`, ' \
                      '`con`.`bonus4`, ' \
                      '`con`.`bonus5`, ' \
                      '`con`.`bonus6`, ' \
                      '`con`.`bonus7`, ' \
                      '`con`.`bonus8`, ' \
                      '`con`.`bonus9`, ' \
                      '`con`.`bonus10`, ' \
                      '`con`.`card_price`, ' \
                      '`con`.`min_card_price`, ' \
                      '`con`.`shop_name`, ' \
                      '`con`.`id`, ' \
                      '`con`.`admin_password`, ' \
                      '`con`.`gil_password`, ' \
                      '`con`.`master_password`, ' \
                      '`con`.`rf_reader_type`,' \
                      '`con`.`version`,' \
                      '`mg`.`no` as `manager_no`, ' \
                      '`mg`.`manager_name` as `manager_name`, ' \
                      '`mg`.`manager_id` as `shop_id`,' \
                      '`mg`.`encrypt`, `con`.`data_collect_state` ' \
                      'FROM config AS `con` INNER JOIN manager AS `mg` ON `con`.`manager_no` = `mg`.`no`'
                curs.execute(sql)

                # 대이터 가져오기
                rows = curs.fetchall()
                for row in rows:
                    self.man = row['bonus1']
                    self.man2 = row['bonus2']
                    self.man3 = row['bonus3']
                    self.man4 = row['bonus4']
                    self.man5 = row['bonus5']
                    self.man6 = row['bonus6']
                    self.man7 = row['bonus7']
                    self.man8 = row['bonus8']
                    self.man9 = row['bonus9']
                    self.man10 = row['bonus10']
                    self.card_price = row['card_price']
                    self.min_card_price = row['min_card_price']
                    self.shop_name = row['shop_name']
                    self.id = row['id']
                    self.shop_id = row['shop_id']
                    self.admin_password = base64.b64decode(row['admin_password'])
                    self.admin_password = self.admin_password.decode('utf-8')
                    self.gil_password = base64.b64decode(row['gil_password'])
                    self.gil_password = self.gil_password.decode('utf-8')
                    self.master_password = base64.b64decode(row['master_password'])
                    self.master_password = self.master_password.decode('utf-8')
                    self.rf_reader_type = row['rf_reader_type']
                    self.version = row['version']
                    self.manager_name = row['manager_name']
                    self.manager_no = row['manager_no']
                    self.encrypt = row['encrypt']
                    self.data_collect_state = row['data_collect_state']

                sql = "SELECT * FROM crc ORDER BY no ASC"
                curs.execute(sql)
                rows = curs.fetchall()
                for row in rows:
                    self.crc.append(row['crc'])

                if self.version != self.UPDATE_VERSION:
                    sql = "UPDATE config SET version = %s"
                    curs.execute(sql, self.UPDATE_VERSION)

                sql = "SELECT * FROM manager ORDER BY no ASC"
                curs.execute(sql)
                rows = curs.fetchall()
                for row in rows:
                    if row['no'] == 1:
                        if row['manager_name'] != "길광":
                            sql = "DELETE FROM manager"
                            curs.execute(sql)

                            sql = "INSERT INTO manager (`no`, `manager_name`, `manager_id`, `encrypt`) VALUE (%s, %s, %s, %s)"
                            curs.execute(sql, ("1", "길광", "05D355B94FEE", "1"))

                            sql = "INSERT INTO manager (`no`, `manager_name`, `manager_id`, `encrypt`) VALUE (%s, %s, %s, %s)"
                            curs.execute(sql, ("2", "주일", "000040BC840C", "0"))

                            sql = "INSERT INTO manager (`no`, `manager_name`, `manager_id`, `encrypt`) VALUE (%s, %s, %s, %s)"
                            curs.execute(sql, ("3", "대진", "0350870E930E", "1"))

                            sql = "INSERT INTO manager (`no`, `manager_name`, `manager_id`, `encrypt`) VALUE (%s, %s, %s, %s)"
                            curs.execute(sql, ("4", "(구)길광", "0000000021B0", "0"))

                            if self.manager_no == 1:
                                update_manager_no = "4"

                            elif self.manager_no == 2:
                                update_manager_no = "1"

                            elif self.manager_no == 3:
                                update_manager_no = "2"

                            else:
                                update_manager_no = "3"

                            sql = "UPDATE config SET manager_no %s"
                            curs.execute(sql, (update_manager_no))
                            break
            conn.commit()
        finally:
            conn.close()

    # 데이터베이스 설정값 불러오기
    def get_config(self, arg):
        if arg == 10000:
            return self.man
        elif arg == 20000:
            return self.man2
        elif arg == 30000:
            return self.man3
        elif arg == 40000:
            return self.man4
        elif arg == 50000:
            return self.man5
        elif arg == 60000:
            return self.man6
        elif arg == 70000:
            return self.man7
        elif arg == 80000:
            return self.man8
        elif arg == 90000:
            return self.man9
        elif arg == 100000:
            return self.man10
        elif arg == "card_price":
            return self.card_price
        elif arg == "min_card_price":
            return self.min_card_price
        elif arg == "shop_name":
            return self.shop_name
        elif arg == "id":
            return self.id
        elif arg == "password":
            return self.admin_password
        elif arg == "gil_password":
            return self.gil_password
        elif arg == "master_password":
            return self.master_password
        elif arg == "rf_reader_type":
            return self.rf_reader_type
        elif arg == "shop_id":
            return self.shop_id
        elif arg == "version":
            return self.version
        elif arg == "manager_name":
            return self.manager_name
        elif arg == "manager_id":
            return self.manager_id
        elif arg == "manager_no":
            return self.manager_no
        elif arg == "encrypt":
            return self.encrypt
        elif arg == "data_collect_state":
            return self.data_collect_state
        else:
            return 0

    # 공급업체 조회하여 세차장 정보 찾아가기
    def load_config(self):
        conn = pymysql.connect(host=self.MYSQL_HOST,
                               port=self.MYSQL_PORT,
                               user='pi',
                               password='1234',
                               charset='utf8',
                               db='glstech')

        curs = conn.cursor(pymysql.cursors.DictCursor)

        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM config as `con` INNER JOIN manager as `mg` ON `con`.`manager_no` = `mg`.`no`"
                curs.execute(sql)

                rows = curs.fetchall()
                for row in rows:
                    self.man = row['bonus1']
                    self.man2 = row['bonus2']
                    self.man3 = row['bonus3']
                    self.man4 = row['bonus4']
                    self.man5 = row['bonus5']
                    self.man6 = row['bonus6']
                    self.man7 = row['bonus7']
                    self.man8 = row['bonus8']
                    self.man9 = row['bonus9']
                    self.man10 = row['bonus10']
                    self.card_price = row['card_price']
                    self.min_card_price = row['min_card_price']
                    self.shop_name = row['shop_name']
                    self.id = row['id']
                    self.admin_password = base64.b64decode(row['admin_password'])
                    self.admin_password = self.admin_password.decode('utf-8')
                    self.gil_password = base64.b64decode(row['gil_password'])
                    self.gil_password = self.gil_password.decode('utf-8')
                    self.master_password = base64.b64decode(row['master_password'])
                    self.master_password = self.master_password.decode('utf-8')
                    self.rf_reader_type = row['rf_reader_type']
                    self.version = row['version']
                    self.shop_id = row['shop_id']
                    self.manager_name = row['manager_name']
                    self.manager_no = row['manager_no']
                    self.encrypt = row['encrypt']
                    self.data_collect_state = row['data_collect_state']
            conn.commit()
        finally:
            conn.close()

    # 관리자 페이지 설정값 변경
    def set_all_data(self, dic):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user='pi', password='1234', charset='utf8', db='glstech')

        admin_pass = dic['admin_password'].encode('utf-8')
        temp = base64.b64encode(admin_pass)
        admin_pass = temp.decode("utf-8")

        try:
            with conn.cursor() as cursor:
                sql = 'UPDATE config SET bonus1 = %s, bonus2 = %s, bonus3 = %s, bonus4 = %s, bonus5 = %s, bonus6 = %s, bonus7 = %s, bonus8 = %s, bonus9 = %s, bonus10 = %s, card_price = %s, id = %s, admin_password = %s, min_card_price = %s'
                cursor.execute(sql, (dic["man"], dic["2man"], dic["3man"], dic["4man"], dic["5man"], dic["6man"], dic["7man"], dic["8man"], dic["9man"], dic["10man"],
                                     dic["card_price"], dic['id'], admin_pass, dic['min_card_price']))
            conn.commit()
        finally:
            conn.close()
        self.load_config()

    # 마스터 페이지 설정값 변경
    def set_all_data_master(self, dic):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user='pi', password='1234', charset='utf8', db='glstech')

        admin_pass = dic['admin_password'].encode("utf-8")
        temp = base64.b64encode(admin_pass)
        admin_pass = temp.decode("utf-8")
        manager_info = self.get_manager(dic['manager_name'])
        print("dic(manager_info) : ", manager_info)

        try:
            with conn.cursor() as cursor:
                sql = 'UPDATE config SET bonus1 = %s, bonus2 = %s, bonus3 = %s, bonus4 = %s, bonus5 = %s, bonus6 = %s, bonus7 = %s, bonus8 = %s, bonus9 = %s, bonus10 = %s, '\
                      'card_price = %s, id = %s, admin_password = %s, min_card_price = %s, manager_no = %s, rf_reader_type = %s, shop_id = %s'
                cursor.execute(sql, (dic["man"], dic["2man"], dic["3man"], dic["4man"], dic["5man"], dic["6man"], dic["7man"], dic["8man"], dic["9man"], dic["10man"],
                                     dic["card_price"], dic['id'], admin_pass, dic['min_card_price'], str(manager_info['no']), dic["binary_type"], str(manager_info['manager_no'])))
            conn.commit()
        finally:
            conn.close()
        self.load_config()

    # 누적금액 계산하기
    def set_total_table(self, dic):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user='pi', password='1234', charset='utf8mb4', db='glstech')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        try:
            with conn.cursor() as cursor:
                total_mny = dic['total_mny']
                charge_mny = dic['charge_mny']
                bonus_mny = dic['bonus_mny']
                card_price = dic["card_price"]
                card_count = dic["card_count"]

                sql = "UPDATE total SET `total` = total + %s, `charge` = charge + %s, `bonus` = bonus + %s, `card` = card + %s, `card_count` = card_count + %s"
                cursor.execute(sql, (total_mny, charge_mny, bonus_mny, card_price, card_count))
            conn.commit()
        finally:
            conn.close()
        return

    # 충전된 카드 내역 계산하기
    def set_card_table(self, dic):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user='pi', password='1234', charset='utf8mb4', db='glstech')
        curs = conn.cursor(pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                card_num = dic['card_num']              # 카드 번호
                total_mny = dic['total_mny']            # 카드 잔액
                current_mny = dic['current_mny']        # 투입 금액
                current_bonus = dic['current_bonus']    # 현재 보너스
                charge_money = dic['charge_money']      # 총 충전 금액
                before_mny = dic['before_mny']          # 충전 전 카드 잔액
                reader_type = dic['reader_type']        # 충전된 리더기 종류
                card_price = dic['card_price']          # 카드 가격
                # ex) 1만원 투입 시
                # 투입금액 : 만원
                # 현재 보너스 : 천원
                # 총 충전금액 : 만천원

                # 카드 발급 여부 확인 :
                # 투입금액 + 현재 보너스 != 총 충전금액 -> 카드 발급 (카드발급금액이 있기 때문에 총 충전금액과 다름)
                # 투입금액 + 현재 보너스 == 총 충전금액 -> 카드 충전
                if int(current_mny) + int(current_bonus) != int(charge_money):
                    kind = 0
                    card_price = self.get_config("card_price")
                else:
                    kind = 1
                    card_price = "0"

                sql = "INSERT INTO card (`card_num`, `total_mny`, `current_mny`, `current_bonus`, `datetime`, `state`, `charge_money`, `card_price`, `kind`, `before_mny`, `reader_type`) " \
                      "VALUE (%s, %s, %s, %s, now(), '0', %s, %s, %s, %s, %s)"
                cursor.execute(sql, (card_num, total_mny, current_mny, current_bonus, charge_money, card_price, kind, before_mny, reader_type))
            conn.commit()
        finally:
            conn.close()
        return

    # 에러로그 수집
    def error_log(self, err_log, place):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user="pi", password="1234", charset="utf8", db="glstech")
        curs = conn.cursor(pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO error (`error`, `place`, `input_date`) VALUE  (%s, %s, now())"
                cursor.execute(sql, (err_log, place))
            conn.commit()
        finally:
            conn.close()

    # 공급업체 리스트 가져오기
    def get_manager_list(self):
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user="pi", password="1234", charset="utf8", db="glstech")
        curs = conn.cursor(pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM manager"
                curs.execute(sql)
                rows = curs.fetchall()
            conn.commit()
        finally:
            conn.close()
        return rows

    # 공급업체 가져오기
    def get_manager(self, name):
        res = OrderedDict()
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user="pi", password="1234", charset="utf8", db="glstech")
        curs = conn.cursor(pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM manager WHERE `manager_name` = %s limit 1"
                curs.execute(sql, name)
                rows = curs.fetchall()

                for row in rows:
                    res['no'] = row['no']
                    res['manager_no'] = row['manager_id']
            conn.commit()
        finally:
            conn.close()
        return res

    # 회원 보너스 설정 적용하기
    def get_member_bonus_config(self, mb_level):
        res = OrderedDict()
        conn = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user="pi", password="1234", charset="utf8", db="glstech")
        curs = conn.cursor(pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM member_bonus WHERE mb_level = %s LIMIT 1"
                curs.execute(sql, (mb_level))
                rows = curs.fetchall()

                for row in rows:
                    self.mb_bonus1 = row['bonus1']
                    self.mb_bonus2 = row['bonus2']
                    self.mb_bonus3 = row['bonus3']
                    self.mb_bonus4 = row['bonus4']
                    self.mb_bonus5 = row['bonus5']
                    self.mb_bonus6 = row['bonus6']
                    self.mb_bonus7 = row['bonus7']
                    self.mb_bonus8 = row['bonus8']
                    self.mb_bonus9 = row['bonus9']
                    self.mb_bonus10 = row['bonus10']
            conn.commit()
        finally:
            conn.close()

        return res

    def get_member_bonus_str(self, money):
        if money == 10000:
            return self.mb_bonus1
        elif money == 20000:
            return self.mb_bonus2
        elif money == 30000:
            return self.mb_bonus3
        elif money == 40000:
            return self.mb_bonus4
        elif money == 50000:
            return self.mb_bonus5
        elif money == 60000:
            return self.mb_bonus6
        elif money == 70000:
            return self.mb_bonus7
        elif money == 80000:
            return self.mb_bonus8
        elif money == 90000:
            return self.mb_bonus9
        elif money == 100000:
            return self.mb_bonus10
        else:
            return 0

    def get_member_bonus(self, arg):
        bonus = 0
        temp_money = arg
        if temp_money >= 100000:
            while temp_money >= 100000:
                bonus += int(self.get_member_bonus_str(100000))
                temp_money -= 100000

        if temp_money >= 90000:
            while temp_money >= 90000:
                bonus += int(self.get_member_bonus_str(90000))
                temp_money -= 90000

        if temp_money >= 80000:
            while temp_money >= 80000:
                bonus += int(self.get_member_bonus_str(80000))
                temp_money -= 80000

        if temp_money >= 70000:
            while temp_money >= 70000:
                bonus += int(self.get_member_bonus_str(70000))
                temp_money -= 70000

        if temp_money >= 60000:
            while temp_money >= 60000:
                bonus += int(self.get_member_bonus_str(60000))
                temp_money -= 60000

        if temp_money >= 50000:
            while temp_money >= 50000:
                bonus += int(self.get_member_bonus_str(50000))
                temp_money -= 50000

        if temp_money >= 40000:
            while temp_money >= 40000:
                bonus += int(self.get_member_bonus_str(40000))
                temp_money -= 40000

        if temp_money >= 30000:
            while temp_money >= 30000:
                bonus += int(self.get_member_bonus_str(30000))
                temp_money -= 30000

        if temp_money >= 20000:
            while temp_money >= 20000:
                bonus += int(self.get_member_bonus_str(20000))
                temp_money -= 20000

        if temp_money >= 10000:
            while temp_money >= 10000:
                bonus += int(self.get_member_bonus_str(10000))
                temp_money -= 10000

        if temp_money > 0:
            res = self.get_member_bonus_str(temp_money)
            bonus += int(res)

        return bonus

    # 보너스 초기화
    def init_member_bonus(self):
        self.mb_bonus1 = 0
        self.mb_bonus2 = 0
        self.mb_bonus3 = 0
        self.mb_bonus4 = 0
        self.mb_bonus5 = 0
        self.mb_bonus6 = 0
        self.mb_bonus7 = 0
        self.mb_bonus8 = 0
        self.mb_bonus9 = 0
        self.mb_bonus10 = 0

