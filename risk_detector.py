"""
risk_detector.py - Risk Detection Engine for Linux Command Explainer
"""

import json
import os
import re
from typing import Optional

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RISK_LEVEL_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "SAFE": 0}

RISK_COLORS = {
    "CRITICAL": "#FF2020",
    "HIGH":     "#FF7A00",
    "MEDIUM":   "#F5C400",
    "LOW":      "#4BB9FF",
    "SAFE":     "#3ECF6A",
}

RISK_ICONS = {
    "CRITICAL": "☠",
    "HIGH":     "⚠",
    "MEDIUM":   "⚡",
    "LOW":      "ℹ",
    "SAFE":     "✔",
}


def _load_risk_rules() -> dict:
    filepath = os.path.join(_BASE_DIR, "risk_rules.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] risk_rules.json not found at {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse risk_rules.json: {e}")
        return {}


_RULES: dict = _load_risk_rules()


def _compile_pattern(pattern: str) -> Optional[re.Pattern]:
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        print(f"[WARNING] Invalid regex '{pattern}': {e}")
        return None


def detect_risks(command: str) -> dict:
    command = command.strip()
    if not command:
        return _build_result(command, "SAFE", [])

    matches = []
    highest_level = "SAFE"
    seen_titles = set()

    for category_key, expected_level in [
        ("critical_patterns", "CRITICAL"),
        ("high_patterns",     "HIGH"),
        ("medium_patterns",   "MEDIUM"),
        ("low_patterns",      "LOW"),
    ]:
        for rule in _RULES.get(category_key, []):
            title = rule.get("title", "")
            if title in seen_titles:
                continue
            compiled = _compile_pattern(rule.get("pattern", ""))
            if compiled and compiled.search(command):
                level = rule.get("level", expected_level)
                seen_titles.add(title)
                matches.append({
                    "level":   level,
                    "title":   title,
                    "message": rule.get("message", ""),
                    "color":   RISK_COLORS.get(level, "#FFFFFF"),
                    "icon":    RISK_ICONS.get(level, "•"),
                })
                if RISK_LEVEL_ORDER.get(level, 0) > RISK_LEVEL_ORDER.get(highest_level, 0):
                    highest_level = level

    matches.sort(key=lambda m: RISK_LEVEL_ORDER.get(m["level"], 0), reverse=True)
    return _build_result(command, highest_level, matches)


def _build_result(command, level, matches):
    return {
        "command":       command,
        "overall_level": level,
        "overall_color": RISK_COLORS.get(level, "#3ECF6A"),
        "overall_icon":  RISK_ICONS.get(level, "✔"),
        "matches":       matches,
    }


if __name__ == "__main__":
    for cmd in ["sudo rm -rf /", "ls -la /home", "chmod 777 /etc/passwd"]:
        r = detect_risks(cmd)
        print(f"{cmd}\n  level={r['overall_level']}  warnings={len(r['matches'])}\n")
