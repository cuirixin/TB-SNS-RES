#!/usr/bin/env python2.7
#-*- coding=utf8 -*-
import socket
import struct
 
from cn_net import *

class IP:
    @staticmethod
    def getVersion():
        return 'v0.0.1'
        
    
    @staticmethod
    def ip2int( ip ):
        return struct.unpack('!L',socket.inet_aton(ip))[0]
    
    @staticmethod
    def int2ip( ip ):
        return socket.inet_ntoa(struct.pack('I',socket.htonl(ip)))
     
    @staticmethod
    def iscn( ip ):
        if ip == '127.0.0.1' or ip == '::1':
            return True
        '''检查的方法：
        1. 把ip地址的第一个段拿出来,如果不在offset中，则说明不是cn的地址
        2. 先把ip地址的第一个段拿出来，用于快速定位到iplist的开始位置，减少循环的次数
        3. 从开始位置，到结束位置查找，如果在里面，则是cn的ip '''
        try:
            int_ip = IP.ip2int( ip )
        except Exception as e:
            return True
        head = ip.split(".")[0]
     
        if head not in offset:
            return False
     
        for i in range(offset[head][0],offset[head][1]+1):
            if int_ip >= iplist[i][0] and int_ip <= iplist[i][1]:
                return True
        return False