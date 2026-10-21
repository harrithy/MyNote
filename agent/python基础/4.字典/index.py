"""
Author       : harrio
Date         : 2026-10-17 01:58:43
LastEditors  : harrio
LastEditTime : 2026-10-17 17:18:53
Description  :
"""
# 字典 dict 相当于js里的map

my_dict = {"name": "harrio", "age": 23, "location": "China"}

print("字典:", my_dict, my_dict["name"])  # 输出字典及其值

# set 只存key 不存value, 相当于js里的set

my_set = {1, 2, 3, 4, 5}

print("集合:", my_set, 1 in my_set)  # 输出集合及元素是否存在
