#!/bin/bash
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import subprocess

def fibb(n):
    res = slow_fib(n)
    print(res)
    return res

def slow_fib(n):
    if n <= 1:
        return 1
    else:
	res =  slow_fib(n-1) + slow_fib(n-2)
	return res

def stopcaffe():
    command = 'ps -efww | grep caffe | grep -v grep | cut -c 9-15|xargs kill -9'
    os.system(command)

def startcaffe(traincmd):
    exec('print("Start training......")')
    command = traincmd
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()

