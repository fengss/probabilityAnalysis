#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


class DynamicAdjust:

    def __init__(self, data):
        self.data = data
        self.keys = sorted(data.keys())
        self.values = []
        for k in self.keys:
             self.values.append(self.data[k])
        self.result = []  # 数量值
        self.result_data = {}  # 结果集时间点->数量值
        self.factor = 0.5  # 阈值
        self.adjustment_factor = 0.5  # 动态调整
        self.result_time = []  # 最终时间点

    # 因子变化
    def resize_factor(self, max):
        print "动态调整系数:{adjustment_factor}".format(adjustment_factor=self.adjustment_factor)
        if max:
            self.adjustment_factor += 0.1 if self.adjustment_factor != 1 else ""
        else:
            self.adjustment_factor -= 0.1 if self.adjustment_factor != 0.1 else ""

    # 动态调整
    def adjust(self):
        self.result = []
        resize_data = 0.0
        for index in range(0, len(self.keys)):
            if index != len(self.keys) - 1:
                confirm_value = random.uniform((self.data[self.keys[index]] * self.adjustment_factor), self.data[self.keys[index]])
                if confirm_value >= (self.data[self.keys[index]] * self.adjustment_factor + self.data[self.keys[index]]) * self.factor:
                    self.resize_factor(False)
                else:
                    self.resize_factor(True)
                # 余数整理
                if resize_data > 1:
                    confirm_value += 1
                    resize_data -= 1
                if confirm_value % 1 != 0 and confirm_value > 1:
                    resize_data += confirm_value % 1
                    confirm_value = int(confirm_value)
                elif confirm_value % 1 != 0 and confirm_value < 1:
                    resize_data += confirm_value % 1
                    confirm_value = 0
                elif confirm_value < 1 and (resize_data + confirm_value) < 1:
                    resize_data += confirm_value
                    confirm_value = 0
                elif confirm_value < 1 and (resize_data + confirm_value) > 1:
                    confirm_value = 1
                    resize_data = 0
                print "确认奖品数量值:{confirm_value}".format(confirm_value=confirm_value)
                self.result.append(confirm_value)
                self.data[self.keys[index + 1]] += (self.data[self.keys[index]] - confirm_value)
                self.result_data[self.keys[index]] = confirm_value
            else:
                confirm_value = self.data[self.keys[index]]
                if resize_data > 0:
                    confirm_value += int(resize_data)
                # 检查总和
                confirm_value -= ((reduce(lambda a, b: a+b, self.result) + confirm_value) - reduce(lambda a, b: a+b, self.values))
                print "确认奖品数量值:{confirm_value}".format(confirm_value=confirm_value)
                self.result.append(confirm_value)
                self.result_data[self.keys[index]] = confirm_value
        print "时间点:{keys}".format(keys=self.keys)
        print "数量值:{result}".format(result=self.result)
        print "时间数量映射:{result_data}".format(result_data=self.result_data)
        print "奖品数量总和:{sum}".format(sum=reduce(lambda a, b: a+b, self.result))

        # 分散
        self.result_time = []
        for index in range(0, len(self.keys)):
            if index == 0:
                self.scatter(0, 0, 0)
            else:
                self.scatter(self.keys[index - 1], self.keys[index], self.result_data[self.keys[index]])
        print "每个奖品发行时间点:{time}".format(time=self.result_time)


    # 分散具体时间点
    def scatter(self, start_time, end_time, number):
        total_time = end_time - start_time
        time = [random.random() * 1 for _ in xrange(0, number)]
        try:
            time = sorted(map(lambda x: (x * total_time) + start_time, time))
        except Exception as ex:
            print ex.message
            print "time:{time}, total_time:{total_time}".format(time=time, total_time=total_time)
        # print time
        # 打印分布的时间戳
        for t in time:
            self.result_time.append(t)

    def draw(self):
        plt.bar(left=self.keys, height=self.values, width=1, color=u'g', label=u"原始数据", alpha=0.5)
        plt.bar(left=self.keys, height=self.result, width=1, color=u'r', label=u"调整后数据", alpha=0.8)
        plt.plot(self.keys, self.result, color='r')  # 画线
        plt.plot(self.keys, self.values, color='g')  # 画线
        v_sum = reduce(lambda a, b: a+b, self.values)
        plt.scatter(self.result_time, [v_sum / 4 for _ in range(len(self.result_time))], color='b', s=1, marker="o", picker=5)
        plt.ylim(0, v_sum / 2)
        plt.xlim(0, 100)
        plt.ylabel(u"奖品数量")
        plt.xlabel(u"时间")
        plt.title(u"数据分析")
        plt.legend()
        plt.show()


if __name__ == '__main__':
    # 时间->奖品数量 关系字典
    da = DynamicAdjust({
        0: 0, 1: 10, 10: 50, 20: 10, 30: 20, 40: 10, 55: 30, 70: 10, 80: 10, 100: 10
    })
    da.adjust()
    da.draw()
