#!/usr/bin/env python3
# -*-coding:utf-8-*-

import tkinter as tk
import tkinter.messagebox as msg_box
import QzoneAuto
import os


class Client(object):
    def __init__(self):
        self.CLIENT_WIDTH = 250
        self.CLIENT_HEIGHT = 350
        self.GEOMETRY_SIZE = str(self.CLIENT_WIDTH) + 'x' + str(self.CLIENT_HEIGHT)
        self.ALIGN_TOP = 20
        self.ALIGN_LABEL_LEFT = 20
        self.ALIGN_ENTRY_LEFT = 85
        self.LABEL_WIDTH = 10
        self.LABEL_HEIGHT = 1
        self.ENTRY_WIDTH = 20
        self.LABEL_VERTICAL_GAP = 40
        self.CHECK_TOP = 150

        self.qzone = None
        self.verify_code = ''

        self.top = tk.Tk()
        self.top.config(bg='gray')
        self.top.title('Qzone Client')
        self.top.geometry(self.GEOMETRY_SIZE)
        self.top.maxsize(self.CLIENT_WIDTH, self.CLIENT_HEIGHT)

        self.label_qq = tk.Label(self.top, text='账号:', width=self.LABEL_WIDTH, height=self.LABEL_HEIGHT, anchor='w',
                                 bg='gray')
        self.label_qq.pack()
        self.label_qq.place(x=self.ALIGN_LABEL_LEFT, y=self.ALIGN_TOP)

        self.label_psw = tk.Label(self.top, text='密码:', width=self.LABEL_WIDTH, height=self.LABEL_HEIGHT, anchor='w',
                                  bg='gray')
        self.label_psw.pack()
        self.label_psw.place(x=self.ALIGN_LABEL_LEFT, y=self.ALIGN_TOP + self.LABEL_VERTICAL_GAP * 1)

        self.label_target = tk.Label(self.top, text='对方账号:', width=self.LABEL_WIDTH, height=self.LABEL_HEIGHT,
                                     anchor='w', bg='gray')
        self.label_target.pack()
        self.label_target.place(x=self.ALIGN_LABEL_LEFT, y=self.ALIGN_TOP + self.LABEL_VERTICAL_GAP * 2)

        self.entry_qq = tk.Entry(self.top, width=self.ENTRY_WIDTH)
        self.entry_qq.pack()
        self.entry_qq.place(x=self.ALIGN_ENTRY_LEFT, y=self.ALIGN_TOP)

        self.entry_psw = tk.Entry(self.top, width=self.ENTRY_WIDTH, show='*')
        self.entry_psw.pack()
        self.entry_psw.place(x=self.ALIGN_ENTRY_LEFT, y=self.ALIGN_TOP + self.LABEL_VERTICAL_GAP * 1)

        self.entry_target = tk.Entry(self.top, width=self.ENTRY_WIDTH)
        self.entry_target.pack()
        self.entry_target.place(x=self.ALIGN_ENTRY_LEFT, y=self.ALIGN_TOP + self.LABEL_VERTICAL_GAP * 2)

        self.check_vote_var = tk.IntVar()
        self.check_imitate_var = tk.IntVar()
        self.check_comment_var = tk.IntVar()

        self.check_vote = tk.Checkbutton(self.top, text='全部点赞', variable=self.check_vote_var, bg='gray')
        self.check_vote.pack()
        self.check_vote.place(x=self.ALIGN_LABEL_LEFT, y=self.CHECK_TOP)

        self.check_imitate = tk.Checkbutton(self.top, text='自动队形', variable=self.check_imitate_var, bg='gray')
        self.check_imitate.pack()
        self.check_imitate.place(x=self.ALIGN_LABEL_LEFT, y=self.CHECK_TOP + self.LABEL_VERTICAL_GAP * 1)

        self.check_comment = tk.Checkbutton(self.top, text='全部评论：', command=self.comment_callback,
                                            variable=self.check_comment_var, bg='gray')
        self.check_comment.pack()
        self.check_comment.place(x=self.ALIGN_LABEL_LEFT, y=self.CHECK_TOP + self.LABEL_VERTICAL_GAP * 2)

        self.entry_comment = tk.Entry(self.top, width=self.ENTRY_WIDTH, state=tk.DISABLED)
        self.entry_comment.pack()
        self.entry_comment.place(x=self.ALIGN_LABEL_LEFT, y=self.CHECK_TOP + self.LABEL_VERTICAL_GAP * 2 + 30)

        self.button_start = tk.Button(self.top, text='开始', command=self.start, width=8)
        self.button_start.pack()
        self.button_start.place(x=90, y=310)

        self.top.mainloop()
        # self.entry_verify_code()

    def comment_callback(self):
        if not self.check_comment_var.get() % 2:
            self.entry_comment.config(state=tk.DISABLED)
        else:
            self.entry_comment.config(state=tk.NORMAL)

    def start(self):
        qq_num = self.entry_qq.get().strip()
        password = self.entry_psw.get()
        target_num = self.entry_target.get().strip()
        vote = False
        imitate = False
        comment = ''
        if not qq_num:
            msg_box.showerror('你娃出错了！', '请输入QQ号码！')
            return
        if not qq_num.isnumeric():
            msg_box.showerror('你娃出错了！', '请输入正确的QQ号码！')
            return
        if not password:
            msg_box.showerror('你娃出错了！', '请输入密码！')
            return
        if not target_num:
            msg_box.showerror('你娃出错了！', '请输入对方的QQ号码！')
            return
        if not target_num.isnumeric():
            msg_box.showerror('你娃出错了！', '请输入正确的QQ号码！')
            return

        if self.check_vote_var.get() % 2:
            vote = True
        if self.check_imitate_var.get() % 2:
            imitate = True
        if self.check_comment_var.get() % 2:
            comment = self.entry_comment.get()
            if not comment:
                msg_box.showerror('你娃出错了！', '请输入自动评论的内容！')
                return
        if not vote and not imitate and not comment:
            msg_box.showerror('你娃出错了！', '请至少选择一项！')
            return

        self.qzone = QzoneAuto.QzoneAuto(self, qq_num, password, target_num, vote, imitate, comment)
        self.qzone.start()
        self.qzone.join()

    def error(self, msg):
        msg_box.showerror('你娃出错了！', msg)

    def verify_submit(self, code):
        self.verify_code = code

    def entry_verify_code(self):
        WIDTH = 250
        HEIGHT = 150
        GEOMETRY_SIZE = str(WIDTH) + 'x' + str(HEIGHT)
        ENTRY_WIDTH = 15
        ENTRY_X = 30
        ENTRY_Y = 40

        box = tk.Tk()
        box.title('请输入验证码')
        box.geometry(GEOMETRY_SIZE)
        box.config(bg='gray')

        entry = tk.Entry(box, width=ENTRY_WIDTH)
        entry.pack()
        entry.place(x=ENTRY_X, y=ENTRY_Y)

        button_reopen = tk.Button(box, text='打开验证码', width=12, command=lambda: os.popen('verifycode.jpg'))
        button_reopen.pack()
        button_reopen.place(x=150, y=38)

        button_submit = tk.Button(box, text='确定', width=8,
                                  command=lambda: [self.verify_submit(entry.get()), box.destroy()])
        button_submit.pack()
        button_submit.place(x=95, y=100)

        box.mainloop()


def main():
    Client()

if __name__ == '__main__':
    main()