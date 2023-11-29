# -*- coding=utf-8 -*-
r"""
debugger = debuglib.Debugger()

@debugger
def my_function(a, b):
    result = a + b
    if result < 10:
        raise ValueError("bad numbers")
    return result

my_function(1, 2)

> call my_funtion(1, 2)
    > ValueError: bad numbers
"""
