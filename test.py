import base64

s = "Hello World!"
b = s.encode("UTF-8")
e = base64.b64encode(b)
s1 = e.decode("UTF-8")
print("Base64 Encoded : ", s1)

b1 = s1.encode("UTF-8")
d = base64.b64decode(b1)
s2 = d.decode("UTF-8")
print(s2)


# import pymysql
# import base64
#
#
# class test:
#     HOST = "glstest.iptime.org"
#     PORT = 30001
#     admin_password = ""
#     gil_password = ""
#     master_password = ""
#
#     def __init__(self):
#         conn = pymysql.connect(host=self.HOST,
#                                port=self.PORT,
#                                db='glstech',
#                                charset='utf8',
#                                user='pi',
#                                password='1234')
#         curs = conn.cursor()
#
#         try:
#             sql = "select * from card"
#             curs.execute(sql)
#             rows = curs.fetchall()
#             print("card table")
#             for row in rows:
#                 print(row)
#
#             sql = "select * from config"
#             curs.execute(sql)
#             rows = curs.fetchall()
#             print("config table")
#             for row in rows:
#                 print(row)
#
#             sql = "select * from crc order by no asc"
#             curs.execute(sql)
#             rows = curs.fetchall()
#             print("crc table")
#             for row in rows:
#                 print(row)
#
#             sql = "select * from manager"
#             curs.execute(sql)
#             rows = curs.fetchall()
#             print("manager table")
#             for row in rows:
#                 print(row)
#
#             sql = "select * from member_bonus"
#             curs.execute(sql)
#             rows = curs.fetchall()
#             print("member_bonus table")
#             for row in rows:
#                 print(row)
#         finally:
#             conn.close()
#
#
# if __name__ == '__main__':
#     t = test()


# import tkinter
#
# window=tkinter.Tk()
# window.title("YUN DAE HEE")
# window.geometry("640x400+100+100")
# window.resizable(False, False)
#
# b1=tkinter.Button(window, text="(0, 0)")
# b2=tkinter.Button(window, text="(0, 1)", width=20)
# b3=tkinter.Button(window, text="(0, 2)")
#
# b4=tkinter.Button(window, text="(1, 0)")
# b5=tkinter.Button(window, text="(1, 1)")
# b6=tkinter.Button(window, text="(1, 3)")
#
# b7=tkinter.Button(window, text="(2, 1)")
# b8=tkinter.Button(window, text="(2, 2)")
# b9=tkinter.Button(window, text="(2, 4)")
#
# b1.grid(row=0, column=0)
# b2.grid(row=0, column=1)
# b3.grid(row=0, column=2)
#
# b4.grid(row=1, column=0, rowspan=2)
# b5.grid(row=1, column=1, columnspan=3)
# b6.grid(row=1, column=3)
#
# b7.grid(row=2, column=1, sticky="w")
# b8.grid(row=2, column=2)
# b9.grid(row=2, column=99)
#
# window.mainloop()
#
