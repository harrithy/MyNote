# 高阶函数 Higher-order function

# 变量可以指向函数

print(abs(-10))  # 10

print(abs)  # <built-in function abs>

x = abs  # 变量 x 指向函数 abs

print(x(-10))  # 10

# abs = 10  # 变量 abs 指向整数 10

# print(abs)  # 10

# abs(-10)  # TypeError: 'int' object is not callable

'''
函数名abs也是变量，它指向一个可以计算绝对值的函数！把abs指向10后，abs变量就不再指向函数了，所以调用abs(-10)就出错了。
'''

# 传入函数

def add(x, y, f):
    return f(x) + f(y)
  
print(add(1, 2, abs))  # 3