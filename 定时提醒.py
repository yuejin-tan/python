# 定时提醒程序 V1.0

import tkinter as tk


def btnApply():
    pass


def btnStart():
    pass


if __name__ == '__main__':
    mainWin = tk.Tk()

    mainWin.geometry('1366x768')
    # mainWin.resizable(False, False)
    mainWin.title("定时提醒程序 ver 1.0")

    ringCnt = tk.IntVar(mainWin)
    deltaSec = tk.IntVar(mainWin)

    frameU = tk.Frame(mainWin)
    frameU.pack(fill="both")
    frameD = tk.Frame(mainWin)
    frameD.pack( fill="both")
    frameD_L = tk.LabelFrame(frameD, text="设定", padx=2, pady=2)
    frameD_L.pack(side="left",fill="y")
    frameD_R = tk.Frame(frameD, padx=2, pady=2)
    frameD_R.pack(side="left", fill="both")

    button01 = tk.Button(frameD_R, text="应用",
                         command=btnApply)
    button01.grid(row=0, column=0, sticky="w", padx=2, pady=2)
    button02 = tk.Button(frameD_R, text="开始",
                         command=btnStart)
    button02.grid(row=1, column=0, sticky="w", padx=2, pady=2)

    lable01 = tk.Label(frameU, text="每x秒响铃一次，共x次")
    lable01.pack(fill="both")

    lable02 = tk.Label(frameU, text="余x秒，共x次")
    lable02.pack(side="bottom", fill="both")

    lable03 = tk.Label(frameD_L, text="每x秒响铃一次")
    lable03.pack(fill="both")

    lable04 = tk.Label(frameD_L, text="共x次")
    lable04.pack(side="bottom", fill="both")

if __name__ == '__main__':

    mainWin.mainloop()
