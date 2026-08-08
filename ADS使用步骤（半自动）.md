1.先手动打开ADS或者使用指令打开ADS

   手动：双击桌面图标 "Advanced Design System 2025 Update 2 (64-bit Simulations)"
   （该图标实际指向：D:\Program Files\Keysight\ADS2025_Update2\bin\ads.exe）

   指令（PowerShell）：
       $env:HPEESOF_DIR = "D:\Program Files\Keysight\ADS2025_Update2"
       Start-Process "$env:HPEESOF_DIR\bin\ads.exe"

   指令（CMD / 运行框 Win+R）：
       start "" "D:\Program Files\Keysight\ADS2025_Update2\bin\ads.exe"

   注意：启动时不加 -ws 参数（让 ADS 自动恢复上次 workspace）；
         若 ads.exe 已在运行，则不要重复启动新实例。

2.打开ADS的python console

   手动：菜单 Tools > Python Console（快捷键 Ctrl+Shift+P）

   自动（一键脚本，未开 ADS 会自动先启动它）：
       powershell -ExecutionPolicy Bypass -File ADS\ads_tools\open_ads_console.ps1

   自动（等价的一行指令）：
       $ws = New-Object -ComObject WScript.Shell
       $ws.AppActivate((Get-Process hpeesofde | ? {$_.MainWindowHandle -ne 0} | select -First 1).Id)
       Start-Sleep -Milliseconds 800
       $ws.SendKeys("^+p")

   说明：ADS 没有开放"直接打开 Python Console"的程序接口，
         自动方式是通过模拟快捷键 Ctrl+Shift+P 触发。
         运行后 ADS 需在前台；若焦点被抢走导致未弹出，再手动点一次菜单即可。

3.和VScode的python建立联系（ADS Live Server（XML RPC 桥））

   【ADS 侧】在 ADS 的 Python Console 里输入（两行都顶格、无缩进，否则报 IndentationError）：
exec(open(r'D:\AppGallery\codex\ADS\ads_tools\ads_live_server.py', encoding='utf-8').read())
start_server()
       看到 "ADS Live Server listening on 127.0.0.1:8765" 即成功
       （服务器运行在 127.0.0.1:8765，线程方式，不阻塞控制台）

   【VS Code 侧】在终端里用 ADS 自带 Python 测试连通：
       $env:HPEESOF_DIR = "D:\Program Files\Keysight\ADS2025_Update2"
       & "$env:HPEESOF_DIR\tools\python\python.exe" -c "import xmlrpc.client; p=xmlrpc.client.ServerProxy('http://127.0.0.1:8765/', allow_none=True); print(p.ping())"
       打印 "OK" 即连通

   【驱动客户端】完整演示（随机生成方块版图）：
       $env:HPEESOF_DIR = "D:\Program Files\Keysight\ADS2025_Update2"
       & "$env:HPEESOF_DIR\tools\python\python.exe" "D:\AppGallery\codex\ADS\ads_tools\ads_live_client.py"

   服务器暴露的 RPC 函数：ping、open_layout、clear_layout、add_polygon、
   add_port、save_layout、view_all、show_all_layers、show_layer、get_emsetup_info、run_em

4.成功后
   1) 可以在 VS Code 里直接编辑 ADS 的 Python Console 脚本，保存后在 ADS 里执行。
   2) 可以在 VS Code 里直接运行 ads_live_client.py，自动生成版图并打开 EM Setup。

   创建或打开workspace（修正版）
import keysight.ads.dataset as dataset   # Read simulation dataset (.ds)
import matplotlib.pyplot as plt          # Plotting
import numpy as np                       # Numerical computation
import os                                # OS interface (path operations)

from keysight.ads import de              # ADS workspace/library management
from keysight.ads.de import db_uu as db  # Schematic design operations
from keysight.edatoolbox import ads      # ADS simulator (CircuitSimulator)
from IPython.core import getipython      # Get IPython instance (for inline plotting)
from pathlib import Path                 # Path handling
from datetime import datetime            # Timestamp (for unique dataset names)


warnings.simplefilter("ignore", DeprecationWarning)

lib_name = "python_lib"          # ← 填你的库名
cell_name = "my_cell"            # ← 填你的 cell 名
wrk_path = r"D:\AppGallery\codex\python_wrk"   # ← 绝对路径，避免 __file__ 问题
lib_path = os.path.join(wrk_path, lib_name)

# PDK（如需加载 CGH40）
pdk_base = r"D:\AppGallery\ADS\adsZIP\zipped"
pdk_path = os.path.join(pdk_base, r"CGH40_r6_converted\CGH40_r6")
pdk_tech_path = os.path.join(pdk_base, r"CGH40_r6_converted\CGH40_r6_tech")


def get_library():
    # 1) 创建或打开 workspace
    if de.workspace_is_open():
        workspace = de.active_workspace()
    elif de.directory_is_workspace(wrk_path):
        workspace = de.open_workspace(wrk_path)
    else:
        workspace = de.create_workspace(wrk_path)
        workspace.open()

    # 2) 创建或打开 library
    if de.library_exists_at_path(lib_path):
        if not de.library_is_open(lib_name):
            library = workspace.open_library(lib_name, lib_path, de.LibraryMode.SHARED)
        else:
            library = de.get_open_library(lib_name)
    else:
        de.create_new_library(lib_name, lib_path)
        workspace.add_library(lib_name, lib_path, de.LibraryMode.SHARED)
        library = workspace.open_library(lib_name, lib_path, de.LibraryMode.SHARED)

    # 3) 加载 PDK（只加尚未加载的）
    for ln, lp in [("CGH40_r6", pdk_path), ("CGH40_r6_tech", pdk_tech_path)]:
        if ln in workspace.library_names:
            print(f"PDK already loaded: {ln}")
        elif os.path.isdir(lp):
            workspace.add_library(ln, lp, de.LibraryMode.READ_ONLY)
            print(f"PDK loaded: {ln}")
        else:
            print(f"PDK path not found: {lp}")

    # 4) 配置 schematic tech（跳过已配置的）
    try:
        library.setup_schematic_tech()
    except Exception:
        pass

    return library


   创建或打开cell
def get_cell(library, name=cell_name, view="schematic"):
    if not library.cell_exists(name):
        cell = library.create_cell(name)
        cell.create_view(view, "Schematic")
        print(f"cell created: {name}:{view}")
    else:
        cell = library.get_cell_if_exists(name)
    return cell


if __name__ == "__main__":
    lib = get_library()
    print("library:", lib.name)
    cell = get_cell(lib)
    print("cell:", cell.name)