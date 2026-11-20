# map/reduce

# python内建了map()和reduce()函数。

# map()函数接收两个参数，一个是函数，一个是Iterable，map将传入的函数依次作用到序列的每个元素，并把结果作为新的Iterator返回。


def f(x):
    return x * x


r = map(f, [1, 2, 3, 4, 5, 6])

print(r)  # <map object at 0x000001F9D8A1B4C0>

print(next(r))  # 1
# list(r) 从 r 当前位置取出所有剩余的值，组装成一个新的列表
print(list(r))  # [4, 9, 16, 25, 36]

# reduce把一个函数作用在一个序列[x1, x2, x3, ...]上，这个函数必须接收两个参数，reduce把结果继续和序列的下一个元素做累积计算，其效果就是：
# reduce(f, [x1, x2, x3, x4]) = f(f(f(x1, x2), x3), x4)

from functools import reduce
def add(x, y):
    return x + y

reduce_result = reduce(add, [1, 3, 5, 7, 9])
print(reduce_result)  # 25

def fn(x, y):
    return x * 10 + y

reduce_result = reduce(fn, [1, 3, 5, 7, 9])
print(reduce_result)  # 13579