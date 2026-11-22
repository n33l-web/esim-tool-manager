import platform
import shutil


def detect_os():
    system = platform.system().lower()

    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    else:
        return "unknown"


def detect_package_manager():
    os_name = detect_os()

    managers = {
        "windows": ["winget", "choco"],
        "linux": ["apt", "dnf", "pacman"],
        "macos": ["brew"]
    }

    for manager in managers.get(os_name, []):
        if shutil.which(manager):
            return manager

    return None