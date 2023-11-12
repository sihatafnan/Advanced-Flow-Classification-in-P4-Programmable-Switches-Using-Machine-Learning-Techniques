import os
import argparse
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description='traffic distribution')
parser.add_argument('--num-hosts', help='Number of hosts', type=int, action="store", default=2)
parser.add_argument('--num-flows', help='Number of flows', type=int, action="store", default=2)
parser.add_argument('--o', help='output file path', required=True)

args = parser.parse_args()

class Traffic_simulator():
	def __init__(self):
		self.size_threshold = [1000, 10240, 10485760, 104857600, 1073741824, 10737418240]
		self.iat_threshold = [7, 2, 0.1, 0.03, 0.001, 0.0001]
		self.no_size1 = 0
		self.no_size2 = 0
		self.no_size3 = 0
		self.no_size4 = 0
		self.no_size5 = 0
		self.size1_flow = []
		self.size2_flow = []
		self.size3_flow = [] 
		self.size4_flow = []
		self.size5_flow = []
		self.size1_threshold = 0
		self.size2_threshold = 0
		self.size3_threshold = 0
		self.size4_threshold = 0
		self.size5_threshold = 0
		# super().__init__(self)

	def generate_flow(self, flows, hosts, ip_list, port_list, proto_list):
		flow_count = 0
		while flow_count < flows:
			# print(flow_count)
			first_ip_list = ip_list[:hosts/2]
			second_ip_list = ip_list[hosts/2:]
			# print(flow_count)
			# print("===")
			while len(first_ip_list) != 0:
				sender_ip_index = int(np.random.uniform(0, len(first_ip_list), 1)[0])
				receiver_ip_index = int(np.random.uniform(0, len(second_ip_list), 1)[0])
				sender_port_index = int(np.random.uniform(0, len(port_list), 1)[0])
				receiver_port_index = int(np.random.uniform(0, len(port_list), 1)[0])
				proto_index = int(np.random.uniform(0, len(proto_list), 1)[0])
				
				flow1 = Flow(first_ip_list[sender_ip_index], 
							second_ip_list[receiver_ip_index], 
							port_list[sender_port_index],
							port_list[receiver_port_index],
							proto_list[proto_index])

				flow2 = Flow(second_ip_list[receiver_ip_index], 
							first_ip_list[sender_ip_index], 
							port_list[receiver_port_index],
							port_list[sender_port_index],
							proto_list[proto_index])

				first_ip_list.pop(sender_ip_index)
				second_ip_list.pop(receiver_ip_index)

				size_dist = self.get_size_distr("basic")
				self.set_size_threshold(size_dist, flows)

				self.set_list(flow1, size_dist)
				flow_count = flow_count + 1
				if flow_count >= flows:
					break
				# print(flow_count)
				# print("=============================")
				self.set_list(flow2, size_dist)
				flow_count = flow_count + 1
				if flow_count >= flows:
					break
				# print(flow_count)
				# print("=============================")

	def set_size_threshold(self, size_distr, no_flow):
		self.size1_threshold = size_distr[0]*no_flow
		self.size2_threshold = size_distr[1]*no_flow
		self.size3_threshold = size_distr[2]*no_flow
		self.size4_threshold = size_distr[3]*no_flow
		self.size5_threshold = size_distr[4]*no_flow

	def get_size_distr(self, distr_type):
		if distr_type == "basic":
			size_distr = [0.75, 0.12, 0.1, 0.02, 0.01]
		return size_distr
	
	def get_size_type(self, distr):
		if self.no_size1 < self.size1_threshold:
			size_type = 0
		elif self.no_size2 < self.size2_threshold:
			size_type = 1
		elif self.no_size3 < self.size3_threshold:
			size_type = 2
		elif self.no_size4 < self.size4_threshold:
			size_type = 3
		else:
			size_type = 4
		return size_type

	def get_size_type1(self, distr):
		size_type = -1
		base = 0
		ceil = 1
		size1_flag = False
		size2_flag = False
		size3_flag = False
		size4_flag = False
		size5_flag = False
		dist = []
		for i in range(len(distr)):
			dist.append(0)
			for j in reversed(range(i+1)):
				dist[i] = dist[i] + distr[j]
		# print(dist[i]) 
		# print("==========")
		while True:
			prob = np.random.uniform(base, ceil,1)[0]
			if prob <= dist[0]:
				size_type = 0
			elif prob > dist[0] and prob <= dist[1]:
				size_type = 1
			elif prob > dist[1] and prob <= dist[2]:
				size_type = 2
			elif prob > dist[2] and prob <= dist[3]:
				size_type = 3
			else:
				size_type = 4
			# print(prob)
			# print(size_type)
			# print(self.no_size1)
			# print(self.no_size2)
			# print(self.no_size3)
			# print(self.no_size4)
			# print(self.no_size5)
			# print("===========")
			if self.no_size1 >= self.size1_threshold and size1_flag == False:
				size1_flag = True
				base = base + distr[0]
			
			if self.no_size2 >= self.size2_threshold and size2_flag == False:
				size2_flag = True
				base = base + distr[1]

			if self.no_size3 >= self.size3_threshold and size3_flag == False:
				size3_flag = True
				base = base + distr[2]

			if self.no_size4 >= self.size4_threshold and size4_flag == False:
				size4_flag = True
				base = base + distr[3]

			if self.no_size5 >= self.size5_threshold and size5_flag == False:
				size5_flag = True
				base = base + distr[4]
				ceil = ceil - distr[4]

			if size_type == 0 and  self.no_size1 < self.size1_threshold:
				break
			elif size_type == 1 and self.no_size2 < self.size2_threshold:
				break
			elif size_type == 2 and self.no_size3 < self.size3_threshold:
				break
			elif size_type == 3 and self.no_size4 < self.size4_threshold:
				break
			elif size_type == 4 and self.no_size5 < self.size5_threshold:
				break
			else:
				continue

		return size_type

	def get_props(self, size_type):
		flow_size = int(np.random.uniform(self.size_threshold[size_type], self.size_threshold[size_type+1], 1)[0])
		flow_iat = int(np.random.uniform(self.iat_threshold[size_type], self.iat_threshold[size_type+1], 1)[0])
		packet_count = flow_size/1400
		if packet_count < 10:
			flow_count = int(np.random.uniform(packet_count, 10, 1)[0])
		else:
			flow_count = int(np.random.uniform(packet_count - 100, packet_count + 100, 1)[0])
		return [flow_size, flow_iat, flow_count, size_type]

	def set_list(self, flow, size_dist):
		
		size_type = self.get_size_type(size_dist)
		
		size, iat, count, label = self.get_props(size_type)
		flow.set_flow_prop(size_type, size, count, iat, label)
		
		if size_type == 0:
			self.size1_flow.append(flow.get_flow_prop())
			self.no_size1 = self.no_size1 + 1
		elif size_type == 1:
			self.size2_flow.append(flow.get_flow_prop())
			self.no_size2 = self.no_size2 + 1
		elif size_type == 2:
			self.size3_flow.append(flow.get_flow_prop())
			self.no_size3 = self.no_size3 + 1
		elif size_type == 3:
			self.size4_flow.append(flow.get_flow_prop())
			self.no_size4 = self.no_size4 + 1
		else:
			self.size5_flow.append(flow.get_flow_prop())
			self.no_size5 = self.no_size5 + 1

	def print_flows(self, columns, outputfile):
		# print(len(self.size1_flow))
		# print(len(self.size2_flow))
		# print(len(self.size3_flow))
		# print(len(self.size4_flow))
		# print(len(self.size5_flow))

		result = self.size1_flow + self.size2_flow + self.size3_flow + self.size4_flow + self.size5_flow
		for i in result:
			dataframe = pd.DataFrame({'src_ip':[i[0]], 'dst_ip':[i[1]], 'src_port':[i[2]], 'dst_port':[i[3]], 'proto':[i[4]], 'size':[i[5]], 'count':[i[6]], 'iat':[i[7]], 'class':[i[8]]})
			# save the dataframe to the csv file, if not exsit, create one.
			if os.path.exists(outputfile):
				dataframe.to_csv(outputfile,index=False,sep=',',mode='a',columns = columns, header=False)
			else:
				dataframe.to_csv(outputfile,index=False,sep=',',columns = columns)


class Flow():
	def __init__(self, src_ip_addr, dst_ip_addr, src_port_addr, dst_port_addr, proto):
		self.src_ip = src_ip_addr
		self.dst_ip = dst_ip_addr
		self.src_port = src_port_addr
		self.dst_port = dst_port_addr
		self.protocol = proto
		self.size_type = 0
		self.size = 0
		self.count = 0
		self.iat = 0
		self.label = 0
		# super().__init__(self)

	def set_flow_prop(self, s_type, size, count, iat, label):
		self.size_type = s_type
		self.size = size
		self.count = count
		self.iat = iat
		self.label = label
	
	def get_flow_prop(self):
		return [self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol, self.size, self.count, self.iat, self.label]


def main():
	hosts = args.num_hosts
	flows = args.num_flows
	output_file = args.o

	# print(hosts)
	# print(flows)
	# print(output_file)
	# print("============================")

	ip_list = []
	proto_list = [6, 17]
	port_list = [23, 69, 80, 443]
	tuple_list = []
	
	columns = ['src_ip', 'dst_ip', 'src_port', 'dst_port', 'proto', 'size', 'count', 'iat', 'class']

	addr1 = 1
	addr2 = 0

	for i in range(hosts):
		if addr2 == 2:
			addr1 = addr1 + 1
			addr2 = 0
		ip_list.append("10.0.%d.%d" % (addr1,addr2+1))
		addr2 = addr2 + 1

	for i in range(10000,60000):
		port_list.append(i)

	traff = Traffic_simulator()
	traff.generate_flow(flows, hosts, ip_list, port_list, proto_list)
	traff.print_flows(columns, output_file)


if __name__ == '__main__':
	main()