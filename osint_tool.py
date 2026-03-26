#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║         OSINT TOOL — Email & Phone Intelligence          ║
║         For authorized / educational use only           ║
╚══════════════════════════════════════════════════════════╝

QUICK SETUP:
  1. pip install -r requirements.txt
  2. Edit config.ini and paste your API keys
  3. Run:
       python osint_tool.py -t user@gmail.com
       python osint_tool.py -t +919876543210
       python osint_tool.py -t user@gmail.com --save
"""

import argparse
import configparser
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime

# ── Dependency check ─────────────────────────────────────
try:
    import requests
except ImportError:
    print("[!] Run: pip install requests")
    sys.exit(1)

# ── Load config ───────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

def get_key(section, key):
    try:
        val = config[section][key].strip()
        return val if val and not val.startswith("YOUR_") else None
    except KeyError:
        return None

HIBP_KEY     = get_key("API_KEYS", "hibp_api_key")
HUNTER_KEY   = get_key("API_KEYS", "hunter_api_key")
NUMVERIFY_KEY= get_key("API_KEYS", "numverify_api_key")
ABSTRACT_KEY = get_key("API_KEYS", "abstractapi_key")

# ── Colors ────────────────────────────────────────────────
class C:
    R  = '\033[91m'   # Red
    G  = '\033[92m'   # Green
    Y  = '\033[93m'   # Yellow
    B  = '\033[94m'   # Blue
    M  = '\033[95m'   # Magenta
    CY = '\033[96m'   # Cyan
    W  = '\033[97m'   # White bold
    DIM= '\033[2m'    # Dim
    BD = '\033[1m'    # Bold
    X  = '\033[0m'    # Reset

# ── Logging helper ────────────────────────────────────────
_results_log = []

def log(symbol, color, label, value, indent=0):
    pad = "  " * indent
    line = f"{pad}{color}[{symbol}] {label:<20}: {value}{C.X}"
    print(line)
    plain = f"[{symbol}] {label:<20}: {value}"
    _results_log.append(" " * (indent * 2) + plain)

def section(title):
    sep = "─" * 54
    print(f"\n{C.BD}{C.CY}{sep}{C.X}")
    print(f"{C.BD}{C.CY}  {title}{C.X}")
    print(f"{C.BD}{C.CY}{sep}{C.X}")
    _results_log.append(f"\n{'─'*54}\n  {title}\n{'─'*54}")

def warn(msg):
    print(f"  {C.Y}[!] {msg}{C.X}")

def save_results(target):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r'[^\w\-\+@\.]', '_', target)
    fname = f"osint_{safe}_{ts}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"OSINT SCAN RESULTS\nTarget: {target}\nDate: {datetime.now()}\n\n")
        f.write("\n".join(_results_log))
    print(f"\n{C.G}[+] Results saved to: {C.BD}{fname}{C.X}")

# ══════════════════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════════════════
def banner():
    print(f"""{C.B}{C.BD}
  ██████╗ ███████╗██╗███╗   ██╗████████╗
 ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
 ██║   ██║███████╗██║██╔██╗ ██║   ██║   
 ██║   ██║╚════██║██║██║╚██╗██║   ██║   
 ╚██████╔╝███████║██║██║ ╚████║   ██║   
  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝  {C.X}
{C.CY}  ┌─────────────────────────────────┐
  │  Email + Phone Intelligence     │
  │  For authorized use only        │
  └─────────────────────────────────┘{C.X}
""")


# ══════════════════════════════════════════════════════════
#  EMAIL MODULES
# ══════════════════════════════════════════════════════════

def mod_gravatar(email):
    section("GRAVATAR — Profile Lookup")
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/{h}.json"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            e = r.json().get("entry", [{}])[0]
            log("+", C.G, "Status",       "ACCOUNT FOUND")
            log("+", C.G, "Display Name", e.get("displayName", "N/A"))
            log("+", C.G, "Location",     e.get("currentLocation", "N/A"))
            log("+", C.G, "About",        e.get("aboutMe", "N/A"))
            log("+", C.CY,"Profile URL",  e.get("profileUrl", "N/A"))
            log("+", C.CY,"Avatar",       f"https://www.gravatar.com/avatar/{h}?s=200")
            accounts = e.get("accounts", [])
            if accounts:
                print(f"  {C.M}[+] {'Linked Socials':<20}:{C.X}")
                for a in accounts:
                    nm  = a.get("shortname","?").capitalize()
                    url2= a.get("url","")
                    print(f"        {C.M}→ {nm}: {url2}{C.X}")
                    _results_log.append(f"       → {nm}: {url2}")
        elif r.status_code == 404:
            log("-", C.Y, "Gravatar",     "No profile found")
        else:
            warn(f"Gravatar HTTP {r.status_code}")
    except Exception as ex:
        warn(f"Gravatar error: {ex}")


def mod_hunter(email):
    section("HUNTER.IO — Email Intelligence")
    if not HUNTER_KEY:
        warn("Hunter.io API key not set → add to config.ini")
        warn("Get free key: https://hunter.io/users/sign_up")
        return
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_KEY}"
    try:
        r = requests.get(url, timeout=10)
        d = r.json().get("data", {})
        status     = d.get("status", "?")
        score      = d.get("score", "?")
        disposable = d.get("disposable", False)
        webmail    = d.get("webmail", False)
        first      = d.get("first_name","")
        last       = d.get("last_name","")
        col = C.G if status == "valid" else C.R
        log("+", col, "Status",       status.upper())
        log("+", C.W, "Score",        f"{score}/100")
        log("+", C.W, "Disposable",   "Yes" if disposable else "No")
        log("+", C.W, "Webmail",      "Yes" if webmail else "No")
        if first or last:
            log("+", C.G, "Name Found",  f"{first} {last}".strip())
        else:
            log("-", C.Y, "Name",        "Not found via Hunter")
    except Exception as ex:
        warn(f"Hunter.io error: {ex}")


def mod_hibp(email):
    section("HAVEIBEENPWNED — Breach Check")
    if not HIBP_KEY:
        warn("HIBP API key not set → add to config.ini")
        warn("Get key: https://haveibeenpwned.com/API/Key (~$3.50 one-time)")
        return
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}"
    headers = {"hibp-api-key": HIBP_KEY, "User-Agent": "OSINTool-Python"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            breaches = r.json()
            log("!", C.R, "BREACHED",    f"Found in {len(breaches)} breach(es)!")
            for b in breaches[:8]:
                classes = ", ".join(b.get("DataClasses", [])[:3])
                print(f"    {C.R}[!] {b['Name']:<22} | Date: {b.get('BreachDate','?')} | {classes}{C.X}")
                _results_log.append(f"    [!] {b['Name']:<22} | Date: {b.get('BreachDate','?')} | {classes}")
            if len(breaches) > 8:
                print(f"    {C.R}[!] ... and {len(breaches)-8} more breaches{C.X}")
        elif r.status_code == 404:
            log("+", C.G, "HIBP",        "Email NOT found in any known breach")
        elif r.status_code == 401:
            warn("Invalid HIBP API key")
        elif r.status_code == 429:
            warn("HIBP rate limited — wait 1 minute")
        else:
            warn(f"HIBP HTTP {r.status_code}")
    except Exception as ex:
        warn(f"HIBP error: {ex}")


def mod_github_email(email):
    section("GITHUB — Commit Search")
    url = f"https://api.github.com/search/commits?q=author-email:{email}"
    headers = {"Accept": "application/vnd.github.cloak-preview"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data  = r.json()
            total = data.get("total_count", 0)
            if total > 0:
                log("+", C.G, "GitHub Commits", str(total))
                for item in data.get("items", [])[:3]:
                    commit = item.get("commit", {})
                    author = commit.get("author", {})
                    repo   = item.get("repository", {}).get("full_name", "?")
                    name   = author.get("name", "?")
                    log("+", C.G,  "Author Name",   name, indent=1)
                    log("+", C.CY, "Repository",    repo, indent=1)
                    log("+", C.CY, "Commit URL",    item.get("html_url",""), indent=1)
                    print()
            else:
                log("-", C.Y, "GitHub", "No public commits found")
        elif r.status_code == 403:
            warn("GitHub rate limited (unauthenticated)")
        else:
            warn(f"GitHub HTTP {r.status_code}")
    except Exception as ex:
        warn(f"GitHub error: {ex}")


def mod_sherlock(usernames):
    section("SHERLOCK — Username Recon on 300+ Sites")
    if not usernames:
        warn("No username could be guessed — skipping Sherlock")
        return

    # Check if sherlock is installed
    sherlock_cmd = None
    for cmd in ["sherlock", "python -m sherlock"]:
        try:
            r = subprocess.run(cmd.split() + ["--help"],
                               capture_output=True, timeout=5)
            if r.returncode == 0 or b"usage" in r.stdout.lower():
                sherlock_cmd = cmd.split()
                break
        except Exception:
            pass

    if not sherlock_cmd:
        warn("Sherlock not found!")
        warn("Install: pip install sherlock-project")
        warn(f"Then run manually: sherlock {' '.join(usernames)}")
        return

    print(f"  {C.CY}[*] Running Sherlock on: {', '.join(usernames)}{C.X}")
    _results_log.append(f"[*] Sherlock targets: {', '.join(usernames)}")
    try:
        result = subprocess.run(
            sherlock_cmd + usernames + ["--print-found"],
            capture_output=False,   # Show live output
            timeout=120
        )
    except subprocess.TimeoutExpired:
        warn("Sherlock timed out after 2 minutes")
    except Exception as ex:
        warn(f"Sherlock error: {ex}")

def guess_usernames(name_str, email):
    """Generate username candidates from name and email"""
    candidates = set()
    # From email local part
    local = email.split("@")[0].lower()
    candidates.add(local)
    candidates.add(local.replace(".", ""))
    candidates.add(local.replace("_", ""))
    candidates.add(local.replace("-", ""))

    # From name
    if name_str and name_str.strip():
        parts = name_str.lower().split()
        if len(parts) >= 1:
            candidates.add(parts[0])
        if len(parts) >= 2:
            candidates.add(parts[0] + parts[-1])
            candidates.add(parts[0] + "." + parts[-1])
            candidates.add(parts[0] + "_" + parts[-1])
            candidates.add(parts[0][0] + parts[-1])
    return [u for u in list(candidates)[:5] if len(u) >= 3]


# ══════════════════════════════════════════════════════════
#  PHONE MODULES
# ══════════════════════════════════════════════════════════

def mod_phone_offline(phone):
    section("OFFLINE ANALYSIS — phonenumbers Library")
    try:
        import phonenumbers as pn
        from phonenumbers import geocoder, carrier, timezone as tz
    except ImportError:
        warn("phonenumbers not installed → run: pip install phonenumbers")
        return

    try:
        parsed   = pn.parse(phone)
        valid    = pn.is_valid_number(parsed)
        possible = pn.is_possible_number(parsed)
        country  = geocoder.description_for_number(parsed, "en")
        carrier_ = carrier.name_for_number(parsed, "en")
        zones    = tz.time_zones_for_number(parsed)
        num_type = pn.number_type(parsed)
        type_map = {
            0: "Fixed Line", 1: "Mobile", 2: "Fixed or Mobile",
            3: "Toll Free", 4: "Premium Rate", 6: "VOIP",
            7: "Personal Number", 10: "Unknown"
        }
        e164  = pn.format_number(parsed, pn.PhoneNumberFormat.E164)
        intl  = pn.format_number(parsed, pn.PhoneNumberFormat.INTERNATIONAL)
        natl  = pn.format_number(parsed, pn.PhoneNumberFormat.NATIONAL)

        col = C.G if valid else C.R
        log("+", col, "Valid",          "Yes ✓" if valid else "No ✗")
        log("+", col, "Possible",       "Yes" if possible else "No")
        log("+", C.G, "Country",        country or "Unknown")
        log("+", C.G, "Carrier",        carrier_ or "Unknown / Not detected")
        log("+", C.G, "Line Type",      type_map.get(num_type, "Unknown"))
        log("+", C.G, "Timezone(s)",    ", ".join(zones) if zones else "Unknown")
        log("+", C.CY,"E.164 Format",   e164)
        log("+", C.CY,"International",  intl)
        log("+", C.CY,"National",       natl)

    except Exception as ex:
        warn(f"phonenumbers error: {ex}")
        warn("Ensure number has country code e.g. +919876543210")


def mod_numverify(phone):
    section("NUMVERIFY — Online Phone Validation")
    if not NUMVERIFY_KEY:
        warn("Numverify API key not set → add to config.ini")
        warn("Get free key (100/mo): https://numverify.com")
        return
    clean = phone.lstrip("+")
    url   = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={clean}"
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        if d.get("valid"):
            log("+", C.G, "Valid",       "Yes")
            log("+", C.G, "Country",     f"{d.get('country_name','?')} ({d.get('country_code','?')})")
            log("+", C.G, "Location",    d.get("location","?"))
            log("+", C.G, "Carrier",     d.get("carrier","?"))
            log("+", C.G, "Line Type",   d.get("line_type","?"))
        else:
            err = d.get("error", {})
            log("-", C.Y, "Numverify",   f"Invalid/not found: {err.get('info','unknown error')}")
    except Exception as ex:
        warn(f"Numverify error: {ex}")


def mod_abstract_phone(phone):
    section("ABSTRACTAPI — Extended Phone Intelligence")
    if not ABSTRACT_KEY:
        warn("AbstractAPI key not set → add to config.ini")
        warn("Get free key (250/mo): https://app.abstractapi.com/api/phone-validation")
        return
    url = f"https://phonevalidation.abstractapi.com/v1/?api_key={ABSTRACT_KEY}&phone={phone}"
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        valid = d.get("valid", False)
        col = C.G if valid else C.R
        log("+", col, "Valid",          "Yes" if valid else "No")
        log("+", C.G, "Country",        d.get("country", {}).get("name","?"))
        log("+", C.G, "Carrier",        d.get("carrier","?"))
        log("+", C.G, "Type",           d.get("type","?"))
        log("+", C.CY,"Format",         d.get("format",{}).get("international","?"))
    except Exception as ex:
        warn(f"AbstractAPI error: {ex}")


# ══════════════════════════════════════════════════════════
#  SCAN ORCHESTRATORS
# ══════════════════════════════════════════════════════════

def scan_email(email, run_sherlock=True, save=False):
    print(f"\n{C.BD}{C.G}  TARGET EMAIL : {email}{C.X}")
    _results_log.append(f"TARGET EMAIL: {email}")

    discovered_name = ""

    # Run modules
    mod_gravatar(email)
    mod_hunter(email)
    mod_hibp(email)
    mod_github_email(email)

    # Sherlock — guess username from name (if we got one from Hunter/Gravatar)
    if run_sherlock:
        usernames = guess_usernames(discovered_name, email)
        print(f"\n{C.CY}  [*] Guessed usernames: {', '.join(usernames)}{C.X}")
        _results_log.append(f"[*] Guessed usernames: {', '.join(usernames)}")
        mod_sherlock(usernames)

    # Footer
    print(f"\n{C.BD}{C.B}{'═'*54}{C.X}")
    print(f"{C.BD}{C.B}  ✓ EMAIL SCAN COMPLETE: {email}{C.X}")
    print(f"{C.BD}{C.B}{'═'*54}{C.X}\n")

    if save:
        save_results(email)


def scan_phone(phone, save=False):
    # Normalize
    if not phone.startswith("+"):
        phone = "+" + phone

    print(f"\n{C.BD}{C.G}  TARGET PHONE : {phone}{C.X}")
    _results_log.append(f"TARGET PHONE: {phone}")

    mod_phone_offline(phone)
    mod_numverify(phone)
    mod_abstract_phone(phone)

    # Footer
    print(f"\n{C.BD}{C.B}{'═'*54}{C.X}")
    print(f"{C.BD}{C.B}  ✓ PHONE SCAN COMPLETE: {phone}{C.X}")
    print(f"{C.BD}{C.B}{'═'*54}{C.X}\n")

    if save:
        save_results(phone)


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="OSINT Tool — Email & Phone Intelligence",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  python osint_tool.py -t user@gmail.com
  python osint_tool.py -t +919876543210
  python osint_tool.py -t user@gmail.com --save
  python osint_tool.py -t user@gmail.com --no-sherlock"""
    )
    parser.add_argument("-t", "--target",     required=True,
                        help="Target email address OR phone number (+91XXXXXXXXXX)")
    parser.add_argument("--save",             action="store_true",
                        help="Save results to a .txt file")
    parser.add_argument("--no-sherlock",      action="store_true",
                        help="Skip Sherlock username recon")
    args = parser.parse_args()

    banner()

    target = args.target.strip()
    EMAIL_RE = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"

    print(f"{C.B}[*] Starting OSINT Scan...{C.X}")
    print(f"{C.DIM}    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.X}")

    if re.match(EMAIL_RE, target):
        scan_email(target,
                   run_sherlock=not args.no_sherlock,
                   save=args.save)
    else:
        scan_phone(target, save=args.save)


if __name__ == "__main__":
    main()
