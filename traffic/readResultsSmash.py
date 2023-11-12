import argparse
import pandas as pd
import os

parser = argparse.ArgumentParser()

parser.add_argument('--res', required=True, help='path to result file')
parser.add_argument('--tes', required=True, help='path to test dataset')
parser.add_argument('--op', required=True, help='path to output file')

args = parser.parse_args()

resultfile = args.res
testfile = args.tes
outputfile = args.op

flow = {}
accuracy = {}
check_flow = {}
size = {}

def check_accuracy(src_ip, dst_ip, src_port, dst_port, proto, class_iden):
        # print(src_ip)
        # print(dst_ip)
        # print(src_port)
        # print(dst_port)
        # print(proto)
        if src_ip == "0.0.0.0" or dst_ip == "0.0.0.0" or src_port == "0" or dst_port == "0" or proto == "0":
                # print("reached here")
                return False
        key = src_ip + "," + dst_ip + "," + proto + "," + str(src_port) + "," + str(dst_port)
        if key in check_flow.keys():
                if not check_flow[key]:
                        if int(flow[key]) == int(class_iden):
                                return True
        else :
                if int(flow[key]) == int(class_iden):
                        check_flow[key] = True
                else :
                        check_flow[key] = False
        return False

def map_test_data(all_flows_np):

        if all_flows_np[10] == '1' or all_flows_np[10] == '2':
                key = all_flows_np[0]+","+all_flows_np[1]+","+str(all_flows_np[4])+","+str(all_flows_np[2])+","+str(all_flows_np[3])
                flow[key] = all_flows_np[8]
                if int(all_flows_np[5]) < 10240:
                    if all_flows_np[10] in accuracy.keys():
                        accuracy[all_flows_np[10]] = accuracy[all_flows_np[10]] + 1
                        size[all_flows_np[10]] = size[all_flows_np[10]] + int(all_flows_np[5])
                    else :
                        accuracy[all_flows_np[10]] = 1
                        size[all_flows_np[10]] = int(all_flows_np[5])
        # print(len(flow))
                # if flo[0] in flow.keys():
                #       if flo[1] in flow[flo[0]].keys():
                #               if flo[4] in flow[flo[0]][flo[1]].keys():
                #                       if flo[2] in flow[flo[0]][flo[1]][flo[4]].keys():
                #                               if flo[3] in flow[flo[0]][flo[1]][flo[4]][flo[2]].keys():
                #                                       flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
                #                               else :
                #                                       flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
                #                                       flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
                #                       else :
                #                               flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
                #                               flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
                #                               flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
                #               else :
                #                       flow[flo[0]][flo[1]][flo[4]] = {}
                #                       flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
                #                       flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
                #                       flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
                #       else :
                #               flow[flo[0]][flo[1]] = {}
                #               flow[flo[0]][flo[1]][flo[4]] = {}
                #               flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
                #               flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
                #               flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
                # else :
                #       flow[flo[0]] = {}
                #       flow[flo[0]][flo[1]] = {}
                #       flow[flo[0]][flo[1]][flo[4]] = {}
                #       flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
                #       flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
                #       flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]

def process_string(res):
        words           = res.split(',')
        if len(words) == 11 or len(words) == 12:
            times               = words[0].split('--')
            if 'src_ip' in words[1]:
                src_ip          = words[1].split('--')
                dst_ip          = words[2].split('--')
                src_port        = words[3].split('--')
                dst_port        = words[4].split('--')
                proto           = words[5].split('--')
                batch           = words[6].split('--')
                size            = words[7].split('--')
                label           = words[10].split('--')
            else:
                src_ip          = words[2].split('--')
                dst_ip          = words[3].split('--')
                src_port        = words[4].split('--')
                dst_port        = words[5].split('--')
                proto           = words[6].split('--')
                batch           = words[7].split('--')
                size            = words[8].split('--')
                label           = words[11].split('--')
            return times[1],src_ip[1],dst_ip[1],src_port[1],dst_port[1],proto[1],label[1].replace("\n", ""),batch[1],size[1]
        else:
            return "123","0.0.0.0","1.1.1.1","0","0","6","0","1","1"
def main():
        res_pattern1 = 'time--'
        results = []
        results_log = []

        with open(resultfile, 'r') as all_logs:
                for line in all_logs:
                        if res_pattern1 in line:
                                results.append(line)
        # print(len(results))
        for i in range(1,9):
                ip_file = testfile+str(i)+"."+str(i)+".txt"
                print(ip_file)
                f = open(ip_file)
                all_flows = f.read()
                all_flow = all_flows.split('\n')
                #print(all_flow[0])
                for flo in all_flow:
                        if flo != '':
                                my_flows = flo.split(',')
                                map_test_data(my_flows)
        for i in range(len(results)):
			#print(results[0])
			if "0Received Packet-in in s1" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s1", "0")
			if "1Received Packet-in in s1" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s1", "1")
			if "2Received Packet-in in s1" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s1", "2")
			if "3Received Packet-in in s1" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s1", "3")
			if "4Received Packet-in in s1" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s1", "4")
			if "0Received Packet-in in s2" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s2", "0")
			if "1Received Packet-in in s2" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s2", "1")
			if "2Received Packet-in in s2" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s2", "2")
			if "3Received Packet-in in s2" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s2", "3")
			if "4Received Packet-in in s2" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s2", "4")
			if "0Received Packet-in in s3" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s3", "0")
			if "1Received Packet-in in s3" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s3", "1")
			if "2Received Packet-in in s3" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s3", "2")
			if "3Received Packet-in in s3" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s3", "3")
			if "4Received Packet-in in s3" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s3", "4")
			if "0Received Packet-in in s4" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s4", "0")
			if "1Received Packet-in in s4" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s4", "1")
			if "2Received Packet-in in s4" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s4", "2")
			if "3Received Packet-in in s4" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s4", "3")
			if "4Received Packet-in in s4" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s4", "4")
			if "0Received Packet-in in s5" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s5", "0")
			if "1Received Packet-in in s5" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s5", "1")
			if "2Received Packet-in in s5" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s5", "2")
			if "3Received Packet-in in s5" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s5", "3")
			if "4Received Packet-in in s5" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s5", "4")
			if "0Received Packet-in in s6" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s6", "0")
			if "1Received Packet-in in s6" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s6", "1")
			if "2Received Packet-in in s6" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s6", "2")
			if "3Received Packet-in in s6" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s6", "3")
			if "4Received Packet-in in s6" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s6", "4")
			if "0Received Packet-in in s7" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s7", "0")
			if "1Received Packet-in in s7" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s7", "1")
			if "2Received Packet-in in s7" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s7", "2")
			if "3Received Packet-in in s7" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s7", "3")
			if "4Received Packet-in in s7" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s7", "4")
			if "0Received Packet-in in s8" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s8", "0")
			if "1Received Packet-in in s8" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s8", "1")
			if "2Received Packet-in in s8" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s8", "2")
			if "3Received Packet-in in s8" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s8", "3")
			if "4Received Packet-in in s8" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s8", "4")
			if "0Received Packet-in in s9" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s9", "0")
			if "1Received Packet-in in s9" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s9", "1")
			if "2Received Packet-in in s9" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s9", "2")
			if "3Received Packet-in in s9" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s9", "3")
			if "4Received Packet-in in s9" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s9", "4")
			if "0Received Packet-in in s10" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s10", "0")
			if "1Received Packet-in in s10" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s10", "1")
			if "2Received Packet-in in s10" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s10", "2")
			if "3Received Packet-in in s10" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s10", "3")
			if "4Received Packet-in in s10" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s10", "4")
			if "0Received Packet-in in s11" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s11", "0")
			if "1Received Packet-in in s11" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s11", "1")
			if "2Received Packet-in in s11" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s11", "2")
			if "3Received Packet-in in s11" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s11", "3")
			if "4Received Packet-in in s11" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s11", "4")
			if "0Received Packet-in in s12" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s12", "0")
			if "1Received Packet-in in s12" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s12", "1")
			if "2Received Packet-in in s12" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s12", "2")
			if "3Received Packet-in in s12" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s12", "3")
			if "4Received Packet-in in s12" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s12", "4")
			if "0Received Packet-in in s13" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s13", "0")
			if "1Received Packet-in in s13" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s13", "1")
			if "2Received Packet-in in s13" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s13", "2")
			if "3Received Packet-in in s13" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s13", "3")
			if "4Received Packet-in in s13" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s13", "4")
			if "0Received Packet-in in s14" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s14", "0")
			if "1Received Packet-in in s14" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s14", "1")
			if "2Received Packet-in in s14" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s14", "2")
			if "3Received Packet-in in s14" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s14", "3")
			if "4Received Packet-in in s14" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s14", "4")
			if "0Received Packet-in in s15" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s15", "0")
			if "1Received Packet-in in s15" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s15", "1")
			if "2Received Packet-in in s15" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s15", "2")
			if "3Received Packet-in in s15" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s15", "3")
			if "4Received Packet-in in s15" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s15", "4")
			if "0Received Packet-in in s16" in results[i]:
				results[i] = results[i].replace("0Received Packet-in in s16", "0")
			if "1Received Packet-in in s16" in results[i]:
				results[i] = results[i].replace("1Received Packet-in in s16", "1")
			if "2Received Packet-in in s16" in results[i]:
				results[i] = results[i].replace("2Received Packet-in in s16", "2")
			if "3Received Packet-in in s16" in results[i]:
				results[i] = results[i].replace("3Received Packet-in in s16", "3")
			if "4Received Packet-in in s16" in results[i]:
				results[i] = results[i].replace("4Received Packet-in in s16", "4")
			t,si,di,sp,dp,p,c,b,siz = process_string(results[i])
			print([t,si,di,sp,dp,p,c,b,siz])
			acc = check_accuracy(si, di, sp, dp, p, c)
			if acc:
					accuracy[b] = accuracy[b] + 1
					if len(size) == 0:
							size[b] = int(siz)
					else :
							size[b] = size[b] + int(siz)

        print(accuracy)
        if len(accuracy) != 0:
            if os.path.exists(outputfile):
                f = open(outputfile, "a")
                for i in range(1, 3):
                        f.write(str(i) + ":" + str(accuracy[str(i)]) + ":" + str(size[str(i)]))
                        f.write('\n')
                f.close()
            else:
                f = open(outputfile, "w")
                for i in range(1, 3):
                        f.write(str(i) + ":" + str(accuracy[str(i)]) + ":" + str(size[str(i)]))
                        f.write('\n')
                f.close()

if __name__ == '__main__':
        main()

# time--0:27:46.760644, src_ip--10.0.1.1, dst_ip--10.0.8.8, src_port--14568, dst_port--50708, proto--6, batch--1, size--9520, count--7, iat--52004, class--0