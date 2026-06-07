# 33000DWT双燃料油轮货油泵系统设计 - 项目总指挥文件

## 项目目标
完成一篇完整的船舶工程设计论文，同时生成配套CAD货仓结构图（DXF格式）。
论文格式参考：张瑞华《阿芙拉型成品油/原油船货油系统设计》（知网格式）。

---

## 船舶基本参数（从总布置图读取，待确认）
- 船型：33000DWT双燃料成品油轮
- 货油舱：20个（左右对称，10对）
- 污油舱：2个
- 最大装卸能力：2400 m³/h（总），400 m³/h（每舱）
- 独立泵系统：22套（每舱完全分隔）
- 可同时装卸油品种类：6种
- 阀门类型：蝶阀或球阀
- 规范依据：CCS规范、MARPOL附则I、IGF Code

总长 LOA = 179.99 m
垂线间长 LBP = 177.00 m
型宽B= 28.00m
型深D = 15.20 m
设计吃水 = 9.50 m
负载重量=约33,000 MT
货舱区实际长度大约是135m
---

## 团队成员与职责

### 🔧 Agent 1：工程计算专家（engineer）
**职责文件：** `agents/engineer.md`
**核心任务：**
- 泵流量计算
- 扬程计算（舱内水头 + 管路损失 + 通岸高度差）
- 轴功率计算
- 气蚀余量（NPSHr/NPSHa）验算
- 泵型号选择（离心泵）
- 管径计算（各段）
- 输出：`output/calculations.md`（计算书）

### 📚 Agent 2：文献与规范研究员（researcher）
**职责文件：** `agents/researcher.md`
**核心任务：**
- 整理CCS规范对货油管系的要求
- 整理MARPOL附则I相关条款
- 整理OCIMF集管区布置要求
- 整理吸油井设计规范要求
- 整理惰气系统（FSS Code）要求
- 整理透气系统规范要求
- 输出：`output/regulations.md`（规范摘要）

### ✍️ Agent 3：论文写作专家（writer）
**职责文件：** `agents/writer.md`
**核心任务：**
- 读取 `output/calculations.md` 和 `output/regulations.md`
- 按知网论文格式撰写各章节
- 生成各子系统原理示意图（SVG/ASCII）
- 输出：`output/thesis.md`（完整论文）

### 🖊️ Agent 4：CAD图纸生成师（cad_engineer）
**职责文件：** `agents/cad_engineer.md`
**核心任务：**
- 读取船舶参数和货仓布置方案
- 用Python ezdxf库生成货仓结构图DXF文件
- 包含：平面图、纵剖面图、横剖面图、舱室编号、尺寸标注
- 输出：`output/cargo_tank_arrangement.dxf`

### 🔍 Agent 5：审校专家（reviewer）
**职责文件：** `agents/reviewer.md`
**核心任务：**
- 检查论文格式是否符合知网标准
- 检查计算数据在论文中是否一致
- 检查图表编号、参考文献格式
- 输出：审校意见，由writer修改后终稿

---

## 工作流程（严格按顺序执行）

```
阶段1：准备
  └── researcher 整理规范要求 → output/regulations.md

阶段2：计算
  └── engineer 完成全部工程计算 → output/calculations.md

阶段3：并行执行
  ├── writer 撰写论文 → output/thesis.md
  └── cad_engineer 生成DXF → output/cargo_tank_arrangement.dxf

阶段4：收尾
  └── reviewer 审校 → writer 修改 → output/thesis_final.md
```

---

## 论文章节结构

```
摘要（中文，150字左右）
关键词（5个）
0. 前言
1. 货仓结构
2. 管材选用
3. 货油泵系统设计
   3.1 流量计算
   3.2 扬程计算
   3.3 功率计算
   3.4 气蚀验算
   3.5 泵型号选择
4. 吸油井设计
5. 管路布置
   5.1 舱内管路
   5.2 甲板管路
6. 惰气吹扫系统
7. 透气系统
8. 结论
参考文献
```

---

## 输出文件清单

| 文件 | 负责Agent | 格式 |
|------|----------|------|
| `output/regulations.md` | researcher | Markdown |
| `output/calculations.md` | engineer | Markdown含公式 |
| `output/thesis.md` | writer | Markdown |
| `output/thesis_final.md` | writer(修订后) | Markdown |
| `output/cargo_tank_arrangement.dxf` | cad_engineer | DXF |
| `output/generate_dxf.py` | cad_engineer | Python脚本 |

---

## 参考文献（任务书指定）
[1] 船舶设计实用手册（第3版）——轮机分册，国防工业出版社，2013
[2] 离心泵应用技术，吴德明，中国石化出版社，2013
[3] 船舶设计原理，谢云平，国防工业出版社，2014
[4] 工程流体力学（第四版），孔珑，中国电力出版社，2013

---

## 启动指令
在Claude Code中输入以下内容开始工作：
"请按照CLAUDE.md的工作流程，从阶段1开始，researcher先整理规范要求"
