import json
import shutil
import subprocess
import logging
from pathlib import Path

from core.platform_utils import detect_os, detect_package_manager


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "tools.json"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_tools():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_tool_info(tool_name):
    tools = load_tools()

    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")

    return tools[tool_name]


def get_package_info(tool_name):
    tool = get_tool_info(tool_name)
    os_name = detect_os()

    package_info = tool.get("packages", {}).get(os_name)

    if not package_info:
        raise RuntimeError(
            f"{tool_name} is not configured for {os_name}"
        )

    return tool, package_info


def run_command(command):
    """
    Run a command safely without using shell=True.
    Return the command output and exit status.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        output = (result.stdout or "") + (result.stderr or "")

        return result.returncode, output.strip()

    except FileNotFoundError:
        return 1, f"Command not found: {command[0]}"

    except Exception as error:
        return 1, str(error)


def check_tool(tool_name):
    """
    Check whether a tool executable is available
    and retrieve its version information.
    """
    tool = get_tool_info(tool_name)
    executable = tool["executable"]

    executable_path = shutil.which(executable)

    if not executable_path:
        return {
            "name": tool["display_name"],
            "installed": False,
            "path": None,
            "version": "Not found"
        }

    command = [executable_path] + tool.get("version_args", ["--version"])
    return_code, output = run_command(command)

    return {
        "name": tool["display_name"],
        "installed": True,
        "path": executable_path,
        "version": output if output else "Version unavailable"
    }


def build_install_command(manager, package_id):
    if manager == "winget":
        return [
            "winget", "install",
            "--id", package_id,
            "--exact",
            "--accept-package-agreements",
            "--accept-source-agreements"
        ]

    elif manager == "apt":
        return ["sudo", "apt-get", "install", package_id]

    elif manager == "dnf":
        return ["sudo", "dnf", "install", package_id]

    elif manager == "pacman":
        return ["sudo", "pacman", "-S", package_id]

    elif manager == "brew":
        return ["brew", "install", package_id]

    elif manager == "choco":
        return ["choco", "install", package_id, "-y"]

    raise RuntimeError(f"Unsupported package manager: {manager}")


def build_upgrade_command(manager, package_id):
    if manager == "winget":
        return [
            "winget", "upgrade",
            "--id", package_id,
            "--exact",
            "--accept-package-agreements",
            "--accept-source-agreements"
        ]

    elif manager == "apt":
        return ["sudo", "apt-get", "install", "--only-upgrade", package_id]

    elif manager == "dnf":
        return ["sudo", "dnf", "upgrade", package_id]

    elif manager == "pacman":
        return ["sudo", "pacman", "-S", package_id]

    elif manager == "brew":
        return ["brew", "upgrade", package_id]

    elif manager == "choco":
        return ["choco", "upgrade", package_id, "-y"]

    raise RuntimeError(f"Unsupported package manager: {manager}")


def install_tool(tool_name):
    """
    Install a tool using the configured package manager.
    """
    tool, package_info = get_package_info(tool_name)

    manager = package_info["manager"]
    package_id = package_info["package_id"]

    if not shutil.which(manager):
        print(f"{manager} is not installed or not available in PATH.")
        return False

    current = check_tool(tool_name)

    if current["installed"]:
        print(f"{tool['display_name']} is already installed.")
        print(f"Version information: {current['version']}")
        return True

    command = build_install_command(manager, package_id)

    print(f"Installing {tool['display_name']}...")
    logging.info("Installing %s using %s", tool_name, manager)

    return_code, output = run_command(command)

    print(output)

    if return_code == 0:
        logging.info("Installation command completed for %s", tool_name)
        print("Installation command completed.")

        result = check_tool(tool_name)

        if result["installed"]:
            print("Installation verified.")
            print("Version:", result["version"])
            return True

        print(
            "The package manager finished, but the executable "
            "was not found in PATH. Restart the terminal or check "
            "the tool's installation location."
        )
        return False

    logging.error("Installation failed for %s: %s", tool_name, output)
    print("Installation failed.")
    return False


def check_for_updates(tool_name):
    """
    Ask the package manager whether an update is available.
    """
    tool, package_info = get_package_info(tool_name)

    manager = package_info["manager"]
    package_id = package_info["package_id"]

    if not shutil.which(manager):
        return {
            "supported": False,
            "update_available": None,
            "message": f"{manager} is not available."
        }

    if manager == "winget":
        command = [
            "winget", "upgrade",
            "--id", package_id,
            "--exact"
        ]

    elif manager == "brew":
        command = ["brew", "outdated", package_id]

    elif manager == "apt":
        command = ["apt", "list", "--upgradable"]

    elif manager == "dnf":
        command = ["dnf", "check-update", package_id]

    elif manager == "pacman":
        command = ["pacman", "-Qu", package_id]

    elif manager == "choco":
        command = ["choco", "outdated", package_id]

    else:
        return {
            "supported": False,
            "update_available": None,
            "message": "Unsupported package manager."
        }

    return_code, output = run_command(command)

    if manager == "winget":
        lower_output = output.lower()

        if "no applicable upgrade found" in lower_output:
            available = False
        elif return_code == 0 and package_id.lower() in lower_output:
            available = True
        else:
            available = None

    elif manager == "brew":
        available = bool(output.strip()) if return_code == 0 else None

    elif manager == "apt":
        available = (
            package_id.lower() in output.lower()
            and return_code == 0
        )

    elif manager == "dnf":
        available = return_code == 100 or (
            return_code == 0 and bool(output.strip())
        )

    elif manager == "pacman":
        available = bool(output.strip()) if return_code == 0 else None

    elif manager == "choco":
        available = (
            return_code == 0 and
            package_id.lower() in output.lower()
        )

    else:
        available = None

    return {
        "supported": True,
        "update_available": available,
        "message": output or "No update information returned."
    }


def upgrade_tool(tool_name):
    """
    Upgrade one selected tool.
    """
    tool, package_info = get_package_info(tool_name)

    manager = package_info["manager"]
    package_id = package_info["package_id"]

    if not shutil.which(manager):
        print(f"{manager} is not available.")
        return False

    status = check_for_updates(tool_name)

    if not status["supported"]:
        print(status["message"])
        return False

    if status["update_available"] is False:
        print(f"{tool['display_name']} is already up to date.")
        return True

    if status["update_available"] is None:
        print("Could not determine update availability.")
        print(status["message"])
        return False

    print(f"An update is available for {tool['display_name']}.")
    confirmation = input("Do you want to upgrade? (y/n): ").strip().lower()

    if confirmation != "y":
        print("Upgrade cancelled.")
        return False

    command = build_upgrade_command(manager, package_id)

    print(f"Upgrading {tool['display_name']}...")
    logging.info("Upgrading %s using %s", tool_name, manager)

    return_code, output = run_command(command)

    print(output)

    if return_code == 0:
        logging.info("Upgrade command completed for %s", tool_name)
        print("Upgrade command completed.")
        print("Check the installed version again to verify.")
        return True

    logging.error("Upgrade failed for %s: %s", tool_name, output)
    print("Upgrade failed.")
    return False