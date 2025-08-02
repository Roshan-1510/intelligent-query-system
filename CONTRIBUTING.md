# 🤝 Contributing to Intelligent Query–Retrieval System

Thank you for considering contributing to this open-source project!  
Your help makes this project better for everyone, and we appreciate every PR, issue, and suggestion.

---

## 📑 Table of Contents

- [Getting Started](#-getting-started)
- [How to Contribute](#-how-to-contribute)
- [Code Style & Guidelines](#-code-style--guidelines)
- [Pull Request Process](#-pull-request-process)
- [Reporting Bugs or Suggesting Features](#-reporting-bugs-or-suggesting-features)
- [Code of Conduct](#-code-of-conduct)
- [License](#-license)

---

## 🛠️ Getting Started

1. Fork this repository
2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/intelligent-query-system.git
   cd intelligent-query-system
   ```

3. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## ✍️ How to Contribute

You can contribute in the following ways:

- 🐛 Report bugs
- 💡 Suggest features or improvements
- 📄 Improve documentation
- 🔧 Refactor or optimize code
- ✅ Write unit tests
- 🚀 Add new capabilities

---

## 🧑‍💻 Code Style & Guidelines

Please follow these conventions:

- ✅ Python 3.8+
- ✅ Follow **PEP8** style guide
- ✅ Use **type hints** wherever possible
- ✅ Include docstrings for all functions and classes
- ✅ Break logic into small, reusable functions/modules

Example:

```python
def get_embedding(text: str) -> List[float]:
    """
    Returns the vector embedding for a given input string.
    """
    ...
```

---

## 🔁 Pull Request Process

1. Create a new branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:

   ```bash
   git add .
   git commit -m "Add: Your short, meaningful commit message"
   ```

3. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request on GitHub.

✅ **Checklist Before PR:**

- [ ] Code compiles and passes `python run.py`
- [ ] Tests are written/updated
- [ ] No sensitive info in commits or code
- [ ] Follows existing code structure and naming

---

## 🐞 Reporting Bugs or Suggesting Features

Please open an [Issue](https://github.com/Roshan-1510/intelligent-query-system/issues) with:

- ✅ A descriptive title
- ✅ A clear summary of the bug/feature
- ✅ Steps to reproduce (if a bug)
- ✅ Expected vs actual behavior

---

## 🌟 Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).  
Please be respectful, inclusive, and kind.

---

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you again for contributing! 🎉  
Let's build something amazing together. 🚀
