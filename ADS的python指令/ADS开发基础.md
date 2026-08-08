# ADS Python 开发基础

> 常用核心内容 — 每个脚本都要用到的 API 和流程。

---

## 一、运行环境

### 1.1 Python 解释器
必须使用 ADS 自带的 Python：
```powershell
D:\Program Files\Keysight\ADS2025_Update2\tools\python\python.exe
```

### 1.2 环境变量
运行前必须设置：
```powershell
$env:HPEESOF_DIR="D:\Program Files\Keysight\ADS2025_Update2"
```

### 1.3 完整命令格式
```powershell
$env:HPEESOF_DIR="D:\Program Files\Keysight\ADS2025_Update2"; `
  & "D:\Program Files\Keysight\ADS2025_Update2\tools\python\python.exe" 脚本名.py
```

---

## 二、ADS 启动规则（重要！）

- 运行前先用 `tasklist` 检查 `ads.exe` 是否已在运行
- **如果 ADS 已运行** → 只打印提示，**不要**启动新实例，**不要**传任何参数
- **如果 ADS 未运行** → 直接启动 ADS，**不要**传 `-ws` 或其他参数
- 禁止重复打开 ADS 窗口

---

## 三、标准导入模块

所有滤波器脚本使用相同的导入：

```python
from keysight.ads import de              # Workspace/Library 管理
from keysight.ads.de import db_uu as db  # 原理图设计操作
from keysight.edatoolbox import ads      # 仿真器 (CircuitSimulator)
import keysight.ads.dataset as dataset   # 读取 .ds 仿真结果
import matplotlib.pyplot as plt          # 绘图
from IPython.core import getipython      # IPython inline 绘图
from pathlib import Path                 # 路径处理
import numpy as np                       # 数值计算
from datetime import datetime            # 时间戳（唯一 dataset 名）
import os                                # 系统接口
```

---

## 四、滤波器通用工作流（11步）

```
 0. Imports
 1. 设置滤波器规格参数 (ripple_db, fc, fs, R0, La)
 2. 切比雪夫原型设计 → g-values
 3. 物理尺寸计算（集总L/C 或 微带线宽/长度）
 4. 打印设计结果
 5. Workspace / Library 打开或创建
 6. 创建原理图（放置元件、端口、仿真控制器）
 7. 添加 VAR 变量块
 8. 添加 MeasEqn 测量方程
 9. 运行 S 参数仿真
10. 读取仿真结果
11. 绘图 (S11/S21, Group Delay)
```

---

## 五、Workspace / Library 管理

### 5.1 标准模板

```python
workspace_path = r"D:\AppGallery\codex\python_wrk"
library_name = "python_lib"

if de.workspace_is_open():
    workspace = de.active_workspace()
elif de.directory_is_workspace(workspace_path):
    workspace = de.open_workspace(workspace_path)
else:
    workspace = de.create_workspace(workspace_path)
    workspace.open()

library_path = workspace.path / library_name

if de.library_exists_at_path(library_path):
    if not de.library_is_open(library_name):
        lib = workspace.open_library(library_name, library_path, de.LibraryMode.SHARED)
    else:
        lib = de.get_open_library(library_name)
else:
    de.create_new_library(library_name, library_path)
    workspace.add_library(library_name, library_path, de.LibraryMode.SHARED)
    lib = workspace.open_library(library_name, library_path, de.LibraryMode.SHARED)

try:
    lib.setup_schematic_tech()
except UnicodeDecodeError:
    print("Warning: setup_schematic_tech encoding issue (non-critical)")
```

---

## 六、原理图设计（db_uu API）

### 6.1 创建原理图

```python
design = db.create_schematic(f"{library_name}:{cell_name}:schematic")
```

### 6.2 组件库路径对照

| 库路径 | 组件 | 用途 |
|--------|------|------|
| `ads_rflib:L:symbol` | 电感 | 集总参数串联电感 |
| `ads_rflib:C:symbol` | 电容 | 集总参数并联电容 |
| `ads_rflib:GROUND:symbol` | 地 | 接地符号 |
| `ads_tlines:MSUB:symbol` | 微带衬底 | 基板参数定义 |
| `ads_tlines:MLIN:symbol` | 微带传输线 | 微带线段 |
| `ads_simulation:TermG:symbol` | 接地端口 | 50Ω 端口匹配 |
| `ads_simulation:S_Param:symbol` | S参数仿真器 | 扫频设置 |
| `ads_simulation:MeasEqn:symbol` | 测量方程 | **(必须用元组路径)** |
| `ads_datacmps:VAR:symbol` | 变量块 | **(必须用元组路径)** |

### 6.3 放置语法

```python
# 字符串路径（大部分元件）
design.add_instance("ads_rflib:L:symbol", (x, y))
design.add_instance("ads_simulation:TermG:symbol", (x, y), name="TermG1")
design.add_instance("ads_rflib:C:symbol", (x, y), angle=-90)

# 元组路径（VAR 和 MeasEqn 必须用此形式）
design.add_instance(("ads_datacmps", "VAR", "symbol"), (x, y), name="VAR1", angle=90)
design.add_instance(("ads_simulation", "MeasEqn", "symbol"), (x, y), name="Meas1", angle=-90)
```

### 6.4 参数设置

```python
inst = design.add_instance("ads_tlines:MLIN:symbol", (x, y), name="TL1")
inst.parameters["W"].value    = "1.2 mm"
inst.parameters["L"].value    = "10.5 mm"
inst.parameters["Subst"].value = '"MSub1"'   # 注意：需要用双引号包裹
inst.update_item_annotation()
```

### 6.5 连线

```python
# 两点连线
design.add_wire([(x1, y1), (x2, y2)])

# 集总元件（间距2单位）：从 prev+1 连到 curr
design.add_wire([(i*2+1, -2), (i*2+2, -2)])

# 微带线（间距2单位）：从 prev_right_pin 连到 curr_left_pin
design.add_wire([(x_positions[i-1] + 1, -2), (x_positions[i], -2)])
```

### 6.6 坐标系规则

| 规则 | 说明 |
|------|------|
| 器件长度 | 默认 1 个单位 |
| 器件宽度 | 默认 0.25 个单位 |
| 加文字后宽 | 约 1.25 个单位 |
| 默认角度 | 0°（横放） |
| 坐标含义 | 指**第一个针脚（pin）**的位置 |
| MSUB 尺寸 | 加文字约 1×3 单位 |
| S_Param 尺寸 | 加文字约 2.5×1.5 单位 |

### 6.7 集总参数 LPF 布局

```
       L1         L2         L3
  ────╴╴────╴╴────╴╴────╴╴────
        │         │         │
        C1        C2        C3
        │         │         │
       ─┴─       ─┴─       ─┴─
```

坐标规则：
- 电感 `L_i` 放在 `(i*2, -2)`，引脚在 `(i*2, -2)` 和 `(i*2+1, -2)`
- 电容 `C_i` 放在 `(i*2+1.5, -3)`，`angle=-90`（竖放）
- 地放在电容下方 `(i*2+1.5, -4)`

### 6.8 微带线 LPF 布局

```
  ──[TL1]──[TL2]──[TL3]──[TL4]──[TL5]──[TL6]──
```

坐标规则：
- 每节 MLIN 放在 `(i*2, -2)`（间距 2 单位）
- 引脚在 `(i*2, -2)`（左）和 `(i*2+1, -2)`（右）
- 连线从 `(prev_x+1, -2)` 到 `(curr_x, -2)`

---

## 七、VAR 变量块

### 7.1 标准模式

```python
var_inst = design.add_instance(
    ("ads_datacmps", "VAR", "symbol"),
    (x, y), name="VAR1", angle=90
)
# 添加变量
var_inst.vars["L1"] = "11.62"
# 删除默认占位变量
del var_inst.vars["X"]
```

### 7.2 关键规则

- 必须用 **元组路径** `("ads_datacmps", "VAR", "symbol")`
- `angle=90` 竖放（推荐配合主电路水平布局）
- 默认变量 `X` 必须用 `del var_inst.vars["X"]` 删除
- 建议按用途拆成多个 VAR 块（如 `VAR1` 放电感、`VAR2` 放电容）

---

## 八、MeasEqn 测量方程

### 8.1 标准模式

```python
eq_list = [
    'groupdelay=(-1/360)*diff(unwrap(phase(S(2,1))))/diff(freq)',
    's21magnitude=mag(S(2,1))',
    's21phase=phase(S(2,1))',
]

def add_measeqn(design, eq_name, eq_list):
    measeqn = design.add_instance(
        ("ads_simulation", "MeasEqn", "symbol"),
        (6, 1), name=eq_name, angle=-90
    )
    # 第一行
    measeqn.parameters["Meas"].value = [eq_list[0]]
    # 后续行
    for i in range(len(eq_list) - 1):
        measeqn.parameters["Meas"].repeats.append(
            db.ParamItemString("Meas", "SingleTextLine", eq_list[i+1])
        )
    measeqn.update_item_annotation()
```

### 8.2 关键规则

- 必须用 **元组路径** `("ads_simulation", "MeasEqn", "symbol")`
- 第一行用 `.value = [字符串]`，后续行用 `.repeats.append(db.ParamItemString(...))`
- `db.ParamItemString` 签名：`(参数名, "SingleTextLine", 公式字符串)`

---

## 九、仿真运行

### 9.1 标准模式

```python
# 唯一 dataset 名（避免文件锁）
ds_name = f"{cell_name}_{datetime.now().strftime('%H%M%S')}"

netlist = design.generate_netlist()
simulator = ads.CircuitSimulator()
target_output_dir = os.path.join(workspace_path, "data")
simulator.run_netlist(netlist, output_dir=target_output_dir, dataset_name=ds_name)
```

### 9.2 关键规则

- 用 `datetime.now().strftime('%H%M%S')` 生成唯一名避免文件锁
- 输出目录固定为 `workspace_path/data`
- 使用 `ads.CircuitSimulator()` 类

### 9.3 原理图构建顺序（重要！）

```
1. 创建原理图     design = db.create_schematic(...)
2. 添加元件       design.add_instance(...)
3. 添加连线       design.add_wire(...)
4. 添加 VAR 块    design.add_instance(("ads_datacmps", "VAR", "symbol"), ...)
5. 添加 MeasEqn   design.add_instance(("ads_simulation", "MeasEqn", "symbol"), ...)
6. 保存设计       design.save_design()          ← 在 VAR 和 MeasEqn 之后！
7. 生成网表       design.generate_netlist()
8. 运行仿真       simulator.run_netlist(...)
```

- `save_design()` **必须在 VAR 和 MeasEqn 之后调用**，否则网表缺少参数
- MLIN 缺少 W/L 参数时 ADS 视为零长度直通线 → S21 全频段平坦在 0 dB

---

## 十、结果读取与绘图

### 10.1 读取 dataset

```python
output_data = dataset.open(Path(os.path.join(target_output_dir, f"{ds_name}.ds")))
print(f"Datablocks: {output_data.varblock_names}")

# 按变量名查找数据块
for datablock in output_data.find_varblocks_with_var_name("groupdelay"):
    gd = datablock.name
for datablock in output_data.find_varblocks_with_var_name("S[2,1]"):
    sp = datablock.name

# 转为 DataFrame
gd_data = output_data[gd].to_dataframe().reset_index()
sp_data = output_data[sp].to_dataframe().reset_index()

# 提取数据
freq = sp_data["freq"] / 1e6           # Hz → MHz
s11  = 20 * np.log10(abs(sp_data["S[1,1]"]))
s21  = 20 * np.log10(abs(sp_data["S[2,1]"]))
groupdelay = gd_data["groupdelay"] / 1e-9  # s → ns
```

### 10.2 绘图模式

```python
ipython = getipython.get_ipython()
ipython.run_line_magic('matplotlib', 'inline')

_, ax = plt.subplots()
ax.set_title("Title")
plt.xlabel("Frequency (MHz)")
plt.ylabel("S11 and S21 (dB)")
plt.grid(True)
plt.plot(freq, s11, label="S11")
plt.plot(freq, s21, label="S21")
plt.legend()
plt.savefig(os.path.join(plot_path, "filename.png"))
```

---

## 十一、ParamSweep 参数扫描（标准模板）

### 11.1 DC 扫描 + ParamSweep（以 CGH40010F I-V 为例）

```python
# VAR 变量块（定义被扫描的变量初值）
var = design.add_instance(
    ("ads_datacmps", "VAR", "symbol"), (5, 1), name="VAR", angle=90
)
var.vars["VGS"] = "-2.5"       # 被 ParamSweep 扫描
var.vars["VDS"] = "28"         # 被 DC 扫描
del var.vars["X"]

# DC 仿真控制器（内层扫描：VDS）
dc = design.add_instance("ads_simulation:DC:symbol", (-5, 2), name="DC1")
dc.parameters["SweepVar"].value = "VDS"
dc.parameters["Start"].value = "0"
dc.parameters["Stop"].value = "50"
dc.parameters["Step"].value = "0.5"
dc.update_item_annotation()

# ParamSweep（外层扫描：VGS）
pswp = design.add_instance(
    ("ads_simulation", "ParamSweep", "symbol"), (-2, 2), name="PSW"
)
pswp.parameters["SweepVar"].value = '"VGS"'
pswp.parameters["SimInstanceName"].repeats[0].value = '"DC1"'
pswp.parameters["Start"].value = "-3"
pswp.parameters["Stop"].value = "0"
pswp.parameters["Step"].value = "0.5"
pswp.parameters["Sort"].value = 'LINEAR START STEP'
pswp.update_item_annotation()
```

### 11.2 关键规则

- `SweepVar` 的值用**双引号包裹**（如 `'"VGS"'`），表示引用 VAR 变量名
- `SimInstanceName` 用 `.repeats[0].value` 设置，引用被控制的仿真控制器（如 `'"DC1"'`）
- 内层扫描（DC）和外层扫描（ParamSweep）组成嵌套扫描
- `Sort` 参数固定为 `'LINEAR START STEP'`

---

## 十二、PDK 晶体管使用要点

### 12.1 组件引用格式

```python
# 格式: <PDK库名>:<晶体管Cell名>:symbol
fet = design.add_instance("CGH40_r6:CGH40010F_r6_CGH40_r6:symbol", (0, -2), name="Q1")
```

**PDK 晶体管不同于标准 `ads_rflib:FET`，引脚位置可能不同！** 需在 ADS 中确认后再连线。

### 12.2 CGH40010F 引脚位置示例

FET 放置于 `(0, -2)` 时的引脚坐标：

| 引脚 | 坐标 | 说明 |
|------|------|------|
| G (栅极) | `(0, -2)` | 即放置点 |
| D (漏极) | `(0.5, -1.5)` | 右上方 |
| Pin4 | `(0.5, -2)` | 中间（需与 Source 短接） |
| S (源极) | `(0.5, -2.5)` | 正下方 |

### 12.3 V_DC 与 angle=-90 布局

```python
# V_DC 竖放：+ 极在放置点 (x,y)，- 极在 (x, y-1)
vgs = design.add_instance("ads_sources:V_DC:symbol", (-3, -2), name="VGS", angle=-90)
vgs.parameters["Vdc"].value = "VGS V"   # 值格式：变量名 + 空格 + 单位
```

### 12.4 I_Probe 电流探针

```python
# I_Probe 间距 0.25 单位，pin1→pin2 为电流正方向
iprobe = design.add_instance("ads_rflib:I_Probe:symbol", (1, -1.5), name="I_Probe")
# pin1 在 (1, -1.5)，pin2 在 (1.25, -1.5)
# 连线: Drain → pin1, pin2 → VDS+
```

### 12.5 GND 与负端同点直连

当 GND 和元件的负端放在**同一坐标**时，无需连线，ADS 自动连接：

```python
# VGS- 在 (-3,-3)，GND 也在 (-3,-3) → 无需 add_wire
design.add_instance("ads_rflib:GROUND:symbol", (-3, -3), name="GND_VGS", angle=-90)
```

### 12.6 仿真结果路径显示

```python
print(f"Dataset path: {os.path.join(target_dir, ds_name)}.ds")
print(f"Netlist path: {os.path.join(target_dir, f'circ{ds_name}.ckt')}")
```

---

## 十三、版图 (Layout) 操作

### 13.1 Workspace 安全模式（不删数据）

```python
if de.workspace_is_open():
    wrk_space = de.active_workspace()
elif de.directory_is_workspace(wrk_path):
    wrk_space = de.open_workspace(wrk_path)
else:
    wrk_space = de.create_workspace(wrk_path)
    wrk_space.open()
```

### 13.2 Library 安全模式（存在则打开）

```python
if de.library_exists_at_path(lib_path):
    lib = wrk_space.open_library(lib_name, lib_path, mode=de.LibraryMode.SHARED)
else:
    lib = de.create_new_library(lib_name, lib_path)
    wrk_space.add_library(lib_name, lib_path, mode=de.LibraryMode.SHARED)
```

### 13.3 Layout 工艺设置

```python
# 设置 schematic 工艺（已知问题：可能抛 UnicodeDecodeError）
try:
    lib.setup_schematic_tech()
except UnicodeDecodeError:
    print("Warning: setup_schematic_tech encoding issue (non-critical)")

# 创建标准 ADS layout 工艺（已存在则跳过）
try:
    lib.create_layout_tech_std_ads("millimeter", 10000, False)
except RuntimeError as e:
    if "duplicate" in str(e).lower():
        print("Layout tech already set up (skipping)")
    else:
        raise
```

| 参数 | 含义 | 说明 |
|------|------|------|
| `"millimeter"` | 单位 | 可选 `"mil"`, `"millimeter"`, `"micron"` |
| `10000` | 版图范围 | 最大坐标值 |
| `False` | 精度控制 | |

### 13.4 创建 Layout 视图

```python
layout = db_uu.create_layout(f"{library.name}:{cell_name}:layout")
```

与 schematic 类似，但视图名为 `layout` 而非 `schematic`。
