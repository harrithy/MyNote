# sorted

# sorted()函数接收一个可迭代对象，返回一个新的已排序的列表。

# 语法： key 可以是函数 reverse 是否反向排序
# sorted(iterable, key=None, reverse=False)

print(sorted([3, 1, 4, 1, 5, 9, 2, 6, 5]))

print(sorted([3, 1, 4, 1, 5, 9, 2, 6, 5], reverse=True))

L = [("Bob", 75), ("Adam", 92), ("Bart", 66), ("Lisa", 88)]


# 按姓名排序
def by_name(t):
    return t[0]


print(sorted(L, key=by_name))


# 按分数排序
def by_score(t):
    return t[1]


print(sorted(L, key=by_score, reverse=True))
