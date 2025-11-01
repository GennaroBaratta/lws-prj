# Contributing to Bitcoin De-anonymization Project

First off, thank you for considering contributing to this project! It's people like you that make this research tool better for everyone in the blockchain analysis community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submission Guidelines](#submission-guidelines)
- [Community](#community)

---

## 🤝 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in your interactions.

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together and help each other
- **Be patient**: Remember that people have different skill levels
- **Be constructive**: Provide helpful feedback and criticism
- **Be academic**: This is a research project - maintain scientific integrity

---

## 💡 How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. **Clear title**: Describe the bug concisely
2. **Steps to reproduce**: Detailed steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**:
   - OS (Windows, macOS, Linux)
   - Python version
   - Relevant package versions
6. **Screenshots/logs**: If applicable

**Example**:
```markdown
### Bug: Scraper crashes when encountering captcha

**Steps to reproduce:**
1. Run `python scaper.py`
2. Wait for 100+ requests
3. Captcha appears

**Expected:** Should transition to 'banned' state gracefully
**Actual:** Crashes with KeyError

**Environment:** Ubuntu 22.04, Python 3.10, Selenium 4.15.0
```

### Suggesting Enhancements

We welcome feature suggestions! Please create an issue with:

1. **Use case**: Why would this feature be useful?
2. **Proposed solution**: How do you envision it working?
3. **Alternatives**: Have you considered any alternative solutions?
4. **Additional context**: Screenshots, mockups, references, etc.

### Pull Requests

We actively welcome your pull requests! Here's the process:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add/update tests if applicable
5. Update documentation (README, docstrings, etc.)
6. Commit your changes (see [Commit Guidelines](#commit-guidelines))
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/bitcoin-deanonymization.git
cd bitcoin-deanonymization

# Add upstream remote for syncing
git remote add upstream https://github.com/ORIGINAL_OWNER/bitcoin-deanonymization.git
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Install development dependencies (if available)
pip install -r requirements-dev.txt  # Optional
```

### 4. Verify Setup

```bash
# Run a quick test
python clustering.py --help  # Or similar verification
```

### 5. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/bug-description
```

---

## 📝 Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some flexibility for readability.

#### Key Points

**Naming Conventions:**
```python
# Classes: PascalCase
class UnionFind:
    pass

# Functions and variables: snake_case
def cluster_addresses(data):
    cluster_size = 0

# Constants: UPPER_SNAKE_CASE
MAX_CLUSTER_SIZE = 10000
```

**Imports:**
```python
# Standard library first
import json
import time

# Third-party packages
import pandas as pd
import numpy as np
from selenium import webdriver

# Local modules
from utils import helper_function
```

**Line Length:**
- Aim for 80-100 characters per line
- Maximum 120 characters (hard limit)

### Documentation Standards

#### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def cluster_addresses(transactions, min_inputs=2):
    """
    Cluster Bitcoin addresses using the multi-input heuristic.

    This function identifies addresses that likely belong to the same
    entity by analyzing transactions with multiple input addresses.

    Args:
        transactions (DataFrame): Transaction data with columns txId, addressId
        min_inputs (int, optional): Minimum inputs to consider. Defaults to 2.

    Returns:
        dict: Cluster mapping where keys are cluster roots and values are
              lists of addresses in that cluster.

    Raises:
        ValueError: If transactions DataFrame is empty or missing required columns.

    Example:
        >>> df = pd.read_csv('transactions.csv')
        >>> clusters = cluster_addresses(df, min_inputs=3)
        >>> print(f"Found {len(clusters)} clusters")
    """
    pass
```

#### Comments

```python
# Good comments explain WHY, not WHAT
addresses = set(data['addressId'].unique())  # Use set for O(1) removal

# Avoid obvious comments
x = x + 1  # Bad: increment x
```

### Code Quality

**Before committing, check:**

1. **Linting** (if configured):
   ```bash
   flake8 clustering.py
   pylint scaper.py
   ```

2. **Type hints** (where appropriate):
   ```python
   def find_cluster(address_id: int) -> List[int]:
       pass
   ```

3. **Error handling**:
   ```python
   # Good: Specific exceptions
   try:
       data = pd.read_csv(filename)
   except FileNotFoundError:
       logger.error(f"File {filename} not found")
       raise
   except pd.errors.EmptyDataError:
       logger.warning(f"File {filename} is empty")
       return pd.DataFrame()
   ```

---

## 📤 Submission Guidelines

### Commit Guidelines

Write clear, descriptive commit messages following these conventions:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
# Good commit messages
git commit -m "feat(clustering): add support for weighted clustering"
git commit -m "fix(scraper): handle captcha timeout gracefully"
git commit -m "docs(README): add installation instructions for Windows"
git commit -m "refactor(union-find): optimize path compression algorithm"

# Bad commit messages
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "asdfasdf"
```

**Detailed example:**
```
feat(scraper): add proxy support for WalletExplorer requests

Implement rotating proxy support to avoid IP-based rate limiting
when scraping WalletExplorer. This uses a proxy pool with automatic
failover if a proxy becomes unresponsive.

Closes #42
```

### Pull Request Process

1. **Update documentation**: README, docstrings, comments
2. **Add tests**: If you're adding functionality
3. **Check code style**: Follow PEP 8 and project conventions
4. **Write clear PR description**:
   ```markdown
   ## Summary
   Brief description of what this PR does

   ## Changes
   - Added feature X
   - Fixed bug Y
   - Refactored module Z

   ## Testing
   - Tested on Python 3.8, 3.10, 3.11
   - Verified clustering still produces correct results
   - Confirmed scraper handles new edge cases

   ## Screenshots (if applicable)
   [Add screenshots demonstrating the change]

   ## Related Issues
   Closes #123
   Related to #456
   ```

5. **Be responsive**: Address review feedback promptly
6. **Squash commits**: If requested, squash related commits before merging

### Review Process

- At least one maintainer will review your PR
- Reviews typically happen within 1-3 days
- Address feedback by pushing new commits or amending
- Once approved, a maintainer will merge your PR

---

## 🎯 Areas for Contribution

Looking for ways to contribute? Here are some areas we'd love help with:

### High Priority

- [ ] **Add unit tests**: Clustering algorithm, Union-Find operations
- [ ] **Improve error handling**: Better exception management in scraper
- [ ] **Add logging**: Replace print statements with proper logging
- [ ] **Performance optimization**: Speed up clustering for larger datasets
- [ ] **Docker support**: Create Dockerfile and docker-compose.yml

### Medium Priority

- [ ] **Additional clustering heuristics**: Change address detection, temporal analysis
- [ ] **More data sources**: Support additional blockchain explorers
- [ ] **Visualization**: Cluster network graphs, statistics dashboards
- [ ] **Configuration file**: YAML/JSON config instead of hardcoded values
- [ ] **CLI interface**: Argument parsing with argparse or click

### Low Priority

- [ ] **Web interface**: Simple Flask/Django app for running analysis
- [ ] **Database support**: Store results in SQLite/PostgreSQL instead of JSON
- [ ] **Export formats**: Support XML, Parquet, etc.
- [ ] **Parallel processing**: Multi-threading for scraper
- [ ] **CI/CD**: GitHub Actions for automated testing

---

## 🧪 Testing

If you add new features, please include tests:

```python
# Example test structure (if we add a tests/ directory)
def test_union_find_basic():
    """Test basic Union-Find operations."""
    uf = UnionFind()
    uf.make_set(1)
    uf.make_set(2)
    uf.union(1, 2)
    assert uf.find(1) == uf.find(2)

def test_clustering_empty_input():
    """Test that clustering handles empty input gracefully."""
    result = cluster_addresses(pd.DataFrame())
    assert len(result) == 0
```

Run tests with:
```bash
pytest tests/
# or
python -m unittest discover tests/
```

---

## 📚 Resources

### Learning Resources

- **Bitcoin Whitepaper**: https://bitcoin.org/bitcoin.pdf
- **Blockchain Explorer APIs**: BitInfoCharts, Blockchain.com APIs
- **Union-Find Algorithm**: https://en.wikipedia.org/wiki/Disjoint-set_data_structure
- **Selenium Documentation**: https://selenium-python.readthedocs.io/

### Academic Papers

- Reid & Harrigan (2013): "An Analysis of Anonymity in the Bitcoin System"
- Meiklejohn et al. (2013): "A Fistful of Bitcoins"
- Androulaki et al. (2013): "Evaluating User Privacy in Bitcoin"

---

## 💬 Community

### Getting Help

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Email**: For private inquiries or academic collaboration

### Acknowledgments

All contributors will be acknowledged in:
- README.md contributors section
- Release notes for their contributions
- Academic publications (if applicable)

---

## 🏆 Recognition

We value all contributions, big or small! Contributors will be:

- Listed in the project README
- Mentioned in release notes
- Eligible for co-authorship on academic papers (for significant contributions)

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers this project. See [LICENSE](LICENSE) for details.

---

## ❓ Questions?

If you have questions about contributing, feel free to:

1. Open a [GitHub Discussion](https://github.com/yourusername/bitcoin-deanonymization/discussions)
2. Create an issue labeled "question"
3. Email the maintainers directly

---

<p align="center">
  Thank you for contributing to blockchain research! 🚀
</p>
