'''
Author: harrio
Date: 2026-11-11 17:52:35
LastEditors: harrio
LastEditTime: 2026-11-19 14:58:37
Description: 
'''
# 生成器 generator

g = (x * x for x in range(1, 11))  # 创建一个生成器对象

L = [x * x for x in range(1, 11)]  # 创建一个列表对象

# 与列表生成式最大的不同就是，外层的[]变成了()

print(next(g))  # 输出生成器对象

print(L)  


