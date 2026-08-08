# 第一章：概述与入门

## 1.1 ADS Python 的两种使用方式

### 方式 A：在 ADS 内部使用（嵌入模式）

ADS 设计环境内置了 Python 解释器，可通过以下方式打开：

- **菜单**: `Tools → Python Console…`
- **快捷键**: `Ctrl + Shift + P`

打开的是 **Jupyter Console**，支持：
- Tab 键自动补全
- IPython Magic 命令（`%clear`, `%matplotlib inline` 等）
- 完整的 ADS 应用层功能（UI、窗口、消息框等）

```python
from keysight.ads import de
ws = de.active_workspace()  # 获取当前打开的 workspace
```

### 方式 B：在 ADS 外部使用（扩展模式）

在 Python 脚本中直接导入 `keysight.ads.de` 包，可以访问 ADS 设计环境功能。

```python
from keysight.ads import de

# 打开 workspace
de.open_workspace(r"D:/AppGallery/codex/codex_wrk")

# 执行操作
lib = de.get_open_library("codex_lib")
```

**前提条件**：

1. 设置环境变量 `HPEESOF_DIR` 指向 ADS 安装目录
2. 使用以下任一方式访问包：
   - 使用 `$HPEESOF_DIR/tools/python` 下的 ADS Python 解释器
   - 创建基于 ADS Python 的虚拟环境（见 [07_howto.md](07_howto.md)）
   - 将 `$HPEESOF_DIR/tools/python/packages` 添加到 `sys.path`

## 1.2 执行模式

| 函数 | 在 ADS 中 | 在 DDS 中 | 独立 Python |
|------|-----------|-----------|------------|
| `de.is_pde_app()` | `True` | `False` | `False` |
| `de.running_automation()` | `False` | `False` | `True` |

- **自动化（Automation）**：在独立 Python 进程中导入 `keysight.ads.de` 时，无法访问 UI 功能
- **`de.is_pde_app()`**：检查是否在 ADS 应用内运行
- **`de.running_animation()`**：检查是否是独立 Python 运行（名称有误，未来将弃用）

## 1.3 推荐的导入方式

```python
from keysight.ads import de
from keysight.ads.de import db_uu as db     # 数据库单位
```

## 1.4 许可（Licensing）

ADS Python API 的使用受 ADS 许可证控制，需要有效的 ADS 许可证才能运行。

## 1.5 自定义 ADS UI

### Addon（插件）机制

Python 实现的 addon 支持三个可选函数（放在 `__init__.py` 中）：

```python
# addon 初始化（不要在此操作 UI 元素）
def setup_addon(addon: "Addon") -> None: ...

# addon 关闭
def shutdown_addon(addon: "Addon") -> None: ...

# 生成自定义菜单
def generate_menu(addon: "Addon", win_def: "WindowDefinition") -> None: ...
```

### PySide2 对话框

ADS 内部已内置 PySide2，可以直接使用：

```python
from PySide2.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout

form = QDialog()
form.setWindowTitle("My Customization")
form.show()
```
