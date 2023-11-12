#!/usr/bin/env python
import sys
import socket
import random
import struct

def send_pkt(flow):
	# print(flow)
	# print(flow[6])
	f_siz = float(flow[5])
	f_cnt = float(flow[6])
	iat = float(flow[7])/1000000
	# siz = f_siz/f_cnt
	totl_time = 0.04*f_cnt
	return totl_time


def main():
    
	# addr = socket.gethostbyname(sys.argv[1])
	iface_ipaddr = "data"
	total_time = 0
	my_flows = []
	f = open(iface_ipaddr+".txt")
	all_flows = f.read()
	all_flow = all_flows.split('\n')
	for flow in all_flow:
		if flow != '':
			my_flows = flow.split(',')
			# print(my_flows)
		total_time = total_time + send_pkt(my_flows)
	print("time %s" % str(total_time/60))

if __name__ == '__main__':
    main()
