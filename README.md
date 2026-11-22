# eSim Automated Tool Manager

## Overview

The eSim Automated Tool Manager is a Python-based application
that helps users manage the installation and updating of
engineering software tools.

This prototype focuses on:

1. Tool Installation Management
2. Update and Upgrade Management

## Features

- Detects the operating system.
- Detects available package managers.
- Maintains a configurable tool catalogue.
- Checks whether a tool executable is available.
- Retrieves installed tool version information.
- Installs tools through supported package managers.
- Checks for available package updates.
- Allows users to upgrade selected tools.
- Maintains an execution log.

## Technologies

- Python
- JSON
- subprocess
- pathlib
- logging
- Package managers: WinGet, APT, DNF, Pacman, Homebrew

## Project Structure

esim-tool-manager/
- main.py
- requirements.txt
- README.md
- config/tools.json
- core/__init__.py
- core/platform_utils.py
- core/manager.py
- logs/

## Requirements

- Python 3.10 or newer
- A supported package manager
- Internet connection for package installation and updates

## Setup

Create and activate a virtual environment.

Windows PowerShell:

    py -m venv venv
    .\venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install -r requirements.txt

## Run

    python main.py

## Supported Package Managers

- Windows: WinGet
- Linux: APT, DNF, Pacman
- macOS: Homebrew

Actual tool availability depends on the package manager's
catalogue and the configured package ID.

## Logging

Execution logs are stored in:

    logs/manager.log

## Scope

This prototype implements tool installation and update
management. Other requirements, such as dependency checking,
configuration-file management, and a graphical interface,
are outside its current scope.