#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import argparse, grpc, os, sys
from time import sleep
from scapy.all import *
import threading
from datetime import datetime, timedelta, time 

# set our lib path
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
        '../../../utils/'))

SWITCH_TO_HOST_PORT = 1
SWITCH_TO_SWITCH_PORT = 2

# And then we import
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

def writeARPReply(p4info_helper, sw, in_port, dst_eth_addr, port=None):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "basic_tutorial_ingress.arp.arp_exact",
        match_fields = {
            "standard_metadata.ingress_port": in_port,
            "hdr.ethernet.dstAddr": dst_eth_addr
        },
        action_name = "basic_tutorial_ingress.arp.arp_reply",
        action_params = {
            "port": port
        })
    sw.WriteTableEntry(table_entry)
    print "Installed ARP Reply rule via P4Runtime."

def writeARPFlood(p4info_helper, sw, in_port, dst_eth_addr, port=None):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "basic_tutorial_ingress.arp.arp_exact",
        match_fields = {
            "standard_metadata.ingress_port": in_port,
            "hdr.ethernet.dstAddr": dst_eth_addr
        },
        action_name = "basic_tutorial_ingress.arp.flooding",
        action_params = {
        }
    )
    sw.WriteTableEntry(table_entry)
    print "Installed ARP Flooding rule via P4Runtime."

def writeIPv4Fwd(p4info_helper, sw, dst_ip_addr, dst_eth_addr, port):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "basic_tutorial_ingress.ipv4_forwarding.ipv4_lpm",
        match_fields = {
            "hdr.ipv4.dstAddr": [dst_ip_addr, 32]
        },
        action_name = "basic_tutorial_ingress.ipv4_forwarding.ipv4_forward",
        action_params = {
            "dstAddr": dst_eth_addr,
            "port": port
        }
    )
    sw.WriteTableEntry(table_entry)
    print "Installed Ipv4 Forward rule via P4Runtime."

def printGrpcError(e):
    print "gRPC Error: ", e.details(),
    status_code = e.code()
    print "(%s)" % status_code.name,
    # detail about sys.exc_info - https://docs.python.org/2/library/sys.html#sys.exc_info
    traceback = sys.exc_info()[2]
    print "[%s:%s]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno)

def listenPacketIn(switch, sw, dat):
    while True:
        packetin = switch.PacketIn()
        if packetin.WhichOneof('update')=='packet':
            now_date = datetime.now()
            print("Received Packet-in in %s\n" % sw)
            packet = packetin.packet.payload
            pkt = Ether(_pkt=packet)
            metadata = packetin.packet.metadata
            #print(str(metadata))
            ips = pkt.getlayer(Ether).getlayer(IP).src
            ipd = pkt.getlayer(Ether).getlayer(IP).dst
            pr = pkt.getlayer(Ether).getlayer(IP).proto
            if TCP in pkt:
                ports = pkt.getlayer(Ether).getlayer(IP).getlayer(TCP).sport
                portd = pkt.getlayer(Ether).getlayer(IP).getlayer(TCP).dport
                dt = pkt.getlayer(Ether).getlayer(IP).getlayer(TCP).getlayer(Raw).load
            elif UDP in pkt:
                ports = pkt.getlayer(Ether).getlayer(IP).getlayer(UDP).sport
                portd = pkt.getlayer(Ether).getlayer(IP).getlayer(UDP).dport
                dt = pkt.getlayer(Ether).getlayer(IP).getlayer(UDP).getlayer(Raw).load
            print("time--%s, src_ip--%s, dst_ip--%s, src_port--%s, dst_port--%s, proto--%s, batch--%s" % 
                    (str(now_date - dat), ips, ipd, str(ports), str(portd), str(pr), str(dt)))


def main(p4info_file_path, bmv2_file_path):
    start_date = datetime.now()
    # Instantiate a P4Runtime helper from the p4info file
    # - then need to read from the file compile from P4 Program, which call .p4info
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)
    port_map = {}
    arp_rules = {}
    flag = 0
    bcast = "ff:ff:ff:ff:ff:ff"
    ip_value = ["10.0.1.1", "10.0.1.2", "10.0.1.3",
                "10.0.2.4", "10.0.2.5", "10.0.2.6",
                "10.0.3.7", "10.0.3.8"]
    mac_value = ["00:00:00:00:01:01", "00:00:00:00:01:02", "00:00:00:00:01:03",
                 "00:00:00:00:02:04", "00:00:00:00:02:05", "00:00:00:00:02:06",
                 "00:00:00:00:03:07", "00:00:00:00:03:08"]
    s1_port_map = {}
    s2_port_map = {}
    s3_port_map = {}
    s4_port_map = {}
    s5_port_map = {}
    s6_port_map = {}
    s7_port_map = {}
    s8_port_map = {}
    s9_port_map = {}
    s1016_port_map = {}
    s1_port_map["00:00:00:00:01:01"] = 1
    s1_port_map["00:00:00:00:01:02"] = 3
    s1_port_map["00:00:00:00:01:03"] = 4
    s1_port_map["00:00:00:00:02:04"] = 5
    s1_port_map["00:00:00:00:02:05"] = 6
    s1_port_map["00:00:00:00:02:06"] = 7
    s1_port_map["00:00:00:00:03:07"] = 8
    s1_port_map["00:00:00:00:03:08"] = 9

    s2_port_map["00:00:00:00:01:01"] = 2
    s2_port_map["00:00:00:00:01:02"] = 1
    s2_port_map["00:00:00:00:01:03"] = 4
    s2_port_map["00:00:00:00:02:04"] = 5
    s2_port_map["00:00:00:00:02:05"] = 6
    s2_port_map["00:00:00:00:02:06"] = 7
    s2_port_map["00:00:00:00:03:07"] = 8
    s2_port_map["00:00:00:00:03:08"] = 9

    s3_port_map["00:00:00:00:01:01"] = 2
    s3_port_map["00:00:00:00:01:02"] = 3
    s3_port_map["00:00:00:00:01:03"] = 1
    s3_port_map["00:00:00:00:02:04"] = 5
    s3_port_map["00:00:00:00:02:05"] = 6
    s3_port_map["00:00:00:00:02:06"] = 7
    s3_port_map["00:00:00:00:03:07"] = 8
    s3_port_map["00:00:00:00:03:08"] = 9

    s4_port_map["00:00:00:00:01:01"] = 2
    s4_port_map["00:00:00:00:01:02"] = 3
    s4_port_map["00:00:00:00:01:03"] = 4
    s4_port_map["00:00:00:00:02:04"] = 1
    s4_port_map["00:00:00:00:02:05"] = 6
    s4_port_map["00:00:00:00:02:06"] = 7
    s4_port_map["00:00:00:00:03:07"] = 8
    s4_port_map["00:00:00:00:03:08"] = 9

    s5_port_map["00:00:00:00:01:01"] = 2
    s5_port_map["00:00:00:00:01:02"] = 3
    s5_port_map["00:00:00:00:01:03"] = 4
    s5_port_map["00:00:00:00:02:04"] = 5
    s5_port_map["00:00:00:00:02:05"] = 1
    s5_port_map["00:00:00:00:02:06"] = 7
    s5_port_map["00:00:00:00:03:07"] = 8
    s5_port_map["00:00:00:00:03:08"] = 9

    s6_port_map["00:00:00:00:01:01"] = 2
    s6_port_map["00:00:00:00:01:02"] = 3
    s6_port_map["00:00:00:00:01:03"] = 4
    s6_port_map["00:00:00:00:02:04"] = 5
    s6_port_map["00:00:00:00:02:05"] = 6
    s6_port_map["00:00:00:00:02:06"] = 1
    s6_port_map["00:00:00:00:03:07"] = 8
    s6_port_map["00:00:00:00:03:08"] = 9

    s7_port_map["00:00:00:00:01:01"] = 2
    s7_port_map["00:00:00:00:01:02"] = 3
    s7_port_map["00:00:00:00:01:03"] = 4
    s7_port_map["00:00:00:00:02:04"] = 5
    s7_port_map["00:00:00:00:02:05"] = 6
    s7_port_map["00:00:00:00:02:06"] = 7
    s7_port_map["00:00:00:00:03:07"] = 1
    s7_port_map["00:00:00:00:03:08"] = 9

    s8_port_map["00:00:00:00:01:01"] = 2
    s8_port_map["00:00:00:00:01:02"] = 3
    s8_port_map["00:00:00:00:01:03"] = 4
    s8_port_map["00:00:00:00:02:04"] = 5
    s8_port_map["00:00:00:00:02:05"] = 6
    s8_port_map["00:00:00:00:02:06"] = 7
    s8_port_map["00:00:00:00:03:07"] = 8
    s8_port_map["00:00:00:00:03:08"] = 1

    s9_port_map["00:00:00:00:01:01"] = 1
    s9_port_map["00:00:00:00:01:02"] = 2
    s9_port_map["00:00:00:00:01:03"] = 3
    s9_port_map["00:00:00:00:02:04"] = 4
    s9_port_map["00:00:00:00:02:05"] = 5
    s9_port_map["00:00:00:00:02:06"] = 6
    s9_port_map["00:00:00:00:03:07"] = 7
    s9_port_map["00:00:00:00:03:08"] = 8

    s1016_port_map["00:00:00:00:01:01"] = 8
    s1016_port_map["00:00:00:00:01:02"] = 1
    s1016_port_map["00:00:00:00:01:03"] = 2
    s1016_port_map["00:00:00:00:02:04"] = 3
    s1016_port_map["00:00:00:00:02:05"] = 4
    s1016_port_map["00:00:00:00:02:06"] = 5
    s1016_port_map["00:00:00:00:03:07"] = 6
    s1016_port_map["00:00:00:00:03:08"] = 7

    try:
        """
            建立與範例當中使用到的兩個 switch - s1, s2
            使用的是 P4Runtime gRPC 的連線。
            並且 dump 所有的 P4Runtime 訊息，並送到 switch 上以 txt 格式做儲存
            - 以這邊 P4 的封裝來說， port no 起始從 50051 開始
         """
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s5-p4runtime-requests.txt')
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
            proto_dump_file='logs/s6-p4runtime-requests.txt')
        s7 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s7',
            address='127.0.0.1:50057',
            device_id=6,
            proto_dump_file='logs/s7-p4runtime-requests.txt')
        s8 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s8',
            address='127.0.0.1:50058',
            device_id=7,
            proto_dump_file='logs/s8-p4runtime-requests.txt')
        s9 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s9',
            address='127.0.0.1:50059',
            device_id=8,
            proto_dump_file='logs/s9-p4runtime-requests.txt')
        s10 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s10',
            address='127.0.0.1:50060',
            device_id=9,
            proto_dump_file='logs/s10-p4runtime-requests.txt')
        s11 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s11',
            address='127.0.0.1:50061',
            device_id=10,
            proto_dump_file='logs/s11-p4runtime-requests.txt')
        s12 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s12',
            address='127.0.0.1:50062',
            device_id=11,
            proto_dump_file='logs/s12-p4runtime-requests.txt')
        s13 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s13',
            address='127.0.0.1:50063',
            device_id=12,
            proto_dump_file='logs/s13-p4runtime-requests.txt')
        s14 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s14',
            address='127.0.0.1:50064',
            device_id=13,
            proto_dump_file='logs/s14-p4runtime-requests.txt')
        s15 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s15',
            address='127.0.0.1:50065',
            device_id=14,
            proto_dump_file='logs/s15-p4runtime-requests.txt')
        s16 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s16',
            address='127.0.0.1:50066',
            device_id=15,
            proto_dump_file='logs/s16-p4runtime-requests.txt')
        s_value = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16]
        s_port_value = [s1_port_map, s2_port_map, s3_port_map, s4_port_map,
                        s5_port_map, s6_port_map, s7_port_map, s8_port_map, 
                        s9_port_map, s1016_port_map, s1016_port_map, s1016_port_map,
                        s1016_port_map, s1016_port_map, s1016_port_map, s1016_port_map]

        # 傳送 master arbitration update message 來建立，使得這個 controller 成為
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        s5.MasterArbitrationUpdate()
        s6.MasterArbitrationUpdate()
        s7.MasterArbitrationUpdate()
        s8.MasterArbitrationUpdate()
        s9.MasterArbitrationUpdate()
        s10.MasterArbitrationUpdate()
        s11.MasterArbitrationUpdate()
        s12.MasterArbitrationUpdate()
        s13.MasterArbitrationUpdate()
        s14.MasterArbitrationUpdate()
        s15.MasterArbitrationUpdate()
        s16.MasterArbitrationUpdate()

        # 安裝目標 P4 程式到 switch 上
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s1"
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s2"
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s3"
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s4"
        s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s5"
        s6.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s6"
        s7.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s7"
        s8.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s8"
        s9.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s9"
        s10.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s10"
        s11.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s11"
        s12.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s12"
        s13.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s13"
        s14.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s14"
        s15.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s15"
        s16.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s16"

        mc_group_entry = p4info_helper.buildMCEntry(
            mc_group_id = 1,
            replicas = {
                1:1,
                2:2,
                3:3
            })
        s1.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s1."
        s2.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s2."
        s3.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s3."
        s4.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s4."
        s5.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s5."
        s6.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s6."
        s7.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s7."
        s8.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s8."
        s9.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s9."
        s10.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s10."
        s11.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s11."
        s12.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s12."
        s13.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s13."
        s14.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s14."
        s15.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s15."
        s16.WritePRE(mc_group = mc_group_entry)
        print "Installed mgrp on s16."
        
        for j in range(len(s_value)):
            for i in range(len(ip_value)):
                port_map = s_port_value[j]
                writeIPv4Fwd(p4info_helper, sw=s_value[j], dst_ip_addr=ip_value[i], dst_eth_addr=mac_value[i], port=port_map[mac_value[i]])

        t1 = threading.Thread(target = listenPacketIn, args = (s1, "s1", start_date,))
        t2 = threading.Thread(target = listenPacketIn, args = (s2, "s2", start_date,))
        t3 = threading.Thread(target = listenPacketIn, args = (s3, "s3", start_date,))
        t4 = threading.Thread(target = listenPacketIn, args = (s4, "s4", start_date,))
        t5 = threading.Thread(target = listenPacketIn, args = (s5, "s5", start_date,))
        t6 = threading.Thread(target = listenPacketIn, args = (s6, "s6", start_date,))
        t7 = threading.Thread(target = listenPacketIn, args = (s7, "s7", start_date,))
        t8 = threading.Thread(target = listenPacketIn, args = (s8, "s8", start_date,))
        t9 = threading.Thread(target = listenPacketIn, args = (s9, "s9", start_date,))
        t10 = threading.Thread(target = listenPacketIn, args = (s10, "s10", start_date,))
        t11 = threading.Thread(target = listenPacketIn, args = (s11, "s11", start_date,))
        t12 = threading.Thread(target = listenPacketIn, args = (s12, "s12", start_date,))
        t13 = threading.Thread(target = listenPacketIn, args = (s13, "s13", start_date,))
        t14 = threading.Thread(target = listenPacketIn, args = (s14, "s14", start_date,))
        t15 = threading.Thread(target = listenPacketIn, args = (s15, "s15", start_date,))
        t16 = threading.Thread(target = listenPacketIn, args = (s16, "s16", start_date,))

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        t9.start()
        t10.start()
        t11.start()
        t12.start()
        t13.start()
        t14.start()
        t15.start()
        t16.start()

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()
        t7.join()
        t8.join()
        t9.join()
        t10.join()
        t11.join()
        t12.join()
        t13.join()
        t14.join()
        t15.join()
        t16.join()
        # while True:
        #     pass
        
        # while True:
        #     packetin = s1.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s1\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s1_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s1, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s1.PacketOut(packetout)
        #             print "Finished PacketOut in s1."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"

        #     packetin = s2.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s2\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s2_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s2, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s2.PacketOut(packetout)
        #             print "Finished PacketOut in s2."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"
            
        #     packetin = s3.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s3\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s3_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s3, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s3.PacketOut(packetout)
        #             print "Finished PacketOut in s3."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"
            
        #     packetin = s4.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s4\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s4_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s4, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s4.PacketOut(packetout)
        #             print "Finished PacketOut in s4."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"
            
        #     packetin = s5.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s5\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s5_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s5, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s5.PacketOut(packetout)
        #             print "Finished PacketOut in s5."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"
            
        #     packetin = s6.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s6\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s6_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s6, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s6.PacketOut(packetout)
        #             print "Finished PacketOut in s6."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"
            
        #     packetin = s7.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s7\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s7_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s7, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s7.PacketOut(packetout)
        #             print "Finished PacketOut in s7."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"
            
        #     packetin = s8.PacketIn()
        #     if packetin.WhichOneof('update')=='packet':
        #         print("Received Packet-in in s8\n")
        #         packet = packetin.packet.payload
        #         pkt = Ether(_pkt=packet)
        #         metadata = packetin.packet.metadata
        #         print(str(metadata)) 
        #         for meta in metadata:
        #             metadata_id = meta.metadata_id 
        #             value = meta.value 

        #         pkt_eth_src = pkt.getlayer(Ether).src 
        #         pkt_eth_dst = pkt.getlayer(Ether).dst 
        #         ether_type = pkt.getlayer(Ether).type 
        #         port_map = s8_port_map
        #         if ether_type == 2048 or ether_type == 2054:
        #             # port_map.setdefault(pkt_eth_src, value)
        #             arp_rules.setdefault(value, [])
        #             if ether_type == 2048:
        #                 pkt_ip_dst = pkt.getlayer(Ether).getlayer(IP).dst
        #                 writeIPv4Fwd(p4info_helper, sw=s8, dst_ip_addr=pkt_ip_dst, dst_eth_addr=pkt_eth_dst, port=port_map[pkt_eth_dst])
        #                 # build packetout
        #                 packetout = p4info_helper.buildPacketOut(
        #                     payload = packet,
        #                     metadata = {
        #                         1: port_map[pkt_eth_dst],
        #                         2: "\000\000"
        #                     }
        #                 )
        #                 s8.PacketOut(packetout)
        #             print "Finished PacketOut in s8."
        #             print "========================="
        #             print "port_map:%s" % port_map
        #             print "arp_rules:%s" % arp_rules
        #             print "=========================\n"

    except KeyboardInterrupt:
        # using ctrl + c to exit
        print "Shutting down."
    except grpc.RpcError as e:
        printGrpcError(e)

    # Then close all the connections
    ShutdownAllSwitchConnections()


if __name__ == '__main__':
    """ Simple P4 Controller
        Args:
            p4info:     指定 P4 Program 編譯產生的 p4info (PI 制定之格式、給予 controller 讀取)
            bmv2-json:  指定 P4 Program 編譯產生的 json 格式，依據 backend 不同，而有不同的檔案格式
     """

    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    # Specified result which compile from P4 program
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
            type=str, action="store", required=False,
            default="./simple.p4info")
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
            type=str, action="store", required=False,
            default="./simple.json")
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nPlease compile the target P4 program first." % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nPlease compile the target P4 program first." % args.bmv2_json
        parser.exit(1)

    # Pass argument into main function
    main(args.p4info, args.bmv2_json)
