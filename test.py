from matplotlib import pyplot
import numpy

from scipy.interpolate import interp1d

x = numpy.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8,
                 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7])
y = numpy.array([31.85, 45.38, 55.73, 64.49, 72.45, 76.83, 79.62, 87.58,
                 104.30, 121.02, 143.31, 189.49, 262.74, 429.94, 955.22, 2547.77, 5095.54])

f1 = interp1d(x, y, kind='nearest')  # 最近插值
f2 = interp1d(x, y, kind='linear')  # 线性插值
f3 = interp1d(x, y, kind='cubic')  # 三次样条插值
x_pred = numpy.linspace(1, 1.6, num=100)
y1 = f1(x_pred)
y2 = f2(x_pred)
y3 = f3(x_pred)
pyplot.plot(x_pred, y1, 'r', label='nearest')
pyplot.plot(x_pred, y2, 'b--', label='linear')
pyplot.plot(x_pred, y3, 'g^', label='cubic')
pyplot.legend()
pyplot.show()
