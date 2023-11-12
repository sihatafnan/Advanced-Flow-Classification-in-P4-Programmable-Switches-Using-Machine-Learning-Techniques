import pandas as pd
import argparse
import os
import itertools

parser = argparse.ArgumentParser(description='divide test flows into batches')

parser.add_argument('-i', help='input file path', required=True)
# parser.add_argument('-o', help='output pattern', required=True)

args = parser.parse_args()

# extract argument value
inputfile = args.i
# outputfile = args.o

def print_batches(outputfile, flows, batch):
	for i in flows:
		dataframe = pd.DataFrame({'src_ip':[i[0]],'dst_ip':[i[1]],'src_port':[i[2]],'dst_port':[i[3]],'proto':[i[4]],'size':[i[5]],'count':[i[6]],'iat':[i[7]],'class':[i[8]],'batch':batch})
		columns = ['src_ip','dst_ip','src_port','dst_port','proto','size','count','iat','class','batch']
		if os.path.exists(outputfile):
			dataframe.to_csv(outputfile,index=False,sep=',',mode='a',columns = columns, header=False)
		else:
			dataframe.to_csv(outputfile,index=False,sep=',',columns = columns)

def main():
	class_flows = pd.read_csv(inputfile)

	len_list = list(itertools.repeat(400, 50))

	flows_list = class_flows.values.tolist()

	flows_list_iter = iter(flows_list)
	split_list = [list(itertools.islice(flows_list_iter, l)) for l in len_list]
	output_file = "data/test/mod_final_test_batches.csv" 
	batch_list = range(1,51) 
	for i in range(len(split_list)):
		print_batches(output_file, split_list[i], batch_list[i])

if __name__ == '__main__':
	main()
