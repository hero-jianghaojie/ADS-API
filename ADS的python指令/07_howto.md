# 第七章：环境配置指南

## 7.1 配置 Python 虚拟环境

### 方法 A：基于 ADS Python 创建新虚拟环境

```bash
# 使用 ADS 自带的 Python 创建 venv
"D:\Program Files\Keysight\ADS2025_Update2\tools\python\python.exe" -m venv ads_venv

# 激活
ads_venv\Scripts\activate

# 现在可以导入 keysight.ads.de
python -c "from keysight.ads import de; print('OK')"
```

### 方法 B：在现有虚拟环境中安装 ADS wheels

```bash
# 激活现有虚拟环境
my_venv\Scripts\activate

# 使用 ADS 提供的 requirements 文件
pip install -r "D:\Program Files\Keysight\ADS2025_Update2\tools\python\packages\requirements.txt"
```

## 7.2 环境变量设置

使用前确保 `HPEESOF_DIR` 已设置：

```cmd
set HPEESOF_DIR=D:\Program Files\Keysight\ADS2025_Update2
```

或在 Python 中：

```python
import os
os.environ["HPEESOF_DIR"] = r"D:\Program Files\Keysight\ADS2025_Update2"
```

## 7.3 使用 Pytest

ADS Python API 支持 pytest 测试框架：

```python
# test_ads.py
from keysight.ads import de

def test_workspace():
    ws = de.open_workspace(r"D:/AppGallery/codex/codex_wrk")
    assert ws is not None
    de.close_workspace()
```

运行：

```bash
pytest test_ads.py -v
```

## 7.4 ADS 内部使用 Python 的最佳实践

1. **使用 Jupyter Console**：在 ADS 中按 `Ctrl+Shift+P` 打开
2. **Tab 补全**：按 Tab 触发自动补全
3. **Magic 命令**：`%clear` 清屏、`%matplotlib inline` 内嵌绘图
4. **脚本加载**：`Tools → Python → Load Script` 加载 `.py` 文件
5. **Addon 自动加载**：将 Addon 放在 ADS 搜索路径中

## 7.5 常见问题

### Q: 如何在 Python 脚本中判断是否在 ADS 内部运行？

```python
from keysight.ads import de
if de.is_pde_app():
    print("在 ADS 内部")
elif de.running_automation():
    print("独立 Python 运行")
```

### Q: 自动化模式下哪些功能不可用？

- `de.app` 中的窗口、菜单、Action、Addon
- 消息框、UI 交互
- 部分仿真控制功能

### Q: 如何将 AEL 脚本迁移到 Python？

使用 `keysight.ads.ael` 模块：

```python
from keysight.ads import ael

# AEL: deFindLib("codex_lib")
# Python: 
lib = ael.call.deFindLib("codex_lib")
```
