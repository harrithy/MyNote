'''
Author: harrio
Date: 2026-11-20 17:44:10
LastEditors: harrio
LastEditTime: 2026-11-20 17:47:30
Description: 返回函数
'''
# 
def calc_sum(*args):
    total = 0
    for n in args:
        total += n
    return total

f = calc_sum(1, 2, 3, 4, 5)
print(f)  # 输出结果为 15

def lazy_sum(*args):
    def sum():
        total = 0
        for n in args:
            total += n
        return total
    return sum

f = lazy_sum(1, 2, 3, 4, 5)
print(f)  # 输出结果为 <function lazy_sum.<locals>.sum at 0x7f8c1c2e0d30>
print(f())  # 输出结果为 15