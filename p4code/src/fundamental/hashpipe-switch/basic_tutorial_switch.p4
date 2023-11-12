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
    register<bit<104>>(32) flow_tracker_stage1;
    register<bit<32>>(1024) packet_counter_stage1;
    register<bit<1>>(1024) valid_bit_stage1;
    register<bit<32>>(1024) src_ip_stage1;
    register<bit<32>>(1024) dst_ip_stage1;
    register<bit<16>>(1024) src_port_stage1;
    register<bit<16>>(1024) dst_port_stage1;
    register<bit<8>>(1024) protocol_stage1;

    register<bit<104>>(32) flow_tracker_stage2;
    register<bit<32>>(1024) packet_counter_stage2;
    register<bit<1>>(1024) valid_bit_stage2;
    register<bit<32>>(1024) src_ip_stage2;
    register<bit<32>>(1024) dst_ip_stage2;
    register<bit<16>>(1024) src_port_stage2;
    register<bit<16>>(1024) dst_port_stage2;
    register<bit<8>>(1024) protocol_stage2;

    register<bit<104>>(32) flow_tracker_stage3;
    register<bit<32>>(1024) packet_counter_stage3;
    register<bit<1>>(1024) valid_bit_stage3;
    register<bit<32>>(1024) src_ip_stage3;
    register<bit<32>>(1024) dst_ip_stage3;
    register<bit<16>>(1024) src_port_stage3;
    register<bit<16>>(1024) dst_port_stage3;
    register<bit<8>>(1024) protocol_stage3;

    register<bit<104>>(32) flow_tracker_stage4;
    register<bit<32>>(1024) packet_counter_stage4;
    register<bit<1>>(1024) valid_bit_stage4;
    register<bit<32>>(1024) src_ip_stage4;
    register<bit<32>>(1024) dst_ip_stage4;
    register<bit<16>>(1024) src_port_stage4;
    register<bit<16>>(1024) dst_port_stage4;
    register<bit<8>>(1024) protocol_stage4;

    bit<32> count_threshold = (bit<32>)7142;

    action do_stage1(){
        // first table stage
        track_meta.mKeyCarried = (bit<104>)(hdr.ipv4.srcAddr++hdr.ipv4.dstAddr++metadata.l4_src_port++metadata.l4_dst_port++hdr.ipv4.protocol);
        track_meta.mCountCarried = 0;
        metadata.overflow_flag = (bit<1>)0;
        // hash using my custom function
        // modify_field_with_hash_based_offset(track_meta.mIndex, 0, stage1_hash, 1024);

        hash(track_meta.mIndex, HashAlgorithm.crc32, (bit<32>)0, {hdr.ipv4.srcAddr,
                                                                    hdr.ipv4.dstAddr,
                                                                    metadata.l4_src_port,
                                                                    metadata.l4_dst_port,
                                                                    hdr.ipv4.protocol}, (bit<32>)32);
        //track_meta.mKeyCarried = track_meta.mIndex;
        // read the key and value at that location
        flow_tracker_stage1.read(track_meta.mKeyInTable, track_meta.mIndex);
        packet_counter_stage1.read(track_meta.mCountInTable, track_meta.mIndex);
        valid_bit_stage1.read(track_meta.mValid, track_meta.mIndex);
        src_ip_stage1.read(track_meta.mSIpInTable, track_meta.mIndex);
        dst_ip_stage1.read(track_meta.mDIpInTable, track_meta.mIndex);
        src_port_stage1.read(track_meta.mSPortInTable, track_meta.mIndex);
        dst_port_stage1.read(track_meta.mDPortInTable, track_meta.mIndex);
        protocol_stage1.read(track_meta.mProtoInTable, track_meta.mIndex);
        metadata.overflow_flag = (track_meta.mCountInTable == count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpInTable;
        metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpInTable;
        metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)1 : track_meta.mSPortInTable;
        metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)1 : track_meta.mDPortInTable;
        metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoInTable;

        // check if location is empty or has a differentkey in there
        track_meta.mKeyInTable = (track_meta.mValid == 0)? track_meta.mKeyCarried : track_meta.mKeyInTable;
        track_meta.mSwapSpace = track_meta.mKeyInTable - track_meta.mKeyCarried;

        // update hash table
        flow_tracker_stage1.write(track_meta.mIndex, track_meta.mKeyCarried);
        packet_counter_stage1.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? (bit<32>)(track_meta.mCountInTable + 1) : (bit<32>)1));
        valid_bit_stage1.write(track_meta.mIndex, (bit<1>)1);
        src_ip_stage1.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? hdr.ipv4.srcAddr : track_meta.mSIpInTable));
        dst_ip_stage1.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? hdr.ipv4.dstAddr : track_meta.mDIpInTable));
        src_port_stage1.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? metadata.l4_src_port : track_meta.mSPortInTable));
        dst_port_stage1.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? metadata.l4_dst_port : track_meta.mDPortInTable));
        protocol_stage1.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? hdr.ipv4.protocol : track_meta.mProtoInTable));

        // update metadata carried to the next table stage
        track_meta.mKeyCarried = ((track_meta.mSwapSpace == 0) ? (bit<104>)0: track_meta.mKeyInTable);
        track_meta.mCountCarried = ((track_meta.mSwapSpace == 0) ? 0: track_meta.mCountInTable);
        track_meta.mSIpCarried = ((track_meta.mSwapSpace == 0) ? 0: track_meta.mSIpInTable);
        track_meta.mDIpCarried = ((track_meta.mSwapSpace == 0) ? 0: track_meta.mDIpInTable);
        track_meta.mSPortCarried = ((track_meta.mSwapSpace == 0) ? 0: track_meta.mSPortInTable);
        track_meta.mDPortCarried = ((track_meta.mSwapSpace == 0) ? 0: track_meta.mDPortInTable);
        track_meta.mProtoCarried = ((track_meta.mSwapSpace == 0) ? 0: track_meta.mProtoInTable);
        //metadata.overflow_flag = (track_meta.mCountCarried >= count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        //metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpCarried;
        //metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpCarried;
        //metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mSPortCarried;
        //metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mDPortCarried;
        //metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoCarried;
    }

    action do_stage2(){
        // hash using my custom function
        hash(track_meta.mIndex, HashAlgorithm.crc32, (bit<32>)0, {track_meta.mKeyCarried}, (bit<32>)32);
        metadata.overflow_flag = (bit<1>)0;
        //track_meta.mIndex = track_meta.mKeyCarried;

        // read the key and value at that location
        flow_tracker_stage2.read(track_meta.mKeyInTable, track_meta.mIndex);
        packet_counter_stage2.read(track_meta.mCountInTable, track_meta.mIndex);
        valid_bit_stage2.read(track_meta.mValid, track_meta.mIndex);
        src_ip_stage2.read(track_meta.mSIpInTable, track_meta.mIndex);
        dst_ip_stage2.read(track_meta.mDIpInTable, track_meta.mIndex);
        src_port_stage2.read(track_meta.mSPortInTable, track_meta.mIndex);
        dst_port_stage2.read(track_meta.mDPortInTable, track_meta.mIndex);
        protocol_stage2.read(track_meta.mProtoInTable, track_meta.mIndex);
        metadata.overflow_flag = (track_meta.mCountInTable == count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpInTable;
        metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpInTable;
        metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mSPortInTable;
        metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mDPortInTable;
        metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoInTable;

        // check if location is empty or has a differentkey in there
        track_meta.mKeyInTable = (track_meta.mValid == 0)? track_meta.mKeyCarried : track_meta.mKeyInTable;
        track_meta.mSwapSpace = (track_meta.mValid == 0)? 0 : track_meta.mKeyInTable - track_meta.mKeyCarried;

        // update hash table
        flow_tracker_stage2.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mKeyInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mKeyCarried : track_meta.mKeyInTable)));
        packet_counter_stage2.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mCountInTable + track_meta.mCountCarried : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mCountCarried : track_meta.mCountInTable)));
        valid_bit_stage2.write(track_meta.mIndex, ((track_meta.mValid == 0) ? ((track_meta.mKeyCarried == 0) ? (bit<1>)0 : (bit<1>)1) : (bit<1>)1));

        src_ip_stage2.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mSIpInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSIpCarried : track_meta.mSIpInTable)));
        dst_ip_stage2.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mDIpInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDIpCarried : track_meta.mDIpInTable)));
        src_port_stage2.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mSPortInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSPortCarried : track_meta.mSPortInTable)));
        dst_port_stage2.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mDPortInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDPortCarried : track_meta.mDPortInTable)));
        protocol_stage2.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mProtoInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mProtoCarried : track_meta.mProtoInTable)));

        // update metadata carried to the next table stage
        track_meta.mKeyCarried = ((track_meta.mSwapSpace == 0) ? (bit<104>)0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mKeyCarried : track_meta.mKeyInTable));
        track_meta.mSIpCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSIpCarried : track_meta.mSIpInTable));
        track_meta.mDIpCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDIpCarried : track_meta.mDIpInTable));
        track_meta.mSPortCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSPortCarried : track_meta.mSPortInTable));
        track_meta.mDPortCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDPortCarried : track_meta.mDPortInTable));
        track_meta.mProtoCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mProtoCarried : track_meta.mProtoInTable));
        track_meta.mCountCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mCountCarried : track_meta.mCountInTable));
        //metadata.overflow_flag = (track_meta.mCountCarried >= count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        //metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpCarried;
        //metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpCarried;
        //metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mSPortCarried;
        //metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mDPortCarried;
        //metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoCarried;
    }

    action do_stage3(){
        // hash using my custom function
        hash(track_meta.mIndex, HashAlgorithm.crc32, (bit<32>)0, {track_meta.mKeyCarried}, (bit<32>)32);
        //track_meta.mIndex = track_meta.mKeyCarried;
        metadata.overflow_flag = (bit<1>)0;
        // read the key and value at that location
        flow_tracker_stage3.read(track_meta.mKeyInTable, track_meta.mIndex);
        packet_counter_stage3.read(track_meta.mCountInTable, track_meta.mIndex);
        valid_bit_stage3.read(track_meta.mValid, track_meta.mIndex);
        src_ip_stage3.read(track_meta.mSIpInTable, track_meta.mIndex);
        dst_ip_stage3.read(track_meta.mDIpInTable, track_meta.mIndex);
        src_port_stage3.read(track_meta.mSPortInTable, track_meta.mIndex);
        dst_port_stage3.read(track_meta.mDPortInTable, track_meta.mIndex);
        protocol_stage3.read(track_meta.mProtoInTable, track_meta.mIndex);
        metadata.overflow_flag = (track_meta.mCountInTable == count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpInTable;
        metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpInTable;
        metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mSPortInTable;
        metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mDPortInTable;
        metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoInTable;

        // check if location is empty or has a differentkey in there
        track_meta.mKeyInTable = (track_meta.mValid == 0)? track_meta.mKeyCarried : track_meta.mKeyInTable;
        track_meta.mSwapSpace = (track_meta.mValid == 0)? 0 : track_meta.mKeyInTable - track_meta.mKeyCarried;

        // update hash table
        flow_tracker_stage3.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mKeyInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mKeyCarried : track_meta.mKeyInTable)));
        packet_counter_stage3.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mCountInTable + track_meta.mCountCarried : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mCountCarried : track_meta.mCountInTable)));
        valid_bit_stage3.write(track_meta.mIndex, ((track_meta.mValid == 0) ? ((track_meta.mKeyCarried == 0) ? (bit<1>)0 : 1) : (bit<1>)1));

        src_ip_stage3.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mSIpInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSIpCarried : track_meta.mSIpInTable)));
        dst_ip_stage3.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mDIpInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDIpCarried : track_meta.mDIpInTable)));
        src_port_stage3.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mSPortInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSPortCarried : track_meta.mSPortInTable)));
        dst_port_stage3.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mDPortInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDPortCarried : track_meta.mDPortInTable)));
        protocol_stage3.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mProtoInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mProtoCarried : track_meta.mProtoInTable)));

        // update metadata carried to the next table stage
        track_meta.mKeyCarried = ((track_meta.mSwapSpace == 0) ? (bit<104>)0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mKeyCarried : track_meta.mKeyInTable));
        track_meta.mSIpCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSIpCarried : track_meta.mSIpInTable));
        track_meta.mDIpCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDIpCarried : track_meta.mDIpInTable));
        track_meta.mSPortCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSPortCarried : track_meta.mSPortInTable));
        track_meta.mDPortCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDPortCarried : track_meta.mDPortInTable));
        track_meta.mProtoCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mProtoCarried : track_meta.mProtoInTable));
        track_meta.mCountCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mCountCarried : track_meta.mCountInTable));
        //metadata.overflow_flag = (track_meta.mCountCarried >= count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        //metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpCarried;
        //metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpCarried;
        //metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mSPortCarried;
        //metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mDPortCarried;
        //metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoCarried;
    }

    action do_stage4(){
        // hash using my custom function
        hash(track_meta.mIndex, HashAlgorithm.crc32, (bit<32>)0, {track_meta.mKeyCarried}, (bit<32>)32);
        //track_meta.mIndex = track_meta.mKeyCarried;
        metadata.overflow_flag = (bit<1>)0;
        // read the key and value at that location
        flow_tracker_stage4.read(track_meta.mKeyInTable, track_meta.mIndex);
        packet_counter_stage4.read(track_meta.mCountInTable, track_meta.mIndex);
        valid_bit_stage4.read(track_meta.mValid, track_meta.mIndex);
        src_ip_stage4.read(track_meta.mSIpInTable, track_meta.mIndex);
        dst_ip_stage4.read(track_meta.mDIpInTable, track_meta.mIndex);
        src_port_stage4.read(track_meta.mSPortInTable, track_meta.mIndex);
        dst_port_stage4.read(track_meta.mDPortInTable, track_meta.mIndex);
        protocol_stage4.read(track_meta.mProtoInTable, track_meta.mIndex);
        metadata.overflow_flag = (track_meta.mCountInTable == count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpInTable;
        metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpInTable;
        metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mSPortInTable;
        metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mDPortInTable;
        metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoInTable;

        // check if location is empty or has a differentkey in there
        track_meta.mKeyInTable = (track_meta.mValid == 0)? track_meta.mKeyCarried : track_meta.mKeyInTable;
        track_meta.mSwapSpace = (track_meta.mValid == 0)? 0 : track_meta.mKeyInTable - track_meta.mKeyCarried;

        // update hash table
        flow_tracker_stage4.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mKeyInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mKeyCarried : track_meta.mKeyInTable)));
        packet_counter_stage4.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mCountInTable + track_meta.mCountCarried : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mCountCarried : track_meta.mCountInTable)));
        valid_bit_stage4.write(track_meta.mIndex, ((track_meta.mValid == 0) ? ((track_meta.mKeyCarried == 0) ? (bit<1>)0 : 1) : (bit<1>)1));

        src_ip_stage4.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mSIpInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSIpCarried : track_meta.mSIpInTable)));
        dst_ip_stage4.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mDIpInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDIpCarried : track_meta.mDIpInTable)));
        src_port_stage4.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mSPortInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSPortCarried : track_meta.mSPortInTable)));
        dst_port_stage4.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mDPortInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDPortCarried : track_meta.mDPortInTable)));
        protocol_stage4.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0)? track_meta.mProtoInTable : ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mProtoCarried : track_meta.mProtoInTable)));

        // update metadata carried to the next table stage
        track_meta.mKeyCarried = ((track_meta.mSwapSpace == 0) ? (bit<104>)0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mKeyCarried : track_meta.mKeyInTable));
        track_meta.mSIpCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSIpCarried : track_meta.mSIpInTable));
        track_meta.mDIpCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDIpCarried : track_meta.mDIpInTable));
        track_meta.mSPortCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mSPortCarried : track_meta.mSPortInTable));
        track_meta.mDPortCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mDPortCarried : track_meta.mDPortInTable));
        track_meta.mProtoCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mProtoCarried : track_meta.mProtoInTable));
        track_meta.mCountCarried = ((track_meta.mSwapSpace == 0) ? 0: ((track_meta.mCountInTable < track_meta.mCountCarried) ? track_meta.mCountCarried : track_meta.mCountInTable));
        //metadata.overflow_flag = (track_meta.mCountCarried >= count_threshold) ? (bit<1>) 1 : (bit<1>) 0;
        //metadata.overflow_flag = (track_meta.mSwapSpace == 0)? (bit<1>) 0 : (bit<1>) 1;
        //metadata.src_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mSIpCarried;
        //metadata.dst_ip   = (metadata.overflow_flag == (bit<1>) 0)? (bit<32>)0 : track_meta.mDIpCarried;
        //metadata.src_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mSPortCarried;
        //metadata.dst_port = (metadata.overflow_flag == (bit<1>) 0)? (bit<16>)0 : track_meta.mDPortCarried;
        //metadata.proto    = (metadata.overflow_flag == (bit<1>) 0)? (bit<8>)0 : track_meta.mProtoCarried;
    }

    action send_to_cpu(){
        standard_metadata.egress_spec = CPU_PORT;
    }

    apply {

        // Pipelines in Ingress

        // forwarding
        ipv4_forwarding.apply(hdr, metadata, standard_metadata);

        do_stage1();
        if (metadata.overflow_flag == (bit<1>)1) {
            send_to_cpu();
        }
        if(track_meta.mKeyCarried != 0){
            do_stage2();
            if (metadata.overflow_flag == (bit<1>)1) {
                send_to_cpu();
            }
            if(track_meta.mKeyCarried != 0){
                do_stage3();
                if (metadata.overflow_flag == (bit<1>)1) {
                    send_to_cpu();
                }
                if(track_meta.mKeyCarried != 0){
                    do_stage4();
                    if (metadata.overflow_flag == (bit<1>)1) {
                        send_to_cpu();
                    }
                }
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