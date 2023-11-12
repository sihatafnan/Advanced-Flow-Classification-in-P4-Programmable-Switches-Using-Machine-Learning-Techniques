import numpy as np
import pandas as pd
import argparse
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import export_graphviz
import pydotplus

def get_lineage(tree, feature_names, file):
    proto = []
    src = []
    dst = []
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value
    le = '<='
    g = '>'
    # get ids of child nodes
    idx = np.argwhere(left == -1)[:, 0]
    
    # traverse the tree and get the node information
    def recurse(left, right, child, lineage=None):
        if lineage is None:
            lineage = [child]
        if child in left:
            parent = np.where(left == child)[0].item()
            split = 'l'
        else:
            parent = np.where(right == child)[0].item()
            split = 'r'
        
        lineage.append((parent, split, threshold[parent], features[parent]))
        if parent == 0:
            lineage.reverse()
            return lineage
        else:
            return recurse(left, right, parent, lineage)

    for j, child in enumerate(idx):
        clause = ' when '
        for node in recurse(left, right, child):
                if len(str(node)) < 3:
                    continue
                i = node
                
                if i[1] == 'l':
                    sign = le
                else:
                    sign = g
                clause = clause + i[3] + sign + str(i[2]) + ' and '
    
    # wirte the node information into text file
        a = list(value[node][0])
        ind = a.index(max(a))
        clause = clause[:-4] + ' then ' + str(ind)
        file.write(clause)
        file.write(";\n")

def dt_train(X,Y, feature_names):
    # prepare training and testing set
    X = np.array(X)
    Y = np.array(Y)
    print(X[0])
    # decision tree fit
    dt = DecisionTreeClassifier(max_depth = 5)
    dt.fit(X, Y)
    Predict_Y = dt.predict(X)

    threshold = dt.tree_.threshold
    features  = [feature_names[i] for i in dt.tree_.feature]

    # output the tree in a text file, write it
    proto        = []
    tcp_sp       = []
    tcp_dp       = []
    size         = []
    count        = []
    int_arr_time = []

    for i, fe in enumerate(features):
        if fe == 'proto':
            if threshold[i] != -2.0:
                proto.append(threshold[i])
        elif fe == 'tcp_sport':
            if threshold[i] != -2.0:
                tcp_sp.append(threshold[i])
        elif fe == 'tcp_dport':
            if threshold[i] != -2.0:
                tcp_dp.append(threshold[i])
        elif fe == 'udp_sport':
            if threshold[i] != -2.0:
                udp_sp.append(threshold[i])
        elif fe == 'udp_dport':
            if threshold[i] != -2.0:
                udp_dp.append(threshold[i])
        elif fe == 'size':
            if threshold[i] != -2.0:
                size.append(threshold[i])
        elif fe == 'count':
            if threshold[i] != -2.0:
                count.append(threshold[i])
        else:
            if threshold[i] != -2.0:
                int_arr_time.append(threshold[i])

    tree = open(outputfile,"w+")

    if len(proto) != 0:
        proto = [int(i) for i in proto]
        proto.sort()
        tree.write("proto = ")
        tree.write(str(proto))
        tree.write(";\n")

    if len(tcp_sp) != 0:
        tcp_sp = [int(i) for i in tcp_sp]
        tcp_sp.sort()
        tree.write("tcp_sp = ")
        tree.write(str(tcp_sp))
        tree.write(";\n")

    if len(tcp_dp) != 0:
        tcp_dp = [int(i) for i in tcp_dp]
        tcp_dp.sort()
        tree.write("tcp_dp = ")
        tree.write(str(tcp_dp))
        tree.write(";\n")

    if len(udp_sp) != 0:
        udp_sp = [int(i) for i in udp_sp]
        udp_sp.sort()
        tree.write("udp_sp = ")
        tree.write(str(udp_sp))
        tree.write(";\n")

    if len(udp_dp) != 0:
        udp_dp = [int(i) for i in udp_dp]
        udp_dp.sort()
        tree.write("udp_dp = ")
        tree.write(str(udp_dp))
        tree.write(";\n")

    if len(size) != 0:
        size = [int(i) for i in size]
        size.sort()
        tree.write("size = ")
        tree.write(str(size))
        tree.write(";\n")

    if len(count) != 0:
        count = [int(i) for i in count]
        count.sort()
        tree.write("count = ")
        tree.write(str(count))
        tree.write(";\n")

    if len(int_arr_time) != 0:
        int_arr_time = [int(i) for i in int_arr_time]
        int_arr_time.sort()
        tree.write("int_arr_time = ")
        tree.write(str(int_arr_time))
        tree.write(";\n")

    get_lineage(dt, feature_names, tree)
    tree.close()

def main():
    parser = argparse.ArgumentParser()

    # Add argument
    parser.add_argument('-i', required=True, help='path to dataset')
    parser.add_argument('-o', required=True, help='path to outputfile')
    args = parser.parse_args()

    # extract argument
    input = args.i
    outputfile = args.o

    # Training set X and Y
    Set1 = pd.read_csv(input)
    Set = Set1.values.tolist()
    X = [i[2:7] for i in Set]
    Y = [i[8] for i in Set]

    class_names = ['label_0','label_1','label_2','label_3','label_4']
    feature_names = ['src_port','dst_port','proto','size','count','int_arr_time']

if __name__ == '__main__':
    main()