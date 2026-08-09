# -*- coding: utf-8 -*-
r"""
ADS 创建/打开 workspace + library + cell + 原理图（独立 .py 版）

功能：
  1. 创建或打开 workspace、library
  2. 加载 PDK（CGH40）/ 元件库（村田 / 标准版图层）
  3. 配置 schematic tech 与标准版图库（单位/分辨率）
  4. 创建 cell 原理图并放置示例电路

用法（ADS 自带 Python）：
  $env:HPEESOF_DIR = "D:\Program Files\Keysight\ADS2025_Update2"
  & "$env:HPEESOF_DIR\tools\python\python.exe" "D:\AppGallery\codex\ADS\ads_tools\ads_setup_workspace.py"
"""
import os                                # OS interface (path operations)
import numpy as np                       # Numerical computation
import warnings                          # 抑制 DeprecationWarning

import keysight.ads.dataset as dataset   # Read simulation dataset (.ds)
import matplotlib.pyplot as plt          # Plotting

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

# Murata 电感电容库（Design Kit，与 CGH40 同在 pdk_base 下）
murata_base = os.path.join(pdk_base, r"murata_lib_ads2011later_521e\murata_lib_ads2011later_521e")
murata_lib_path = os.path.join(murata_base, "muRataLibWeb")
murata_tech_path = os.path.join(murata_base, "muRataLibWeb_tech")

# Layout 设置（标准版图库）
layout_unit = "millimeter"   # 版图单位：毫米（可选 "mil" / "millimeter" / "micron"）
layout_dbu_per_uu = 1000     # 版图分辨率：每用户单位的数据库单位数（1mm=1000dbu → 1µm）


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

    # 3) 加载 PDK / 元件库（只加尚未加载的）
    # 标准版图层库路径在函数内计算，保证自包含（不依赖顶部全局变量）
    hpeesof_dir = os.environ.get("HPEESOF_DIR", r"D:\Program Files\Keysight\ADS2025_Update2")
    std_layout_lib_path = os.path.join(hpeesof_dir, r"oalibs\tech\ads_standard_layers")
    libs = [
        ("CGH40_r6", pdk_path),                  # 氮化镓功率管 PDK
        ("CGH40_r6_tech", pdk_tech_path),        # CGH40 技术库
        ("muRataLibWeb", murata_lib_path),       # 村田电感电容库
        ("muRataLibWeb_tech", murata_tech_path), # 村田技术库
        ("ads_standard_layers", std_layout_lib_path),  # 标准版图层库（ADS 自带）
    ]
    for ln, lp in libs:
        if ln in workspace.library_names:
            print(f"library already loaded: {ln}")
        elif os.path.isdir(lp):
            workspace.add_library(ln, lp, de.LibraryMode.READ_ONLY)
            print(f"library loaded: {ln}")
        else:
            print(f"library path not found: {lp}")

    # 4) 配置 schematic tech（跳过已配置的）
    try:
        library.setup_schematic_tech()
    except Exception:
        pass

    # 5) 创建标准 ADS 版图库（版图单位 + 分辨率；已存在则跳过）
    try:
        library.create_layout_tech_std_ads(layout_unit, layout_dbu_per_uu, False)
        print(f"Layout tech created: unit={layout_unit}, dbu_per_uu={layout_dbu_per_uu}")
    except RuntimeError as e:
        if "duplicate" in str(e).lower() or "lock" in str(e).lower():
            print("Layout tech already set up (skipping)")
        else:
            raise

    # 6) 设置版图参数（Snap Grid / Pin text Size / Text 尺寸；需在 preferences 上下文中）
    try:
        from keysight.ads.de.experimental.preferences import (
            LibSpecificPreference as _L,
        )
        with de.experimental.preferences():
            # Snap Grid 吸附距离（mm）
            library.set_layout_preference(_L.GRID_SNAP_X, 0.5)
            library.set_layout_preference(_L.GRID_SNAP_Y, 0.5)
            # Pin 文字尺寸（mm）—— 引脚/实例标注文字高度（instTextHeight）
            library.set_layout_preference(_L.INST_TEXT_HEIGHT, 0.5)
            # Text 文字尺寸（mm）
            library.set_layout_preference(_L.TEXT_HEIGHT, 0.5)
        print("Layout prefs set: snap_grid=0.5, pin_text=0.5, text_height=0.5")
    except Exception as e:
        print("Layout prefs warn:", repr(e))

    return library


def get_cell(library, name=cell_name, view="schematic"):
    if not library.cell_exists(name):
        cell = library.create_cell(name)
        cell.create_view(view, "Schematic")
        print(f"cell created: {name}:{view}")
    else:
        cell = library.get_cell_if_exists(name)
    return cell


def create_schematic(library, name=cell_name, view="schematic"):
    """创建/打开 cell 的原理图并放置完整示例电路。

    name  指定 cell 名（默认取全局 cell_name）
    view  指定原理图 view 名（默认 "schematic"，可自定义如 "schematic2"）

    放置内容（S 参数仿真示例）：
      MSUB      微带衬底定义（Rogers4350B，完整参数）
      SP1       S 参数仿真器（0.1~3 GHz）
      TermG1/2  两个 50Ω 端口（直通连线）
      VAR1      变量块（演示 L1/C1 可调参数）
      Meas1     测量方程（S21 幅度/相位/群时延）
    构建顺序：创建→元件→连线→VAR→MeasEqn→保存→网表
    """
    # 1) 打开（不存在则创建）原理图设计
    design = db.create_schematic(f"{library.name}:{name}:{view}")
    print(f"schematic opened: {library.name}:{name}:{view}")

    # 2) 衬底（微带仿真用）（Rogers4350B）
    msub = design.add_instance("ads_tlines:MSUB:symbol", (-3, 2), name="MSub1")
    msub.parameters["H"].value     = "0.762 mm"      # 基板高度
    msub.parameters["Er"].value    = "3.66"          # 相对介电常数
    msub.parameters["Mur"].value   = "1"             # 相对磁导率
    msub.parameters["Cond"].value  = "5.8e7"         # 导体电导率（铜）
    msub.parameters["Hu"].value    = "1.0e+33 mm"    # 封装高度（近似无限大）
    msub.parameters["T"].value     = "0.035 mm"      # 金属厚度（1oz）
    msub.parameters["TanD"].value  = "0.0037"        # 损耗角正切
    msub.parameters["Rough"].value = "0 mm"          # 表面粗糙度
    msub.update_item_annotation()

    # 3) S 参数仿真器
    spar = design.add_instance("ads_simulation:S_Param:symbol", (0, 3), name="SP1")
    spar.parameters["Start"].value = "0.1 GHz"
    spar.parameters["Stop"].value  = "3 GHz"
    spar.parameters["Step"].value  = "0.01 GHz"
    spar.update_item_annotation()

    # 4) 两个端口（angle=-90 竖放）
    design.add_instance("ads_simulation:TermG:symbol", (-4, -1), name="TermG1", angle=-90)
    design.add_instance("ads_simulation:TermG:symbol", (3, -1), name="TermG2", angle=-90)

    # 5) 连线（两端口直通）
    design.add_wire([(-4, -1), (3, -1)])

    # 6) VAR 变量块（必须用元组路径；删除默认占位变量 X）
    var_inst = design.add_instance(
        ("ads_datacmps", "VAR", "symbol"), (3, 1), name="VAR1", angle=90
    )
    var_inst.vars["L1"] = "1.5"      # 示例电感（nH）
    var_inst.vars["C1"] = "1.0"      # 示例电容（pF）
    del var_inst.vars["X"]           # 删除默认占位变量
    var_inst.update_item_annotation()

    # 7) MeasEqn 测量方程（必须用元组路径）
    measeqn = design.add_instance(
        ("ads_simulation", "MeasEqn", "symbol"), (6, 1), name="Meas1", angle=-90
    )
    eq_list = [
        's21mag=mag(S(2,1))',
        's21phase=phase(S(2,1))',
        'groupdelay=(-1/360)*diff(unwrap(phase(S(2,1))))/diff(freq)',
    ]
    measeqn.parameters["Meas"].value = [eq_list[0]]
    for i in range(len(eq_list) - 1):
        measeqn.parameters["Meas"].repeats.append(
            db.ParamItemString("Meas", "SingleTextLine", eq_list[i + 1])
        )
    measeqn.update_item_annotation()

    # 8) 保存（必须在 VAR 和 MeasEqn 之后调用！）
    design.save_design()
    print(f"schematic saved: {library.name}:{name}:{view}")

    # 9) 生成网表（验证电路可编译）
    netlist = design.generate_netlist()
    print(f"netlist generated: {len(netlist.splitlines())} lines")
    return design


def show_cond_layer(layout=None):
    """自动打开版图的 cond 层：确保所有层可见，并把当前绘制层设为 cond。

    说明：ADS 中不存在 de_layer_display 命令（探测已证实），
    改用可用的 de_layer_prefs_all_visible + de_set_layer。
    """
    try:
        from keysight.ads import ael

        if layout is not None:
            ctx = ael.call.de_get_design_context_from_name(layout.design_name)
        else:
            ctx = ael.call.de_get_current_design_context()

        # 1) 确保所有层可见（cond 在其中，默认 visible=1）
        ael.call.de_layer_prefs_all_visible(ctx)

        # 2) 把当前绘制层设为 cond（db_find_layerid_by_name 需要 ctx；de_set_layer 需要整数 layerid）
        try:
            lid = ael.call.db_find_layerid_by_name(ctx, "cond")
            if hasattr(lid, "layer"):
                lid = lid.layer          # 取 layer_num（整数）
            ael.call.de_set_layer(lid)
            print(f"current layer -> cond (layerid={lid})")
        except Exception as e:
            print("de_set_layer warn:", repr(e))

        try:
            ael.call.de_refresh_layers()
        except Exception:
            pass
    except Exception as e:
        print("show_cond_layer warn:", repr(e))


def create_layout(library, name=cell_name, view="layout"):
    """创建/打开 cell 的版图（layout）视图，并自动打开 CONDUCTOR 层。"""
    layout = db.create_layout(f"{library.name}:{name}:{view}")
    print(f"layout opened: {library.name}:{name}:{view}")
    show_cond_layer(layout)
    return layout


if __name__ == "__main__":
    lib = get_library()
    print("library:", lib.name)

    # 如需显式创建 cell view，可取消下面两行注释：
    # cell = get_cell(lib)
    # print("cell:", cell.name)

    # 默认用全局 cell_name 和 view="schematic"；也可在括号里直接指定 cell / view 名：
    design = create_schematic(lib, "my_cell2", "schematic2")
    print("design ready")

    # 创建版图并自动打开 CONDUCTOR 层（不需要版图时可注释掉此行）
    layout = create_layout(lib, "my_cell2", "layout")
    print("layout ready")

    # 打印当前打开的 workspace 与库（ADS 真实 API，替代不存在的 get_all_open_pointers）
    if de.workspace_is_open():
        ws = de.active_workspace()
        print("workspace:", ws.path)
        print("libraries in workspace:", sorted(ws.library_names))
    print("open (writable) libraries:", sorted(de.get_open_writable_library_names()))

