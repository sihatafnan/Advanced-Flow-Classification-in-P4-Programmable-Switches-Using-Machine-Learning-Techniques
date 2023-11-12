import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser(description='host flow')

parser.add_argument('-i', help='input file path', required=True)
parser.add_argument('-o', help='output file path', required=True)

args = parser.parse_args()

# extract argument value
inputfile = args.i
outputfile = args.o

# columns = ['src_ip','dst_ip','tcp_sport','tcp_dport','udp_sport','udp_dport','proto','size','count','int_arr_time','start_time','last_time','class']

all_flows = pd.read_csv(inputfile)
print(all_flows.shape[0])
for i in range(0,all_flows.shape[0]-1):
	if all_flows.at[i,"proto"] == 6:
		# all_flows.at[i,"size"] = all_flows.at[i,"size"]/1024
		dataframe = pd.DataFrame({'src_ip':[all_flows.at[i,"src_ip"]],'dst_ip':[all_flows.at[i,"dst_ip"]],'src_port':[all_flows.at[i,"tcp_sport"]],'dst_port':[all_flows.at[i,"tcp_dport"]],'proto':[all_flows.at[i,"proto"]],'size':[all_flows.at[i,"size"]],'count':[all_flows.at[i,"count"]],'int_arr_time':[all_flows.at[i,"int_arr_time"]],'class':[all_flows.at[i,"class"]]})
		columns = ['src_ip','dst_ip','src_port','dst_port','proto','size','count','int_arr_time','class']
		if os.path.exists(outputfile):
			dataframe.to_csv(outputfile,index=False,sep=',',mode='a',columns = columns, header=False)
		else:
			dataframe.to_csv(outputfile,index=False,sep=',',columns = columns)
	elif all_flows.at[i,"proto"] == 17:
		# all_flows.at[i,"size"] = all_flows.at[i,"size"]/1024
		dataframe = pd.DataFrame({'src_ip':[all_flows.at[i,"src_ip"]],'dst_ip':[all_flows.at[i,"dst_ip"]],'src_port':[all_flows.at[i,"udp_sport"]],'dst_port':[all_flows.at[i,"udp_dport"]],'proto':[all_flows.at[i,"proto"]],'size':[all_flows.at[i,"size"]],'count':[all_flows.at[i,"count"]],'int_arr_time':[all_flows.at[i,"int_arr_time"]],'class':[all_flows.at[i,"class"]]})
		columns = ['src_ip','dst_ip','src_port','dst_port','proto','size','count','int_arr_time','class']
		if os.path.exists(outputfile):
			dataframe.to_csv(outputfile,index=False,sep=',',mode='a',columns = columns, header=False)
		else:
			dataframe.to_csv(outputfile,index=False,sep=',',columns = columns)
