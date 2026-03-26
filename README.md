# 🕵️ OSINT Tool — Email & Phone Intelligence Gatherer

> A powerful terminal-based OSINT tool for gathering intelligence from email addresses and phone numbers. Works on **Windows**, **Linux**, and **Kali Linux**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Kali-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

---

## 📸 Preview

```
  ██████╗ ███████╗██╗███╗   ██╗████████╗
 ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
 ██║   ██║███████╗██║██╔██╗ ██║   ██║   
 ██║   ██║╚════██║██║██║╚██╗██║   ██║   
 ╚██████╔╝███████║██║██║ ╚████║   ██║   
  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝  
  ┌─────────────────────────────────┐
  │  Email + Phone Intelligence     │
  │  For authorized use only        │
  └─────────────────────────────────┘

[*] Starting OSINT Scan...

──────────────────────────────────────────────────────
  GRAVATAR — Profile Lookup
──────────────────────────────────────────────────────
[+] Status               : ACCOUNT FOUND
[+] Display Name         : John Doe
[+] Location             : Delhi, India
[+] Linked Socials       :
       → Twitter: twitter.com/johndoe
       → GitHub: github.com/johndoe

──────────────────────────────────────────────────────
  GITHUB — Commit Search
──────────────────────────────────────────────────────
[+] GitHub Commits       : 12
[+] Author Name          : John Doe
[+] Repository           : johndoe/secret-project

──────────────────────────────────────────────────────
  HAVEIBEENPWNED — Breach Check
──────────────────────────────────────────────────────
[!] BREACHED             : Found in 3 breach(es)!
[!] LinkedIn             | Date: 2021-06-22 | Emails, Passwords
[!] Adobe                | Date: 2013-10-04 | Emails, Passwords
```

---

## ✨ Features

### 📧 Email Intelligence
| Module | What It Does | API Key? |
|--------|-------------|----------|
| **Gravatar** | Profile pic, name, bio, linked social accounts | ❌ Free |
| **GitHub Search** | Find public commits, repos linked to email | ❌ Free |
| **Hunter.io** | Email validation, name, company lookup | ✅ Free tier |
| **HaveIBeenPwned** | Check data breaches involving the email | ✅ Paid ($3.50) |
| **Sherlock** | Auto-guess username → search 300+ sites | ❌ Free |

### 📱 Phone Intelligence
| Module | What It Does | API Key? |
|--------|-------------|----------|
| **phonenumbers** | Offline: country, carrier, line type, timezone | ❌ Free |
| **Numverify** | Online carrier, location validation | ✅ Free tier |
| **AbstractAPI** | Extended phone details | ✅ Free tier |

---

## ⚙️ Installation

### Prerequisites
- Python 3.8+
- pip / pip3
- Git

### Clone the Repo

```bash
git clone https://github.com/anand87794/PYTHON_OSINT_TOOL.git
cd PYTHON_OSINT_TOOL
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install requests phonenumbers sherlock-project
```

---

## 🔑 API Keys Setup

Copy the config template and add your keys:

```bash
cp config.ini.example config.ini
nano config.ini       # Linux/Kali
notepad config.ini    # Windows
```

Edit `config.ini`:

```ini
[API_KEYS]
hibp_api_key      = YOUR_KEY_HERE
hunter_api_key    = YOUR_KEY_HERE
numverify_api_key = YOUR_KEY_HERE
abstractapi_key   = YOUR_KEY_HERE
```

### Where to Get Free API Keys

| API | Link | Free Quota |
|-----|------|-----------|
| Hunter.io | https://hunter.io/users/sign_up | 25 req/month |
| Numverify | https://numverify.com | 100 req/month |
| AbstractAPI | https://app.abstractapi.com/api/phone-validation | 250 req/month |
| HaveIBeenPwned | https://haveibeenpwned.com/API/Key | ~$3.50 one-time |

> **Note:** The tool works without API keys too! Gravatar, GitHub, and offline phone analysis run for free with no setup.

---

## 🚀 Usage

### Email Scan
```bash
python3 osint_tool.py -t target@gmail.com
```

### Phone Scan
```bash
python3 osint_tool.py -t +919876543210
```

### Save Results to File
```bash
python3 osint_tool.py -t target@gmail.com --save
```

### Skip Sherlock (Faster)
```bash
python3 osint_tool.py -t target@gmail.com --no-sherlock
```

### Full Help
```bash
python3 osint_tool.py --help
```

---

## 🐧 Kali Linux Usage

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/osint-tool.git
cd osint-tool

# Install
pip3 install -r requirements.txt

# Create config
cp config.ini.example config.ini
nano config.ini

# Run
python3 osint_tool.py -t target@email.com
python3 osint_tool.py -t +919876543210 --save
```

---

## 📁 Project Structure

```
osint-tool/
├── osint_tool.py        # Main tool
├── config.ini           # API keys (DO NOT commit this!)
├── config.ini.example   # Template (safe to commit)
├── requirements.txt     # Python dependencies
├── .gitignore           # Ignores config.ini
└── README.md            # This file
```

---

## ⚠️ Disclaimer

> This tool is intended for **authorized penetration testing**, **bug bounty hunting**, and **educational purposes ONLY**.
> 
> - Do NOT use on targets without explicit written permission.
> - The author is not responsible for any misuse.
> - Always follow your country's laws and ethical guidelines.

---

## 📜 License

MIT License — feel free to use, modify, and distribute with credit.

---

## 🤝 Contributing

Pull requests welcome! Feel free to open issues or suggest new modules.

---

*Made with 🖤 for the security community*
