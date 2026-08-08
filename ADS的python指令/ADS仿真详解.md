# ADS 仿真（Simulation）文档整理

> 来源：ADS 2025 Update2 帮助文档 `Simulation.html`（`doc\ads\Content\ads2025update2\support\Simulation.html`）
> 该页面是 ADS「仿真」主题的**总入口/导航页**，下面按主题整理了全部仿真相关内容及子页面结构。

## 总览：Simulation 页面子主题

| # | 子主题 | 说明 |
|---|--------|------|
| 1 | [xxPro EM Tools](#1-xxpro-em-tools) | xxPro 系列电磁仿真工具（SIPro/PIPro/RFPro/PEPro/QuantumPro） |
| 2 | [Simulation-Analog RF](#2-simulation-analog-rf-模拟rf仿真) | 模拟/RF 电路仿真器全集 |
| 3 | [Equations and Expressions](#3-equations-and-expressions-方程与表达式) | 测量表达式、仿真器表达式、方程类型 |
| 4 | [Electromagnetic](#4-electromagnetic-em-仿真momentum-和-fem) | EM 仿真：Momentum 与 FEM |
| 5 | [Test Benches](#5-test-benches-测试台) | RF 功放测试台、虚拟测试台 |
| 6 | [Model Creation](#6-model-creation-模型创建) | 模型创建与兼容性 |
| 7 | Photonic Designer | 光子设计器 |
| 8 | [Simulation Error Messages](#8-simulation-error-messages-仿真错误消息) | 仿真错误消息 |

---

## 1. xxPro EM Tools

> **适用范围**：SIPro、PIPro、RFPro、PEPro 工具及 QuantumPro。

- ADS 提供用于设计和评估现代通信系统产品的 EM 仿真工具。
- 为 **Momentum** 和 **FEM** 仿真器提供**统一接口**。
- 计算 **S 参数、表面电流和场**。
- 支持微带（microstrip）、带状线（stripline）、共面波导（coplanar waveguide）等一般平面电路拓扑。

子主题：
- **xxPro**
- **RFPro**
- **SIPro and PIPro**
- **PEPro**
- **QuantumPro**
- **Upgrading Python Scripts**（升级 Python 脚本）

---

## 2. Simulation-Analog RF（模拟/RF 仿真）

电路仿真器全集（Circuit Simulators）：

### 基础电路仿真
- **Using Circuit Simulators** — 使用电路仿真器
- **DC Simulation** — 直流仿真
- **AC Simulation** — 交流小信号仿真
- **S-Parameter Simulation** — S 参数仿真

### 大信号 / 非线性仿真
- **Harmonic Balance Simulation** — 谐波平衡（HB）仿真
- **X-Parameter Generator** — X 参数生成器
- **Large-Signal S-Parameter Simulation** — 大信号 S 参数仿真
- **Gain Compression Simulation** — 增益压缩仿真
- **P2D Simulation** — P2D 仿真

### 时域 / 数字
- **Transient and Convolution Simulation** — 瞬态与卷积仿真
- **Circuit Envelope Simulation** — 电路包络仿真
- **Channel Simulation** — 通道仿真
- **DDR Memory Simulation** — DDR 存储器仿真
- **Chiplet PHY Designer Simulation** — Chiplet PHY 设计器仿真
- **HSD Simulation** — 高速数字（HSD）仿真
- **System Designer for PCIe Simulation** — PCIe 系统设计器仿真
- **System Designer for USB Simulation** — USB 系统设计器仿真

### 自动化 / 分析 / 专项
- **Batch Simulation** — 批处理仿真
- **Data Based Load Pull Simulation** — 基于数据的负载牵引仿真
- **Sensitivity Analysis** — 灵敏度分析
- **Simulation Instruments** — 仿真仪器
- **Tuning and Optimization and Statistical Design** — 调谐、优化与统计设计
- **ElectroThermal Simulator** — 电热仿真器
- **Quantum Circuit Simulation** — 量子电路仿真

---

## 3. Equations and Expressions（方程与表达式）

- **Measurement Expressions** — 测量表达式
- **Simulator Expressions** — 仿真器表达式
- **Summary of ADS Equation Types** — ADS 方程类型总结

---

## 4. Electromagnetic（EM 仿真：Momentum 和 FEM）

EM 仿真是 ADS 仿真体系中体量最大的部分，分为 **Momentum（矩量法）** 与 **FEM（有限元）** 两大求解器。

### 4.1 EM 仿真概述
- **EM Simulation Overview** — EM 仿真概述

### 4.2 Momentum（矩量法）
- Momentum Overview — 概述
- Theory of Operation for Momentum — 工作原理
- Setting up Momentum Simulations — 设置仿真
- Examples — 设置示例
- HSD Applications — HSD 应用 EM 设置指南

### 4.3 FEM（有限元法）
- FEM Overview — 概述
- Theory of Operation for FEM — 工作原理
- Setting up FEM Simulations — 设置仿真
- **Example: Designing a Microstrip Filter** — 微带滤波器设计示例
- Guidelines for Optimal Performance — 最优性能指南

### 4.4 布局（Layout）起步
- Getting Started with a Layout for EM Simulations — 布局起步
  - Creating a Layout for EM Simulations — 创建布局
  - Using the Cookie Cutter — 使用 Cookie Cutter
  - Defining Component Parameters — 定义组件参数
  - Converting Layers between Strip and Slot — 条带/缝隙层转换
  - Example: Designing a Microstrip Line — 微带线设计示例

### 4.5 EM 衬底（Substrate）
- Defining Substrates for EM — 定义衬底
- Sweeping Substrate Name and Mesh Density — 扫描衬底名称与网格密度
- Adding Boxes, Waveguides, and Symmetry Planes — 添加盒子、波导与对称面
- Modeling Through-Silicon Vias — 硅通孔（TSV）建模
- Variables in Substrates and Materials — 衬底与材料中的变量
- Dielectric Substrate Modeling — 介质衬底建模
- Generating Thermal Technology Files — 用衬底编辑器生成热技术文件
- Converting Substrate Files to LTD Format — 衬底文件转 LTD 格式

### 4.6 端口（Ports）
- Ports Overview — 端口概述
- Defining Ports — 定义端口
- Ports for Momentum — Momentum 端口
- Ports for FEM — FEM 端口

### 4.7 设置 EM 仿真
- EM Setup Window Overview — 设置窗口概述
- Viewing Layout Information — 查看布局信息
- Automatic EM Circuit Partitioning — 自动 EM 电路分区
- Viewing the Substrate — 查看衬底
- Viewing Ports — 查看端口
- Defining a Frequency Plan — 定义频率计划
- Defining Simulation Options — 定义仿真选项
- Defining an Output Plan — 定义输出计划
- Specifying Simulation Resources — 指定仿真资源
- Generating an EM Model — 生成 EM 模型
- Using EM Setup Window Tools — 设置窗口工具
- Using an EM Setup Template — 设置模板

### 4.8 管理 EM 仿真
- Running EM Simulations — 运行仿真
- Using the Job Manager — 使用作业管理器
- Viewing Simulation Summary — 查看仿真摘要
- Running a Momentum simulation from Command Line — 命令行运行 Momentum

### 4.9 3D 查看结果
- Visualizing 3D View before EM Simulations — 仿真前 3D 预览
- Visualizing Momentum Simulations — Momentum 结果可视化
- Visualizing FEM Simulations — FEM 结果可视化
- Computing Radiation Patterns — 计算辐射方向图

### 4.10 EM 电路协同仿真（Cosimulation）
- EM Circuit Cosimulation Overview — 概述
- Using the EM Cosimulation View — 协同仿真视图
- Using the EM Model View — EM 模型视图
- Using the EM Circuit Excitation AEL Addon — EM 电路激励 AEL 插件
- Manual Versus Automatic EM Circuit Partitioning — 手动 vs 自动分区

### 4.11 EM 设计与 ADS 集成
- EM Design and ADS Integration Process — 集成流程
- Saving EMPro Designs in a Library — 保存 EMPro 设计到库
- Adding an EM Design Library in ADS — 添加 EM 设计库
- Using EM Design Components in ADS Schematic — 原理图中使用 EM 组件
- Exporting ADS Layouts to EM Design — 导出 ADS 布局
- EM Design and ADS Integration FAQs
- Using EM Design Components in ADS Layout — 布局中使用 EM 组件
- Exporting from xxPro to EM Design — 从 xxPro 导出

### 4.12 其他 EM 功能
- **Package Model Extraction** — 封装模型提取
- **CoilSys**（电感综合工具）
  - Using CoilSys
  - Using the CoilSys Package
  - Synthesis and Inductor Finder — 综合与电感查找器
- **Preview Layouts** — 布局预览

---

## 5. Test Benches（测试台）

- **RF Power Amplifier Test Benches** — RF 功率放大器测试台
- **Virtual Test Benches** — 虚拟测试台

---

## 6. Model Creation（模型创建）

- **Broadband SPICE Model Generator** — 宽带 SPICE 模型生成器
- **Narrowband SPICE Model Generator** — 窄带 SPICE 模型生成器
- **Model Composer** — 模型编辑器
- **Advanced Model Composer** — 高级模型编辑器
- **HSPICE Compatibility** — HSPICE 兼容性
- **Spectre Compatibility** — Spectre 兼容性
- **RF Intellectual Property Encoder** — RF 知识产权（IP）编码器
- **User-Defined Models** — 用户自定义模型
- **ANN Modeling** — 人工神经网络建模

---

## 7. Photonic Designer（光子设计器）

ADS 光子设计相关主题（详见 `photonics/Photonic_Designer.html`）。

---

## 8. Simulation Error Messages（仿真错误消息）

仿真错误信息汇总（详见 `simerror/Simulation_Error_Messages.html`），用于排查仿真失败/告警。

---

## 备注

- 以上子页面均为 ADS 本地帮助文档，路径前缀：`D:\Program Files\Keysight\ADS2025_Update2\doc\ads\Content\ads2025update2\`
- 仿真核心组件在 Python 脚本中通常通过 `Simulation` 数据组件（如 `SimDC`、`SimAC`、`SimS_Param`、`SimHB` 等）与 `Sweep`、`MeasEqn` 配合使用。
