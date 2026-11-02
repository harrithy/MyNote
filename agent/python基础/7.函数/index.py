# 内置函数
# 举例
print(abs(-20))  # 取绝对值
print(max(1, 2, 3, 4, 5))  # 求最大值


# 定义函数
def add(a, b):
    return a + b


print(add(10, 20))  # 调用函数


# 空函数
def empty():
    pass  # pass语句表示空函数，什么都不做


# 函数的参数


def greet(name, age=18):  # age是默认参数
    print(f"Hello, {name}! You are {age} years old.")


greet("Alice")  # 使用默认参数
greet("Bob", 25)  # 覆盖默认参数


# 递归


def fact(n):
    if n == 1:
        return 1
    return n * fact(n - 1)

print(fact(100))  # 计算5的阶乘