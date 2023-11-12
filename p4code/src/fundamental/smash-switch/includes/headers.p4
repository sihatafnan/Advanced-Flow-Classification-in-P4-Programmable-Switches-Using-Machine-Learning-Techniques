#ifndef __HEADERS__
#define __HEADERS__

#include "codex/enum.p4"
#include "codex/l2.p4"
#include "codex/l3.p4"
#include "codex/l4.p4"
#include "codex/l567.p4"

#define CPU_PORT 255

// packet in 
@controller_header("packet_in")
header packet_in_header_t {
	bit<16> algo_indicator;
    bit<32> src_ip;
    bit<32> dst_ip;
    bit<16> src_port;
    bit<16> dst_port;
    bit<8>  proto;
    bit<32> siz;
    bit<32> count;
    bit<48> iat;
    bit<16> class;
    bit<16> ingress_port;
}

// packet out 
@controller_header("packet_out")
header packet_out_header_t {
    bit<16> egress_port;
    bit<16> mcast_grp;
}

// header struct for packet
struct headers_t {
    packet_out_header_t     packet_out;
    packet_in_header_t      packet_in;
    ethernet_t              ethernet;
    ipv4_t                  ipv4;
    tcp_t                   tcp;
    udp_t                   udp;
}

// metadata inside switch pipeline
struct metadata_t {
    bit<16> l4_src_port;
    bit<16> l4_dst_port;
    bit<1>  l3_admit;
    bit<12> dst_vlan;
    bit<1>  overflow_flag;
    bit<32> siz;
    bit<32> count;
    bit<48> iat;
    bit<16> class;
    bit<1>  send_cont;
}

struct tracking_metadata_t {
    bit<104> mKeyInTable;
    bit<32> mCountInTable;
    bit<32> mSizeInTable;
    bit<48> mIatInTable;
    bit<48> mLastTimeInTable;
    bit<32> mIndex;
    bit<104> mKeyCarried;
    bit<32> mCountCurrent;
    bit<32> mSizeCurrent;
    bit<48> mIatCurrent;
    bit<48> mLastTimeCurrent;
    bit<104> mSwapSpace;
}

#endif
