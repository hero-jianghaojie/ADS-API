ADS 全自动初始化（一键运行）

  运行下面一条命令，自动完成：
    1) 启动 ADS（如未运行），并自动关闭 Get Started 欢迎窗口
    2) 打开 ADS 的 Python Console
    3) 自动启动 ADS Live Server（XML RPC 桥，127.0.0.1:8765）
    4) 自动创建/打开 workspace、library、cell，并创建、打开原理图窗口
    5) 校验连通性并报告结果

  一键命令（ADS 自带 Python）：
      $env:HPEESOF_DIR = "D:\Program Files\Keysight\ADS2025_Update2"
      & "$env:HPEESOF_DIR\tools\python\python.exe" "D:\AppGallery\codex\ADS\ads_tools\ads_auto_setup.py"

  可指定 workspace / library / cell：
      ...\ads_auto_setup.py --wrk D:/AppGallery/codex/python_wrk --lib python_lib --cell my_cell

  可选参数：
      --no-open-schematic    创建 cell 后不自动打开原理图
      --skip-console         跳过自动打开 Console（Server 已在运行）

  相关脚本：
      ADS/ads_tools/ads_auto_setup.py      # 全自动主脚本（外部运行）
      ADS/ads_tools/ads_live_server.py     # ADS 内 Live Server（含 run_python RPC）
      ADS/ads_tools/open_ads_console.ps1   # 单独打开 Python Console

  自动失败时的备选（手动）：
    1) 打开 ADS（见 ADS使用步骤（半自动） 步骤1），若弹出 Get Started 点右下角 Close
    2) 打开 Python Console：Tools > Python Console（Ctrl+Shift+P）
    3) 在 Console 里顶格输入两行：
exec(open(r'D:\AppGallery\codex\ADS\ads_tools\ads_live_server.py', encoding='utf-8').read())
start_server()
    4) 重跑 ads_auto_setup.py（会自动连上已启动的 server）

  说明：
    - 自动方式是模拟按键（Ctrl+Shift+P 打开 Console、Ctrl+V 粘贴代码），
      需在登录的桌面会话运行；若焦点被抢走导致 Console 未弹出，按上面备选手动打开。
    - 脚本会自动检测并关闭 ADS 的 Get Started 欢迎窗口（不关会挡住 Python Console）。
    - server 通过 run_python RPC 在 ADS 主线程执行创建逻辑，安全可靠。
    - 修改 ads_live_server.py 后需在 Console 重启 Live Server：
      先 stop_server()，再重新 exec 脚本 + start_server()。
    - 详细手动步骤见 ADS使用步骤（半自动） 文档。
