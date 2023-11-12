import numpy as np
import pandas as pd
import argparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import export_graphviz
import pydot

parser = argparse.ArgumentParser()

# Add argument
parser.add_argument('-i', required=True, help='path to dataset')
# parser.add_argument('-o', required=True, help='path to outputfile')
parser.add_argument('-t', required=True, help='path to testfile')
args = parser.parse_args()

# extract argument
input = args.i
# outputfile = args.o
testfile = args.t

# Training set X and Y
Set1 = pd.read_csv(input)
Set = Set1.values.tolist()
X = [i[2:10] for i in Set]
Y = [i[12] for i in Set]

# Test set Xt and Yt
Set2 = pd.read_csv(input)
Sett = Set2.values.tolist()
Xt = [i[2:10] for i in Set]
Yt = [i[12] for i in Set]

class_names = ['0','1','2','3','4']
feature_names = ['tcp_sport','tcp_dport','udp_sport','udp_dport','proto','size','count','int_arr_time']

# prepare training and testing set
X = np.array(X)
Y = np.array(Y)
Xt = np.array(Xt)
Yt = np.array(Yt)

# decision tree fit
rf = RandomForestClassifier(n_estimators = 2)
rf.fit(X, Y)
Predict_Y = rf.predict(X)
print(accuracy_score(Y, Predict_Y))

Predict_Yt = rf.predict(Xt)

e2e = 0
e2m = 0
m2e = 0
m2m = 0

for i in range(Predict_Yt.shape[0]):
	if Yt[i] == Predict_Yt[i] and Yt[i] == 1:
		e2e = e2e + 1
	elif Yt[i] == Predict_Yt[i] and Yt[i] == 0:
		m2m = m2m + 1
	elif Yt[i] != Predict_Yt[i] and Yt[i] == 0 and Predict_Yt[i] == 1:
		m2e = m2e + 1
	elif Yt[i] != Predict_Yt[i] and Yt[i] == 1 and Predict_Yt[i] == 0:
		e2m = e2m + 1

print("e2e: " + str(e2e) + " m2m: " + str(m2m) + " m2e: " + str(m2e) + " e2m: " + str(e2m))
j=0
for i in rf.estimators_:
	export_graphviz(i,
					out_file='tree'+str(j)+'.dot',
					feature_names = feature_names,
					class_names = class_names,
					rounded = True,
					proportion = False,
                	precision = 2,
					filled = True)
	j = j + 1

# (graph,) = pydot.graph_from_dot_file('tree0.dot')
# graph.write_png('tree0.png')

# from subprocess import call
# call(['dot', '-Tpng', 'tree0.dot', '-o', 'tree0.png', '-Gdpi=600'])
# # from subprocess import call
# call(['dot', '-Tpng', 'tree1.dot', '-o', 'tree1.png', '-Gdpi=600'])