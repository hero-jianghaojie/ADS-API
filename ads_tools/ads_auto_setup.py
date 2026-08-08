# -*- coding: utf-8 -*-
"""
ADS 全自动初始化脚本
运行后自动完成：
  1. 启动 ADS（如未运行）
  2. 打开 ADS 的 Python Console
  3. 在 Console 里自动启动 ADS Live Server（XML RPC, 127.0.0.1:8765）
  4. 通过 RPC 自动创建/打开 workspace、library、cell
  5. 校验连通性并报告

用法：
  python ads_auto_setup.py
  python ads_auto_setup.py --wrk D:/AppGallery/codex/python_wrk --lib python_lib --cell my_cell

注意：
  - 本脚本需要在你登录的桌面会话中运行（要操作 ADS GUI 窗口）。
  - ADS 的 Python Console 打开/注入代码依赖窗口焦点，若焦点被抢走可能失败，
    失败时会给出提示，可手动按 Ctrl+Shift+P 打开 Console 后重跑。
"""
import argparse
import ctypes
import ctypes.wintypes
import os
import subprocess
import sys
import time
import xmlrpc.client
from pathlib import Path

ADS_EXE = r"D:\Program Files\Keysight\ADS2025_Update2\bin\ads.exe"
PORT = 8765
SERVER_SCRIPT = r"D:\AppGallery\codex\ADS\ads_tools\ads_live_server.py"

# 虚拟键
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_ENTER = 0x0D
VK_P = 0x50
VK_V = 0x56
VK_ESCAPE = 0x1B
WM_CLOSE = 0x0010
KEYEVENTF_KEYUP = 0x0002

user32 = ctypes.windll.user32


# ---------------- 窗口 / 按键 ----------------
WNDENUMPROC = ctypes.WINFUNCTYPE(
    ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

kernel32 = ctypes.windll.kernel32
kernel32.CreateToolhelp32Snapshot.restype = ctypes.wintypes.HANDLE
kernel32.CreateToolhelp32Snapshot.argtypes = [ctypes.wintypes.DWORD,
                                              ctypes.wintypes.DWORD]
kernel32.CloseHandle.argtypes = [ctypes.wintypes.HANDLE]


class _PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.wintypes.DWORD),
        ("cntUsage", ctypes.wintypes.DWORD),
        ("th32ProcessID", ctypes.wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.wintypes.ULONG)),
        ("th32ModuleID", ctypes.wintypes.DWORD),
        ("cntThreads", ctypes.wintypes.DWORD),
        ("th32ParentProcessID", ctypes.wintypes.DWORD),
        ("pcPriClassBase", ctypes.wintypes.LONG),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("szExeFile", ctypes.c_wchar * 260),
    ]


kernel32.Process32FirstW.argtypes = [ctypes.wintypes.HANDLE,
                                     ctypes.POINTER(_PROCESSENTRY32W)]
kernel32.Process32NextW.argtypes = [ctypes.wintypes.HANDLE,
                                    ctypes.POINTER(_PROCESSENTRY32W)]
user32.GetWindowThreadProcessId.argtypes = [ctypes.wintypes.HWND,
                                            ctypes.POINTER(ctypes.wintypes.DWORD)]


def _window_title(hwnd):
    """返回窗口标题；无标题返回空串。"""
    n = user32.GetWindowTextLengthW(hwnd)
    if n <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


def _find_windows_by_title(substr):
    """返回所有可见且标题包含 substr 的窗口句柄（ctypes 枚举，免子进程）。"""
    found = []

    @WNDENUMPROC
    def cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            if substr.lower() in _window_title(hwnd).lower():
                found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    return found


def _process_pids_by_name(name_part):
    """枚举进程，返回 exe 文件名包含 name_part 的 PID 集合（Toolhelp32，免子进程）。"""
    pids = set()
    TH32CS_SNAPPROCESS = 0x00000002
    pe = _PROCESSENTRY32W()
    pe.dwSize = ctypes.sizeof(_PROCESSENTRY32W)
    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == -1:
        return pids
    try:
        if kernel32.Process32FirstW(snap, ctypes.byref(pe)):
            while True:
                if name_part.lower() in pe.szExeFile.lower():
                    pids.add(pe.th32ProcessID)
                if not kernel32.Process32NextW(snap, ctypes.byref(pe)):
                    break
    finally:
        kernel32.CloseHandle(snap)
    return pids


def _find_windows_by_pids(pids):
    """返回指定进程所有可见且有标题的顶层窗口句柄。"""
    if not pids:
        return []
    found = []

    @WNDENUMPROC
    def cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            pid = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value in pids and _window_title(hwnd):
                found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    return found


def find_ads_hwnd():
    """返回 ADS 主窗口句柄；未找到返回 0。
    优先按进程名 hpeesofde 定位主窗口（ADS 主窗口标题未必含
    'Advanced Design System'，仅靠标题检测曾导致永远找不到窗口而超时），
    失败再用标题回退。
    """
    wins = _find_windows_by_pids(_process_pids_by_name("hpeesofde"))
    # 排除 Get Started 等辅助窗口，优先取主窗口
    wins = [h for h in wins if "get started" not in _window_title(h).lower()]
    if not wins:
        wins = _find_windows_by_title("Advanced Design System")
    return wins[0] if wins else 0


def ads_process_running():
    """ADS GUI 主进程（hpeesofde）是否已存在（无论窗口是否就绪）。"""
    return bool(_process_pids_by_name("hpeesofde"))


def start_ads(timeout=120):
    """启动 ADS 并等待主窗口出现。返回 (hwnd, 是否本次刚启动)。"""
    hwnd = find_ads_hwnd()
    if hwnd:
        print("[1] ADS 已在运行")
        return hwnd, False
    if ads_process_running():
        # 进程已在（启动中/标题未就绪）→ 只等待，不重复启动新实例
        print("[1] ADS 进程已存在，等待主窗口出现 ...")
        started_now = False
    else:
        print("[1] 启动 ADS ...")
        subprocess.Popen([ADS_EXE])
        started_now = True
    for _ in range(timeout * 2):  # 0.5s 步进，更快感知就绪
        time.sleep(0.5)
        hwnd = find_ads_hwnd()
        if hwnd:
            print(f"[1] ADS 主窗口已就绪 (hwnd={hwnd})")
            return hwnd, started_now
    print("[1] 启动 ADS 超时")
    return 0, started_now


def _key(vk, up=False):
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP if up else 0, 0)
    time.sleep(0.015)


def _hotkey(*vks):
    for vk in vks:
        _key(vk)
    time.sleep(0.04)
    for vk in reversed(vks):
        _key(vk, up=True)
    time.sleep(0.08)


def activate(hwnd):
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)


def close_getstarted(wait_first=0.0):
    """关闭 Get Started 欢迎窗口；没有则快速返回。
    wait_first>0：先等窗口出现再处理（用于 ADS 刚启动场景）。
    """
    if not _find_windows_by_title("Get Started"):
        if wait_first <= 0:
            return True
        time.sleep(wait_first)
    for _ in range(10):
        wins = _find_windows_by_title("Get Started")
        if not wins:
            return True
        for h in wins:
            try:
                user32.SetForegroundWindow(h)
                time.sleep(0.1)
                _key(VK_ESCAPE)
                _key(VK_ESCAPE, up=True)
                user32.PostMessageW(h, WM_CLOSE, 0, 0)
            except Exception:
                pass
        time.sleep(0.3)
    return not _find_windows_by_title("Get Started")


def open_console(hwnd):
    activate(hwnd)
    _hotkey(VK_CONTROL, VK_SHIFT, VK_P)  # Ctrl+Shift+P
    time.sleep(2.0)  # 等 Console 打开


def set_clipboard(text):
    """把文本写入剪贴板（经临时文件避免编码问题）。"""
    tmp = Path(os.environ.get("TEMP", ".")) / "ads_auto_clip.txt"
    tmp.write_text(text, encoding="utf-8")
    ps = f"Get-Content -Raw -Encoding UTF8 '{tmp}' | Set-Clipboard"
    subprocess.run(["powershell", "-Command", ps], check=True, timeout=10)


def inject_text(text):
    """把文本粘贴到当前焦点并执行（Ctrl+V 粘贴，Shift+Enter 执行）。"""
    set_clipboard(text)
    time.sleep(0.2)
    _hotkey(VK_CONTROL, VK_V)  # 粘贴
    time.sleep(0.3)
    _key(VK_SHIFT)
    _key(VK_ENTER)
    _key(VK_ENTER, up=True)
    _key(VK_SHIFT, up=True)
    time.sleep(0.3)


# ---------------- RPC ----------------
def wait_server(timeout=25, interval=0.3):
    proxy = xmlrpc.client.ServerProxy(f"http://127.0.0.1:{PORT}/", allow_none=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            proxy.ping()
            return proxy
        except Exception:
            time.sleep(interval)
    return None


def setup_via_rpc(proxy, wrk, lib_name, cell_name, open_schematic=True):
    """在 ADS 内创建/打开 workspace、library、cell，并（可选）打开原理图。"""
    open_part = ""
    if open_schematic:
        open_part = '''
from keysight.ads.de import db_uu as _db
try:
    _des = _db.create_schematic(f"{lib_name}:{cell_name}:schematic")
    print("schematic opened:", _des.design_name)
except Exception as _e:
    print("open schematic warn:", repr(_e))
'''
    code = f'''
import os
from keysight.ads import de

wrk_path = r"{wrk}"
lib_name = "{lib_name}"
cell_name = "{cell_name}"
lib_path = os.path.join(wrk_path, lib_name)

if de.workspace_is_open():
    workspace = de.active_workspace()
elif de.directory_is_workspace(wrk_path):
    workspace = de.open_workspace(wrk_path)
else:
    workspace = de.create_workspace(wrk_path)
    workspace.open()

if de.library_exists_at_path(lib_path):
    if de.library_is_open(lib_name):
        library = de.get_open_library(lib_name)
    else:
        library = workspace.open_library(lib_name, lib_path, de.LibraryMode.SHARED)
else:
    de.create_new_library(lib_name, lib_path)
    workspace.add_library(lib_name, lib_path, de.LibraryMode.SHARED)
    library = workspace.open_library(lib_name, lib_path, de.LibraryMode.SHARED)

try:
    library.setup_schematic_tech()
except Exception:
    pass

if not library.cell_exists(cell_name):
    cell = library.create_cell(cell_name)
    cell.create_view("schematic", "Schematic")
    print("cell created:", cell_name)
else:
    print("cell exists:", cell_name)
{open_part}
print("workspace:", workspace.path)
print("library:", library.name)
'''
    return proxy.run_python(code)


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser(description="ADS 全自动初始化")
    ap.add_argument("--wrk", default=r"D:\AppGallery\codex\python_wrk")
    ap.add_argument("--lib", default="python_lib")
    ap.add_argument("--cell", default="my_cell")
    ap.add_argument("--no-open-schematic", action="store_true",
                    help="创建后不自动打开原理图")
    ap.add_argument("--skip-console", action="store_true",
                    help="跳过自动打开 Console（Server 已在运行）")
    args = ap.parse_args()

    # 1) ADS
    hwnd, started_now = start_ads()
    if not hwnd:
        sys.exit("无法获取 ADS 主窗口，请确认 ADS 已打开。")

    # 2) 若 server 未在跑，自动打开 Console 并注入启动代码
    proxy = wait_server(timeout=2)
    if proxy is None and not args.skip_console:
        print("[1.5] 关闭 Get Started 欢迎窗口 ...")
        close_getstarted(wait_first=1.5 if started_now else 0.0)
        print("[2] 自动打开 Python Console ...")
        open_console(hwnd)
        print("[3] 注入 Live Server 启动代码 ...")
        inject_text(
            "exec(open(r'" + SERVER_SCRIPT + "', encoding='utf-8').read())\nstart_server()"
        )
        time.sleep(1)
        proxy = wait_server(timeout=25)
    elif args.skip_console:
        proxy = wait_server(timeout=10)

    if proxy is None:
        sys.exit("Live Server 未能启动。请手动打开 Python Console (Ctrl+Shift+P) "
                 "并运行 start_server()，然后重跑本脚本。")

    print("[4] Live Server 已连通 (127.0.0.1:%d)" % PORT)

    # 3) 创建 workspace / library / cell
    print("[5] 通过 RPC 创建/打开 workspace、library、cell ...")
    result = setup_via_rpc(proxy, args.wrk, args.lib, args.cell,
                           open_schematic=not args.no_open_schematic)
    print("---- ADS 返回 ----")
    print(result)
    if result is None:
        print("!! 返回为空：当前 Live Server 可能是旧版，请重启后再跑：")
        print("   在 ADS Python Console 里：")
        print("     stop_server()")
        print("     exec(open(r'" + SERVER_SCRIPT + "', encoding='utf-8').read())")
        print("     start_server()")
    print("---- 全自动初始化完成 ----")


if __name__ == "__main__":
    main()
