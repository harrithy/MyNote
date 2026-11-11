# List Comprehensions

print(list(range(1, 11)))  # 输出1到10的整数列表

# 生成 1*1, 2*2, 3*3, ..., 10*10 的列表
print([x * x for x in range(1, 11)])  # 输出1,4,9,16,25,36,49,64,81,100

# 加上条件判断，生成1-10中所有偶数的平方
print([x * x for x in range(1, 11) if x % 2 == 0])  # 输出4,16,36,64,100
