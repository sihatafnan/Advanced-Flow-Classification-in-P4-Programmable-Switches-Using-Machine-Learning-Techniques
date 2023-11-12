/*
    Basic P4 switch program for tutor. (with simple functional support)
*/
#include <core.p4>
#include <v1model.p4>

#include "includes/headers.p4"
#include "includes/actions.p4"
#include "includes/checksums.p4"
#include "includes/parser.p4"

// application
#include "includes/ipv4_forward.p4"
#include "includes/packetio.p4"
#include "includes/arp.p4"

//------------------------------------------------------------------------------
// INGRESS PIPELINE
//------------------------------------------------------------------------------
control basic_tutorial_ingress(
    inout headers_t hdr,
    inout metadata_t metadata,
    inout standard_metadata_t standard_metadata
){
    tracking_metadata_t track_meta;

    bit<48> arrival_time = standard_metadata.ingress_global_timestamp;
    bit<32> size = (bit<32>)hdr.ipv4.totalLen;

    register<bit<48>>(1024) packet_start_time_stage1;
    register<bit<48>>(1024) packet_last_time_stage1;
    register<bit<32>>(1024) packet_size_stage1;
    
    register<bit<48>>(1024) packet_start_time_stage2;
    register<bit<48>>(1024) packet_last_time_stage2;
    register<bit<32>>(1024) packet_size_stage2;
    
    register<bit<48>>(1024) packet_start_time_stage3;
    register<bit<48>>(1024) packet_last_time_stage3;
    register<bit<32>>(1024) packet_size_stage3;
    
    register<bit<48>>(1024) packet_start_time_stage4;
    register<bit<48>>(1024) packet_last_time_stage4;
    register<bit<32>>(1024) packet_size_stage4;
    
    bit<48> time_threshold = (bit<48>) 16000000;
    bit<48> duration_threshold = (bit<48>) 10000000;
    bit<48> first_time;
    bit<48> last_time;
    bit<32> new_size;
    bit<32> size_threshold = (bit<32>) 10240;
    bit<32> size_threshold_limit = (bit<32>) 13240;
    //bit<32> size_threshold = (bit<32>) 10485760;
    //bit<32> size_threshold_limit = (bit<32>) 10488760;
    bit<1> new_flow;

    bit<32> key1;
    bit<32> key2;
    bit<32> key3;
    bit<32> key4;

    bit<32> size1;
    bit<32> size2;
    bit<32> size3;
    bit<32> size4;

    bit<48> time1;
    bit<48> time2;
    bit<48> time3;
    bit<48> time4;

    bit<1> val1;
    bit<1> val2;
    bit<1> val3;
    bit<1> val4;

    bit<1> bf1;
    bit<1> bf2;
    bit<1> bf3;
    bit<1> bf4;
    bit<1> bf5;
    bit<1> bf6;
    bit<1> bf7;
    bit<1> bf8;
    bit<1> bf9;
    bit<1> bf10;
    bit<1> bf11;
    bit<1> bf12;
    bit<1> bf13;
    bit<1> bf14;
    bit<1> bf15;
    bit<1> bf16;
    bit<1> bf17;
    bit<1> bf18;
    bit<1> bf19;
    bit<1> bf20;
    bit<1> bf21;
    bit<1> bf22;
    bit<1> bf23;
    bit<1> bf24;
    bit<1> bf25;
    bit<1> bf26;
    bit<1> bf27;
    bit<1> bf28;
    bit<1> bf29;
    bit<1> bf30;
    bit<1> bf31;
    bit<1> bf32;

    bit<32> ky1 = (bit<32>)1;
    bit<32> ky2 = (bit<32>)2;
    bit<32> ky3 = (bit<32>)3;
    bit<32> ky4 = (bit<32>)4;
    bit<32> ky5 = (bit<32>)5;
    bit<32> ky6 = (bit<32>)6;
    bit<32> ky7 = (bit<32>)7;
    bit<32> ky8 = (bit<32>)8;
    bit<32> ky9 = (bit<32>)9;
    bit<32> ky10 = (bit<32>)10;
    bit<32> ky11 = (bit<32>)11;
    bit<32> ky12 = (bit<32>)12;
    bit<32> ky13 = (bit<32>)13;
    bit<32> ky14 = (bit<32>)14;
    bit<32> ky15 = (bit<32>)15;
    bit<32> ky16 = (bit<32>)16;
    bit<32> ky17 = (bit<32>)17;
    bit<32> ky18 = (bit<32>)18;
    bit<32> ky19 = (bit<32>)19;
    bit<32> ky20 = (bit<32>)20;
    bit<32> ky21 = (bit<32>)21;
    bit<32> ky22 = (bit<32>)22;
    bit<32> ky23 = (bit<32>)23;
    bit<32> ky24 = (bit<32>)24;
    bit<32> ky25 = (bit<32>)25;
    bit<32> ky26 = (bit<32>)26;
    bit<32> ky27 = (bit<32>)27;
    bit<32> ky28 = (bit<32>)28;
    bit<32> ky29 = (bit<32>)29;
    bit<32> ky30 = (bit<32>)30;
    bit<32> ky31 = (bit<32>)31;
    bit<32> ky32 = (bit<32>)32;
    bit<1> reset_flag;

    bit<1> f = (bit<1>) 0;
    bit<1> size_overflow = (bit<1>) 0;
    bit<1> duration_overflow = (bit<1>) 0;

    register<bit<1>>(4096) bloom_filter;
    //, bit<32> siz4
    action min_size(bit<32> siz1, bit<32> siz2, bit<32> siz3) {

        new_size = (siz1 <= siz2) ? ((siz1 <= siz3) ? siz1 : siz3) : ((siz2 <=siz3) ? siz2 : siz3);


        //(siz1 <= siz2 && siz3 <= siz4) ? ((siz1 <= siz3) ? siz1 : siz3) : ((siz2 <= siz1 && siz3 <= siz4) ? ((siz2 <= siz3) ? siz2 : siz3) : ((siz1 <= siz2 && siz4 <= siz3) ? ((siz1 <= siz4) ? siz1 : siz4) : ((siz2 <= siz1 && siz4 <= siz3) ? ((siz2 <= siz4) ? siz2 : siz4) : siz1)));
    }
    //, bit<48> tim4
    action max_time(bit<48> tim1, bit<48> tim2, bit<48> tim3) {

        first_time = (tim1 <= tim2) ? ((tim2 <= tim3) ? tim3 : tim2) : ((tim1 <= tim3) ? tim3 : tim1);


        //(tim1 <= tim2 && tim3 <= tim4) ? ((tim2 <= tim4) ? tim4 : tim2) : ((tim2 <= tim1 && tim3 <= tim4) ? ((tim1 <= tim4) ? tim4 : tim1) : ((tim1 <= tim2 && tim4 <= tim3) ? ((tim2 <= tim3) ? tim3 : tim2) : ((tim2 <= tim1 && tim4 <= tim3) ? ((tim1 <= tim3) ? tim3 : tim1) : tim4)));

    }

    action hash1(bit<32> ipAddr1, bit<32> ipAddr2, bit<16> port1, bit<16> port2){
        
        size = (hdr.ipv4.protocol == 0x06) ? (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.tcp.minSizeInBytes()) : (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.udp.minSizeInBytes());
        arrival_time = standard_metadata.ingress_global_timestamp;

        // hashing the 5 tuple
        hash(track_meta.mIndex, HashAlgorithm.crc16, (bit<32>)0, {ipAddr1, 
                                                                  ipAddr2,
                                                                  port1,
                                                                  port2,
                                                                  hdr.ipv4.protocol}, (bit<32>)32);

        // read the key and value at that location
        packet_last_time_stage1.read(last_time, track_meta.mIndex);
        packet_size_stage1.read(track_meta.mSizeInTable, track_meta.mIndex);
        packet_start_time_stage1.read(track_meta.mFirstTimeInTable, track_meta.mIndex);
        new_flow = ((arrival_time - last_time) > time_threshold) ? (bit<1>)1 : (bit<1>)0;
        
        // update hash table
        packet_start_time_stage1.write(track_meta.mIndex, ((new_flow == 0) ? (bit<48>)track_meta.mFirstTimeInTable : (bit<48>)arrival_time));
        packet_size_stage1.write(track_meta.mIndex, ((new_flow == 0) ? (bit<32>)(track_meta.mSizeInTable + size) : (bit<32>)size));
        packet_last_time_stage1.write(track_meta.mIndex, arrival_time);
    }

    action hash2(bit<32> ipAddr1, bit<32> ipAddr2, bit<16> port1, bit<16> port2){
        
        size = (hdr.ipv4.protocol == 0x06) ? (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.tcp.minSizeInBytes()) : (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.udp.minSizeInBytes());
        arrival_time = standard_metadata.ingress_global_timestamp;

        // hashing the 5 tuple
        hash(track_meta.mIndex, HashAlgorithm.crc32, (bit<32>)0, {ipAddr1, 
                                                                  ipAddr2,
                                                                  port1,
                                                                  port2,
                                                                  hdr.ipv4.protocol}, (bit<32>)32);

        // read the key and value at that location
        packet_last_time_stage2.read(last_time, track_meta.mIndex);
        packet_size_stage2.read(track_meta.mSizeInTable, track_meta.mIndex);
        packet_start_time_stage2.read(track_meta.mFirstTimeInTable, track_meta.mIndex);
        new_flow = ((arrival_time - last_time) > time_threshold) ? (bit<1>)1 : (bit<1>)0;
        
        // update hash table
        packet_start_time_stage2.write(track_meta.mIndex, ((new_flow == 0) ? (bit<48>)track_meta.mFirstTimeInTable : (bit<48>)arrival_time));
        packet_size_stage2.write(track_meta.mIndex, ((new_flow == 0) ? (bit<32>)(track_meta.mSizeInTable + size) : (bit<32>)size));
        packet_last_time_stage2.write(track_meta.mIndex, arrival_time);
    }

    action hash3(bit<32> ipAddr1, bit<32> ipAddr2, bit<16> port1, bit<16> port2){
        
        size = (hdr.ipv4.protocol == 0x06) ? (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.tcp.minSizeInBytes()) : (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.udp.minSizeInBytes());
        arrival_time = standard_metadata.ingress_global_timestamp;

        // hashing the 5 tuple
        hash(track_meta.mIndex, HashAlgorithm.csum16, (bit<32>)0, {ipAddr1, 
                                                                  ipAddr2,
                                                                  port1,
                                                                  port2,
                                                                  hdr.ipv4.protocol}, (bit<32>)32);

        // read the key and value at that location
        packet_last_time_stage3.read(last_time, track_meta.mIndex);
        packet_size_stage3.read(track_meta.mSizeInTable, track_meta.mIndex);
        packet_start_time_stage3.read(track_meta.mFirstTimeInTable, track_meta.mIndex);
        new_flow = ((arrival_time - last_time) > time_threshold) ? (bit<1>)1 : (bit<1>)0;
        
        // update hash table
        packet_start_time_stage3.write(track_meta.mIndex, ((new_flow == 0) ? (bit<48>)track_meta.mFirstTimeInTable : (bit<48>)arrival_time));
        packet_size_stage3.write(track_meta.mIndex, ((new_flow == 0) ? (bit<32>)(track_meta.mSizeInTable + size) : (bit<32>)size));
        packet_last_time_stage3.write(track_meta.mIndex, arrival_time);
    }

    action hash4(bit<32> ipAddr1, bit<32> ipAddr2, bit<16> port1, bit<16> port2){
        
        size = (hdr.ipv4.protocol == 0x06) ? (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.tcp.minSizeInBytes()) : (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.udp.minSizeInBytes());
        arrival_time = standard_metadata.ingress_global_timestamp;

        // hashing the 5 tuple
        hash(track_meta.mIndex, HashAlgorithm.crc16, (bit<32>)0, {ipAddr1, 
                                                                  ipAddr2,
                                                                  port1,
                                                                  port2,
                                                                  hdr.ipv4.protocol}, (bit<32>)32);

        // read the key and value at that location
        packet_last_time_stage4.read(last_time, track_meta.mIndex);
        packet_size_stage4.read(track_meta.mSizeInTable, track_meta.mIndex);
        packet_start_time_stage4.read(track_meta.mFirstTimeInTable, track_meta.mIndex);
        new_flow = ((arrival_time - last_time) > time_threshold) ? (bit<1>)1 : (bit<1>)0;
        
        // update hash table
        packet_start_time_stage4.write(track_meta.mIndex, ((new_flow == 0) ? (bit<48>)track_meta.mFirstTimeInTable : (bit<48>)arrival_time));
        packet_size_stage4.write(track_meta.mIndex, ((new_flow == 0) ? (bit<32>)(track_meta.mSizeInTable + size) : (bit<32>)size));
        packet_last_time_stage4.write(track_meta.mIndex, arrival_time);
    }

    action check_flow(bit<32> ipAddr1, bit<32> ipAddr2, bit<16> port1, bit<16> port2){
        hash(key1, HashAlgorithm.crc16, (bit<32>)0, {ipAddr1, ipAddr2, port1, port2, hdr.ipv4.protocol}, (bit<32>)32);
        hash(key2, HashAlgorithm.crc32, (bit<32>)0, {ipAddr1, ipAddr2, port1, port2, hdr.ipv4.protocol}, (bit<32>)32);
        hash(key3, HashAlgorithm.csum16, (bit<32>)0, {ipAddr1, ipAddr2, port1, port2, hdr.ipv4.protocol}, (bit<32>)32);
        //hash(key4, HashAlgorithm.crc16, (bit<32>)0, {ipAddr1, ipAddr2, port1, port2, hdr.ipv4.protocol}, (bit<32>)32);

        bloom_filter.read(val1, key1);
        bloom_filter.read(val2, key2);
        bloom_filter.read(val3, key3);
        //bloom_filter.read(val4, key4);
        metadata.overflow_flag = (bit<1>) 0;
        //&& val4 == (bit<1>)1
        f = (val1 == (bit<1>)1 && val2 == (bit<1>)1 && val3 == (bit<1>)1) ? (bit<1>)1 : (bit<1>)0;
    }

    action classify_flow() {
        packet_size_stage1.read(size1, key1);
        packet_size_stage2.read(size2, key2);
        packet_size_stage3.read(size3, key3);
        //packet_size_stage4.read(size4, key4);
        //,size4
        min_size(size1,size2,size3);

        packet_start_time_stage1.read(time1, key1);
        packet_start_time_stage2.read(time2, key2);
        packet_start_time_stage3.read(time3, key3);
        //packet_start_time_stage4.read(time4, key4);
        //, time4
        max_time(time1, time2, time3);
        size_overflow = (new_size >= size_threshold && new_size < size_threshold_limit) ? (bit<1>)1 : (bit<1>)0;
        duration_overflow = ((arrival_time - first_time) >= duration_threshold) ? (bit<1>)1 : (bit<1>)0;

        bloom_filter.write(key1, ((size_overflow == (bit<1>)1 && duration_overflow == (bit<1>)1) ? (bit<1>)1 : (bit<1>)0));
        bloom_filter.write(key2, ((size_overflow == (bit<1>)1 && duration_overflow == (bit<1>)1) ? (bit<1>)1 : (bit<1>)0));
        bloom_filter.write(key3, ((size_overflow == (bit<1>)1 && duration_overflow == (bit<1>)1) ? (bit<1>)1 : (bit<1>)0));
        //bloom_filter.write(key4, ((size_overflow == (bit<1>)1 && duration_overflow == (bit<1>)1) ? (bit<1>)1 : (bit<1>)0));
    }

    action send_controller(){
        standard_metadata.egress_spec = CPU_PORT;
    }

    action send_to_controller(bit<16> srcport, bit<16> dstport) {
        //hdr.packet_in.setValid();
        metadata.overflow_flag = (bit<1>) 1;
        //hdr.packet_in.algo_indicator = (bit<14>) 2;
        //hdr.packet_in.src_ip = hdr.ipv4.srcAddr;
        //hdr.packet_in.dst_ip = hdr.ipv4.dstAddr;
        //hdr.packet_in.src_port = srcport;
        //hdr.packet_in.dst_port = dstport;
        //hdr.packet_in.proto = hdr.ipv4.protocol;
        standard_metadata.egress_spec = CPU_PORT;
    }

    action check_reset_bloom_filter() {
        
        bloom_filter.read(bf1, ky1);
        bloom_filter.read(bf2, ky2);
        bloom_filter.read(bf3, ky3);
        bloom_filter.read(bf4, ky4);
        bloom_filter.read(bf5, ky5);
        bloom_filter.read(bf6, ky6);
        bloom_filter.read(bf7, ky7);
        bloom_filter.read(bf8, ky8);
        bloom_filter.read(bf9, ky9);
        bloom_filter.read(bf10, ky10);
        bloom_filter.read(bf11, ky11);
        bloom_filter.read(bf12, ky12);
        bloom_filter.read(bf13, ky13);
        bloom_filter.read(bf14, ky14);
        bloom_filter.read(bf15, ky15);
        bloom_filter.read(bf16, ky16);
        bloom_filter.read(bf17, ky17);
        bloom_filter.read(bf18, ky18);
        bloom_filter.read(bf19, ky19);
        bloom_filter.read(bf20, ky20);
        bloom_filter.read(bf21, ky21);
        bloom_filter.read(bf22, ky22);
        bloom_filter.read(bf23, ky23);
        bloom_filter.read(bf24, ky24);
        bloom_filter.read(bf25, ky25);
        bloom_filter.read(bf26, ky26);
        bloom_filter.read(bf27, ky27);
        bloom_filter.read(bf28, ky28);
        bloom_filter.read(bf29, ky29);
        bloom_filter.read(bf30, ky30);
        bloom_filter.read(bf31, ky31);
        bloom_filter.read(bf32, ky32);

        reset_flag = (bf1 == (bit<1>)1 && bf2 == (bit<1>)1 && bf3 == (bit<1>)1 && bf4 == (bit<1>)1 && bf5 == (bit<1>)1 && bf6 == (bit<1>)1 && bf7 == (bit<1>)1 && bf8 == (bit<1>)1 && bf9 == (bit<1>)1 && bf10 == (bit<1>)1 && bf11 == (bit<1>)1 && bf12 == (bit<1>)1 && bf13 == (bit<1>)1 && bf14 == (bit<1>)1 && bf15 == (bit<1>)1 && bf16 == (bit<1>)1 && bf17 == (bit<1>)1 && bf18 == (bit<1>)1 && bf19 == (bit<1>)1 && bf20 == (bit<1>)1 && bf21 == (bit<1>)1 && bf22 == (bit<1>)1 && bf23 == (bit<1>)1 && bf24 == (bit<1>)1 && bf25 == (bit<1>)1 && bf26 == (bit<1>)1 && bf27 == (bit<1>)1 && bf28 == (bit<1>)1 && bf29 == (bit<1>)1 && bf30 == (bit<1>)1 && bf31 == (bit<1>)1 && bf32 == (bit<1>)1) ? (bit<1>) 1 : (bit<1>) 0; 

        bloom_filter.write(ky1, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf1);
        bloom_filter.write(ky2, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf2);
        bloom_filter.write(ky3, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf3);
        bloom_filter.write(ky4, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf4);
        bloom_filter.write(ky5, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf5);
        bloom_filter.write(ky6, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf6);
        bloom_filter.write(ky7, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf7);
        bloom_filter.write(ky8, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf8);
        bloom_filter.write(ky9, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf9);
        bloom_filter.write(ky10, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf10);
        bloom_filter.write(ky11, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf11);
        bloom_filter.write(ky12, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf12);
        bloom_filter.write(ky13, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf13);
        bloom_filter.write(ky14, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf14);
        bloom_filter.write(ky15, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf15);
        bloom_filter.write(ky16, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf16);
        bloom_filter.write(ky17, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf17);
        bloom_filter.write(ky18, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf18);
        bloom_filter.write(ky19, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf19);
        bloom_filter.write(ky20, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf20);
        bloom_filter.write(ky21, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf21);
        bloom_filter.write(ky22, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf22);
        bloom_filter.write(ky23, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf23);
        bloom_filter.write(ky24, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf24);
        bloom_filter.write(ky25, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf25);
        bloom_filter.write(ky26, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf26);
        bloom_filter.write(ky27, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf27);
        bloom_filter.write(ky28, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf28);
        bloom_filter.write(ky29, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf29);
        bloom_filter.write(ky30, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf30);
        bloom_filter.write(ky31, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf31);
        bloom_filter.write(ky32, (reset_flag == (bit<1>)1) ? (bit<1>)0 : bf32);
    }

    apply {

        // Pipelines in Ingress

        // forwarding
        ipv4_forwarding.apply(hdr, metadata, standard_metadata);

        hash1(hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, metadata.l4_src_port, metadata.l4_dst_port);
        hash2(hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, metadata.l4_src_port, metadata.l4_dst_port);
        hash3(hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, metadata.l4_src_port, metadata.l4_dst_port);
        //hash4(hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, metadata.l4_src_port, metadata.l4_dst_port);
        check_flow(hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, metadata.l4_src_port, metadata.l4_dst_port);
        if (f == (bit<1>)0) {
            classify_flow();
            check_reset_bloom_filter();
            if (size_overflow == (bit<1>)1 && duration_overflow == (bit<1>)1) {
                send_to_controller(metadata.l4_src_port, metadata.l4_dst_port);
            }
        }
        // arp
        //arp.apply(hdr, metadata, standard_metadata);
    }
}

//------------------------------------------------------------------------------
// EGRESS PIPELINE
//------------------------------------------------------------------------------
control basic_tutorial_egress(
    inout headers_t hdr,
    inout metadata_t metadata,
    inout standard_metadata_t standard_metadata
){
    apply {
        // Pipelines in Egress
        packetio_egress.apply(hdr,metadata,standard_metadata);
    }
}

//------------------------------------------------------------------------------
// SWITCH ARCHITECTURE
//------------------------------------------------------------------------------
V1Switch(
    basic_tutor_switch_parser(),
    basic_tutor_verifyCk(),
    basic_tutorial_ingress(),
    basic_tutorial_egress(),
    basic_tutor_computeCk(),
    basic_tutor_switch_deparser()
) main;