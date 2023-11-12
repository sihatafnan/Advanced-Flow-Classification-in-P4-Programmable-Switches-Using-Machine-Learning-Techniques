#!/usr/bin/env python
import sys
import socket
import random
import struct

from time import sleep

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, get_if_addr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in ifs: #eth0
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def send_pkt(flow, iface):
    iface_hwaddr = get_if_hwaddr(iface)
    # iface_ipaddr = get_if_addr(iface)
    # print(flow)
    # print(flow[6])
    f_siz = float(flow[5])
    f_cnt = float(flow[6])
    f_iat = float(flow[7])/1000000
    siz = f_siz/f_cnt
    pkt =  Ether(src=iface_hwaddr, dst=flow[9]) #'ff:ff:ff:ff:ff:ff'
    if int(flow[4]) == 6:
        pkt = pkt /IP(src=flow[0], dst=flow[1], proto=int(flow[4]), len=int(siz)) / TCP(dport=int(flow[3]), sport=int(flow[2]), flags="P") / flow[10]
    elif int(flow[4]) == 17:
        pkt = pkt /IP(src=flow[0], dst=flow[1], proto=int(flow[4]), len=int(siz)) / UDP(dport=int(flow[3]), sport=int(flow[2])) / flow[10]
    pkt.show2()
    for j in range(int(flow[6])):
        sendp(pkt, iface=iface, verbose=False)
        sleep(f_iat)

def main():
    
    # addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()
    iface_hwaddr = get_if_hwaddr(iface)
    iface_ipaddr = get_if_addr(iface)
    # iface_ipaddr = "10.0.1.1"

    my_flows = []

    f = open(iface_ipaddr+".txt")
    all_flows = f.read()
    all_flow = all_flows.split('\n')
    for flow in all_flow:
        if flow != '':
            my_flows = flow.split(',')
            # print(my_flows)
            send_pkt(my_flows, iface)

    # print("sending on interface %s to %s" % (iface, str(addr)))
    


if __name__ == '__main__':
    main()
