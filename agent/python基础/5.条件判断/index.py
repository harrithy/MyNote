'''
Author       : harrio
Date         : 2026-10-17 19:49:44
LastEditors  : harrio
LastEditTime : 2026-10-24 14:32:01
Description  : 
'''

# if else

harrio = "harrio"

if harrio == "harrio":
    print("Hello, harrio!")
elif harrio == "harrio2":
    print("Hello, harrio2!")
else:
    print("Hello, world!")


# match case

match harrio:
    case "harrio":
        print("Hello, harrio13!")
    case "harrio2":
        print("Hello, harrio2!")
    case _:
        print("Hello, world!")