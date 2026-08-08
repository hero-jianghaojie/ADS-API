# -*- coding: utf-8 -*-
"""供 xxpro_context 调用的函数（必须在独立模块中定义，pickle 才能序列化）。"""

EMPRO_BIN = r"D:\Program Files\Keysight\ADS2025_Update2\fem\2025.20\win32_64\bin"


def _setup_qt_env():
    """EMPro 子进程需要正确的 Qt 插件路径，否则报 'Could not find the Qt platform plugin'。"""
    import os
    qt_plugins = os.path.join(EMPRO_BIN, "plugins", "qt")
    os.environ["QT_PLUGIN_PATH"] = qt_plugins


def probe_rfpro():
    """加载 BT:rfpro 视图并返回项目摘要信息。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        info = {
            "location": str(project.location),
            "n_geometries": len(project.geometry),
            "n_params": len(project.parameters),
            "n_analyses": len(project.analyses),
        }
        return info


def simple_ping():
    """仅测试连接。"""
    import empro
    return empro.__file__


def inspect_analyses():
    """加载 RFPro 视图并打印 analyses 的配置信息。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        out = []
        for a in project.analyses:
            out.append({
                "name": a.name,
                "type": type(a).__name__,
            })
        params = {}
        for p in project.parameters:
            try:
                params[p.name] = p.formula
            except Exception:
                pass
        return {"analyses": out, "params": params}


def inspect_analysis_methods():
    """打印第一个 Analysis 对象和 activeProject 的可用方法。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        a = project.analyses[0]
        amethods = [m for m in dir(a) if not m.startswith('_')]
        pmethods = [m for m in dir(project) if not m.startswith('_') and any(
            k in m.lower() for k in ['sim', 'run', 'anal', 'queue', 'freq', 'save', 'result'])]
        return {"analysis_methods": amethods, "project_methods": pmethods}


def create_sim_test():
    """加载视图 → 检查分析频率设置 → 尝试从分析创建仿真（不运行）。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        out = {}
        a = project.analyses[0]
        out["analysis_name"] = a.name
        out["analysis_type"] = str(a.analysisType)
        # 频率设置
        try:
            ss = a.simulationSettings
            out["sim_settings"] = str(ss)
        except Exception as e:
            out["sim_settings_err"] = str(e)
        # 端口
        try:
            out["n_ports"] = len(list(a.ports))
        except Exception as e:
            out["ports_err"] = str(e)
        # 尝试创建仿真
        try:
            sim = project.createSimulationFromAnalysis(a)
            out["sim_created"] = str(sim)
            out["n_sims"] = len(list(project.simulations))
        except Exception as e:
            out["create_sim_err"] = f"{type(e).__name__}: {str(e)[:300]}"
        return out


def inspect_sim_api():
    """打印 createSimulationFromAnalysis / createSimulationsFromAnalysis 的签名。"""
    _setup_qt_env()
    import empro, inspect
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        out = {}
        for mname in ["createSimulationFromAnalysis", "createSimulationsFromAnalysis",
                      "createSimulationEx", "createSimulationsEx", "addSimulationDataToProject"]:
            m = getattr(project, mname, None)
            if m is None:
                out[mname] = "(无)"
                continue
            try:
                out[mname] = str(inspect.signature(m))
            except Exception as e:
                out[mname] = f"signature err: {e}"
            try:
                doc = inspect.getdoc(m) or ""
                out[mname + "_doc"] = doc[:400]
            except Exception:
                pass
        return out


def inspect_settings_and_create():
    """探查 simulationSettings 并尝试直接创建仿真（不运行）。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        out = {}
        ss = project.simulationSettings
        for attr in ["engine", "sParametersEnabled", "name", "parameterSweepEnabled"]:
            try:
                out[attr] = str(getattr(ss, attr))
            except Exception as e:
                out[attr] = f"err {e}"
        try:
            out["freq_plan"] = str(list(ss.femFrequencyPlanList()))
        except Exception as e:
            out["freq_plan"] = f"err {e}"
        try:
            sim = project.createSimulation(False)
            out["createSimulation_ok"] = str(sim)
            out["n_sims"] = len(list(project.simulations))
        except Exception as e:
            out["createSimulation_err"] = f"{type(e).__name__}: {str(e)[:300]}"
        return out


def create_simulations_from_analysis_test():
    """按 analysis/__init__.py 源码格式调用 createSimulationsFromAnalysis。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        out = {}
        a = project.analyses[0]
        # 先保存项目，确保处于有效状态
        try:
            project.saveActiveProject()
            out["saved"] = True
        except Exception as e:
            out["save_err"] = f"{type(e).__name__}: {str(e)[:200]}"
        try:
            sims = project.createSimulationsFromAnalysis(False, False, [""], a, {}, {})
            out["ok"] = [str(s) for s in sims]
            out["n_sims"] = len(list(project.simulations))
        except Exception as e:
            out["err"] = f"{type(e).__name__}: {str(e)[:300]}"
        return out


def inspect_validity():
    """探查项目和分析的 validity / 更新状态。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        out = {}
        for attr in ["isValid", "reasonWhyInvalid"]:
            try:
                out["project." + attr] = str(getattr(project, attr)())
            except Exception as e:
                out["project." + attr] = f"err {e}"
        a = project.analyses[0]
        for attr in ["isValid", "reasonWhyInvalid", "isEmpty"]:
            try:
                out["analysis." + attr] = str(getattr(a, attr)())
            except Exception as e:
                out["analysis." + attr] = f"err {e}"
        return out


def create_with_retry():
    """加载视图后等待更新完成（带重试），再创建仿真。"""
    _setup_qt_env()
    import time
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    out = {}
    with empro.activeProject as project:
        a = project.analyses[0]
        project.saveActiveProject()

        last_err = ""
        for attempt in range(5):
            try:
                sims = project.createSimulationsFromAnalysis(False, False, [""], a, {}, {})
                out["ok"] = [str(s) for s in sims]
                out["n_sims"] = len(list(project.simulations))
                out["attempts"] = attempt + 1
                return out
            except Exception as e:
                last_err = str(e)[:200]
                time.sleep(3)
        out["err"] = last_err
        return out


def inspect_all_project_methods():
    """列出 project 的全部公开方法。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        return [m for m in dir(project) if not m.startswith('_')]


def deep_diagnose():
    """深入诊断：检查 geometry/mesh/analyses 状态。"""
    _setup_qt_env()
    import time
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    out = {}
    with empro.activeProject as project:
        out["name"] = str(project.name)
        try:
            out["n_geom"] = len(list(project.geometry))
        except Exception as e:
            out["n_geom_err"] = str(e)
        try:
            out["mesh"] = str(project.mesh)
        except Exception as e:
            out["mesh_err"] = str(e)
        try:
            out["simulations"] = [str(s) for s in project.simulations]
        except Exception as e:
            out["sims_err"] = str(e)
        # 等待几秒看 update 是否完成
        time.sleep(5)
        try:
            out["isValid_after_wait"] = str(project.isValid())
        except Exception as e:
            out["isValid_err"] = str(e)
        # 尝试 addSimulationDataToProject
        try:
            s = project.addSimulationDataToProject(False)
            out["addSimulationData"] = str(s)
        except Exception as e:
            out["addSimulationData_err"] = f"{type(e).__name__}: {str(e)[:200]}"
        return out


def create_with_internal_analysis():
    """初始化 base app + 设置 analysisToUseForSimulation 后创建仿真。"""
    _setup_qt_env()
    import sys
    import types
    import empro
    import empro.toolkit.analysis  # 可能触发 internal 模块注册
    from empro.toolkit.simulation import _enforceBaseApp
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    _enforceBaseApp()
    out = {"internal_import": ""}
    # 尝试激活 empro.internal.analysis
    ia = None
    try:
        import empro.internal.analysis as ia_mod
        ia = ia_mod
        out["internal_import"] = "ok"
    except Exception as e:
        out["internal_import"] = f"fail: {e}"
        # 手动注入
        try:
            internal = sys.modules.get("empro.internal")
            if internal is None:
                internal = types.ModuleType("empro.internal")
                sys.modules["empro.internal"] = internal
            if not hasattr(internal, "analysis"):
                an = types.ModuleType("empro.internal.analysis")
                sys.modules["empro.internal.analysis"] = an
                internal.analysis = an
            ia = sys.modules["empro.internal.analysis"]
            out["internal_import"] = "injected"
        except Exception as e2:
            out["internal_import"] = f"inject fail: {e2}"

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        a = project.analyses[0]
        project.saveActiveProject()
        if ia is not None:
            ia.analysisToUseForSimulation = a
        try:
            sims = project.createSimulationsFromAnalysis(False, False, [""], a, {}, {})
            out["ok"] = [str(s) for s in sims]
            out["n_sims"] = len(list(project.simulations))
        except Exception as e:
            out["err"] = f"{type(e).__name__}: {str(e)[:400]}"
        return out

def inspect_existing_simulations():
    """检查项目已有仿真的状态、路径和结果。"""
    _setup_qt_env()
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace("python_wrk")
    pro = LibraryCellView(library="python_lib", cell="BT", view="rfpro")
    xxpro.load_pro_view(pro)

    out = {}
    with empro.activeProject as project:
        sims = list(project.simulations)
        out["n_sims"] = len(sims)
        for s in sims:
            info = {}
            for attr in ["name", "status", "simulationPath", "simulationDir"]:
                try:
                    info[attr] = str(getattr(s, attr))
                except Exception:
                    try:
                        info[attr] = str(getattr(s, attr)())
                    except Exception as e:
                        info[attr] = f"err {e}"
            out[str(s)] = info
        return out