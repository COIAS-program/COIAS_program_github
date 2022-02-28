#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Asthunter ver 0.2 /2020/1/27"
# Asthunter => COIAS ver 0.0 /2020/6/10"

import os
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.scrolledtext as st
import tkinter.simpledialog as simpledialog

# SU. revised
from tkinter import messagebox

import numpy as np
from PIL import Image

# input ast data

ast_xy = np.loadtxt("redisp.txt", dtype="str")
img = Image.open("warp1_bin.png")
xpix = img.size[0]
ypix = img.size[1]
path_name = os.getcwd()


# class
class Asthunter(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    # first window
    def create_widgets(self):
        self.button1 = tk.Button(
            root, text="Load img", font=("", 14), command=self.load_file
        )
        self.button1.grid(row=0, column=0, sticky="NW")
        self.button4 = tk.Button(root, text="Quit", font=("", 14), command=root.quit)
        self.button4.grid(row=0, column=2, sticky="NE")
        self.button5 = tk.Button(
            root, text="OutPut", font=("", 14), command=self.output
        )
        self.button5.grid(row=0, column=1, sticky="NE")
        # moving object H number
        self.t0 = st.ScrolledText(font=("Helvetica", 14), width=10, height=20)
        self.t0.grid(row=1, column=0, columnspan=1000, sticky=tk.W + tk.E)

    # second window
    def sub_window(self):
        global image_data
        #        global inputnumber
        #        self.inputnumber = []
        self.file_num = 0
        self.SqOnOffFlag = 1
        self.sub_win = tk.Toplevel(root)
        self.sub_win.title("COIAS ver 0")
        self.sub_win.geometry("1440x900")
        self.canvas = tk.Canvas(self.sub_win, width=1350, height=800)
        self.canvas.grid(
            row=1, column=0, columnspan=70, sticky=tk.W + tk.E + tk.N + tk.S
        )
        # set scroll
        self.xscroll = tk.Scrollbar(
            self.sub_win, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.xscroll.grid(row=2, column=0, columnspan=70, sticky=tk.E + tk.W)
        self.yscroll = tk.Scrollbar(
            self.sub_win, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.yscroll.grid(row=1, column=70, sticky=tk.N + tk.S)
        self.canvas.config(yscrollcommand=self.yscroll.set)
        self.canvas.config(xscrollcommand=self.xscroll.set)

        #   scrollregion (west,north,east,south)
        self.canvas.config(scrollregion=(0, 0, xpix, ypix))

        # set first image (center x,y coord of image)/self.image_on_canvas is tag
        self.image_on_canvas = self.canvas.create_image(
            xpix / 2, ypix / 2, image=self.image_data[self.image_number]
        )

        # set ast coord of the first image/self.coord_on_canvas is tag
        self.astdata = [
            ast_xy[i] for i in np.where(ast_xy[:, 1] == str(self.image_number))
        ]  # NM 2021.07.08

        for i in range(len(self.astdata[0])):
            xpos = int(float(self.astdata[0][i][2]))
            ypos = int(float(self.astdata[0][i][3]))
            # set moving object personal name
            name = str(self.astdata[0][i][0])

            self.coord_on_canvas = self.canvas.create_rectangle(
                xpos - 20,
                ypix - ypos + 20,
                xpos + 20,
                ypix - ypos - 20,
                outline="#000000",
                width=5,
            )
            self.canvas.create_text(
                xpos - 25,
                ypix - ypos - 30,
                text=name,
                fill="#000000",
                font=("Purisa", 16),
            )

        # set condition
        self.do_blink = False
        # set button
        self.button2 = tk.Button(
            self.sub_win,
            text="Blink start/stop",
            font=("", 14),
            command=self.start_stop_blinking,
        )
        self.button2.grid(row=0, column=0, sticky=tk.W)
        self.button3 = tk.Button(
            self.sub_win,
            text="close window",
            font=("", 14),
            command=self.sub_win.destroy,
        )
        self.button3.grid(row=0, column=69, sticky=tk.E)
        self.button_back = tk.Button(
            self.sub_win, text="Back", command=self.onBackButton, font=("", 14)
        )
        self.button_back.grid(row=0, column=1, sticky=tk.W)
        self.button_next = tk.Button(
            self.sub_win, text="Next", command=self.onNextButton, font=("", 14)
        )
        self.button_next.grid(row=0, column=2, sticky=tk.W)
        self.button_SqOnOff = tk.Button(
            self.sub_win, text="Sq. On/Off", command=self.sq_on_off, font=("", 14)
        )
        self.button_SqOnOff.grid(row=0, column=3, sticky=tk.W)
        # set entry of image name
        self.message_num = tk.Entry(self.sub_win, font=("", 14), width=10)
        self.message_num.insert(tk.END, (("Image # ") + str(self.image_number + 1)))
        self.message_num.grid(row=0, column=4, sticky=tk.W)
        # print coord & set entry
        self.canvas.bind("<Motion>", self.mousecoord)
        self.xycoord = tk.Entry(self.sub_win, font=("", 14), width=20)
        self.xycoord.insert(tk.END, ("X pix, Y pix:"))
        self.xycoord.grid(row=0, column=5, columnspan=20, sticky=tk.W)
        # set mouse coordinate at click. If the coordinate is included in the range of new objects, print those numbers to the ScrolledText
        self.canvas.bind("<ButtonPress-1>", self.mouseClickAndOutputObjectsNumber)
        # set scrolledText box for message
        self.messageBox = tk.Entry(self.sub_win, font=("", 14), width=50)
        self.messageBox.insert(tk.END, "message:")
        self.messageBox.grid(row=0, column=26, columnspan=42, sticky=tk.W)
        # SU added 2021/7/12
        # set mouse coorinate by rightclick.
        self.sub_win.bind("<ButtonPress-3>", self.rightClick)

    # load_file
    def load_file(self):
        self.image_data = []
        # multi select
        self.filename = fd.askopenfilenames(
            filetypes=[
                ("Image Files", (".gif", ".png", ".ppm")),
                ("GIF Files", ".gif"),
                ("PNG Files", ".png"),
                ("PPM Files", ".ppm"),
            ],
            initialdir=path_name,
        )
        n = len(self.filename)
        for self.i in range(0, n):
            self.image_data.append(tk.PhotoImage(file=self.filename[self.i]))
        self.image_number = 0
        # make sub_window
        self.sub_window()

    # ------------------------------------

    def onBackButton(self):
        # 最後の画像に戻る
        if self.image_number == 0:
            self.image_number = len(self.image_data) - 1
        else:
            # 一つ戻る
            self.image_number -= 1

        # 表示画像を更新
        self.draw()

        # Entryの中身を更新
        self.message_num.delete(0, tk.END)
        self.message_num.insert(tk.END, ("Image # " + str(self.image_number + 1)))

    def onNextButton(self):
        # 一つ進む
        self.image_number += 1

        # 最初の画像に戻る
        if self.image_number == len(self.image_data):
            self.image_number = 0

        # 表示画像を更新
        self.draw()

        # Entryの中身を更新
        self.message_num.delete(0, tk.END)
        self.message_num.insert(tk.END, ("Image # " + str(self.image_number + 1)))

    def start_stop_blinking(self):
        if self.do_blink:
            self.do_blink = False
        else:
            self.do_blink = True
            self.blink()

    def blink(self):
        if self.do_blink:
            self.image_number += 1
            # 最初の画像に戻る
            if self.image_number == len(self.image_data):
                self.image_number = 0

            # 表示画像を更新
            self.draw()

            self.after(100, self.blink)
        # Entryの中身を更新
        self.message_num.delete(0, tk.END)
        self.message_num.insert(tk.END, ("Image # " + str(self.image_number + 1)))

    def stop(self):
        print("stop")

    # --------------------------------------------------------------------
    def mousecoord(self, event):
        # get the top left coord in image
        xp = self.xscroll.get()
        yp = self.yscroll.get()
        # top left coord in image
        xp1 = int(xp[0] * xpix)
        yp1 = int(yp[0] * ypix)
        # add the mouse position
        self.xp2 = event.x + xp1
        self.yp2 = event.y + yp1
        self.xycoord.delete(0, tk.END)
        self.xycoord.insert(
            tk.END, ("X pix " + str(self.xp2) + ", Y pix " + str(self.yp2))
        )

    # SU added 2021/07/12  get coordinate by right click --------------------------------------------------------
    def rightClick(self, event):
        #        print('right click')
        res = messagebox.askquestion("New number", "Same object with a previous image?")
        #        print(res)
        if res == "no":
            # get the top left coord in image
            xp = self.xscroll.get()
            yp = self.yscroll.get()
            # top left coord in image
            xp1 = int(xp[0] * xpix)
            yp1 = int(yp[0] * ypix)
            # add the mouse position
            self.xp2 = event.x + xp1
            self.yp2 = event.y + yp1
            self.coord = self.xp2, self.yp2
            print(self.coord)
            #            comment = str("If you measure (X, Y) = (") + str(self.xp2) + " pix, " + str(self.yp2) + str(" pix), please input temporay number")
            comment = "Input temporary number"
            self.inputnumber = simpledialog.askstring("Temporary number", comment)

            # get filename(full path)
            tmp = str(self.filename[self.image_number])
            # only filename
            #       tmp[-13:]
            # change to fits file name
            tmp2 = tmp[-13:].replace("png", "fits")
            # out put file on the current directry
            # coord + filename
            self.coord = str(self.xp2), str(self.yp2), str(tmp2), str(self.inputnumber)
            #        self.coord2 = list(self.coord)
            #        self.f2=open(tmp4,'a')
            self.f2 = open("memo2.txt", "a")
            self.f2.writelines(str(self.coord) + "\n")
            self.f2.close()
        else:
            # get the top left coord in image
            xp = self.xscroll.get()
            yp = self.yscroll.get()
            # top left coord in image
            xp1 = int(xp[0] * xpix)
            yp1 = int(yp[0] * ypix)
            # add the mouse position
            self.xp2 = event.x + xp1
            self.yp2 = event.y + yp1
            self.coord = self.xp2, self.yp2
            #            print(self.coord)

            # get filename(full path)
            tmp = str(self.filename[self.image_number])
            # only filename
            #       tmp[-13:]
            # change to fits file name
            tmp2 = tmp[-13:].replace("png", "fits")
            # out put file on the current directry
            # coord + filename
            self.coord = str(self.xp2), str(self.yp2), str(tmp2), str(self.inputnumber)
            #        self.coord2 = list(self.coord)
            #        self.f2=open(tmp4,'a')
            self.f2 = open("memo2.txt", "a")
            self.f2.writelines(str(self.coord) + "\n")
            self.f2.close()

    # ------------------------------------------------------------

    def output(self):
        self.f = open("memo.txt", "w")
        self.f.write(self.t0.get("1.0", "end -1c"))
        # self.f.write(self.t0.get('1.0',tk.END))
        self.f.close()

    # KS added 2020/12/24----------------------------------------------------------------
    def mouseClickAndOutputObjectsNumber(self, event):
        # get numbers already input in the ScrolledText
        self.inputText = self.t0.get("1.0", "end -1c")
        if len(self.inputText) < 2:
            self.writtenNumbersText = []
        else:
            self.writtenNumbersText = self.inputText.split()
        self.writtenNumbers = [
            int(text) for text in self.writtenNumbersText if text.isdigit()
        ]

        # get the top left coord in image
        xp = self.xscroll.get()
        yp = self.yscroll.get()
        # top left coord in image
        xp1 = int(xp[0] * xpix)
        yp1 = int(yp[0] * ypix)
        # add the mouse position
        self.xp2 = event.x + xp1
        self.yp2 = event.y + yp1

        # get asteroids coordinates stored in disp.txt
        self.astdata = [
            ast_xy[i] for i in np.where(ast_xy[:, 1] == str(self.image_number))
        ]  # NM 2021.07.08
        # compare asteroids coordinates and clicked coordinates
        self.matchAsteroidNamesStr = []
        for i in range(len(self.astdata[0])):
            xpos = int(float(self.astdata[0][i][2]))
            ypos = int(float(self.astdata[0][i][3]))
            if (
                xpos - 20 < self.xp2
                and xpos + 20 > self.xp2
                and ypix - (ypos + 20) < self.yp2
                and ypix - (ypos - 20) > self.yp2
            ):
                asteroidNameStr = self.astdata[0][i][0]
                if len(asteroidNameStr) != 7 or asteroidNameStr[0] != "H":
                    # print("This is not a new object! name=",asteroidNameStr)
                    self.messageBox.delete(0, tk.END)
                    self.messageBox.insert(
                        tk.END, "message: not a new object! name=" + asteroidNameStr
                    )
                else:
                    self.matchAsteroidNamesStr.append(asteroidNameStr.lstrip("H"))

        # put clicked asteroid number that are not yet written on the ScrolledText
        for asteroidNumberStr in self.matchAsteroidNamesStr:
            matchFlag = 0
            for num in self.writtenNumbers:
                if int(asteroidNumberStr) == num:
                    # print("This object is already written in the ScrolledText! num=",asteroidNumberStr)
                    self.messageBox.delete(0, tk.END)
                    self.messageBox.insert(
                        tk.END,
                        "message: already written in the ScrolledText! name="
                        + asteroidNameStr,
                    )
                    matchFlag = 1
            if matchFlag == 0:
                self.t0.insert(tk.END, asteroidNumberStr + "\n")
                self.messageBox.delete(0, tk.END)
                self.messageBox.insert(tk.END, "message:")

        # 再描画
        self.draw()

    def sq_on_off(self):
        if self.SqOnOffFlag == 1:
            self.SqOnOffFlag = 0
        elif self.SqOnOffFlag == 0:
            self.SqOnOffFlag = 1

        # 再描画
        self.draw()

    def draw(self):
        # get numbers already input in the ScrolledText
        self.inputText = self.t0.get("1.0", "end -1c")
        if len(self.inputText) < 2:
            self.writtenNumbersText = []
        else:
            self.writtenNumbersText = self.inputText.split()
        self.writtenNumbers = [
            int(text) for text in self.writtenNumbersText if text.isdigit()
        ]

        # 表示画像を更新
        self.canvas.delete("all")
        self.image_on_canvas = self.canvas.create_image(
            xpix / 2, ypix / 2, image=self.image_data[self.image_number]
        )
        # refresh new ast coord
        self.astdata = [
            ast_xy[i] for i in np.where(ast_xy[:, 1] == str(self.image_number))
        ]  # NM 2021.07.08

        for i in range(len(self.astdata[0])):
            xpos = int(float(self.astdata[0][i][2]))
            ypos = int(float(self.astdata[0][i][3]))

            if self.SqOnOffFlag == 1:
                name = str(self.astdata[0][i][0])
                matchFlag = 0
                if name.lstrip("H").isdigit():
                    nameInt = int(name.lstrip("H"))
                    for n in self.writtenNumbers:
                        if n == nameInt:
                            matchFlag = 1

                if matchFlag == 0:
                    self.coord_on_canvas = self.canvas.create_rectangle(
                        xpos - 20,
                        ypix - ypos + 20,
                        xpos + 20,
                        ypix - ypos - 20,
                        outline="#000000",
                        width=5,
                    )
                    self.canvas.create_text(
                        xpos - 25,
                        ypix - ypos - 30,
                        text=name,
                        fill="#000000",
                        font=("Purisa", 16),
                    )
                elif matchFlag == 1:
                    self.coord_on_canvas = self.canvas.create_rectangle(
                        xpos - 20,
                        ypix - ypos + 20,
                        xpos + 20,
                        ypix - ypos - 20,
                        outline="#FF0000",
                        width=5,
                    )
                    self.canvas.create_text(
                        xpos - 25,
                        ypix - ypos - 30,
                        text=name,
                        fill="#FF0000",
                        font=("Purisa", 16),
                    )


# -----------------------------------------------------------------------------------

root = tk.Tk()
# instance
app = Asthunter(master=root)
app.mainloop()
