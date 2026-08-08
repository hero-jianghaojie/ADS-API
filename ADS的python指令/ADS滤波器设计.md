# ADS 滤波器设计

> 切比雪夫低通滤波器设计公式、集总参数和微带线实现。

---

## 一、切比雪夫滤波器设计公式

### 1.1 规格参数

| 符号 | 含义 | 典型值 |
|------|------|--------|
| `ripple_db` / $\delta$ | 通带纹波 (dB) | 0.1 |
| `fc` / $f_c$ | 截止频率 (GHz) | 0.8 |
| `fs` / $f_s$ | 阻带频率 (GHz) | 1.5 |
| `R0` | 参考阻抗 ($\Omega$) | 50 |
| `La` / $\alpha_s$ | 阻带要求衰减 (dB) | 40 |

### 1.2 核心公式

**纹波因子：**
$$\varepsilon^2 = 10^{\delta/10} - 1$$

**最小阶数：**
$$n = \left\lceil \frac{\operatorname{arccosh}\left(\sqrt{(10^{\alpha_s/10} - 1) / \varepsilon^2}\right)}{\operatorname{arccosh}(\omega_s / \omega_c)} \right\rceil$$

**实际阻带衰减：**
$$A_s = 10 \log_{10}\left[1 + \varepsilon^2 \cosh^2\left(N \cdot \operatorname{arccosh}(\omega_s / \omega_c)\right)\right]$$

**Cauer 原型参数：**
$$\beta = \ln\left(\coth\frac{\delta}{17.37}\right),\quad \gamma = \sinh\left(\frac{\beta}{2n}\right)$$

$$A_k = \sin\frac{(2k-1)\pi}{2n},\quad B_k = \gamma^2 + \sin^2\frac{k\pi}{n}$$

**原型元件值：**
$$G_1 = \frac{2A_1}{\gamma},\quad G_k = \frac{4A_{k-1}A_k}{B_{k-1}G_{k-1}}\;(k=2,3,\dots,n)$$

### 1.3 Python 实现

```python
def chebyshev_lowpass_design(ripple_db, fc, fs, R0, La):
    pi = np.pi
    wc = 2 * pi * fc * 1e9
    ws = 2 * pi * fs * 1e9
    eps_sq = 10**(ripple_db / 10) - 1

    N = int(np.ceil(
        np.arccosh(np.sqrt((10**(La / 10) - 1) / eps_sq)) /
        np.arccosh(ws / wc)
    ))

    Atten = round(10 * np.log10(1 + eps_sq * np.cosh(N * np.arccosh(ws / wc)) ** 2), 2)

    beta  = np.log(np.cosh(ripple_db / 17.37) / np.sinh(ripple_db / 17.37))
    gamma = np.sinh(beta / (2 * N))

    ak, bk, gk = [], [], []
    for k in range(1, N + 1):
        ak.append(np.sin((2 * k - 1) * pi / (2 * N)))
        bk.append(gamma**2 + np.sin(k * pi / N)**2)

    for k in range(1, N + 1):
        if k == 1:
            gk.append(round(2 * ak[0] / gamma, 4))
        else:
            gk.append(round(4 * ak[k-1] * ak[k-2] / (bk[k-2] * gk[k-2]), 4))
    return N, Atten, gk
```

---

## 二、集总参数 LPF

### 2.1 去归一化

```python
# 奇数次 → 串联电感 (nH)
L_k = G_k * R0 / ωc * 1e9
# 偶数次 → 并联电容 (pF)
C_k = G_k / (R0 * ωc) * 1e12
```

### 2.2 原理图结构

```
TermG1 ── L1 ──┬── L2 ──┬── L3 ──┬── TermG2
               │        │        │
               C1       C2       C3
               │        │        │
              GND      GND      GND
```

### 2.3 关键组件参数

| 组件 | 参数 | 值格式 |
|------|------|--------|
| `L:symbol` | `L` | `"L1 nH"`（引用 VAR 变量） |
| `C:symbol` | `C` | `"C1 pF"`（引用 VAR 变量） |
| `TermG:symbol` | `Z` | `"50 Ohm"`（默认） |
| `S_Param:symbol` | `Start/Stop/Step` | `"0.01 GHz"`, `"3 GHz"`, `"0.001 GHz"` |

---

## 三、微带线 LPF

### 3.1 阶梯阻抗原理

```
奇数次 (k=1,3,5,...) → high-Z 线 → 串联电感:  θ = g·R₀ / Z_high
偶数次 (k=2,4,6,...) → low-Z 线  → 并联电容:  θ = g·Z_low / R₀
```

| 参数 | 含义 | 典型值 |
|------|------|--------|
| `Z_high` | 高阻抗线特性阻抗 ($\Omega$) | 100 |
| `Z_low` | 低阻抗线特性阻抗 ($\Omega$) | 15 |

### 3.2 物理长度

$$l_k = \frac{\theta_k}{2\pi} \cdot \lambda_{gk}, \quad \lambda_{gk} = \frac{c_0}{f_c \sqrt{\varepsilon_{\text{eff},k}}}$$

### 3.3 微带线宽计算（Hammerstad & Jensen）

```python
def microstrip_width(Z0, H, Er):
    """微带线宽 (mm), 给定 Z₀(Ω)、H(mm)、Er"""
    eta0 = 376.730313
    B = eta0 * np.pi / (2 * Z0 * np.sqrt(Er))
    A = (Z0 / 60) * np.sqrt((Er + 1) / 2) + \
        ((Er - 1) / (Er + 1)) * (0.23 + 0.11 / Er)
    WH_est = 8 * np.exp(A) / (np.exp(2 * A) - 2)
    if WH_est <= 2:
        WH = WH_est
    else:
        WH = (2 / np.pi) * (
            B - 1 - np.log(2 * B - 1) +
            ((Er - 1) / (2 * Er)) * (np.log(B - 1) + 0.39 - 0.61 / Er)
        )
    return WH * H


def microstrip_eff_eps(W, H, Er):
    """微带线有效介电常数 ε_eff"""
    WH = W / H
    if WH <= 1:
        F = (1 + 12 / WH)**(-0.5) + 0.04 * (1 - WH)**2
    else:
        F = (1 + 12 / WH)**(-0.5)
    return (Er + 1) / 2 + (Er - 1) / 2 * F
```

### 3.4 MSUB 衬底参数

```python
msub = design.add_instance("ads_tlines:MSUB:symbol", (-3, 2), name="MSub1")
msub.parameters["H"].value     = "0.762 mm"    # 基板高度
msub.parameters["Er"].value    = "3.66"         # 相对介电常数
msub.parameters["Mur"].value   = "1"            # 相对磁导率
msub.parameters["Cond"].value  = "5.8e7"        # 导体电导率 (铜)
msub.parameters["Hu"].value    = "1.0e+33 mm"   # 封装高度（无限大）
msub.parameters["T"].value     = "0.035 mm"     # 金属厚度 (1oz)
msub.parameters["TanD"].value  = "0.0037"       # 损耗角正切
msub.parameters["Rough"].value = "0 mm"         # 表面粗糙度
```

### 3.5 MLIN 参数

```python
mlin = design.add_instance("ads_tlines:MLIN:symbol", (x, -2), name=f"TL{i+1}")
mlin.parameters["W"].value     = "W1 mm"        # 线宽（引用VAR变量，单位在组件参数中）
mlin.parameters["L"].value     = "L1 mm"        # 线长（引用VAR变量，单位在组件参数中）
mlin.parameters["Subst"].value = '"MSub1"'      # 衬底引用（必须加双引号）
```

**重要：** 
- `Subst` 参数的值必须用双引号包裹，即 `'"MSub1"'`，ADS 网表中才能正确解析为 `Subst="MSub1"`。
- **VAR 值只存裸数值**，不要在 VAR 中带单位。单位统一在组件参数中指定。
  - ✅ VAR: `"0.2815"`  →  MLIN: `"W1 mm"`
  - ❌ VAR: `"0.2815 mm"` → MLIN: `"W1 mm"`（双重单位，导致参数异常）

### 3.6 阶梯阻抗滤波器设计经验

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `Z_high` | 90~120 Ω | 太低则串联电感不足，太高则线宽过细难以制造 |
| `Z_low` | 10~20 Ω | 太高则并联电容不足，阻带衰减不够 |
| 阻抗比 `Z_high/Z_low` | ≥ 5 | 比值越大滤波效果越好 |
| 最小线宽 | ≥ 0.1 mm | 取决于工艺能力，过细的线导致阻抗不准 |

### 3.7 微带线原理图布局

```
TermG1 ── [feed_in] ── [TL1] ── [TL2] ── ... ── [TL7] ── [feed_out] ── TermG2
```

坐标规则（间距 2 单位）：
- feed_in 放在 `(-3, -2)`，引脚在 `(-3, -2)` 和 `(-2, -2)`
- MLIN `TL_i` 放在 `((i-1)*2, -2)`，引脚在 `((i-1)*2, -2)` 和 `((i-1)*2+1, -2)`
- 连线从 `(prev_x+1, -2)` 到 `(curr_x, -2)`
- TermG 放在端口处，`angle=-90`

### 3.8 参数扫描（ParamSweep）

如需扫描 Er、H 等衬底参数，需要：
1. 在 VAR 块中定义变量（如 `Er = 3.66`）
2. MSUB 参数引用该变量：`msub.parameters["Er"].value = "Er"`
3. 添加 ParamSweep 控制器，设置 `SweepVar` 为 `"Er"`
4. ParamSweep 的 `SimInstanceName` 引用仿真控制器：`"SP1"`
