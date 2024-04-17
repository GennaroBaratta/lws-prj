import pandas as pd
import numpy as np
from time import process_time,perf_counter
from pandas import DataFrame, Int64Dtype, UInt32Dtype, UInt64Dtype
from collections import defaultdict

t1_start = process_time() 
p1_start = perf_counter()

Transations = pd.read_csv('DataSets/2013/transactions.csv',
                          names=['timestamp', 'blockId',
                                 'txId', 'isCoinbase', 'fee'],
                          dtype={'timestamp': 'int64', 'blockId': 'uint32',
                                 'txId': 'uint32', 'isCoinbase': 'bool', 'fee': UInt64Dtype.type})
Transations['timestamp'] = pd.to_datetime(Transations['timestamp'],unit='s')

Inputs = pd.read_csv('DataSets/2013/inputs.csv',
                     names=['txId', 'prevTxId', 'prevTxpos'],
                     dtype={'prevTxpos': 'uint16', 'prevTxId': 'uint32',
                                 'txId': 'uint32'}
                     )

Outputs = pd.read_csv('DataSets/2013/outputs.csv',
                      names=['txId', 'position', 'addressId',
                             'amount', 'scripttype'],
                      dtype={'txId': 'uint32',
                             'position': 'uint16',
                             'addressId': 'uint32',
                             'amount': 'uint64',
                             'scripttype ': 'int'})
Outputs['scripttype'] = Outputs['scripttype'].astype('category')

Mapping = pd.read_csv('DataSets/2013/mapAddr2Ids8708820.csv',
                      names=['hash', 'addressId'])
Mapping['addressId'] = pd.to_numeric(Mapping['addressId'],downcast='unsigned')

# Select only the necessary columns
reduced_outputs = Outputs[['addressId', 'txId', 'position']]
reduced_inputs = Inputs[['txId', 'prevTxId', 'prevTxpos']]

# Merge Inputs and Outputs using prevTxId
merged_data: DataFrame = pd.merge(reduced_inputs, reduced_outputs, left_on=['prevTxId', 'prevTxpos'], right_on=['txId', 'position'], how='inner')

# Filtra solo le transazioni con più di un input
multiple_input_txs = merged_data[merged_data.duplicated(subset=['txId_x'], keep=False)]


t1_stop = process_time()
p1_stop = perf_counter()
print("Elapsed time during reading data in seconds:",
                                         t1_stop-t1_start) 
print("Elapsed time performance during reading data in seconds:",
                                         p1_stop-p1_start) 
class UnionFind:
    def __init__(self):
        self.parent = dict()
        self.rank = dict()

    def make_set(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return

        if self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_x] = root_y
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_y] += 1
                
def cluster_addresses_union_find_opt_v4(multiple_input_txs):
    uf = UnionFind()

    # Crea un set di tutti gli indirizzi presenti nei dati
    all_addresses = set(multiple_input_txs['addressId'].unique())

    # Inizializza l'oggetto uf con tutti gli indirizzi unici
    for address in all_addresses:
        uf.make_set(address)

    for _, group in multiple_input_txs.groupby('txId_x'):
        addresses = group['addressId'].tolist()

        # Unisci tutti gli indirizzi nell'input corrente nel nuovo cluster
        for i in range(1, len(addresses)):
            uf.union(addresses[i - 1], addresses[i])

    cluster_mapping = {}
    for address in all_addresses:
        root = uf.find(address)
        if root not in cluster_mapping:
            cluster_mapping[root] = []
        cluster_mapping[root].append(address)
        
    return cluster_mapping

output_clustering = cluster_addresses_union_find_opt_v4(multiple_input_txs)
# Calcola le dimensioni di ciascun cluster
cluster_sizes = [len(addresses) for addresses in output_clustering.values()]

# Calcola la dimensione media, minima e massima dei cluster
mean_size = np.mean(cluster_sizes)
min_size = np.min(cluster_sizes)
max_size = np.max(cluster_sizes)

print("Dimensione media dei cluster:", mean_size)
print("Dimensione minima dei cluster:", min_size)
print("Dimensione massima dei cluster:", max_size)

import json
    
    
with open("clusters.json", "w") as outfile:
    json.dump({int(k):[int(i) for i in v] for k,v in output_clustering.items()}, outfile)

t1_stop = process_time()
p1_stop = perf_counter()

print("Elapsed time:", t1_stop, t1_start) 
print("Elapsed time performance:", p1_stop, p1_start) 
   
print("Elapsed time during the whole program in seconds:",
                                         t1_stop-t1_start) 
print("Elapsed time performance during the whole program in seconds:",
                                         p1_stop-p1_start) 