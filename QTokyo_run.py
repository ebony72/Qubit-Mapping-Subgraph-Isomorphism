# Created on June 10, 2019 by Sanjiang Li || mrlisj@gmail.com
#@2020-04-15: output way added
#@2020-04-19: Types of Filters are introduced to facilitate selection of different filters 
#@2020-04-19: Intorduced SIZE (bool)
#@2020-09-14: Introduced SPL and a new filter R_hat

#\__/#\#/\#\__/#\#/\__/--\__/#\__/#\#/~\
#import numpy as np
import networkx as nx
from ag import q20 # architecture graph
from inimap import _tau_bsg_, _tau_bstg_ # two initial mappings
from QTokyo_f import * 
import json
import os
import time

#\__/#\#/\#\__/#\#/\__/--\__/#\__/#\#/~\
def save_result(name, content):
    name = str(name)
    content = str(content)
    file = open("testRecord/qct-" + "2020-09-14-" + name + ".txt", mode = 'a')
    file.write(content)
    file.write('\n')
    file.close()
#\__/#\#/\#\__/#\#/\__/--\__/#\__/#\#/~\
#select QFilter_type, SIZE, and initial_mapping
#Filter type
QFilter_type = '0' # select type from {'0', '1', '12', '12x', '2x'}
#initial mapping
initial_mapping = 'topgraph' #select mapping from {'topgraph', 'wgtgraph', 'empty', 'naive'}
#size of circuits
SIZE = 'medium' #select size from {'small', 'medium', 'large', 'all'}

def qubit_in_circuit(D): # the set of logic qubits appeared in D, a subset of C
    ''' Return the set of qubits in a circuit D
        Args:
            D (list): a sublist of CNOT gates of the input circuit C
        Returns:
            Q (set): the set of qubits in D
    '''
    Q = set()
    for gate in D:
        Q.add(gate[0])
        Q.add(gate[1])
    return Q
#\__/#\#/\#\__/#\#/\__/--\__/#\__/#\#/~\
# The architecture graph
G = q20()
#G = nx.Graph.to_undirected(H)
EG = nx.edges(G)

'''Generate the shortest_path_length dict for Q20 '''
def SPLQ20():
    G = q20()
    spl_dic = dict() 
    V = list(range(20))
    for p in V:
        for q in V:
            if (q,p) in spl_dic:
                d = spl_dic[(q,p)]
            else:
                d = nx.shortest_path_length(G,p,q)
            spl_dic[(p,q)] = d
    return spl_dic

SPL = SPLQ20()
#\__/#\#/\#\__/#\#/\__/--\__/#\__/#\#/~\
# The benchmark circuits

path = "CNOT_lists2/" 
files= os.listdir(path) 

#Filter types (following the terminologies in the paper)
A0 = '0 :: if no filter is used,\n'
A1 = '1 :: if Q0 is used for all layers,\n'
A12 = '12 :: if Q0 is used for the first layer and Q1 is used for the other layers,\n'
A12x = '12x :: if Q0 is used for the first layer and Q0+Q1 is used for the other layers,\n'
A2x = '2x :: if Q0+Q1 is used for all layers '


name = 'Q' + QFilter_type
content = '*****************************************'
save_result(name, content)
content = 'QFilter types (string):\n' + A0 + A1 + A12 + A12x + A2x 
save_result(name, content)

content = 'In this test, we use Type %s filter and %s initial mapping for %s circuits' %(QFilter_type, initial_mapping, SIZE)
print(content)
save_result(name, content)
content = '*****************************************'
save_result(name, content)

content = time.asctime()
print(content)
save_result(name, content)

count = 0
sum_in = 0
sum_out = 0
COST_TIME = 0
for file_name in files:
    count += 1
    current_path = 'CNOT_lists2/' + file_name
    #print('This is the %dth circuit'%count)
    with open(current_path, 'r') as f: 
        sqn = json.loads(f.read())
    C = sqn
    l = len(C)
    if SIZE == 'small':
        if l >= 100:
            continue
    if SIZE == 'medium':
        if l>1000 or l<100:
            continue
    if SIZE == 'large':
        if l <= 1000:
            continue
        
    #if count != 53:
        #continue
        
    nl = len(qubit_in_circuit(C))
    #print('The input circuit contains %s gates and %s qubits' %(l,nl))
            
    ##################################################################
    ### We compare four different initial mappings
    
    if initial_mapping == 'wgtgraph': # weighted graph initial mapping
        tau = _tau_bsg_(C,G)
    elif initial_mapping == 'empty': #empty mapping
        tau = [20]*20
    elif initial_mapping == 'topgraph': # topsubgraph mapping
        tau = _tau_bstg_(C,G,nl)
    elif initialmapping == 'naive': #naive mapping
        tau = [20]*20
        for i in range(nl):
            tau[i] = i
    else: 
        pass
    ##################################################################

    sum_in += l
    
    C_out, cost_time = qct(C,G,EG,tau,QFilter_type,SPL)
    COST_TIME += cost_time
    sum_out += len(C_out)
    
    content = count, file_name, nl, l, len(C_out), len(C_out)-l, round(cost_time,2), round(len(C_out)/l, 4)
    print(content)
    save_result(name, content)

content = 'The average ratio is %s : %s = %s ' %(sum_out, sum_in, sum_out/sum_in)
print(content)
save_result(name, content)
content = 'The time spent for this test is %s' %COST_TIME
print(content)
save_result(name, content)
#\__/#\#/\#\__/#\#/\__/--\__/#\__/#\#/~\
