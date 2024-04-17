### Bitcoin De-anonymization Project Repository

#### Overview
This repository contains the source code and related materials for the "Clustering and Scraping For Bitcoin De-anonymization" project. The goal of this project is to implement a set of analyses and de-anonymization techniques for the Bitcoin blockchain.

#### DataSet Description
The provided Bitcoin DataSet encompasses a selection of transactions from the genesis block mined on January 3, 2009, to the block of height 214562 mined on December 31, 2012. This data has been transformed from public blockchain data to reduce its size by:
- Removing all unspent Coinbase transaction outputs as of the last block date.
- Replacing transaction hashes, output addresses, and scripts with unique integer identifiers.
- Storing a mapping of blockchain addresses to DataSet identifiers in a separate mapping file.

#### Files in DataSet
1. **transactions.csv**: Contains details like timestamp, block ID, transaction ID, Coinbase status, and fees for each transaction.
2. **inputs.csv**: Details about each input in the transactions, including the ID of the transaction that created the currently spent output.
3. **outputs.csv**: Each output's details such as transaction ID, position, address ID, amount transferred, and script type.
4. **mapping.csv**: Mapping of unique identifiers to the corresponding blockchain address.

#### Required Analyses
1. **General Blockchain Data Analysis**:
   - Distribution of transactions per block over time.
   - Evolution of block occupancy over time shown in a bimonthly graph.
   - Total amount of unspent transaction outputs (UTXOs) at the end of the dataset.
   - Distribution of time intervals between the generation and spending of UTXOs.

2. **Bitcoin Address Clustering (Multi-input Heuristic)**:
   - Implementation of de-anonymization techniques to cluster addresses likely controlled by the same user based on transaction inputs.
   - Statistical analysis of the clustering results such as average, minimum, and maximum cluster sizes.

3. **Address De-anonymization**:
   - Implementation of a web scraper to attempt de-anonymization of addresses in the largest clusters using resources like WalletExplorer and Bitcoininfocharts.

#### Resources
- Address De-anonymization Tools:
  - [WalletExplorer](https://www.walletexplorer.com/)
  - [Bitcoininfocharts](https://bitinfocharts.com/)
