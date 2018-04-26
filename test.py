# -*- coding: utf-8 -*-

'a test model'

__author__ = 'sxf'

import sys

def test():
    args = sys.argv
    if len(args)==1:
        print('Hello World!')
    elif len(args)==2:
        print('hello,%s!' % args[1])
    else:
        print('Too many arguments!')

if __name__=='__main__':
    test()