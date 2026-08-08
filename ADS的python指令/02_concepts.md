# 第二章：关键概念

## 2.1 术语

| 术语 | 说明 |
|------|------|
| **Workspace** | ADS 项目容器，包含一个或多个 Library |
| **Library** | 设计库，包含 Cell |
| **Cell** | 设计单元（如 `impedance_coupler`、`balanced_pa`） |
| **View** | Cell 的视图（`schematic` 原理图、`layout` 版图、`symbol` 符号） |
| **CellviewRef / LCVName** | Library-Cell-View 三元组引用 |
| **Design** | 打开的 cellview 设计对象 |
| **DesignHierarchy** | 设计层次结构，用于遍历子电路 |

### 设计元素结构

```
Workspace
 └── Library
      └── Cell
           └── View (schematic / layout / symbol)
                └── Design 实例
                     ├── Instances (元件实例)
                     ├── Nets (连线)
                     ├── Pins (引脚)
                     ├── Terminals (端口)
                     └── Parameters (参数)
```

## 2.2 OpenAccess 集成

ADS 使用 **OpenAccess (OA)** 作为底层数据库格式。这意味着：
- Cell/View 概念与 OA 标准一致
- 可以通过 `get_cell_module()`、`get_view_module()` 导入 OA 对象的 Python 模块
- 库文件存储在 `.oa` 文件中

## 2.3 Python 脚本执行上下文

### 三种执行模式

| 模式 | 描述 | UI 可用 | 适用场景 |
|------|------|---------|---------|
| **ADS 应用内** | 在 ADS 的 Python Console 中运行 | ✅ | 自动化设计、UI 交互 |
| **DDS 应用内** | 在 Data Display 中运行 | DDS UI 可用 | 数据处理与绘图 |
| **独立 Python** | 命令行运行 `python script.py` | ❌ | 批量处理、CI/CD |

### 脚本如何判断当前上下文

```python
from keysight.ads import de

if de.is_pde_app():
    print("在 ADS 内部运行")
elif de.running_automation():
    print("独立 Python 运行 - 自动化模式")
```

### 注意事项

1. **UI 功能限制**：自动化模式下不能使用 `keysight.ads.de.app` 中的窗口/菜单/Action 功能
2. **仿真**：自动化模式下的仿真需使用 `keysight.edatoolbox` 包
3. **导入链**：在 ADS 中导入 `keysight.ads.dds` 被视为 DDS 自动化（反之亦然）
