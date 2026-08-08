# 第四章：子模块参考

## 4.1 `keysight.ads.de.ael` —— AEL 桥接

通过 `ael.call` 代理对象调用所有 ADS AEL 函数。

```python
from keysight.ads import ael

# ── 库操作 ──
lib = ael.call.deFindLib("codex_lib")
if lib.is_null():
    lib = ael.call.deCreateLib("codex_lib")

# ── Cell/View 操作 ──
cell = ael.call.deFindCell(lib, "my_cell")
if cell.is_null():
    cell = ael.call.deCreateCell(lib, "my_cell")

view = ael.call.deFindView(cell, "schematic")
if view.is_null():
    view = ael.call.deCreateView(cell, "schematic")

# ── 设计窗口 ──
win = ael.call.deOpenDesign(view)
ael.call.deSaveDesign(win)
ael.call.deCloseDesign(win)

# ── 放置元件 ──
comp = ael.call.deNewComponent(win, "MLIN", "TL1", 200, 200)
ael.call.deSetComponentParams(win, comp, "W", "1.12 mm", "L", "18.75 mm")

# ── 衬底操作 ──
ael.call.deSetSubstrateParams(win, "MSub1",
    "H", "0.508 mm", "Er", "3.55", ...)
ael.call.deSetSubstrate(win, "MSub1")
ael.call.deSetModelMode(win, "MSub1", "microstrip")

# ── 实例化子电路 ──
inst = ael.call.deNewComponent(win, "INST", "InputMatch", 150, 200)
ael.call.deSetComponentParams(win, inst, "Lib", "codex_lib")
ael.call.deSetComponentParams(win, inst, "Cell", "input_matching")
ael.call.deSetComponentParams(win, inst, "View", "schematic")
```

> **注意**: `ael.call.deXXX()` 返回的 handle 使用 `.is_null()` 检查是否为 NULL，而不是 Python 的 `None`。

## 4.2 `keysight.ads.de.app` —— 应用交互

| 子模块 | 说明 |
|--------|------|
| `de.app.action` | Actions 和菜单定义 |
| `de.app.addon` | Addon 插件管理 |
| `de.app.callbacks` | 回调函数 |
| `de.app.window` | 窗口和控件 |
| `de.app.dds` | DDS (Data Display) 集成 |

适用于 ADS 内部运行模式，自动化模式下不可用。

## 4.3 `keysight.ads.de.db` —— 数据库操作

| 子模块 | 说明 |
|--------|------|
| `de.db.callbacks` | 数据库回调 |
| `de.db.enums` | 枚举类型 |
| `de.db.forms` | 参数表单 |
| `de.db.genpolyline` | GenPolyline 多段线 |
| `de.db.model_def` | 模型定义 |
| `de.db.parameters` | 组件参数 |
| `de.db.properties` | 属性系统 |
| `de.db.transaction` | 事务管理 |

## 4.4 `keysight.ads.de.db_uu` —— 设计元素

设计元素是原理图和版图中的核心对象。

| 模块 | 说明 |
|------|------|
| `de.db_uu.Design` | 设计对象（打开的 cellview） |
| `de.db_uu.Instance` | 元件实例 |
| `de.db_uu.Net` | 连线 |
| `de.db_uu.Pin` | 引脚 |
| `de.db_uu.Terminal` | 端口 |
| `de.db_uu.LayerId` | 层 ID |
| `de.db_uu.LineTypeInfo` | 线型信息 |

## 4.5 `keysight.ads.de.db_dbu` —— 数据库单位

数据库底层单位转换相关。

## 4.6 `keysight.ads.de.tech` —— 工艺技术

| 模块 | 说明 |
|------|------|
| `de.tech.Tech` | 工艺技术定义 |
| `de.tech.pads` | Padstacks（焊盘堆叠） |
| `de.tech.rule` | Via 规则 |
| `de.tech.nested` | 嵌套工艺技术 |

## 4.7 `keysight.ads.de.experimental` —— 实验性 API

> **警告**: 这些 API 可能在未来版本中发生变化。

| 模块 | 说明 |
|------|------|
| `de.experimental.cdf` | CDF (Common Data Format) 组件参数 |
| `de.experimental.commands` | 命令系统 |
| `de.experimental.handles` | 句柄管理 |
| `de.experimental.netlist_helper` | 网表工具 |
| `de.experimental.polygon_utils` | 多边形工具 |
| `de.experimental.preferences` | 偏好设置 |
| `de.experimental.pro_view` | xxPro View |
| `de.experimental.symbol` | Symbol 符号生成器 |
| `de.experimental.text_maker` | 文本生成器 |
