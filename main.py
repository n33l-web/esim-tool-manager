from core.manager import (
    load_tools,
    check_tool,
    install_tool,
    check_for_updates,
    upgrade_tool
)

from core.platform_utils import detect_os, detect_package_manager


def display_tools(tools):
    print("\nAvailable tools:")

    for index, (key, tool) in enumerate(tools.items(), start=1):
        print(f"{index}. {tool['display_name']} ({key})")


def select_tool(tools):
    display_tools(tools)

    choice = input("\nEnter tool name: ").strip().lower()

    if choice not in tools:
        print("Invalid tool name.")
        return None

    return choice


def main():
    try:
        tools = load_tools()
    except Exception as error:
        print("Could not load tool configuration:", error)
        return

    while True:
        print("\n================================")
        print("       eSim AUTOMATED TOOL MANAGER")
        print("================================")
        print("Operating System:", detect_os())
        print("Available Package Manager:", detect_package_manager())
        print("--------------------------------")
        print("1. List available tools")
        print("2. Check installed tool and version")
        print("3. Install a tool")
        print("4. Check for updates")
        print("5. Upgrade a tool")
        print("6. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            display_tools(tools)

        elif choice == "2":
            name = select_tool(tools)

            if name:
                result = check_tool(name)

                print("\nTool:", result["name"])
                print("Installed:", result["installed"])
                print("Path:", result["path"])
                print("Version:", result["version"])

        elif choice == "3":
            name = select_tool(tools)

            if name:
                install_tool(name)

        elif choice == "4":
            name = select_tool(tools)

            if name:
                result = check_for_updates(name)

                print("\nUpdate check:")
                print("Supported:", result["supported"])
                print("Update available:", result["update_available"])
                print("Details:", result["message"])

        elif choice == "5":
            name = select_tool(tools)

            if name:
                upgrade_tool(name)

        elif choice == "6":
            print("Exiting eSim Tool Manager.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()