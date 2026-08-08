# -*- coding: utf-8 -*-
"""诊断：外部 ADS Python 进程能否启动可用的 Live Server？

结论（2026-08-01 验证）：
    外部进程的 `_pde_app` 是空占位模块（无 `ui` 属性），缺少 ADS GUI
    内嵌 Python 才有的 `_pde_app.ui`。因此外部启动的服务器只能响应
    `ping`，所有需要操作版图的调用（open_layout/add_polygon 等）都会
    抛 `AttributeError: module '_pde_app' has no attribute 'ui'`。

    真正的 Live Server 必须在 ADS GUI 的 Python Console 里运行：
        exec(open(r'D:\\AppGallery\\codex\\ads_tools\\ads_live_server.py', encoding='utf-8').read())
        start_server()

本脚本保留为诊断工具：`--test` 可验证端口监听与 ping，但无法操作 ADS。
"""
import sys
import time
from pathlib import Path

SERVER_SCRIPT = Path(__file__).resolve().parent / "ads_live_server.py"


def main():
    import _pde_app

    if not hasattr(_pde_app, "ui"):
        print("警告: 当前进程的 _pde_app 缺少 'ui' 属性 —— 无法操作 ADS 版图。", flush=True)
        print("真正的 Live Server 必须在 ADS GUI 的 Python Console 中运行:", flush=True)
        print("    exec(open(r'D:\\\\AppGallery\\\\codex\\\\ads_tools\\\\ads_live_server.py', encoding='utf-8').read())", flush=True)
        print("    start_server()", flush=True)
        if "--test" not in sys.argv:
            return

    # 加载 ads_live_server.py 中所有定义（start_server 等）
    src = SERVER_SCRIPT.read_text(encoding="utf-8")
    exec(compile(src, str(SERVER_SCRIPT), "exec"), globals())

    msg = start_server()
    print(msg, flush=True)

    if "--test" in sys.argv:
        import xmlrpc.client
        p = xmlrpc.client.ServerProxy("http://127.0.0.1:8765/", allow_none=True)
        print("ping:", p.ping(), flush=True)
        return

    print("服务器运行中... (Ctrl+C 停止)", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        stop_server()
        print("服务器已停止")


if __name__ == "__main__":
    main()
