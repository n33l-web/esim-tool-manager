
import json

from core.detector import check_tool
from core.installer import install_tool


# Load tool information
with open("config/tools.json") as file:
    TOOLS = json.load(file)


def check_all_tools():

    for name, info in TOOLS.items():

        result = check_tool(
            info["executable"],
            info["version_args"]
        )

        print("\nTool:", name)

        if result["installed"]:
            print("Status: Installed")
            print("Version:", result["version"])
            print("Path:", result["path"])
        else:
            print("Status: Missing")


def install_selected_tool(name):

    if name not in TOOLS:
        print("Unknown tool:", name)
        return

    info = TOOLS[name]

    # Check if already installed
    result = check_tool(
        info["executable"],
        info["version_args"]
    )

    if result["installed"]:
        print(name, "is already installed.")
        print("Version:", result["version"])
        return

    # Ask permission
    choice = input(
        "Do you want to install " + name + "? (y/n): "
    )

    if choice.lower() != "y":
        print("Installation cancelled.")
        return

    success = install_tool(name, info)

    if success:

        # Verify installation
        result = check_tool(
            info["executable"],
            info["version_args"]
        )

        if result["installed"]:
            print("Installation verified!")
            print("Version:", result["version"])
        else:
            print("Installation ran, but verification failed.")


if __name__ == "__main__":

    print("================================")
    print("       eSim TOOL MANAGER")
    print("================================")

    print("1. Check installed tools")
    print("2. Install a tool")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        check_all_tools()

    elif choice == "2":

        name = input("Enter tool name: ").lower()

        install_selected_tool(name)

    else:
        print("Invalid choice.")
