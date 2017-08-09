#-*- coding=utf-8 -*-


import sys


class Log:
    PRINT = True
    DEBUG = True
    INFO = True
    ERROR = True
    WARNING = True
    
    @staticmethod
    def log(state, info, stdout=sys.stdout):
        if Log.PRINT == False or state == False:
            return
        stdout.write(info)
        
    @staticmethod
    def i(info, stdout=sys.stdout):
        Log.log(Log.INFO, info, stdout)
        
    @staticmethod
    def e(info, stdout=sys.stdout):
        Log.log(Log.ERROR, info, stdout)
        
    @staticmethod
    def d(info, stdout=sys.stdout):
        Log.log(Log.DEBUG, info, stdout)
        
    @staticmethod
    def w(info, stdout=sys.stdout):
        Log.log(Log.WARNING, info, stdout)
    
    
    
if __name__ == '__main__':
    Log.e("hello", sys.stdout)