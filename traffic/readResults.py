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
		label = 0
		if flow[5] >= 10485760:
			label = 1
		if key not in flow.keys():
			flow[key] = label
		if label == 0:
			if all_flows_np[10] in accuracy.keys():
				accuracy[all_flows_np[10]] = accuracy[all_flows_np[10]] + 1
			else :
				accuracy[all_flows_np[10]] = 1
	# print(len(flow))
		# if all_flows_np[0] in flow.keys():
		# 	if flo[1] in flow[flo[0]].keys():
		# 		if flo[4] in flow[flo[0]][flo[1]].keys():
		# 			if flo[2] in flow[flo[0]][flo[1]][flo[4]].keys():
		# 				if flo[3] in flow[flo[0]][flo[1]][flo[4]][flo[2]].keys():
		# 					flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
		# 				else :
		# 					flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
		# 					flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
		# 			else :
		# 				flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
		# 				flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
		# 				flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
		# 		else :
		# 			flow[flo[0]][flo[1]][flo[4]] = {}
		# 			flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
		# 			flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
		# 			flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
		# 	else :
		# 		flow[flo[0]][flo[1]] = {}
		# 		flow[flo[0]][flo[1]][flo[4]] = {}
		# 		flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
		# 		flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
		# 		flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]
		# else :
		# 	flow[flo[0]] = {}
		# 	flow[flo[0]][flo[1]] = {}
		# 	flow[flo[0]][flo[1]][flo[4]] = {}
		# 	flow[flo[0]][flo[1]][flo[4]][flo[2]] = {}
		# 	flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]] = {}
		# 	flow[flo[0]][flo[1]][flo[4]][flo[2]][flo[3]]["class"] = flo[8]

def process_string(res):
	words 		= res.split(',')
	times 		= words[0].split('--')
	if 'src_ip' in words[1]:
		src_ip 		= words[1].split('--')
		dst_ip 		= words[2].split('--')
		src_port 	= words[3].split('--')
		dst_port 	= words[4].split('--')
		proto 		= words[5].split('--')
		batch 		= words[6].split('--')
	else:
		src_ip 		= words[2].split('--')
		dst_ip 		= words[3].split('--')
		src_port 	= words[4].split('--')
		dst_port 	= words[5].split('--')
		proto 		= words[6].split('--')
		batch 		= words[7].split('--')
	return times[1],src_ip[1],dst_ip[1],src_port[1],dst_port[1],proto[1],1,batch[1]

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
		f = open(testfile+str(i)+"."+str(i)+".txt")
		all_flows = f.read()
		all_flow = all_flows.split('\n')
		for flo in all_flow:
			if flo != '':
				my_flows = flo.split(',')
				map_test_data(my_flows)
	for i in range(len(results)):
		# print(res)
		if "0Received Packet-in in s1" in results[i] or "0 Received Packet-in in s1":
				results[i] = results[i].replace("Received Packet-in in s1", "")
		if "1Received Packet-in in s1" in results[i] or "1 Received Packet-in in s1":
				results[i] = results[i].replace("Received Packet-in in s1", "")
		if "2Received Packet-in in s1" in results[i] or "2 Received Packet-in in s1":
				results[i] = results[i].replace("Received Packet-in in s1", "")
		if "3Received Packet-in in s1" in results[i] or "3 Received Packet-in in s1":
				results[i] = results[i].replace("Received Packet-in in s1", "")
		if "4Received Packet-in in s1" in results[i] or "4 Received Packet-in in s1":
				results[i] = results[i].replace("Received Packet-in in s1", "")
		if "0Received Packet-in in s2" in results[i] or "0 Received Packet-in in s2":
				results[i] = results[i].replace("Received Packet-in in s2", "")
		if "1Received Packet-in in s2" in results[i] or "1 Received Packet-in in s2":
				results[i] = results[i].replace("Received Packet-in in s2", "")
		if "2Received Packet-in in s2" in results[i] or "2 Received Packet-in in s2":
				results[i] = results[i].replace("Received Packet-in in s2", "")
		if "3Received Packet-in in s2" in results[i] or "3 Received Packet-in in s2":
				results[i] = results[i].replace("Received Packet-in in s2", "")
		if "4Received Packet-in in s2" in results[i] or "4 Received Packet-in in s2":
				results[i] = results[i].replace("Received Packet-in in s2", "")
		if "0Received Packet-in in s3" in results[i] or "0 Received Packet-in in s3":
				results[i] = results[i].replace("Received Packet-in in s3", "")
		if "1Received Packet-in in s3" in results[i] or "1 Received Packet-in in s3":
				results[i] = results[i].replace("Received Packet-in in s3", "")
		if "2Received Packet-in in s3" in results[i] or "2 Received Packet-in in s3":
				results[i] = results[i].replace("Received Packet-in in s3", "")
		if "3Received Packet-in in s3" in results[i] or "3 Received Packet-in in s3":
				results[i] = results[i].replace("Received Packet-in in s3", "")
		if "4Received Packet-in in s3" in results[i] or "4 Received Packet-in in s3":
				results[i] = results[i].replace("Received Packet-in in s3", "")
		if "0Received Packet-in in s4" in results[i] or "0 Received Packet-in in s4":
				results[i] = results[i].replace("Received Packet-in in s4", "")
		if "1Received Packet-in in s4" in results[i] or "1 Received Packet-in in s4":
				results[i] = results[i].replace("Received Packet-in in s4", "")
		if "2Received Packet-in in s4" in results[i] or "2 Received Packet-in in s4":
				results[i] = results[i].replace("Received Packet-in in s4", "")
		if "3Received Packet-in in s4" in results[i] or "3 Received Packet-in in s4":
				results[i] = results[i].replace("Received Packet-in in s4", "")
		if "4Received Packet-in in s4" in results[i] or "4 Received Packet-in in s4":
				results[i] = results[i].replace("Received Packet-in in s4", "")
		if "0Received Packet-in in s5" in results[i] or "0 Received Packet-in in s5":
				results[i] = results[i].replace("Received Packet-in in s5", "")
		if "1Received Packet-in in s5" in results[i] or "1 Received Packet-in in s5":
				results[i] = results[i].replace("Received Packet-in in s5", "")
		if "2Received Packet-in in s5" in results[i] or "2 Received Packet-in in s5":
				results[i] = results[i].replace("Received Packet-in in s5", "")
		if "3Received Packet-in in s5" in results[i] or "3 Received Packet-in in s5":
				results[i] = results[i].replace("Received Packet-in in s5", "")
		if "4Received Packet-in in s5" in results[i] or "4 Received Packet-in in s5":
				results[i] = results[i].replace("Received Packet-in in s5", "")
		if "0Received Packet-in in s6" in results[i] or "0 Received Packet-in in s6":
				results[i] = results[i].replace("Received Packet-in in s6", "")
		if "1Received Packet-in in s6" in results[i] or "1 Received Packet-in in s6":
				results[i] = results[i].replace("Received Packet-in in s6", "")
		if "2Received Packet-in in s6" in results[i] or "2 Received Packet-in in s6":
				results[i] = results[i].replace("Received Packet-in in s6", "")
		if "3Received Packet-in in s6" in results[i] or "3 Received Packet-in in s6":
				results[i] = results[i].replace("Received Packet-in in s6", "")
		if "4Received Packet-in in s6" in results[i] or "4 Received Packet-in in s6":
				results[i] = results[i].replace("Received Packet-in in s6", "")
		if "0Received Packet-in in s7" in results[i] or "0 Received Packet-in in s7":
				results[i] = results[i].replace("Received Packet-in in s7", "")
		if "1Received Packet-in in s7" in results[i] or "1 Received Packet-in in s7":
				results[i] = results[i].replace("Received Packet-in in s7", "")
		if "2Received Packet-in in s7" in results[i] or "2 Received Packet-in in s7":
				results[i] = results[i].replace("Received Packet-in in s7", "")
		if "3Received Packet-in in s7" in results[i] or "3 Received Packet-in in s7":
				results[i] = results[i].replace("Received Packet-in in s7", "")
		if "4Received Packet-in in s7" in results[i] or "4 Received Packet-in in s7":
				results[i] = results[i].replace("Received Packet-in in s7", "")
		if "0Received Packet-in in s8" in results[i] or "0 Received Packet-in in s8":
				results[i] = results[i].replace("Received Packet-in in s8", "")
		if "1Received Packet-in in s8" in results[i] or "1 Received Packet-in in s8":
				results[i] = results[i].replace("Received Packet-in in s8", "")
		if "2Received Packet-in in s8" in results[i] or "2 Received Packet-in in s8":
				results[i] = results[i].replace("Received Packet-in in s8", "")
		if "3Received Packet-in in s8" in results[i] or "3 Received Packet-in in s8":
				results[i] = results[i].replace("Received Packet-in in s8", "")
		if "4Received Packet-in in s8" in results[i] or "4 Received Packet-in in s8":
				results[i] = results[i].replace("Received Packet-in in s8", "")
		if "0Received Packet-in in s9" in results[i] or "0 Received Packet-in in s9":
				results[i] = results[i].replace("Received Packet-in in s9", "")
		if "1Received Packet-in in s9" in results[i] or "1 Received Packet-in in s9":
				results[i] = results[i].replace("Received Packet-in in s9", "")
		if "2Received Packet-in in s9" in results[i] or "2 Received Packet-in in s9":
				results[i] = results[i].replace("Received Packet-in in s9", "")
		if "3Received Packet-in in s9" in results[i] or "3 Received Packet-in in s9":
				results[i] = results[i].replace("Received Packet-in in s9", "")
		if "4Received Packet-in in s9" in results[i] or "4 Received Packet-in in s9":
				results[i] = results[i].replace("Received Packet-in in s9", "")
		if "0Received Packet-in in s10" in results[i] or "0 Received Packet-in in s10":
				results[i] = results[i].replace("Received Packet-in in s10", "")
		if "1Received Packet-in in s10" in results[i] or "1 Received Packet-in in s10":
				results[i] = results[i].replace("Received Packet-in in s10", "")
		if "2Received Packet-in in s10" in results[i] or "2 Received Packet-in in s10":
				results[i] = results[i].replace("Received Packet-in in s10", "")
		if "3Received Packet-in in s10" in results[i] or "3 Received Packet-in in s10":
				results[i] = results[i].replace("Received Packet-in in s10", "")
		if "4Received Packet-in in s10" in results[i] or "4 Received Packet-in in s10":
				results[i] = results[i].replace("Received Packet-in in s10", "")
		if "0Received Packet-in in s11" in results[i] or "0 Received Packet-in in s11":
				results[i] = results[i].replace("Received Packet-in in s11", "")
		if "1Received Packet-in in s11" in results[i] or "1 Received Packet-in in s11":
				results[i] = results[i].replace("Received Packet-in in s11", "")
		if "2Received Packet-in in s11" in results[i] or "2 Received Packet-in in s11":
				results[i] = results[i].replace("Received Packet-in in s11", "")
		if "3Received Packet-in in s11" in results[i] or "3 Received Packet-in in s11":
				results[i] = results[i].replace("Received Packet-in in s11", "")
		if "4Received Packet-in in s11" in results[i] or "4 Received Packet-in in s11":
				results[i] = results[i].replace("Received Packet-in in s11", "")
		if "0Received Packet-in in s12" in results[i] or "0 Received Packet-in in s12":
				results[i] = results[i].replace("Received Packet-in in s12", "")
		if "1Received Packet-in in s12" in results[i] or "1 Received Packet-in in s12":
				results[i] = results[i].replace("Received Packet-in in s12", "")
		if "2Received Packet-in in s12" in results[i] or "2 Received Packet-in in s12":
				results[i] = results[i].replace("Received Packet-in in s12", "")
		if "3Received Packet-in in s12" in results[i] or "3 Received Packet-in in s12":
				results[i] = results[i].replace("Received Packet-in in s12", "")
		if "4Received Packet-in in s12" in results[i] or "4 Received Packet-in in s12":
				results[i] = results[i].replace("Received Packet-in in s12", "")
		if "0Received Packet-in in s13" in results[i] or "0 Received Packet-in in s13":
				results[i] = results[i].replace("Received Packet-in in s13", "")
		if "1Received Packet-in in s13" in results[i] or "1 Received Packet-in in s13":
				results[i] = results[i].replace("Received Packet-in in s13", "")
		if "2Received Packet-in in s13" in results[i] or "2 Received Packet-in in s13":
				results[i] = results[i].replace("Received Packet-in in s13", "")
		if "3Received Packet-in in s13" in results[i] or "3 Received Packet-in in s13":
				results[i] = results[i].replace("Received Packet-in in s13", "")
		if "4Received Packet-in in s13" in results[i] or "4 Received Packet-in in s13":
				results[i] = results[i].replace("Received Packet-in in s13", "")
		if "0Received Packet-in in s14" in results[i] or "0 Received Packet-in in s14":
				results[i] = results[i].replace("Received Packet-in in s14", "")
		if "1Received Packet-in in s14" in results[i] or "1 Received Packet-in in s14":
				results[i] = results[i].replace("Received Packet-in in s14", "")
		if "2Received Packet-in in s14" in results[i] or "2 Received Packet-in in s14":
				results[i] = results[i].replace("Received Packet-in in s14", "")
		if "3Received Packet-in in s14" in results[i] or "3 Received Packet-in in s14":
				results[i] = results[i].replace("Received Packet-in in s14", "")
		if "4Received Packet-in in s14" in results[i] or "4 Received Packet-in in s14":
				results[i] = results[i].replace("Received Packet-in in s14", "")
		if "0Received Packet-in in s15" in results[i] or "0 Received Packet-in in s15":
				results[i] = results[i].replace("Received Packet-in in s15", "")
		if "1Received Packet-in in s15" in results[i] or "1 Received Packet-in in s15":
				results[i] = results[i].replace("Received Packet-in in s15", "")
		if "2Received Packet-in in s15" in results[i] or "2 Received Packet-in in s15":
				results[i] = results[i].replace("Received Packet-in in s15", "")
		if "3Received Packet-in in s15" in results[i] or "3 Received Packet-in in s15":
				results[i] = results[i].replace("Received Packet-in in s15", "")
		if "4Received Packet-in in s15" in results[i] or "4 Received Packet-in in s15":
				results[i] = results[i].replace("Received Packet-in in s15", "")
		if "0Received Packet-in in s16" in results[i] or "0 Received Packet-in in s16":
				results[i] = results[i].replace("Received Packet-in in s16", "")
		if "1Received Packet-in in s16" in results[i] or "1 Received Packet-in in s16":
				results[i] = results[i].replace("Received Packet-in in s16", "")
		if "2Received Packet-in in s16" in results[i] or "2 Received Packet-in in s16":
				results[i] = results[i].replace("Received Packet-in in s16", "")
		if "3Received Packet-in in s16" in results[i] or "3 Received Packet-in in s16":
				results[i] = results[i].replace("Received Packet-in in s16", "")
		if "4Received Packet-in in s16" in results[i] or "4 Received Packet-in in s16":
				results[i] = results[i].replace("Received Packet-in in s16", "")
		t,si,di,sp,dp,p,c,b = process_string(results[i])
		acc = check_accuracy(si, di, sp, dp, p, c)
		if acc:
			accuracy[b] = accuracy[b] + 1
	# print(accuracy)
	if os.path.exists(outputfile):
		f = open(outputfile, "a")
		for i in range(1, 51):
			f.write(str(i) + ":" + str(accuracy(i)))
		f.close()
	else:
		f = open(outputfile, "w")
		for i in range(1, 51):
			f.write(str(i) + ":" + str(accuracy(i)))
		f.close()

if __name__ == '__main__':
	main()

# time--1 day, 23:47:53.251293, src_ip--10.0.4.4, dst_ip--10.0.7.7, src_port--31978, dst_port--17447, proto--6, batch--1