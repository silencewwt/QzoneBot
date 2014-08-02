#!/usr/bin/env python3
# -*-coding:utf-8-*-

import tkinter as tk
import QzoneAuto


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

        self.entry_psw = tk.Entry(self.top, width=self.ENTRY_WIDTH)
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

    def comment_callback(self):
        if not self.check_comment_var.get() % 2:
            self.entry_comment.config(state=tk.DISABLED)
        else:
            self.entry_comment.config(state=tk.NORMAL)

    def start(self):
        qq_num = self.entry_qq.get()
        password = self.entry_psw.get()
        target_num = self.entry_target.get()
        vote = False
        imitate = False
        comment = ''

        if self.check_vote_var.get() % 2:
            vote = True
        if self.check_imitate_var.get() % 2:
            imitate = True
        if self.check_comment_var.get() % 2:
            comment = self.entry_comment.get()

        qzone_auto = QzoneAuto.QzoneAuto(qq_num, password, target_num, vote, imitate, comment)
        qzone_auto.main()


def main():
    Client()

if __name__ == '__main__':
    main()
