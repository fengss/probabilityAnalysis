#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import threading
import time

import numpy as np
from matplotlib.ticker import MultipleLocator
from scipy.special import comb, perm
from matplotlib import pyplot as plt
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

#==================================================
#==================================================
#=================数据参数==========================
#==================================================
#==================================================
gifts_number = 100  # 奖品数量
gifts_time = 1000   # 奖品发放时间区间
gifts_point_number = 30  # 奖品细粒度
XMultipleLocator = 100  # X轴密度比
YMultipleLocator = 10  # X轴密度比


class Bezier(threading.Thread):
    def __init__(self, line, data_ax, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.data_ax = data_ax
        self.line = line
        self.index_02 = None  # 保存拖动的这个点的索引
        self.press = None  # 状态标识，1为按下，None为没按下
        self.pick = None  # 状态标识，1为选中点并按下,None为没选中
        self.motion = None  # 状态标识，1为进入拖动,None为不拖动
        self.xs = list()  # 保存点的x坐标
        self.ys = list()  # 保存点的y坐标
        self.cid_press = line.figure.canvas.mpl_connect('button_press_event', self.on_press)  # 鼠标按下事件
        self.cid_release = line.figure.canvas.mpl_connect('button_release_event', self.on_release)  # 鼠标放开事件
        self.cid_motion = line.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)  # 鼠标拖动事件
        self.cid_pick = line.figure.canvas.mpl_connect('pick_event', self.on_picker)  # 鼠标选中事件
        self.data_x = []
        self.data_y = []
        self.gifts = []
        self.real_gifts_time = []

    def init_default(self):
        self.xs.append(0)
        self.ys.append(gifts_number)

        self.xs.append(gifts_time / 10)
        self.ys.append(gifts_number / 10)

        self.xs.append(gifts_time)
        self.ys.append(0)
        self.draw_01()

    def on_press(self, event):  # 鼠标按下调用
        if event.inaxes != self.line.axes: return
        self.press = 1

    def on_motion(self, event):  # 鼠标拖动调用
        try:
            if event.inaxes != self.line.axes: return
            if self.press is None: return
            if self.pick is None: return
            if self.motion is None:  # 整个if获取鼠标选中的点是哪个点
                self.motion = 1
                x = self.xs
                x_data = event.xdata
                y_data = event.ydata
                index_01 = 0
                for i in x:
                    if abs(i - x_data) < 0.02 * gifts_time:  # 0.02 为点的半径
                        if abs(self.ys[index_01] - y_data) < 0.02 * gifts_number: break
                    index_01 = index_01 + 1
                self.index_02 = index_01
            if self.index_02 is None: return
            self.xs[self.index_02] = event.xdata  # 鼠标的坐标覆盖选中的点的坐标
            self.ys[self.index_02] = event.ydata
            self.draw_01()
        except Exception as ex:
            print ex.message


    def on_release(self, event):  # 鼠标按下调用
        if event.inaxes != self.line.axes: return
        if self.pick == None:  # 如果不是选中点，那就添加点
            for x in self.xs:
                if event.xdata < x:
                    print "分步轴不允许时间倒逆"
                    return
            self.xs.append(event.xdata)
            self.ys.append(event.ydata)
        if self.pick == 1 and self.motion != 1:  # 如果是选中点，但不是拖动点，那就降阶
            x = self.xs
            x_data = event.xdata
            y_data = event.ydata
            index_01 = 0
            for i in x:
                if abs(i - x_data) < 0.02 * gifts_time:
                    if abs(self.ys[index_01] - y_data) < 0.02 * gifts_number: break
                index_01 = index_01 + 1
            self.xs.pop(index_01)
            self.ys.pop(index_01)
        self.draw_01()
        self.pick = None  # 所有状态恢复，鼠标按下到稀放为一个周期
        self.motion = None
        self.press = None
        self.index_02 = None

    def on_picker(self, event):  # 选中调用
        self.pick = 1

    def draw_01(self):  # 绘图
        self.line.clear()  # 不清除的话会保留原有的图
        self.line.axis([0, gifts_time, 0, gifts_number])  # x和y范围0到1
        self.bezier(self.xs, self.ys)  # Bezier曲线
        self.line.set_title(u'曲线计算')
        self.line.scatter(self.xs, self.ys, color='b', s=30, marker="o", picker=5)  # 画点
        self.line.plot(self.xs, self.ys, color='r')  # 画线
        self.line.yaxis.set_major_locator(MultipleLocator(YMultipleLocator))
        self.line.xaxis.set_major_locator(MultipleLocator(XMultipleLocator))
        self.line.grid(True)  # 网格使用刻度
        self.calculate()
        self.line.figure.canvas.draw()  # 重构子图

    # 不允许有时间倒逆
    def time_check(self):
        for index in range(0, len(self.data_x) - 1):
            if self.data_x[index] > self.data_x[index+1]:
                print "不允许时间倒逆,此分布图数据有误"
                return True
        return False

    def bezier(self, *args):  # Bezier曲线公式转换，获取x和y
        t = np.linspace(0, 1, gifts_point_number)  # t 范围0到1
        le = len(args[0]) - 1
        le_1 = 0
        b_x, b_y = 0, 0
        for x in args[0]:
            b_x = b_x + x * (t ** le_1) * ((1 - t) ** le) * comb(len(args[0]) - 1, le_1)  # comb 组合，perm 排列
            le = le - 1
            le_1 = le_1 + 1

        le = len(args[0]) - 1
        le_1 = 0
        for y in args[1]:
            b_y = b_y + y * (t ** le_1) * ((1 - t) ** le) * comb(len(args[0]) - 1, le_1)
            le = le - 1
            le_1 = le_1 + 1
        self.line.plot(b_x, b_y)
        self.line.scatter(b_x, b_y, color='g', s=10, marker="o", picker=10)  # 画点
        self.data_x = b_x
        self.data_y = b_y

    def calculate(self):
        #前置检查
        if self.time_check(): return
        print "=================================================="
        print "=================================================="
        print "=================    坐标轴情况     ================"
        print "=================================================="
        print "=================================================="
        for index in range(0, len(self.data_x)):
            print "x:{x},y:{y}\n".format(x=self.data_x[index], y=self.data_y[index])
        sum = reduce(lambda x,y: x+y, self.data_y)
        print "数据总和:{sum}".format(sum=sum)
        print "=================================================="
        print "=================================================="
        print "=================    数据占比情况     =============="
        print "=================================================="
        print "=================================================="
        resize_gift = 0.0
        # 重置
        self.gifts = []
        for index in range(0, len(self.data_x)):
            data = self.data_y[index] / sum
            gift = gifts_number * data
            # 余数整理
            if resize_gift > 1:
                gift += 1
                resize_gift -= 1
            if gift % 1 != 0 and gift > 1:
                resize_gift += gift % 1
                gift = int(gift)
            elif gift % 1 != 0 and gift < 1:
                resize_gift += gift % 1
                gift = 0
            elif gift < 1 and (resize_gift + gift) < 1:
                resize_gift += gift
                gift = 0
            elif gift < 1 and (resize_gift + gift) > 1:
                gift = 1
                resize_gift = 0
            if index == (len(self.data_x) - 1) and resize_gift > 0:
                gift += int(resize_gift)
                if gift < 1:
                    gift = 1
                gift -= ((reduce(lambda a, b: a + b, self.gifts) + gift) - gifts_number)
            self.gifts.append(int(gift))
            print "第:{x}个小时,发送奖品数量值:{gift}\n".format(x=self.data_x[index],gift=gift)
        print "分散点总数: {point_sum},奖品总数:{gift_sum}".format(
            point_sum=len(self.data_x), gift_sum=reduce(lambda x, y: x+y, self.gifts))
        # 搜集点
        self.real_gifts_time = []
        for index in range(0, len(self.data_x)):
            if index == len(self.data_x) - 1:
                self.real_data(self.data_x[index], gifts_time, self.gifts[index])
                break
            self.real_data(self.data_x[index], self.data_x[index + 1], self.gifts[index])
        # 绘制实际数据
        self.paint_real_data()


    # 二图绘点
    def real_data(self, start_x, end_x, number):
        total_x = end_x - start_x
        res_x = [random.random() * 1 for _ in xrange(0, number)]
        res_x = map(lambda x: ((x * 1.0) * total_x) + start_x, res_x)
        # x 从大到小排序
        res_x = sorted(res_x)
        for x in res_x:
            self.real_gifts_time.append(x)

    # 绘制实际数据
    def paint_real_data(self):
        # "=================================================="
        # "=================================================="
        # "=================    数据实际情况     =============="
        # "=================================================="
        # "=================================================="
        self.data_ax.figure.canvas.draw()  # 重构子图
        self.data_ax.clear()
        self.data_ax.yaxis.set_major_locator(MultipleLocator(1))
        self.data_ax.xaxis.set_major_locator(MultipleLocator(XMultipleLocator))
        self.data_ax.grid(True)  # 网格使用刻度
        # 计算颜色值
        color = np.arctan2(self.real_gifts_time, self.real_gifts_time)
        self.data_ax.scatter(self.real_gifts_time, [1 for _ in range(0, len(self.real_gifts_time))], s=10, c=color, alpha=0.7)
        self.data_ax.figure.canvas.draw()  # 重构子图
        print "动态调整奖品发送时间点如下:"
        print self.real_gifts_time

    def run(self):
        while True:
            time.sleep(3)
            self.real_gifts_time = []
            for index in range(0, len(self.data_x)):
                if index == len(self.data_x) - 1:
                    self.real_data(self.data_x[index], gifts_time, self.gifts[index])
                    break
                self.real_data(self.data_x[index], self.data_x[index + 1], self.gifts[index])
            # 绘制实际数据
            self.paint_real_data()


if __name__ == '__main__':
    fig = plt.figure(2, figsize=(12, 6))  # 创建第2个绘图对象,1200*600像素
    ax = fig.add_subplot(2, 1, 1)  # 二行一列第一个子图
    data_ax = fig.add_subplot(2, 1, 2)  # 一行一列第一个子图
    ax.yaxis.set_major_locator(MultipleLocator(YMultipleLocator))
    ax.xaxis.set_major_locator(MultipleLocator(XMultipleLocator))
    data_ax.axis([0, gifts_time, 0, 3])  # x和y范围0到1
    data_ax.yaxis.set_major_locator(MultipleLocator(1))
    data_ax.xaxis.set_major_locator(MultipleLocator(XMultipleLocator))
    ax.grid(True)  # 网格使用刻度
    data_ax.grid(True)

    bezier = Bezier(ax, data_ax, 1, "Thread")
    x = np.arange(0, gifts_time, XMultipleLocator)
    y = np.arange(0, gifts_number, YMultipleLocator)
    bezier.init_default()

    # bezier.start()
    plt.show()
