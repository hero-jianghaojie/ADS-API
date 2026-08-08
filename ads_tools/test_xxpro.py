# -*- coding: utf-8 -*-
"""测试：能否通过 xxpro_context 加载 BT 的 RFPro 视图。"""
from keysight.edatoolbox import multi_python


def probe_rfpro(workspace_name, lib, cell, view):
    """在 EMPro 环境中加载 RFPro 视图并返回项目信息。"""
    import empro
    from keysight.edatoolbox import xxpro
    from keysight.edatoolbox.ads import LibraryCellView

    xxpro.use_workspace(workspace_name)
    pro = LibraryCellView(library=lib, cell=cell, view=view)
    xxpro.load_pro_view(pro)

    with empro.activeProject as project:
        info = {
            "location": str(project.location),
            "n_layouts": len(project.geometry),
            "n_params": len(project.parameters),
            "sim_settings": str(project.simulationSettings),
        }
        return info


if __name__ == "__main__":
    try:
        with multi_python.xxpro_context() as caller:
            result = caller.call(
                probe_rfpro,
                args=["python_wrk", "python_lib", "BT", "rfpro"],
            )
        print("RFPro 加载成功:", result)
    except Exception as e:
        print("xxpro_context 失败:", type(e).__name__, str(e)[:500])
