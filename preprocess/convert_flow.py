import numpy as np
import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()

# Add argument
parser.add_argument('-i', required=True, help='path to dataset')
parser.add_argument('-o', required=True, help='output path')

args = parser.parse_args()

# extract argument value
inputfile = args.i
outputfile = args.o

columns = ['src_ip','dst_ip','tcp_sport','tcp_dport','udp_sport','udp_dport','proto','size','count','int_arr_time','start_time','last_time','class']

all_flows = pd.read_csv(inputfile)

for i in range(0,all_flows.shape[0]-1):
	if all_flows.at[i,"proto"] == 6:
		# all_flows.at[i,"size"] = all_flows.at[i,"size"]/1024
		dataframe = pd.DataFrame({'src_ip':[all_flows.at[i,"src_ip"]],'dst_ip':[all_flows.at[i,"dst_ip"]],'tcp_sport':[all_flows.at[i,"src_port"]],'tcp_dport':[all_flows.at[i,"dst_port"]],'udp_sport':0,'udp_dport':0,'proto':[all_flows.at[i,"proto"]],'size':[all_flows.at[i,"size"]],'count':[all_flows.at[i,"count"]],'int_arr_time':[all_flows.at[i,"iat"]],'start_time':0,'last_time':0,'class':[all_flows.at[i,"class"]]})
		columns = ['src_ip','dst_ip','tcp_sport','tcp_dport','udp_sport','udp_dport','proto','size','count','int_arr_time','start_time','last_time','class']
		if os.path.exists(outputfile):
			dataframe.to_csv(outputfile,index=False,sep=',',mode='a',columns = columns, header=False)
		else:
			dataframe.to_csv(outputfile,index=False,sep=',',columns = columns)
	elif all_flows.at[i,"proto"] == 17:
		# all_flows.at[i,"size"] = all_flows.at[i,"size"]/1024
		dataframe = pd.DataFrame({'src_ip':[all_flows.at[i,"src_ip"]],'dst_ip':[all_flows.at[i,"dst_ip"]],'tcp_sport':0,'tcp_dport':0,'udp_sport':[all_flows.at[i,"src_port"]],'udp_dport':[all_flows.at[i,"dst_port"]],'proto':[all_flows.at[i,"proto"]],'size':[all_flows.at[i,"size"]],'count':[all_flows.at[i,"count"]],'int_arr_time':[all_flows.at[i,"iat"]],'start_time':0,'last_time':0,'class':[all_flows.at[i,"class"]]})
		columns = ['src_ip','dst_ip','tcp_sport','tcp_dport','udp_sport','udp_dport','proto','size','count','int_arr_time','start_time','last_time','class']
		if os.path.exists(outputfile):
			dataframe.to_csv(outputfile,index=False,sep=',',mode='a',columns = columns, header=False)
		else:
			dataframe.to_csv(outputfile,index=False,sep=',',columns = columns)