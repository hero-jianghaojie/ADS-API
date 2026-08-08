# -*- coding: utf-8 -*-
r"""
S 参数图导出工具（替代 RFPro 的 Save Image，因 RFPro 导出有 bug）。

两种用法：
  1) 命令行（用 ADS 自带 Python）：
     python export_s_params.py <数据集.ds> <输出.png>
     例：python export_s_params.py D:/AppGallery/codex/ADS/sim_lpf/lpf25.ds C:/Users/30671/Desktop/1.png

  2) 在 ADS Python Console 中：
     exec(open(r'D:\AppGallery\codex\ADS\ads_tools\export_s_params.py', encoding='utf-8').read())
     export(r'D:\AppGallery\codex\ADS\sim_lpf\lpf25.ds', r'C:\Users\30671\Desktop\1.png')
"""
import sys
from pathlib import Path

# 兼容两种运行方式：
#   1) 命令行：python export_s_params.py ...      （__file__ 存在）
#   2) ADS Python Console：exec(open(...).read())  （__file__ 不存在）
try:
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
except NameError:
    _PROJECT_ROOT = Path(r"D:\AppGallery\codex")

if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from s_params import read_s_params, s21_db, s11_db


def export(ds_path, out_path, title="S-Parameters"):
    """读取 .ds 数据集并导出 S11/S21 曲线图到 out_path (PNG)。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    ds_path = Path(ds_path)
    out_path = Path(out_path)
    if not ds_path.exists():
        print(f"数据集不存在: {ds_path}")
        return False

    f, s11, s21 = read_s_params(ds_path)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(f, s21_db(s21), label="S21", lw=1.6, color="tab:blue")
    ax.plot(f, s11_db(s11), label="S11", lw=1.6, color="tab:green")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_title(f"{title}\n{ds_path.name}")
    ax.set_xlim(float(f[0]), float(f[-1]))
    ax.set_ylim(-60, 5)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"已保存: {out_path}")
    return True


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        export(sys.argv[1], sys.argv[2])
    else:
        print(__doc__)
