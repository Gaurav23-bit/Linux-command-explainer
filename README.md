# Linux Command Explainer & Risk Detector

A lightweight cross-distro desktop application that helps you understand Linux terminal commands **before** executing them. Built with Python and Tkinter — no internet connection required.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Command Breakdown** | Splits any command into tokens and explains each one (base command, flags, paths, pipes, etc.) |
| **Risk Detection** | Detects dangerous patterns and warns you with CRITICAL / HIGH / MEDIUM / LOW / SAFE ratings |
| **200+ Commands** | Local database covering common, system, network, and package-manager commands |
| **150+ Flags** | Explanations for the most common Unix/Linux flags and options |
| **Offline** | Fully offline — no network calls, no telemetry |
| **Cross-Distro** | Runs on Ubuntu, Debian, Arch, Fedora, Mint, Manjaro, CachyOS, and any distro with Python 3.10+ |

---

## 📋 Requirements

- Python **3.10** or newer
- `tkinter` (usually bundled with Python)

### Check your Python version

```bash
python3 --version
```

### Install tkinter if missing

```bash
# Debian / Ubuntu / Mint
sudo apt install python3-tk

# Fedora / RHEL / CentOS
sudo dnf install python3-tkinter

# Arch Linux / Manjaro / CachyOS
sudo pacman -S tk

# openSUSE
sudo zypper install python3-tk

# Gentoo
sudo emerge dev-lang/python[tk]
```

---

## 🚀 Installation & Running

### 1. Clone or download the project

```bash
git clone https://github.com/yourname/linux-command-explainer.git
cd linux-command-explainer
```

### 2. Run the application

```bash
python app.py
```

No virtual environment or `pip install` required — the project uses only the Python standard library.

---

## 🗂 Project Structure

```
linux-command-explainer/
├── app.py                  # Entry point — run this
├── parser.py               # Command tokenisation & explanation engine
├── risk_detector.py        # Risk pattern matching engine
├── requirements.txt        # (No third-party dependencies)
├── README.md               # This file
├── data/
│   ├── commands.json       # Command descriptions database (200+ entries)
│   ├── flags.json          # Flag/option descriptions database (150+ entries)
│   └── risk_rules.json     # Risk detection patterns with levels and messages
└── gui/
    └── interface.py        # Tkinter GUI — layout, widgets, rendering
```

---

## 🖥 Usage

1. Launch the app: `python app.py`
2. Type any Linux command in the input box, for example:

   ```
   sudo rm -rf /var/cache/*
   ```

3. Press **Enter** or click **Explain ▶**
4. The **Breakdown** tab shows each token explained with its category
5. The **Risk Details** tab shows all triggered warnings

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Enter` | Explain the current command |
| `Ctrl+L` | Clear the input and output |
| `Esc` | Clear the input and output |

---

## ⚠ Risk Levels

| Level | Icon | Meaning |
|---|---|---|
| **CRITICAL** | ☠ | Command will likely cause severe, irreversible damage (e.g. `rm -rf /`, fork bomb, disk wipe) |
| **HIGH** | ⚠ | Command poses significant risk to data or system stability (e.g. recursive delete, forced kill, firewall flush) |
| **MEDIUM** | ⚡ | Command modifies important system settings or could cause unintended side effects |
| **LOW** | ℹ | Command uses elevated privileges or has minor implications worth noting |
| **SAFE** | ✔ | No known risks detected |

---

## 🔧 Extending the Database

The knowledge base is stored in plain JSON files under `data/`. You can add your own entries:

### Add a new command (`data/commands.json`)

```json
{
  "mycommand": "Description of what mycommand does"
}
```

### Add a new flag (`data/flags.json`)

```json
{
  "--my-flag": "Description of what --my-flag does"
}
```

### Add a new risk rule (`data/risk_rules.json`)

```json
{
  "high_patterns": [
    {
      "pattern": "\\bmydangerouscommand\\b",
      "level": "HIGH",
      "title": "Dangerous Operation",
      "message": "This command can cause X. Be careful because Y."
    }
  ]
}
```

Risk rule patterns are Python regular expressions (with `re.IGNORECASE`).

---

## 🛠 Architecture

```
app.py
  └── gui/interface.py          # Tkinter UI
        ├── parser.py           # shlex tokenisation + JSON DB lookup
        └── risk_detector.py    # Regex-based risk pattern matching
              └── data/*.json   # Knowledge base files
```

- **parser.py** uses Python's `shlex` library for POSIX-correct tokenisation, then classifies each token as COMMAND / FLAG / PATH / GLOB / PIPE / REDIRECT / OPERATOR / VARIABLE / ARGUMENT.
- **risk_detector.py** runs the full command string through a priority-ordered list of compiled regex patterns, collecting all matches and returning the highest severity level found.
- **gui/interface.py** renders results as styled card components inside a tabbed notebook widget with a scrollable content area.

---

## 📦 Compatibility

| Distribution | Status |
|---|---|
| Ubuntu 20.04+ | ✅ Tested |
| Debian 11+ | ✅ Tested |
| Linux Mint 21+ | ✅ Compatible |
| Fedora 38+ | ✅ Compatible |
| Arch Linux | ✅ Compatible |
| Manjaro | ✅ Compatible |
| CachyOS | ✅ Compatible |
| openSUSE Tumbleweed | ✅ Compatible |
| Any Python 3.10+ distro | ✅ Should work |

---

## 📄 Licence

MIT Licence — free to use, modify, and distribute.

---

## 🗺 Roadmap

- [ ] AI-powered command explanation (API integration)
- [ ] Command history analysis
- [ ] Terminal plugin integration
- [ ] VS Code extension
- [ ] Suggest safer command alternatives
- [ ] Auto-detect destructive shell scripts
- [ ] PyQt / GTK UI backends
