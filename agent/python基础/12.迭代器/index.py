"""
Author: harrio
Date: 2026-11-19 15:05:38
LastEditors: harrio
LastEditTime: 2026-11-19 15:10:14
Description: 迭代器
"""

# 迭代器

# 可以for循环的数据类型有集合数据类型，如 list, tuple, dict, set, str等
# 第二种就是generator，包含生成器和带 yield 的 generator function
# 这些可以直接作用于for循环的对象统称为可迭代对象：Iterable。
# 可以用 isinstance() 判断一个对象是否是 Iterable 对象

from collections.abc import Iterable

print(isinstance([], Iterable))  # True
print(isinstance((), Iterable))  # True
print(isinstance({}, Iterable))  # True
print(isinstance(set(), Iterable))  # True
print(isinstance("hello", Iterable))  # True
print(isinstance((x * x for x in range(1, 11)), Iterable))  # True

# 可以被 next() 函数调用并不断返回下一个值的对象称为迭代器：Iterator。
# 可以使用 isinstance() 判断一个对象是否是 Iterator 对象

from collections.abc import Iterator

print("---------隔断线----------")
print(isinstance([], Iterator))  # False
print(isinstance((), Iterator))  # False
print(isinstance({}, Iterator))  # False
print(isinstance(set(), Iterator))  # False
print(isinstance("hello", Iterator))  # False
print(isinstance((x * x for x in range(1, 11)), Iterator))  # True
print(isinstance(iter([]), Iterator))  # True
print(isinstance(iter("hello"), Iterator))  # True


"""
- 为什么list dist str 等数据类型不是Iterator?
这是因为Python的Iterator对象表示的是一个数据流,Iterator对象可以被next()函数调用并不断返回下一个值,直到没有数据时抛出StopIteration错误
可以把这个数据流看做是一个有序序列，但我们却不能提前知道序列的长度，
只能不断通过next()函数实现按需计算下一个数据,所以Iterator的计算是惰性的,只有在需要返回下一个数据时它才会计算。
"""
