"""Open or create ADS workspace and library, then launch ADS"""

from keysight.ads import de
import subprocess
import os
from pathlib import Path

# 定位项目根目录（python_wrk 位于根目录下；本脚本位于 ADS/ads_tools/ 下，上溯三级）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

workspace_path = str(_PROJECT_ROOT / "python_wrk")
library_name = "python_lib"
ads_exe = os.environ.get("HPEESOF_DIR", "") + r"\bin\ads.exe"

# Open or create workspace
if de.workspace_is_open():
    workspace = de.active_workspace()
    print(f"Using already open workspace: {workspace.path}")
elif de.directory_is_workspace(workspace_path):
    workspace = de.open_workspace(workspace_path)
    print(f"Workspace opened: {workspace_path}")
else:
    workspace = de.create_workspace(workspace_path)
    workspace.open()
    print(f"Workspace created: {workspace_path}")

# Open or create library
library_path = workspace.path / library_name
if de.library_exists_at_path(library_path):
    if not de.library_is_open(library_name):
        lib = workspace.open_library(library_name, library_path, de.LibraryMode.SHARED)
    else:
        lib = de.get_open_library(library_name)
    print(f"Library opened: {library_name}")
else:
    de.create_new_library(library_name, library_path)
    workspace.add_library(library_name, library_path, de.LibraryMode.SHARED)
    lib = workspace.open_library(library_name, library_path, de.LibraryMode.SHARED)
    print(f"Library created: {library_name}")

# Close workspace in Python
de.close_workspace()

# Launch ADS if not already running
# Use Get-Process to avoid false positive from lkads.exe (licensing process)
ps_check = subprocess.run(
    ["powershell", "-Command", "Get-Process -Name ads -ErrorAction SilentlyContinue"],
    capture_output=True, text=True
)
if ps_check.stdout.strip():
    print("ADS is already running.")
else:
    print("Launching ADS...")
    subprocess.Popen([ads_exe])
        