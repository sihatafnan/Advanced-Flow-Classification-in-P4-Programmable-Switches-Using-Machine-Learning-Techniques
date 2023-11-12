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
    
    register<bit<104>>(1024) flow_tracker;
    register<bit<32>>(1024) packet_counter;
    register<bit<32>>(1024) flow_size;
    register<bit<48>>(1024) flow_iat;
    register<bit<48>>(1024) flow_last_time;
    register<bit<104>>(1024) flow_classified;
    register<bit<16>>(1024) classified;
    
    bit<48> arrival_time;
    bit<48> avg_time;
    bit<48> time_threshold = (bit<48>)10000000;
    bit<32> siz;
    bit<32> new_size;
    bit<32> size_threshold = (bit<32>)10240;
    bit<32> count;
    bit<1>  new_flow;
    bit<1>  size_overflow;
    bit<16> class;
    bit<104> key_class;
    bit<104> key_class_exact;
    bit<1> key_diff;
    bit<1> class_diff;
    bit<16> class_exact;

    action hash_and_store(bit<32> ipAddr1, bit<32> ipAddr2, bit<16> port1, bit<16> port2){
        // first table stage
        
        siz = (hdr.ipv4.protocol == 0x06) ? (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.tcp.minSizeInBytes()) : (bit<32>)(hdr.ipv4.totalLen - (bit<16>)hdr.ipv4.minSizeInBytes() - (bit<16>)hdr.udp.minSizeInBytes());
        arrival_time = standard_metadata.ingress_global_timestamp;
        size_overflow = (bit<1>) 0;
        // hash using my custom function 
        // modify_field_with_hash_based_offset(track_meta.mIndex, 0, stage1_hash, 1024);

        hash(track_meta.mIndex, HashAlgorithm.crc16, (bit<32>)0, {ipAddr1, ipAddr2, port1, port2, hdr.ipv4.protocol}, (bit<32>)32);
	track_meta.mKeyCarried = (bit<104>)(hdr.ipv4.srcAddr++hdr.ipv4.dstAddr++metadata.l4_src_port++metadata.l4_dst_port++hdr.ipv4.protocol);
        //track_meta.mKeyCarried = track_meta.mIndex;
        // read the key and value at that location
        flow_tracker.read(track_meta.mKeyInTable, track_meta.mIndex);
        packet_counter.read(track_meta.mCountInTable, track_meta.mIndex);
        flow_size.read(track_meta.mSizeInTable, track_meta.mIndex);
        flow_last_time.read(track_meta.mLastTimeInTable, track_meta.mIndex);
        flow_iat.read(track_meta.mIatInTable, track_meta.mIndex);

        // check if location is empty or has a differentkey in there
        // track_meta.mKeyInTable = (track_meta.mValid == 0)? track_meta.mKeyCarried : track_meta.mKeyInTable;
        track_meta.mSwapSpace = track_meta.mKeyInTable - track_meta.mKeyCarried;

        //check if the flow is same or new one
        new_flow = ((arrival_time - track_meta.mLastTimeInTable) < time_threshold) ? (bit<1>)0 : (bit<1>)1;

        // update hash table

        /*If the mSwapSpace == 0 then there is no collision, just update the values*/
        flow_tracker.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0 && new_flow == 0) ? track_meta.mKeyInTable : track_meta.mKeyCarried));
        packet_counter.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0 && new_flow == 0) ? (bit<32>)(track_meta.mCountInTable + 1) : (bit<32>)1));
        flow_size.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0 && new_flow == 0) ? (bit<32>)(track_meta.mSizeInTable + siz) : (bit<32>)siz));
        flow_last_time.write(track_meta.mIndex, arrival_time);
        //flow_iat.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0 && new_flow == 0) ? (bit<48>)((arrival_time - track_meta.mLastTimeInTable) + track_meta.mIatInTable) : (bit<48>)0));
        flow_iat.write(track_meta.mIndex, ((track_meta.mSwapSpace == 0 && new_flow == 0) ? (bit<48>)(arrival_time - track_meta.mLastTimeInTable) : (bit<48>)0));

        //check if the flow size is greater than the size_threshold
        flow_size.read(new_size, track_meta.mIndex);
        size_overflow = (new_size < size_threshold) ? (bit<1>)0 : (bit<1>)1;

        /*If the mSwapSpace == 0 then there is no collision, just check the new flows the values*/
        track_meta.mCountCurrent    = track_meta.mCountInTable;
        track_meta.mSizeCurrent     = track_meta.mSizeInTable;
        track_meta.mLastTimeCurrent = track_meta.mLastTimeInTable;
        track_meta.mIatCurrent      = track_meta.mIatInTable;
    }

/*
*/
    action fill_meta(){
        metadata.send_cont = (bit<1>)1;
        metadata.siz = track_meta.mSizeCurrent;
        metadata.count = track_meta.mCountCurrent;
        metadata.iat = track_meta.mIatCurrent;
        metadata.class = class;
        classified.write(track_meta.mIndex, class);
    }

    action send_to_classify2(bit<16> label1, bit<16> label2, bit<16> label3, bit<16> label4, bit<32> pkt_count1, bit<32> flow_size1, bit<32> pkt_count2) {
        class = (track_meta.mSizeCurrent > flow_size1) ? ((track_meta.mCountCurrent > pkt_count1) ? ((track_meta.mCountCurrent > pkt_count2) ? label4 : label3) : label2) : label1;
        key_class = (bit<104>)(hdr.ipv4.srcAddr++hdr.ipv4.dstAddr++metadata.l4_src_port++metadata.l4_dst_port++hdr.ipv4.protocol);
        flow_classified.read(key_class_exact, track_meta.mIndex);
        flow_classified.write(track_meta.mIndex, (key_class_exact == 0) ? key_class : key_class_exact);
        key_diff = (key_class - key_class_exact) == (bit<104>)0 ? (bit<1>)1 : (bit<1>)0;
        classified.read(class_exact, track_meta.mIndex);
        class_diff = (class == class_exact && key_diff == (bit<1>)0) ? (bit<1>)0: (bit<1>)1;
    }

    action send_to_classify(bit<16> label) {
        class = label;
        key_class = (bit<104>)(hdr.ipv4.srcAddr++hdr.ipv4.dstAddr++metadata.l4_src_port++metadata.l4_dst_port++hdr.ipv4.protocol);
        flow_classified.read(key_class_exact, track_meta.mIndex);
        flow_classified.write(track_meta.mIndex, (key_class_exact == 0) ? key_class : key_class_exact);
        key_diff = (key_class - key_class_exact) == (bit<104>)0 ? (bit<1>)0 : (bit<1>)1;
        classified.read(class_exact, track_meta.mIndex);
        class_diff = (class == class_exact && key_diff == (bit<1>)0) ? (bit<1>)0: (bit<1>)1;
    }
    
    @switchstack("pipeline_stage: CLASSIFY")
    table classify_count_table {
        key = {
            track_meta.mCountCurrent: exact;
        }
        actions = {
            send_to_classify;
            NoAction;
        }
        default_action = NoAction();
        size = 65536;
    }
    @switchstack("pipeline_stage: CLASSIFY")
    table classify_size_table {
        key = {
            track_meta.mSizeCurrent: exact;
        }
        actions = {
            send_to_classify;
            NoAction;
        }
        default_action = NoAction();
        size = 65536;
    }
    @switchstack("pipeline_stage: CLASSIFY")
    table classify_iat_table {
        key = {
            track_meta.mIatCurrent: exact;
        }
        actions = {
            send_to_classify;
            send_to_classify2;
            NoAction;
        }
        default_action = NoAction();
        size = 100000;
    }

    action send_to_controller(bit<16> srcport, bit<16> dstport){
        hdr.packet_in.setValid();
        metadata.overflow_flag        = (bit<1>) 1;
        standard_metadata.egress_spec       = CPU_PORT;
        hdr.packet_in.ingress_port = (bit<16>)standard_metadata.ingress_port;
    }

    apply {

        // Pipelines in Ingress
        size_overflow = (bit<1>)0;
        // forwarding
        ipv4_forwarding.apply(hdr, metadata, standard_metadata);
        hash_and_store(hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, metadata.l4_src_port, metadata.l4_dst_port);
        if (size_overflow == (bit<1>)1) {
            //classify_count_table.apply();
            //classify_size_table.apply();
            classify_iat_table.apply();
            if (class_diff == (bit<1>)1) {
                fill_meta();
            }

            //send_to_classify((bit<16>)0);
        }
        if (metadata.send_cont == (bit<1>)1) {
            send_to_controller(metadata.l4_src_port, metadata.l4_dst_port);
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
