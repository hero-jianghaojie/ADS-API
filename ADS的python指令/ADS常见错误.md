# ADS Python 常见错误与注意事项

---

## 一、组件库路径错误
- MSUB 在 `ads_tlines`，**不在** `ads_rflib`
- MLIN 在 `ads_tlines`，**不在** `ads_rflib`
- VAR 和 MeasEqn 必须用 **元组路径**

## 二、VAR 默认变量
- 创建 VAR 块后默认存在变量 `X`，必须用 `del var_inst.vars["X"]` 删除

## 三、Subst 参数引用
- `Subst` 参数值必须加双引号：`'"MSub1"'`

## 四、偶数阶滤波器
- 偶数阶切比雪夫滤波器两端端接相等阻抗时存在匹配问题
- 输出端 $G_{n+1} = \coth^2(\beta/4)$ 不为 1，实际响应与理论有偏差

## 五、Dataset 文件名冲突
- 必须用 `datetime.now().strftime('%H%M%S')` 生成唯一名，避免文件锁

## 六、UnicodeDecodeError
- `lib.setup_schematic_tech()` 可能抛出 `UnicodeDecodeError`，不影响功能，捕获即可

## 七、BUF 器件不存在
- ADS 标准库中**没有**名为 `BUF` 的器件
- 可用 `ads_behavioral:OpAmpIdeal:symbol` 配置为单位增益缓冲器替代
- 也可用 `ads_behavioral:Amplifier:symbol` 设增益为 0dB 替代

## 八、VAR 值不要带单位（重要！）
- VAR 块中**只存裸数值**，单位在组件参数中指定
- ❌ 错误：`var_w.vars["W1"] = "0.2815 mm"` → MLIN: `"W1 mm"` → 双重单位
- ✅ 正确：`var_w.vars["W1"] = "0.2815"` → MLIN: `"W1 mm"` → W1 * 1mm
- 集总元件同理：`var.vars["L1"] = "11.62"` → 电感参数: `"L1 nH"`

## 九、调试：打印网表
- 在 `generate_netlist()` 后加 `print(netlist[:2000])`
- 直接检查 ADS 收到的元件参数和连接是否正确
- 网表中能清楚看到每个 MLIN 的 W、L、Subst 值

## 十、调试阶段简化
- 初次调试**去掉 group delay** 等非必要测量方程
- 先确认 S11/S21 曲线基本正确，再加其他测量
- 仿真频段范围不宜过大（0~5×fc 足够）

## 十一、MSTEP 在电路仿真中不可用
- `ads_tlines:MSTEP:symbol` 是**版图元件**，`hpeesofsim` 电路仿真器不支持
- 在电路仿真中直接用 MLIN 级联加连线即可，MSTEP 的寄生效应可忽略
- 如需考虑阶跃不连续性，可手动调整相邻 MLIN 的长度

## 十二、ParamSweep 使用要点
- ParamSweep 的 `SimInstanceName` 参数引用被扫描的仿真控制器（如 `SP1`）
- 被扫描的参数必须在 **VAR 变量块**中定义，**不能是硬编码值**
  - ✅ MSUB 参数引用 VAR: `msub.parameters["Er"].value = "Er"`
  - ❌ MSUB 参数硬编码: `msub.parameters["Er"].value = "3.66"`
- ParamSweep 需要在 `design.save_design()` 之前添加
- 实例名冲突时用时间戳: `name=f"ParamSweep_{datetime.now().strftime('%H%M%S')}"`

## 十三、原理图构建顺序
- 正确顺序：
  1. 创建原理图
  2. 添加所有元件（MSUB、MLIN、TermG、S_Param 等）
  3. 添加连线
  4. 添加 VAR 变量块
  5. 添加 MeasEqn
  6. `design.save_design()` ← 最后保存！
  7. `design.generate_netlist()`
  8. 运行仿真
