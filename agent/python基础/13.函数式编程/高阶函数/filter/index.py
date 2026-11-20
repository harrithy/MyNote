# filter

# filter()函数接收一个函数和一个Iterable，filter将传入的函数依次作用于序列的每个元素，然后根据返回值是True还是False来决定保留还是丢弃该元素。

def is_odd(x):
    return x % 2 == 1
  
print(list(filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9])))

def not_empty(s):
    return s and s.strip()

print(list(filter(not_empty, ['A', '', 'B', None, 'C', '  '])))


def is_palindrome(n):
    s = str(n)
    return s == s[::-1]

print(list(filter(is_palindrome, [121, 123, 1221, 1234])))