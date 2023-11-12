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

def make_flow_file(flows):
	print(flows[0])
	f = open(outputfile, "w")
	f.write(',\n'.join('"{}"'.format(item) for item in flows))
	f.close()

def main():

	all_flows = pd.read_csv(inputfile)
	flows_np = all_flows.to_numpy()
	print(inputfile)
	flow_list = []
	counter = 0
	for flow in flows_np:
		if counter % 8000 == 0:
			flow_list.append('\n')
		flow_str = str(flow[2]) + "," + str(flow[3]) + "," + str(flow[4]) + "," + str(flow[5]) + "," + str(flow[6]) + "," + str(flow[7]) + "," + str(flow[8])
		flow_list.append(flow_str)
		counter = counter + 1
	make_flow_file(flow_list)

if __name__ == '__main__':
	main()
