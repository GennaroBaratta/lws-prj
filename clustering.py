"""
Bitcoin Address Clustering Module

This module implements Bitcoin address clustering using the multi-input heuristic
and Union-Find data structure. The multi-input heuristic assumes that all input
addresses in a transaction are controlled by the same entity, allowing us to
cluster addresses that likely belong to the same wallet or user.

The module processes Bitcoin blockchain data (transactions, inputs, outputs) and
produces clusters of addresses using an optimized Union-Find algorithm with
path compression and union by rank.

Dataset: Bitcoin transactions from genesis block (Jan 3, 2009) to block 214562 (Dec 31, 2012)
"""

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

# Filter to keep only transactions with multiple inputs (2 or more)
# These are the transactions where multi-input heuristic can be applied
multiple_input_txs = merged_data[merged_data.duplicated(subset=['txId_x'], keep=False)]


t1_stop = process_time()
p1_stop = perf_counter()
print("Elapsed time during reading data in seconds:",
                                         t1_stop-t1_start) 
print("Elapsed time performance during reading data in seconds:",
                                         p1_stop-p1_start) 
class UnionFind:
    """
    Union-Find (Disjoint Set Union) data structure with path compression and union by rank.

    This implementation provides efficient operations for clustering elements into
    disjoint sets. It's optimized with two key techniques:
    - Path compression: flattens the tree structure during find operations
    - Union by rank: keeps trees balanced by attaching smaller trees to larger ones

    Attributes:
        parent (dict): Maps each element to its parent in the tree structure
        rank (dict): Tracks the approximate depth of each tree for balancing
    """

    def __init__(self):
        """Initialize an empty Union-Find structure."""
        self.parent = dict()
        self.rank = dict()

    def make_set(self, x):
        """
        Create a new set containing only element x.

        Args:
            x: Element to create a set for (typically a Bitcoin address ID)

        Note:
            If x already exists in the structure, this is a no-op.
        """
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):
        """
        Find the root (representative) of the set containing x.

        Implements path compression: all nodes along the path to root
        are directly connected to the root for faster future lookups.

        Args:
            x: Element to find the root for

        Returns:
            The root element of the set containing x
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        """
        Merge the sets containing x and y into a single set.

        Implements union by rank: the root of the smaller tree (by rank)
        becomes a child of the root of the larger tree, keeping trees balanced.

        Args:
            x: Element from first set
            y: Element from second set

        Note:
            If x and y are already in the same set, this is a no-op.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return

        # Union by rank: attach smaller tree to larger tree
        if self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_x] = root_y
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_y] += 1
                
def cluster_addresses_union_find_opt_v4(multiple_input_txs):
    """
    Cluster Bitcoin addresses using the multi-input heuristic and Union-Find algorithm.

    This function implements the multi-input heuristic: if multiple addresses appear
    as inputs to the same transaction, they are assumed to be controlled by the same
    entity and are clustered together.

    Algorithm:
    1. Initialize each unique address as its own cluster
    2. For each transaction with multiple inputs:
       - Group all input addresses together (they likely belong to same owner)
       - Merge their clusters using Union-Find union operation
    3. Build final cluster mapping by finding the root for each address

    Args:
        multiple_input_txs (DataFrame): DataFrame containing transaction data with columns:
            - txId_x: Transaction ID
            - addressId: Bitcoin address ID
            Must only contain transactions with 2+ inputs (already filtered)

    Returns:
        dict: Cluster mapping where:
            - Keys are cluster root IDs (representative address of each cluster)
            - Values are lists of all address IDs in that cluster

    Example:
        >>> clusters = cluster_addresses_union_find_opt_v4(multi_input_df)
        >>> print(f"Number of clusters: {len(clusters)}")
        >>> print(f"Largest cluster size: {max(len(v) for v in clusters.values())}")

    Time Complexity: O(n * α(n)) where n is number of addresses and α is inverse Ackermann
    Space Complexity: O(n) for storing parent and rank dictionaries
    """
    uf = UnionFind()

    # Create a set of all unique addresses in the data
    all_addresses = set(multiple_input_txs['addressId'].unique())

    # Initialize the Union-Find structure with all unique addresses
    for address in all_addresses:
        uf.make_set(address)

    # Group by transaction and merge addresses that appear together as inputs
    for _, group in multiple_input_txs.groupby('txId_x'):
        addresses = group['addressId'].tolist()

        # Union all addresses in the current transaction (multi-input heuristic)
        # They likely belong to the same wallet/entity
        for i in range(1, len(addresses)):
            uf.union(addresses[i - 1], addresses[i])

    # Build the final cluster mapping: root -> list of addresses in cluster
    cluster_mapping = {}
    for address in all_addresses:
        root = uf.find(address)
        if root not in cluster_mapping:
            cluster_mapping[root] = []
        cluster_mapping[root].append(address)

    return cluster_mapping

output_clustering = cluster_addresses_union_find_opt_v4(multiple_input_txs)

# Calculate cluster size statistics
cluster_sizes = [len(addresses) for addresses in output_clustering.values()]

# Compute mean, minimum, and maximum cluster sizes
mean_size = np.mean(cluster_sizes)
min_size = np.min(cluster_sizes)
max_size = np.max(cluster_sizes)

print("Average cluster size:", mean_size)
print("Minimum cluster size:", min_size)
print("Maximum cluster size:", max_size)

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