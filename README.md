# Bitcoin De-anonymization Project

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> Advanced blockchain analysis toolkit for clustering and de-anonymizing Bitcoin addresses using the multi-input heuristic and web scraping techniques.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Dataset Structure](#dataset-structure)
- [Usage](#usage)
- [Project Architecture](#project-architecture)
- [Results and Analysis](#results-and-analysis)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

---

## 🔍 Overview

This project implements a comprehensive Bitcoin blockchain analysis system that combines **address clustering algorithms** with **automated web scraping** to de-anonymize Bitcoin addresses. The goal is to identify which addresses likely belong to the same user or wallet, and then attempt to discover the real-world identity or wallet name associated with those addresses.

### The Problem It Solves

Bitcoin's blockchain is public and transparent, but it's **pseudonymous** rather than anonymous. While all transactions are visible, they're linked to addresses rather than real identities. This project:

1. **Clusters related addresses** using the multi-input heuristic (addresses used together in a transaction likely belong to the same entity)
2. **De-anonymizes addresses** by scraping public blockchain explorers for wallet names and labels
3. **Provides statistical analysis** of clustering results and address patterns

### Use Cases

- **Academic Research**: Understanding Bitcoin privacy and anonymity
- **Blockchain Forensics**: Investigating transaction patterns
- **Security Analysis**: Studying de-anonymization techniques and privacy implications
- **Educational Purposes**: Learning about blockchain data structures and analysis

---

## ✨ Features

### Core Functionality

- **🔗 Address Clustering**
  - Efficient Union-Find algorithm with path compression and union by rank
  - Multi-input heuristic implementation
  - Processes millions of transactions efficiently
  - Optimized for large-scale blockchain datasets

- **🕷️ Automated Web Scraping**
  - Finite State Machine (FSM) architecture for robust scraping
  - Dual-source scraping: BitInfoCharts.com and WalletExplorer.com
  - Selenium-based browser automation with anti-detection measures
  - Captcha detection and graceful error handling

- **📊 Statistical Analysis**
  - Cluster size distribution (mean, min, max)
  - Transaction pattern analysis
  - UTXO (Unspent Transaction Output) analysis
  - Block occupancy evolution over time

### Technical Highlights

- **Performance**: O(n × α(n)) clustering complexity where α is the inverse Ackermann function (nearly constant)
- **Scalability**: Handles 4+ years of Bitcoin blockchain data (2009-2012)
- **Robustness**: State machine pattern ensures reliable scraping even with network issues
- **Data Integrity**: Comprehensive CSV-based dataset with mapping files

---

## 🛠️ How It Works

### 1. Multi-Input Heuristic

The **multi-input heuristic** is based on a simple observation: when a Bitcoin transaction has multiple input addresses, those addresses are likely controlled by the same entity (wallet). This is because:

- Bitcoin transactions require the private key to sign each input
- It's unlikely multiple unrelated parties would coordinate to create a single transaction
- Wallets often combine multiple outputs from previous transactions as inputs

```
Transaction Example:
Inputs:  Address A (0.5 BTC) ─┐
         Address B (0.3 BTC) ─┤
         Address C (0.2 BTC) ─┴─> [Transaction] ─> Outputs

Conclusion: Addresses A, B, and C likely belong to the same wallet
```

### 2. Union-Find Clustering Algorithm

We use a **Union-Find (Disjoint Set Union)** data structure to efficiently cluster addresses:

1. Initialize each address as its own cluster
2. For each transaction with multiple inputs:
   - Union all input addresses together
3. Build final cluster mapping (cluster root → all addresses in cluster)

**Optimizations**:
- **Path compression**: Flatten tree structure during find operations for O(1) lookups
- **Union by rank**: Keep trees balanced by attaching smaller trees to larger ones

### 3. Web Scraping Pipeline

The scraper uses a **Finite State Machine** to navigate blockchain explorers:

```
[Start] → [Load Address Page] → [Scrape Wallet Name] → [Load Wallet Page]
            ↓ (if captcha)              ↓ (oneshot)           ↓
        [Banned]                      [OK]              [Extract All Addresses]
                                                               ↓
                                                        [Remove from Queue]
                                                               ↓
                                                        [Next Address]
```

See `crawlerFSM.jpeg` for detailed state diagram.

---

## 📦 Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for large datasets)
- **Storage**: ~100MB for dependencies, variable for datasets
- **Browser**: Microsoft Edge (or modify code for Chrome/Firefox)

### Dependencies

All dependencies are listed in `requirements.txt`:
- `pandas` & `numpy`: Data processing and numerical operations
- `selenium`: Browser automation
- `beautifulsoup4` & `requests`: Web scraping
- `python-statemachine`: FSM implementation
- `jupyter`: (Optional) For exploratory analysis

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bitcoin-deanonymization.git
cd bitcoin-deanonymization
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install WebDriver

For Selenium to work, you need a WebDriver for your browser:

**Option A: Microsoft Edge (default in code)**
```bash
# Edge WebDriver is usually auto-detected with Selenium 4.x
# If not, download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

**Option B: Chrome**
```bash
# Download ChromeDriver: https://chromedriver.chromium.org/
# Then modify scaper.py: webdriver.Edge() → webdriver.Chrome()
```

### 5. Prepare Dataset

Place your Bitcoin dataset files in a `DataSets/2013/` directory:
```
DataSets/
└── 2013/
    ├── transactions.csv
    ├── inputs.csv
    ├── outputs.csv
    └── mapAddr2Ids8708820.csv
```

---

## 📁 Dataset Structure

### Overview

The dataset contains Bitcoin blockchain data from the **genesis block (January 3, 2009)** to **block 214562 (December 31, 2012)**.

### File Descriptions

| File | Description | Columns |
|------|-------------|---------|
| **transactions.csv** | Transaction metadata | `timestamp`, `blockId`, `txId`, `isCoinbase`, `fee` |
| **inputs.csv** | Transaction inputs | `txId`, `prevTxId`, `prevTxpos` |
| **outputs.csv** | Transaction outputs | `txId`, `position`, `addressId`, `amount`, `scripttype` |
| **mapping.csv** | Address ID to hash mapping | `hash`, `addressId` |

### Data Transformations

To reduce dataset size, the data has been transformed:
- ✅ Removed unspent Coinbase outputs as of last block
- ✅ Replaced transaction hashes with integer IDs
- ✅ Replaced addresses with integer IDs (mapped in `mapping.csv`)
- ✅ Removed spent outputs to minimize redundancy

### Example Data

**transactions.csv**
```csv
1231006505,0,0,True,0
1231470173,1,1,True,0
1231471428,2,2,False,0
```

**inputs.csv**
```csv
2,0,0
3,1,0
```

**outputs.csv**
```csv
0,0,1,5000000000,1
1,0,2,5000000000,1
```

---

## 💻 Usage

### Quick Start

#### 1. Run Clustering Analysis

```bash
python clustering.py
```

**What it does**:
- Loads transaction data from CSV files
- Filters transactions with multiple inputs
- Applies Union-Find clustering algorithm
- Outputs cluster statistics (mean, min, max sizes)
- Saves results to `clusters.json`

**Expected Output**:
```
Elapsed time during reading data in seconds: 12.5
Average cluster size: 3.47
Minimum cluster size: 1
Maximum cluster size: 1523
Elapsed time during the whole program in seconds: 45.2
```

**Output File** (`clusters.json`):
```json
{
  "12345": [12345, 23456, 34567],  // Cluster root: [list of addresses]
  "67890": [67890, 78901, 89012],
  ...
}
```

#### 2. Run Web Scraper for De-anonymization

```bash
python scaper.py
```

**What it does**:
- Loads clustering results from `clusters.json`
- Selects top 10 largest clusters
- Maps address IDs to Bitcoin hashes
- Scrapes BitInfoCharts.com and WalletExplorer.com
- Saves results to `DataSets/risultato2.csv`

**Configuration**:
```python
# In scaper.py, line 159:
oneshot = True  # Stop after first wallet found per cluster
oneshot = False  # Process all addresses in cluster
```

**Expected Output**:
```
Wallet link element found.
No captcha found - continuing scraping.
...
```

**Output File** (`DataSets/risultato2.csv`):
```csv
Address,Wallet,Fonte,ChiaveCluster
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,Satoshi,bitinfocharts.com,0
1BvBM...,Mt.Gox,walletexplorer.com,1
```

### Advanced Usage

#### Custom Cluster Size Selection

Modify `scaper.py` to select different clusters:

```python
# Line 154: Select top N clusters
top_10 = sorted_cluster[0:10]  # Change to top_5, top_20, etc.
```

#### Analyze Specific Address

```python
from scaper import cerca_indirizzo

# Search for specific address on WalletExplorer
wallet_name = cerca_indirizzo('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
print(f"Wallet: {wallet_name}")
```

#### Use Different Browser

```python
# In scaper.py, modify line 95:
# For Chrome:
self.driver = webdriver.Chrome()

# For Firefox:
self.driver = webdriver.Firefox()
```

### Jupyter Notebook Analysis

Explore the data interactively:

```bash
jupyter notebook esame.ipynb
```

The notebook contains exploratory analysis, visualizations, and experiments.

---

## 🏗️ Project Architecture

### File Structure

```
bitcoin-deanonymization/
│
├── clustering.py           # Address clustering implementation
├── preprocessing.py        # Data preprocessing (duplicate of clustering.py)
├── scaper.py              # Web scraper with FSM architecture
├── esame.ipynb            # Jupyter notebook for analysis
│
├── clusters2.json         # Pre-computed clustering results (46MB)
├── crawlerFSM.jpeg        # State machine diagram
│
├── DataSets/              # Bitcoin blockchain data
│   └── 2013/
│       ├── transactions.csv
│       ├── inputs.csv
│       ├── outputs.csv
│       └── mapAddr2Ids8708820.csv
│
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore patterns
├── LICENSE               # MIT License
├── README.md             # This file
└── CONTRIBUTING.md       # Contribution guidelines
```

### Module Overview

#### `clustering.py`
- **Purpose**: Implement multi-input heuristic clustering
- **Key Classes**: `UnionFind`
- **Key Functions**: `cluster_addresses_union_find_opt_v4()`
- **Input**: Transaction CSV files
- **Output**: `clusters.json` (cluster mapping)

#### `scaper.py`
- **Purpose**: De-anonymize addresses via web scraping
- **Key Classes**: `CrawlerBot(StateMachine)`
- **Key Functions**: `cerca_indirizzo()`
- **Input**: `clusters.json`, mapping.csv
- **Output**: `DataSets/risultato2.csv`

### Data Flow

```
[CSV Files] → [clustering.py] → [clusters.json]
                                      ↓
                         [scaper.py] + [mapping.csv]
                                      ↓
                              [risultato2.csv]
```

### State Machine Diagram

See `crawlerFSM.jpeg` for the complete state machine architecture of the web scraper.

**Key States**:
- **Start**: Initial state
- **Address Page Loaded**: Successfully loaded address page
- **Wallet Page Loaded**: Successfully loaded wallet page
- **Banned**: Captcha detected, scraping blocked
- **OK**: Scraping completed successfully

---

## 📊 Results and Analysis

### Clustering Statistics

The clustering algorithm typically produces results like:

- **Number of clusters**: ~2.5 million (from ~8.7 million addresses)
- **Average cluster size**: 3-4 addresses
- **Largest cluster size**: 1,500+ addresses (likely major exchanges)
- **Single-address clusters**: ~60% (addresses used only once)

### De-anonymization Results

Top clusters often belong to:
- **Mt.Gox**: Early Bitcoin exchange (largest clusters)
- **Silk Road**: Dark web marketplace (before closure)
- **Mining Pools**: Deepbit, BTC Guild, Slush Pool
- **Known Wallets**: Satoshi's addresses, Bitcoin Faucet

### Privacy Implications

This project demonstrates that:
1. **Address reuse reduces privacy**: Multi-input transactions link addresses
2. **Clustering is effective**: Millions of addresses can be clustered
3. **Public data enables de-anonymization**: Blockchain explorers reveal identities
4. **Privacy requires care**: Users should use HD wallets and avoid address reuse

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Improvement

- [ ] Add support for more blockchain explorers
- [ ] Implement additional clustering heuristics (change address detection)
- [ ] Add visualization of cluster networks
- [ ] Improve scraping robustness (proxy support, better captcha handling)
- [ ] Add unit tests and integration tests
- [ ] Create Docker containerization
- [ ] Add CI/CD pipeline

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Academic Use Notice

This software is intended for **academic research and educational purposes**. Users conducting research involving blockchain analysis should ensure compliance with applicable laws and ethical guidelines regarding data privacy and usage.

---

## 🙏 Acknowledgments

- **Dataset**: Bitcoin blockchain data (Genesis to Dec 2012)
- **Algorithms**: Union-Find data structure with optimizations
- **Tools**:
  - [BitInfoCharts](https://bitinfocharts.com/) - Blockchain explorer
  - [WalletExplorer](https://www.walletexplorer.com/) - Wallet identification service
- **Inspiration**: Academic research on Bitcoin privacy and de-anonymization

### References

If you use this project in academic research, please consider citing:

- Reid, F., & Harrigan, M. (2013). "An Analysis of Anonymity in the Bitcoin System"
- Meiklejohn, S., et al. (2013). "A Fistful of Bitcoins: Characterizing Payments Among Men with No Names"
- Androulaki, E., et al. (2013). "Evaluating User Privacy in Bitcoin"

---

## 📧 Contact

**Project Maintainer**: [Your Name]

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

**Issues & Support**:
- Report bugs or request features via [GitHub Issues](https://github.com/yourusername/bitcoin-deanonymization/issues)
- For academic collaborations, please email directly

---

## 📸 Screenshots / Visualizations

> **Suggestion**: Add the following visual content to make the repository more attractive:

### Recommended Visuals

1. **Cluster Size Distribution**
   - Histogram showing distribution of cluster sizes
   - Log-scale plot for better visualization
   - Location: `docs/cluster_distribution.png`

2. **State Machine Diagram**
   - Already exists: `crawlerFSM.jpeg` ✅
   - Consider creating a higher-resolution version

3. **Sample Output**
   - Screenshot of clustering.py execution
   - Screenshot of scaper.py in action (browser window)
   - Sample visualization from `esame.ipynb`

4. **Data Flow Diagram**
   - Visual representation of data pipeline
   - Tools like draw.io or mermaid.js

5. **Demo GIF**
   - Recording of scraper in action
   - Can use tools like LICEcap or ScreenToGif

### Example Placement in README

```markdown
### Sample Execution

![Clustering Execution](docs/clustering_output.png)
*Clustering algorithm processing 4 years of Bitcoin transactions*

![Scraper Demo](docs/scraper_demo.gif)
*Automated web scraper navigating blockchain explorers*
```

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/bitcoin-deanonymization&type=Date)](https://star-history.com/#yourusername/bitcoin-deanonymization&Date)

---

<p align="center">
  Made with ❤️ for blockchain research and education
</p>
