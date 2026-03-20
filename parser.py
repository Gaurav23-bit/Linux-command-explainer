"""
parser.py - Command parsing engine for Linux Command Explainer
"""

import shlex
import json
import os
import re
from typing import Optional

# Data files live in the same directory as this script
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_json(filename: str) -> dict:
    filepath = os.path.join(_BASE_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] Data file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse {filepath}: {e}")
        return {}


COMMANDS_DB: dict = _load_json("commands.json")
FLAGS_DB: dict = _load_json("flags.json")


def tokenize(command: str) -> list[str]:
    command = command.strip()
    if not command:
        return []
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _is_flag(token: str) -> bool:
    return token.startswith("-") and len(token) > 1


def _is_path(token: str) -> bool:
    return (
        token.startswith("/")
        or token.startswith("~/")
        or token.startswith("./")
        or token.startswith("../")
        or token == "~"
    )


def _is_glob(token: str) -> bool:
    return any(c in token for c in ("*", "?", "[", "]", "{", "}"))


def _is_pipe_or_redirect(token: str) -> bool:
    return token in ("|", "||", "&&", ";", ">", ">>", "<", "<<", "2>", "2>>", "&")


def _get_command_explanation(token: str) -> Optional[str]:
    return COMMANDS_DB.get(token.lower())


def _get_flag_explanation(flag: str) -> Optional[str]:
    if flag in FLAGS_DB:
        return FLAGS_DB[flag]
    if re.match(r'^-[a-zA-Z]{2,}$', flag):
        explanations = []
        for char in flag[1:]:
            single = f"-{char}"
            if single in FLAGS_DB:
                explanations.append(f"  -{char}: {FLAGS_DB[single]}")
        if explanations:
            return "Combined flags:\n" + "\n".join(explanations)
    return None


def _get_glob_explanation(token: str) -> str:
    parts = []
    if "*" in token:
        parts.append("* matches any number of characters")
    if "?" in token:
        parts.append("? matches exactly one character")
    if "[" in token:
        parts.append("[ ] matches characters inside the brackets")
    base = re.sub(r'[\*\?\[\]{}].*', '', token).rstrip("/")
    prefix = f"Path pattern targeting '{base}' — " if base else "Glob pattern — "
    return prefix + ("; ".join(parts) if parts else "contains wildcard characters")


def _categorize_token(index: int, tokens: list[str]) -> dict:
    token = tokens[index]

    if _is_pipe_or_redirect(token):
        op_map = {
            "|":   ("PIPE",     "Pipe — sends output of the left command as input to the right"),
            "||":  ("OPERATOR", "OR — runs the right command only if the left one fails"),
            "&&":  ("OPERATOR", "AND — runs the right command only if the left one succeeds"),
            ";":   ("OPERATOR", "Semicolon — runs commands sequentially regardless of success"),
            ">":   ("REDIRECT", "Output redirect — writes stdout to a file (overwrites)"),
            ">>":  ("REDIRECT", "Append redirect — appends stdout to a file"),
            "<":   ("REDIRECT", "Input redirect — reads stdin from a file"),
            "<<":  ("REDIRECT", "Here-document — provides multi-line input in the shell"),
            "2>":  ("REDIRECT", "Error redirect — redirects stderr to a file"),
            "2>>": ("REDIRECT", "Append error redirect — appends stderr to a file"),
            "&":   ("OPERATOR", "Background — runs the preceding command in the background"),
        }
        if token in op_map:
            cat, expl = op_map[token]
            return {"token": token, "category": cat, "explanation": expl}

    PASSTHROUGH = ("sudo", "nohup", "env", "time", "watch", "xargs",
                   "nice", "ionice", "timeout", "strace", "ltrace")
    is_cmd_pos = (
        index == 0
        or (index > 0 and _is_pipe_or_redirect(tokens[index - 1]))
        or (index > 0 and tokens[index - 1] in PASSTHROUGH)
    )

    if is_cmd_pos:
        explanation = _get_command_explanation(token)
        if explanation:
            return {"token": token, "category": "COMMAND", "explanation": explanation}
        return {"token": token, "category": "COMMAND",
                "explanation": f"'{token}' — not found in database; may be a script, alias, or custom command."}

    if _is_flag(token):
        explanation = _get_flag_explanation(token)
        if explanation:
            return {"token": token, "category": "FLAG", "explanation": f"{token}: {explanation}"}
        return {"token": token, "category": "FLAG",
                "explanation": f"{token}: Unknown flag — check the command's man page."}

    if _is_glob(token):
        return {"token": token, "category": "GLOB", "explanation": _get_glob_explanation(token)}

    if _is_path(token):
        path_desc = f"Path: '{token}'"
        if token in ("/", "~"):
            path_desc = "Root directory — top of the Linux filesystem" if token == "/" else "Home directory"
        elif token.startswith("/dev/"):
            path_desc = f"Device file: '{token}' — represents a hardware or virtual device"
        elif token.startswith("/etc/"):
            path_desc = f"Configuration path: '{token}'"
        elif token.startswith("/var/"):
            path_desc = f"Variable data path: '{token}' (logs, caches, runtime data)"
        elif token.startswith("/tmp/"):
            path_desc = f"Temporary path: '{token}' — cleared on reboot"
        elif token.startswith("/home/"):
            path_desc = f"User home directory: '{token}'"
        elif token.startswith("/usr/"):
            path_desc = f"User programs path: '{token}'"
        elif token.startswith("~/"):
            path_desc = f"Path inside home directory: '{token}'"
        return {"token": token, "category": "PATH", "explanation": path_desc}

    if token.startswith("$"):
        return {"token": token, "category": "VARIABLE",
                "explanation": f"Shell variable '{token}' — expands to its value at runtime"}

    if token.lstrip("-").isdigit():
        return {"token": token, "category": "ARGUMENT", "explanation": f"Numeric argument: {token}"}

    return {"token": token, "category": "ARGUMENT",
            "explanation": f"Argument: '{token}' — passed as a parameter to the preceding command or flag"}


def parse_command(command: str) -> dict:
    command = command.strip()
    if not command:
        return {"raw": "", "tokens": [], "components": [], "summary": "No command entered."}

    tokens = tokenize(command)
    if not tokens:
        return {"raw": command, "tokens": [], "components": [], "summary": "Could not parse the command."}

    components = [_categorize_token(i, tokens) for i in range(len(tokens))]

    base_cmd = tokens[0]
    base_expl = _get_command_explanation(base_cmd)
    summary = f"'{base_cmd}': {base_expl}" if base_expl else f"'{base_cmd}': Command not found in database."

    return {"raw": command, "tokens": tokens, "components": components, "summary": summary}


if __name__ == "__main__":
    tests = ["sudo rm -rf /var/cache/*", "ls -la /home", "grep -r 'pat' /etc/ | sort"]
    for cmd in tests:
        r = parse_command(cmd)
        print(f"{cmd}\n  tokens={r['tokens']}\n  summary={r['summary']}\n")
