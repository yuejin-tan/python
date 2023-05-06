# 特定电磁场问题有限差分法分析程序 ver 1.0
# author: Tangent (email: 498339337@qq.com)
# 基于tkinter的图形界面，编写时版本 python3.7.6
# 使用自带标准库即可运行，最小分辨率 1366x768
# 本代码程序遵循CC BY-NC-SA 4.0 协议

import tkinter as tk
from tkinter import messagebox
import time
import multiprocessing
from array import array
from random import randint
from math import sin, cos, sinh, pi

if __name__ == '__main__':

    # 0 创建主窗口,声明变量
    mainWin = tk.Tk()
    mainWin.geometry('1100x660+80+60')
    mainWin.resizable(True, True)
    mainWin.title("特定电磁场问题有限差分法分析程序 ver 1.0 by Tangent")

    voltage01 = 10000  # 顶盖电压

    multiProcess = tk.IntVar(mainWin)  # 迭代器状态记录
    multiProcess.set(2)

    iterationCount = tk.IntVar(mainWin)  # 迭代次数指示
    iterationCount.set(100)

    statusString = tk.StringVar(mainWin)  # 状态栏字符串
    statusString.set("就绪。")

    settingString = tk.StringVar(mainWin)  # 参数说明栏字符串
    settingString.set(r"""
画布分辨率：800x600
上端电压值：10000 V
其余电压值：0        V
伪色渲染：双线性插值法
内部精度：64bit 浮点
差分网格数：30行x40列
注：由于字体大小原因，部分点
未显示数值，但参与了运算
程序内部分为显示数组和buffer
计算时将改变buffer中的内容
""")

    alpha = tk.DoubleVar(mainWin)
    alpha.set(1)

    voltageMat = [array("d", ((voltage01/31)*(31-line) for line in range(32)))
                  for col in range(42)]  # 电压值矩阵

    voltageMatTemp = [array("d", (0 for line in range(32)))
                      for col in range(42)]  # 矩阵buffer

    renderStatus = 0  # 渲染器状态
    renderStatusString = tk.StringVar()
    renderStatusString.set("渲染伪色")

    bufferStatus = 0
    bufferString = tk.StringVar()
    bufferString.set("将现结果暂存buffer再载入标准值")

    # 1 核心计算模块

    # 1.1 多进程环境准备工作
    mpArray01 = multiprocessing.RawArray('d', [0 for x in range(32*42)])
    mpArray02 = multiprocessing.RawArray('d', [0 for x in range(32*42)])

    tempList1 = []
    tempList2 = []
    for ii in range(5):
        tempList1.append(multiprocessing.Event())
        tempList2.append(multiprocessing.Event())
    eventList = [tempList1, tempList2]

# 多进程负载函数


def multiProcessJob(offset, alpha, times, mpArray01, mpArray02, eventList):

    arraySourse = mpArray01
    arrayTarget = mpArray02
    iterationCounter = 0

    while 1:  # 核心进程同步代码

        eventList[0][offset].set()
        if iterationCounter == times:
            break
        eventList[0][4].wait()
        eventList[0][offset].clear()

        for col in range(1+offset*10, 11+offset*10):
            for line in range(1, 31):
                arrayTarget[col*32+line] = ((arraySourse[col*32+line-1] + arraySourse[col*32+line+1] + arraySourse[col*32+line-32] +
                                             arraySourse[col*32+line+32])/4 - arraySourse[col*32+line]) * alpha + arraySourse[col*32+line]
        arraySourse, arrayTarget = arrayTarget, arraySourse
        iterationCounter += 1

        eventList[1][offset].set()
        if iterationCounter == times:
            break
        eventList[1][4].wait()
        eventList[1][offset].clear()

        for col in range(1+offset*10, 11+offset*10):
            for line in range(1, 31):
                arrayTarget[col*32+line] = ((arraySourse[col*32+line-1] + arraySourse[col*32+line+1] + arraySourse[col*32+line-32] +
                                             arraySourse[col*32+line+32])/4 - arraySourse[col*32+line]) * alpha + arraySourse[col*32+line]
        arraySourse, arrayTarget = arrayTarget, arraySourse
        iterationCounter += 1


# 1.2 finite difference method （Fdm） module 有限差分法模块
class Fdm(object):

    def __init__(self):  # 数据表的初始化
        global voltageMat
        global voltageMatTemp

        for col in range(42):
            voltageMat[col][0] = voltage01
            voltageMat[col][31] = 0
        for line in range(32):
            voltageMat[0][line] = 0
            voltageMat[41][line] = 0

        for col in range(42):
            voltageMatTemp[col][0] = voltage01
            voltageMatTemp[col][31] = 0
        for line in range(32):
            voltageMatTemp[0][line] = 0
            voltageMatTemp[41][line] = 0

    def compute(self):  # 核心计算函数

        global voltageMat
        global voltageMatTemp
        global mpArray01
        global mpArray02
        global eventList

        # 管理buffer
        global bufferStatus
        while(bufferStatus):
            bufferFunc()

        tempStartTime = time.time()
        tempAlpha = alpha.get()
        processList = []
        IterTarget = iterationCount.get()

        if multiProcess.get() == 2:  # 雅克比单线程迭代
            for ii in range(IterTarget):
                for col in range(1, 41):
                    for line in range(1, 31):
                        voltageMatTemp[col][line] = ((
                            voltageMat[col-1][line] + voltageMat[col][line-1] + voltageMat[col+1][line] + voltageMat[col][line+1])/4 - voltageMat[col][line]) * tempAlpha + voltageMat[col][line]
                voltageMat, voltageMatTemp = voltageMatTemp, voltageMat
                if (ii % 23 == 1):
                    statusString.set(
                        "正在进行第{}轮雅克比单线程迭代，共{}轮。alpha={}".format(ii+1, IterTarget, tempAlpha))
                    mainWin.update()

        if multiProcess.get() == 1:  # 雅克比四线程迭代
            # 将数据传输到共享内存区
            for col in range(42):
                for line in range(32):
                    mpArray01[col*32+line] = voltageMat[col][line]
                    mpArray02[col*32+line] = voltageMat[col][line]

            # 基于“事件（event）”的同步机制
            for event in eventList[1]:
                event.clear()
            for event in eventList[0]:
                event.clear()

            for ii in range(4):
                processList.append(multiprocessing.Process(target=multiProcessJob, args=(
                    ii, tempAlpha, IterTarget, mpArray01, mpArray02, eventList)))
            for ii in range(4):
                processList[ii].start()

            iterationCounter = 0
            eventList[0][4].set()

            while 1:  # 核心同步代码

                for jj in range(4):
                    eventList[1][jj].wait()

                iterationCounter += 1
                if (iterationCounter % 23 == 1):
                    statusString.set(
                        "正在进行第{}轮雅克比四线程迭代，共{}轮。alpha={}".format(iterationCounter, IterTarget, tempAlpha))
                    mainWin.update()

                if iterationCounter == IterTarget:
                    break

                eventList[0][4].clear()
                eventList[1][4].set()
                for jj in range(4):
                    eventList[0][jj].wait()

                iterationCounter += 1
                if (iterationCounter % 23 == 1):
                    statusString.set(
                        "正在进行第{}轮雅克比四线程迭代，共{}轮。alpha={}".format(iterationCounter, IterTarget, tempAlpha))
                    mainWin.update()

                if iterationCounter == IterTarget:
                    break

                eventList[1][4].clear()
                eventList[0][4].set()

            for ii in range(4):  # 等待回收计算进程
                processList[ii].join()

            # 将结果传回目标矩阵
            targetMat = mpArray02 if (IterTarget % 2) else mpArray01
            for col in range(42):
                for line in range(32):
                    voltageMat[col][line] = targetMat[col*32+line]

        if multiProcess.get() == 0:  # 赛德尔迭代
            for ii in range(IterTarget):
                for col in range(1, 41):
                    for line in range(1, 31):
                        voltageMat[col][line] = ((
                            voltageMat[col-1][line] + voltageMat[col][line-1] + voltageMat[col+1][line] + voltageMat[col][line+1])/4-voltageMat[col][line]) * tempAlpha + voltageMat[col][line]
                if (ii % 23 == 1):
                    statusString.set(
                        "正在进行第{}轮赛德尔迭代，共{}轮。alpha={}".format(ii+1, IterTarget, tempAlpha))
                    mainWin.update()

        # 计算用时
        statusString.set("完成计算。用时{:.4f}秒。".format(
            time.time()-tempStartTime))
        showDigits(voltageMat)


if __name__ == '__main__':
    # 计算模块实例化、初始化
    fdm01 = Fdm()

    # 2 创建基本布局形式
    frameU = tk.Frame(mainWin)
    frameU.pack(fill="both")

    frameD = tk.Frame(mainWin)
    frameD.pack(side="bottom", fill="x")

    frameL = tk.Frame(frameU, padx=2, pady=2)
    frameL.pack(fill='y', side="left")

    frameR = tk.Frame(frameU, padx=2, pady=2)
    frameR.pack(fill="both", side="left", expand=True)

    frameRU = tk.LabelFrame(frameR, text="模型参数", padx=2, pady=2)
    frameRU.pack(fill="both", expand=True)

    frameRD = tk.LabelFrame(frameR, text="操作", padx=2, pady=2)
    frameRD.pack(fill="x")

    # 3 细化各项模块

    # 3.1 画板部分
    # 主画板
    canvas01 = tk.Canvas(frameL, width=830, height=630,
                         bg="white")
    canvas01.pack(side="left")
    # 侧栏画板
    canvas02 = tk.Canvas(frameL, width=30, height=630, bg="white")
    canvas02.pack(padx=2)


def render():  # 伪色渲染器0
    global voltageMat
    global renderStatus
    if renderStatus == 0:
        tempStartTime = time.time()
        canvas01.delete("digital")
        tempCounter = 0
        for ii in range(41):
            for jj in range(31):
                tempVoltageMat = bilinearInterpolation(
                    voltageMat[ii][jj], voltageMat[ii+1][jj], voltageMat[ii][jj+1], voltageMat[ii+1][jj+1])
                for iii in range(20):
                    for jjj in range(20):
                        temp = canvas01.create_line(
                            5+ii*20+iii, 5+jj*20+jjj, 5+ii*20+iii+1, 5+jj*20+jjj, fill=colorMap(tempVoltageMat[iii][jjj]), width=1)
                        canvas01.addtag_withtag("point", temp)
                tempCounter += 1
                if (1 == randint(0, 20)):
                    statusString.set(
                        "正在渲染第{}块区域，共1271块.!!请耐心等待，不要搞事，以免死机!!".format(tempCounter))
                    mainWin.update()

        statusString.set("完成渲染。用时{:.4f}秒。".format(
            time.time()-tempStartTime))
        renderStatusString.set("清除伪色")
        renderStatus = 1
    else:
        renderStatus = 0
        canvas01.delete("point")
        showDigits(voltageMat)
        renderStatusString.set("渲染伪色")
        statusString.set("就绪。")


def bilinearInterpolation(a, b, c, d):
    ansMat = []
    upLine = array("d", [(b*i/20+a*(20-i)/20) for i in range(20)])
    downLine = array("d", [(d*i/20+c*(20-i)/20) for i in range(20)])
    for ii in range(20):
        ansMat.append(
            array("d", [(upLine[ii]*(20-i)/20+downLine[ii]*i/20) for i in range(20)]))
    return ansMat


def colorMap(voltage):  # 数值向颜色的归一化映射
    global voltage01
    voltage02 = voltage01*0.01 if bufferStatus == 2 else voltage01
    ratio = (voltage/voltage02)*pi/2
    r = int(255*sin(ratio))
    g = int(255*sin(2*ratio))
    b = int(255*cos(ratio))
    r = max(r, 0)
    r = min(r, 255)
    g = max(g, 0)
    g = min(g, 255)
    b = max(b, 0)
    b = min(b, 255)
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def showDigits(targetMat):  # 显示数字

    if renderStatus == 1:  # 若有伪色，则清除
        render()

    canvas01.delete("digital")
    for ii in range(1, 41, 2):
        for jj in range(1, 31):
            temp = canvas01.create_text(5+20*ii, 5+20*jj,
                                        text=str(float(targetMat[ii][jj]))[:5], font=("", 10))
            canvas01.addtag_withtag("digital", temp)


"asdf"[1:2]


def drawBoader():  # 绘制边框
    temp1 = canvas01.create_line(5, 5, 825, 5, fill='red', width=5)
    temp2 = canvas01.create_line(5, 5, 5, 625, fill="blue", width=5)
    temp3 = canvas01.create_line(5, 625, 825, 625, fill="blue", width=5)
    temp4 = canvas01.create_line(825, 625, 825, 5, fill="blue", width=5)
    canvas01.addtag_withtag("dashline", temp1)
    canvas01.addtag_withtag("dashline", temp2)
    canvas01.addtag_withtag("dashline", temp3)
    canvas01.addtag_withtag("dashline", temp4)


def drawNet():  # 绘制网格线
    for i in range(30):
        canvas01.create_line(5, 25+20*i, 825, 25+20*i,
                             fill='green', dash=(3, 1))

    for i in range(40):
        canvas01.create_line(25+20*i, 5, 25+20*i, 625,
                             fill='green', dash=(3, 1))


def sideBarInit():
    for ii in range(600):
        canvas02.create_line(0, ii+30, 30, ii+30,
                             fill=colorMap((600-ii)/600*voltage01))
    for ii in range(1, 21):
        canvas02.create_text(
            15, 28+ii/20*600, text="{}-".format((20-ii)*5), font=("", 14))

    canvas02.create_text(15, 34, text="100", font=("", 12))

    canvas02.create_text(15, 10, text="百分", font=("", 9))
    canvas02.create_text(15, 22, text="比值", font=("", 9))


# 3.2 弹出式设置窗口（合集）


def gugugu():  # 咕~咕~咕~ 弹出框
    guguguWin = tk.Toplevel(mainWin)
    guguguWin.geometry("400x300+240+180")
    guguguWin.title("咕~咕~咕~")
    guguguWin.attributes("-topmost", True)
    guguguWin.resizable(0, 0)
    tk.Label(guguguWin, text="占坑，此版本暂不支持\n\n敬请期待 Ver 2.0\n（如果有的话）",
             font=("楷体", 24)).pack(fill='both', expand=True)


def standardValue(col, line):
    global voltage01
    phi = 0
    l = 0
    while 1:
        delta_phi = sin((2*l+1)*pi*col/41)*sinh((2*l+1)*pi *
                                                line/41)/(2*l+1)/sinh((2*l+1)*pi*31/41)
        phi += delta_phi
        l += 1
        if abs(delta_phi) < 0.00000001:
            break

    return 4*voltage01/pi*phi
    pass
# 将原结果写回显示区 将原结果写回显示区


def bufferFunc():
    global bufferStatus
    if bufferStatus == 0:
        bufferStatus = 1
        bufferString.set("将显示区值与原结果求差")
        for col in range(42):
            for line in range(32):
                voltageMatTemp[col][line] = voltageMat[col][line]

        for col in range(1, 41):
            for line in range(1, 31):
                voltageMat[col][line] = standardValue(col, 31-line)

    elif bufferStatus == 1:
        bufferStatus = 2
        bufferString.set("将原结果从buffer写回显示区")
        for col in range(1, 41):
            for line in range(1, 31):
                voltageMat[col][line] = abs(
                    voltageMat[col][line]-voltageMatTemp[col][line])

    else:
        bufferStatus = 0
        bufferString.set("将现结果暂存buffer再载入标准值")
        for col in range(1, 41):
            for line in range(1, 31):
                voltageMat[col][line] = voltageMatTemp[col][line]

    showDigits(voltageMat)
    statusString.set("就绪。")


if __name__ == '__main__':
    entryVar01 = tk.StringVar()
    entryVar01.set("1000")
    Avar = tk.DoubleVar()
    Avar.set(0)
    Bvar = tk.DoubleVar()
    Bvar.set(0)
    Cvar = tk.DoubleVar()
    Cvar.set(0)


def initVoltageMat():  # 电压初始化弹出框
    initVoltageMatWin = tk.Toplevel(mainWin)
    initVoltageMatWin.geometry("+900+200")
    initVoltageMatWin.title("电压值初始化")
    initVoltageMatWin.attributes("-topmost", True)

    # 管理buffer
    global bufferStatus
    while(bufferStatus):
        bufferFunc()

    button05 = tk.Button(initVoltageMatWin, text="全设为：",
                         command=initVoltageFunc01)
    button05.grid(row=0, column=0, sticky="w", padx=2, pady=2)

    entry01 = tk.Entry(initVoltageMatWin, textvariable=entryVar01, width=25)
    entry01.grid(row=0, column=1, sticky="w", padx=2, pady=2)

    button06 = tk.Button(initVoltageMatWin, text="线性函数",
                         command=initVoltageFunc02)
    button06.grid(row=1, column=0, sticky="w", padx=2, pady=2)

    tk.Label(initVoltageMatWin, text="U=AX+BY+C 归一x,y的范围于(0,1)").grid(
        row=1, column=1, sticky="w", padx=2, pady=2)

    tk.Label(initVoltageMatWin, text="A:").grid(
        row=2, column=0, sticky="w", padx=2, pady=2)

    tk.Label(initVoltageMatWin, text="B:").grid(
        row=3, column=0, sticky="w", padx=2, pady=2)

    tk.Label(initVoltageMatWin, text="C:").grid(
        row=4, column=0, sticky="w", padx=2, pady=2)

    scaleA = tk.Scale(initVoltageMatWin, from_=-1, to=1,
                      resolution=0.01, digits=3, orient="horizontal", length=200, tickinterval=0.4, variable=Avar)
    scaleA.grid(row=2, column=1, sticky="w", padx=2, pady=2)

    scaleB = tk.Scale(initVoltageMatWin, from_=-1, to=1,
                      resolution=0.01, digits=3, orient="horizontal", length=200, tickinterval=0.4, variable=Bvar)
    scaleB.grid(row=3, column=1, sticky="w", padx=2, pady=2)

    scaleC = tk.Scale(initVoltageMatWin, from_=-1, to=1,
                      resolution=0.01, digits=3, orient="horizontal", length=200, tickinterval=0.4, variable=Cvar)
    scaleC.grid(row=4, column=1, sticky="w", padx=2, pady=2)

    button07 = tk.Button(initVoltageMatWin, text="随机值",
                         command=initVoltageFunc03)
    button07.grid(row=5, column=0, sticky="w", padx=2, pady=2)

    button08 = tk.Button(initVoltageMatWin, text="关闭窗口",
                         command=initVoltageMatWin.withdraw)
    button08.grid(row=5, column=1,  padx=2, pady=2, sticky="ew")


def initVoltageFunc01():  # 电压初始化弹出框的回调函数
    temp = float(entryVar01.get())
    for col in range(1, 41):
        for line in range(1, 31):
            voltageMat[col][line] = temp
    showDigits(voltageMat)


def initVoltageFunc02():  # 电压初始化弹出框的回调函数
    A, B, C = Avar.get(), Bvar.get(), Cvar.get()
    for col in range(1, 41):
        for line in range(1, 31):
            voltageMat[col][line] = voltage01 * (col/42*A+line/32*B+C)
    showDigits(voltageMat)


def initVoltageFunc03():  # 电压初始化弹出框的回调函数
    for col in range(1, 41):
        for line in range(1, 31):
            voltageMat[col][line] = randint(0, voltage01)
    showDigits(voltageMat)


def about():  # 附加说明弹出框
    tk.messagebox.showinfo(
        "关于", "图形界面基于Python tkinter\n编写时的运行环境：\npython 3.7.7 + win7 sp1 64bit\n分辨率最低1366x768\n本代码程序遵循CC BY-NC-SA 4.0 协议")


if __name__ == '__main__':
    # 3.3 参数一览块
    settingLabel01 = tk.Label(
        frameRU, textvariable=settingString,                              justify='left')
    settingLabel01.pack(fill='both')

    button01 = tk.Button(
        frameRU, textvariable=bufferString, command=bufferFunc)
    button01.pack(fill="x", padx=2, pady=3)

    button03 = tk.Button(frameRU, text="电压值初始化设置", command=initVoltageMat)
    button03.pack(fill='x', padx=2, pady=3)

    # 3.4 迭代计算块
    labelFrame02 = tk.LabelFrame(frameRD, text="算法选择")
    labelFrame02.pack(fill='x')

    radioButton03 = tk.Radiobutton(
        labelFrame02, text="雅克比迭代（单线程）", variable=multiProcess, value=2)
    radioButton03.pack(fill="x")

    radioButton01 = tk.Radiobutton(
        labelFrame02, text="雅克比迭代（四线程）", variable=multiProcess, value=1)
    radioButton01.pack(fill="x")

    radioButton02 = tk.Radiobutton(
        labelFrame02, text="赛德尔迭代", variable=multiProcess, value=0)
    radioButton02.pack(fill="x")

    labelFrame01 = tk.LabelFrame(frameRD, text="连续迭代次数设定:")
    labelFrame01.pack(fill="x")

    scale01 = tk.Scale(labelFrame01, from_=1, to=1001,
                       tickinterval=500, orient="horizontal", variable=iterationCount)
    scale01.pack(fill="x")

    labelFrame02 = tk.LabelFrame(frameRD, text="alpha值设定：")
    labelFrame02.pack(fill="x")

    scale02 = tk.Scale(labelFrame02, from_=0, to=2.5,
                       resolution=0.01, digits=3, variable=alpha, orient="horizontal")
    scale02.pack(fill="x")

    button02 = tk.Button(frameRD, text="开始计算", command=fdm01.compute)
    button02.pack(side="left", fill="x", padx=1, expand=True)

    button04 = tk.Button(
        frameRD, textvariable=renderStatusString, command=render)
    button04.pack(side="left", fill="x", padx=1, expand=True)

if __name__ == '__main__':

    # 3.5 菜单及其相关
    menuBar = tk.Menu(mainWin)
    mainWin.config(menu=menuBar)
    menu01 = tk.Menu(menuBar, tearoff=False)
    menuBar.add_cascade(label="操作", menu=menu01)
    menuBar.add_command(label="关于", command=about)

    menu01.add_command(label="修改非更改性参数", command=gugugu)
    menu01.add_command(label="电压值初始化", command=initVoltageMat)
    menu01.add_command(label="开始计算", command=fdm01.compute)
    menu01.add_command(label="渲染伪色", command=render)

    # 3.6 状态栏
    statusBar = tk.Label(frameD, textvariable=statusString, bd=1,
                         relief="sunken", anchor="w")
    statusBar.pack(side="left", fill='x', expand=True)

    # 4 界面初始化，进入消息循环
    drawNet()
    drawBoader()
    sideBarInit()
    showDigits(voltageMat)

    mainWin.mainloop()