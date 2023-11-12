import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser(description='host flow')

parser.add_argument('-i', help='input file path', required=True)
parser.add_argument('-op', help='output file path pattern', required=True)

args = parser.parse_args()

def return_mac(dst_ip, mac_list):
	if "10.0.1.1" in dst_ip:
		return mac_list[0]
	elif "10.0.2.2" in dst_ip:
		return mac_list[1]
	elif "10.0.3.3" in dst_ip:
		return mac_list[2]
	elif "10.0.4.4" in dst_ip:
		return mac_list[3]
	elif "10.0.5.5" in dst_ip:
		return mac_list[4]
	elif "10.0.6.6" in dst_ip:
		return mac_list[5]
	elif "10.0.7.7" in dst_ip:
		return mac_list[6]
	elif "10.0.8.8" in dst_ip:
		return mac_list[7]

def make_flow_file(flows, src_ip, output_pattern, mac_list):
	for flow in flows:
		if src_ip == flow[0]:
			output_file = output_pattern+src_ip+".txt"
			if os.path.exists(output_file):
				f = open(output_file, "a")
				f.write(flow[0]+","+flow[1]+","+str(flow[2])+","+str(flow[3])+","+str(flow[4])+","+str(flow[5])+","+str(flow[6])+","+str(flow[7])+","+str(flow[8])+","+return_mac(flow[1], mac_list)+","+str(flow[9])+"\n")
				f.close()
			else:
				f = open(output_file, "w")
				f.write(flow[0]+","+flow[1]+","+str(flow[2])+","+str(flow[3])+","+str(flow[4])+","+str(flow[5])+","+str(flow[6])+","+str(flow[7])+","+str(flow[8])+","+return_mac(flow[1], mac_list)+","+str(flow[9])+"\n")
				f.close()

def main():
	input_file = args.i
	output_pattern = args.op
	all_flows = pd.read_csv(input_file)
	result = []
	flows_np = all_flows.to_numpy()
        ip_addrs = ["10.0.1.1", "10.0.2.2", "10.0.3.3", "10.0.4.4", "10.0.5.5", "10.0.6.6", "10.0.7.7", "10.0.8.8"]
        mac_addrs = ["00:00:00:00:01:01", "00:00:00:00:02:02", "00:00:00:00:03:03", 
		     "00:00:00:00:04:04", "00:00:00:00:05:05", "00:00:00:00:06:06",
		     "00:00:00:00:07:07", "00:00:00:00:08:08"]
	print(flows_np[0])
	for flow in flows_np:
		if len(result) == 0:
			result.append(flow[0])
		else:
			if flow[0] in result:
				continue
			else :
				result.append(flow[0])
	print(len(result))
	for r in result:
		make_flow_file(flows_np, r, output_pattern, mac_addrs)

if __name__ == '__main__':
	main()
