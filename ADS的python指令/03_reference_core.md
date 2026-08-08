# 第三章：核心 API —— `keysight.ads.de`

## 3.1 顶层函数

### Workspace 操作

| 函数 | 说明 |
|------|------|
| `de.open_workspace(wrk_path, *, force=False)` | 打开 workspace，`force=True` 强制关闭当前 |
| `de.create_workspace(wrk_path)` | 创建新 workspace（路径不存在时） |
| `de.close_workspace()` | 关闭当前 workspace |
| `de.active_workspace()` → `Workspace` | 获取当前打开的 workspace（无则报错） |
| `de.workspace_is_open()` → `bool` | 检查 workspace 是否已打开 |
| `de.directory_is_workspace(path)` → `bool` | 目录是否是 workspace |
| `de.directory_might_be_workspace(path)` → `bool` | 目录可能是 workspace |

### Library 操作

| 函数 | 说明 |
|------|------|
| `de.get_open_library(lib_name)` → `Library` | 获取已打开的库 |
| `de.create_new_library(name, path)` | 创建新库 |
| `de.close_library(lib_name)` | 关闭库 |
| `de.close_library_if_open(lib_name)` | 如果已打开则关闭 |
| `de.library_is_open(lib_name)` → `bool` | 检查库是否打开 |
| `de.library_is_read_only(lib_name)` → `bool` | 检查库是否只读 |
| `de.library_exists_at_path(path)` → `bool` | 路径是否包含库 |
| `de.get_open_writable_library_names()` → `set[str]` | 获取所有可写库名 |
| `de.get_path_to_open_library(lib_name)` → `Path` | 获取库路径 |
| `de.is_open_library_in_workspace(lib)` → `bool` | 库是否在 workspace 内 |

### Cell/View 操作

| 函数 | 说明 |
|------|------|
| `de.cellview_exists(lib, cell, view)` → `bool` | 检查 cellview 是否存在 |
| `de.get_cell_module(lib_name, cell_name)` → `module` | 导入 OA cell 的 Python 模块 |
| `de.get_view_module(lib, cell, view)` → `module` | 导入 OA cellview 的 Python 模块 |
| `de.get_library_module(lib_name)` → `module` | 导入 OA lib 的 Python 模块 |

### 设计 / 网表

| 函数 | 说明 |
|------|------|
| `de.generate_netlist(hierarchy)` → `str` | 生成网表文本 |
| `de.find_equivalent_design(design)` | 返回等效设计（schematic ↔ layout） |
| `de.find_inst_in_schematic_hierarchy(name, hierarchy)` | 在层次结构中查找实例 |
| `de.find_inst_in_associated_schematic(name, design)` | 在关联原理图中查找实例 |
| `de.get_view_name_for_sub_design_from_hierarchy(hierarchy, inst)` | 获取子设计的 view 名称 |
| `de.designs_have_different_parameters(d1, d2)` → `bool` | 两设计的参数是否不同 |
| `de.update_design_parameters_to_match_other_design(d1, d2)` | 更新参数以匹配另一设计 |

### Smart Package

| 函数 | 说明 |
|------|------|
| `de.add_smart_package(name, path)` | 创建 Smart Package |
| `de.remove_smart_package(name)` | 移除 Smart Package |
| `de.get_smart_package_module(name)` → `module` | 导入 Smart Package 模块 |

### 工具函数

| 函数 | 说明 |
|------|------|
| `de.format_number(num)` | 格式化数字为 ADS 样式字符串 |
| `de.product_version()` → `str` | 获取 ADS 产品版本 |
| `de.version()` → `int` | 获取 API 版本号 |
| `de.hpeesof_path()` → `str` | 获取 `HPEESOF_DIR` 路径 |
| `de.is_pde_app()` → `bool` | 是否在 ADS PDE 中运行 |
| `de.running_automation()` → `bool` | 是否独立 Python 运行 |
| `de.unarchive_file(zap_path, dest, exclude_em_files=True)` | 解压 `.7zads` 文件 |
| `de.get_hierarchy_from_current_expr_context()` → `DesignHierarchy` | 从当前表达式上下文获取层次结构 |

## 3.2 核心类

### Workspace

```python
ws = de.active_workspace()
# 或
ws = de.open_workspace("path/to/workspace")

ws.name          # workspace 名称
ws.path          # workspace 路径
ws.save()        # 保存
ws.close()       # 关闭
ws.list_libraries()  # 列出库
```

### Library

```python
lib = de.get_open_library("codex_lib")

lib.name                 # 库名
lib.path                 # 库路径
lib.is_read_only         # 是否只读
lib.list_cells()         # 列出所有 Cell
lib.find_cell(name)      # 查找 Cell
lib.create_cell(name)    # 创建 Cell
```

### Cell

```python
cell = lib.find_cell("impedance_coupler")
# 或
cell = lib.create_cell("impedance_coupler")

cell.name                # Cell 名
cell.list_views()        # 列出所有 View
cell.find_view(name)     # 查找 View
cell.create_view(name)   # 创建 View
```

### View

```python
view = cell.find_view("schematic")
# 或
view = cell.create_view("schematic")

view.name                # View 名
view.open_design()       # 打开设计
```

### CellviewRef / LCVName

用于引用三元组 (Library, Cell, View)：

```python
# LCVName 格式
ref = de.LCVName("codex_lib:impedance_coupler:schematic")
# 或
ref = de.CellviewRef("codex_lib", "impedance_coupler", "schematic")
```

### DesignHierarchy

用于遍历设计层次结构：

```python
hierarchy = de.DesignHierarchy(top_design)
hierarchy.designs       # 所有设计
hierarchy.top_design    # 顶层设计
```

### DMData

设计数据管理对象。

### ItemInfo

设计元素信息，包含多种子类型和枚举。

## 3.3 坐标点类型

| 类型 | 说明 |
|------|------|
| `de.PointF` | 浮点坐标 (x, y) |
| `de.PointDBU` | 数据库单位坐标 |
| `de.PointUU` | 用户单位坐标 |
| `de.PointMKS` | 米制坐标 |
| `de.BoxF` | 浮点矩形区域 |
| `de.dbu()` | 转换为数据库单位 |
| `de.uu()` | 数据库单位转用户单位 |

## 3.4 集合类型

| 类型 | 说明 |
|------|------|
| `IndexedMutableCollectionAbc` | 按索引访问的可变集合 |
| `NamedMutableCollectionAbc` | 按名称访问的可变集合 |
