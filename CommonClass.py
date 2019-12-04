import tkinter.messagebox
import re  # 정규 표현식 지원 모듈


class Common:
    # 문자 형식
    def number_format(self, n):
        s = str(n)

        if s.find('.') < 0:
            e = re.compile(r"(\d)(\d\d\d)$")
            s, cnt = re.subn(e, r"\1,\2", s)

        e = re.compile(r"(\d)(\d\d\d([.,]))")

        while 1:
            s, cnt = re.subn(e, r"\1,\2", s)
            if not cnt:
                break
        return s

    def toggle(self, label, label_pi):  # 라벨이 보였다 안보였다 반복
        if label.visible:
            label.place_forget()
        else:
            label.place(label_pi)
        label.visible = not label.visible

    def show_msg(self, msg):
        tkinter.messagebox.showinfo("확인", msg)

    def show_msg_ys(self, msg):
        res = tkinter.messagebox.askyesno("확인", msg)
        return res


# if __name__ == "__main__":
#     app = Common()
#     a = app.number_format(1000000)
#     print(a)