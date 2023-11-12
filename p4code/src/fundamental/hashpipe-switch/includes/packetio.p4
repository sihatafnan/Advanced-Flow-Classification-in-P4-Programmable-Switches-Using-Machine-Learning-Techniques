#ifndef __PACKETIO__
#define __PACKETIO__

#include "headers.p4"

control packetio_ingress(inout headers_t hdr,
                         inout metadata_t metadata,
                         inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.ingress_port == CPU_PORT) {
            standard_metadata.egress_spec = (bit<9>)hdr.packet_out.egress_port;
            hdr.packet_out.setInvalid();
            exit;
        }
    }
}

control packetio_egress(inout headers_t hdr,
                        inout metadata_t metadata,
                        inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.egress_port == CPU_PORT) {
            hdr.packet_in.setValid();
            if (metadata.overflow_flag == (bit<1>) 1) {
                hdr.packet_in.algo_indicator =  (bit<16>) 2;
                hdr.packet_in.src_ip = hdr.ipv4.srcAddr;
                hdr.packet_in.dst_ip = hdr.ipv4.dstAddr;
                hdr.packet_in.proto = hdr.ipv4.protocol;
                if (hdr.tcp.isValid()) {
                    hdr.packet_in.src_port = hdr.tcp.srcPort;
                    hdr.packet_in.dst_port = hdr.tcp.dstPort;
                } else {
                    hdr.packet_in.src_port = hdr.udp.srcPort;
                    hdr.packet_in.dst_port = hdr.udp.dstPort;
                }
            }
            hdr.packet_in.ingress_port = (bit<16>)standard_metadata.ingress_port;
        }
    }
}

#endif