# 团队任务总清单

## 状态说明
- [ ] 未开始
- [~] 进行中
- [x] 已完成

---

## 阶段0：项目启动（你来做）
- [ ] 从总布置图PDF右下角读取船舶主要参数，填入CLAUDE.md
- [ ] 确认Python环境已安装（`python --version`）
- [ ] 确认ezdxf已安装（`pip install ezdxf --break-system-packages`）
- [ ] 在Claude Code中打开本项目文件夹

---

## 阶段1：规范整理（researcher负责）
- [ ] Task R-1：整理CCS货油管系要求
- [ ] Task R-2：整理MARPOL附则I相关条款
- [ ] Task R-3：整理OCIMF集管区布置要求
- [ ] Task R-4：整理惰气系统（FSS Code）要求
- [ ] Task R-5：整理透气系统规范要求
- [ ] Task R-6：整理吸油井设计规范要求
- [ ] 输出：`output/regulations.md` ✓

---

## 阶段2：工程计算（engineer负责）
- [ ] Task E-1：流量计算（确认每舱400 m³/h，换算管段流量）
- [ ] Task E-2：扬程计算（静扬程+管路损失）
- [ ] Task E-3：功率计算（轴功率+电机功率）
- [ ] Task E-4：气蚀验算（NPSHa vs NPSHr）
- [ ] Task E-5：管径计算（各段管径）
- [ ] Task E-6：泵型号选择
- [ ] 输出：`output/calculations.md` ✓

---

## 阶段3A：论文写作（writer负责）
- [ ] Task W-1：摘要+关键词
- [ ] Task W-2：第0章 前言
- [ ] Task W-3：第1章 货仓结构
- [ ] Task W-4：第2章 管材选用
- [ ] Task W-5：第3章 货油泵系统设计（含全部计算）
- [ ] Task W-6：第4章 吸油井设计
- [ ] Task W-7：第5章 管路布置
- [ ] Task W-8：第6章 惰气吹扫系统
- [ ] Task W-9：第7章 透气系统
- [ ] Task W-10：第8章 结论
- [ ] Task W-11：参考文献
- [ ] 输出：`output/thesis.md` ✓

---

## 阶段3B：CAD图纸（cad_engineer负责，与3A并行）
- [ ] Task C-1：安装ezdxf依赖
- [ ] Task C-2：编写generate_dxf.py脚本
  - [ ] 图层设置
  - [ ] 平面图（10对货油舱+2污油舱+泵舱）
  - [ ] 纵剖面图
  - [ ] 横剖面图
  - [ ] 尺寸标注
  - [ ] 舱室文字标注
- [ ] Task C-3：运行脚本生成DXF
- [ ] Task C-4：验证DXF文件可用
- [ ] 输出：`output/generate_dxf.py` ✓
- [ ] 输出：`output/cargo_tank_arrangement.dxf` ✓

---

## 阶段4：审校与修订（reviewer + writer）
- [ ] Task V-1：reviewer执行格式审校
- [ ] Task V-2：reviewer执行数据一致性检查
- [ ] Task V-3：reviewer执行内容完整性检查
- [ ] Task V-4：reviewer执行工程合理性检查
- [ ] Task V-5：writer按审校意见修改
- [ ] 输出：`output/thesis_final.md` ✓

---

## 最终交付物检查
- [ ] `output/thesis_final.md`（论文正文）
- [ ] `output/cargo_tank_arrangement.dxf`（货仓结构图CAD文件）
- [ ] `output/calculations.md`（计算书，可作附录）

---

## 给你的操作提示

在Claude Code里，每次启动新任务这样说：

**启动researcher：**
> "你是researcher，读取agents/researcher.md，开始执行Task R-1到R-6，结果写入output/regulations.md"

**启动engineer：**
> "你是engineer，读取agents/engineer.md和output/regulations.md，执行Task E-1到E-6，结果写入output/calculations.md"

**启动writer：**
> "你是writer，读取agents/writer.md、output/calculations.md、output/regulations.md，执行Task W-1到W-11，结果写入output/thesis.md"

**启动cad_engineer：**
> "你是cad_engineer，读取agents/cad_engineer.md和CLAUDE.md中的船舶参数，执行Task C-1到C-4"

**启动reviewer：**
> "你是reviewer，读取agents/reviewer.md和output/thesis.md，执行全部审校任务"
