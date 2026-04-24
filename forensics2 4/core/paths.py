"""
Кросс-платформенные пути к профилям браузеров.
Автоматически определяет Windows / macOS / Linux.
"""

import sys
from pathlib import Path


def _home() -> Path:
    return Path.home()


def get_browser_paths() -> dict[str, Path]:
    """Возвращает пути к папкам профилей для текущей ОС."""

    if sys.platform == "win32":
        local   = _home() / "AppData" / "Local"
        roaming = _home() / "AppData" / "Roaming"
        return {
            "chrome":  local   / "Google"    / "Chrome"        / "User Data",
            "edge":    local   / "Microsoft" / "Edge"          / "User Data",
            "firefox": roaming / "Mozilla"   / "Firefox"       / "Profiles",
            "brave":   local   / "BraveSoftware" / "Brave-Browser" / "User Data",
        }

    elif sys.platform == "darwin":  # macOS
        app_support = _home() / "Library" / "Application Support"
        return {
            "chrome":  app_support / "Google"    / "Chrome",
            "edge":    app_support / "Microsoft Edge",
            "firefox": app_support / "Firefox"   / "Profiles",
            "brave":   app_support / "BraveSoftware" / "Brave-Browser",
        }

    else:  # Linux
        config = _home() / ".config"
        return {
            "chrome":  config / "google-chrome",
            "edge":    config / "microsoft-edge",
            "firefox": _home() / ".mozilla" / "firefox",
            "brave":   config / "BraveSoftware" / "Brave-Browser",
        }


def get_os_name() -> str:
    return {"win32": "Windows", "darwin": "macOS"}.get(sys.platform, "Linux")
