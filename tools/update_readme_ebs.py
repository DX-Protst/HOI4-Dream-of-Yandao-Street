# -*- coding: utf-8 -*-
import sys
from pathlib import Path

path = Path("README_EBS.md")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = "### 5.4 全节点高质事件覆盖规范 (Every Political Focus Has an Event)"
if target not in text:
    print("[ERROR] target not found")
    sys.exit(1)

# Find the start and end of section 5.4 and 6 header
idx_start = text.find(target)
idx_end = text.find("```mermaid\nsequenceDiagram\n    participant C as 大院特权派")
if idx_end == -1:
    print("[ERROR] idx_end not found")
    sys.exit(1)

new_content = """### 5.4 全节点高质事件覆盖与 YDJ 级文学叙事规范 (YDJ-Tier Literary & Pagination Standards)
除工业线专注数值建设不设弹窗外，**所有政治路线、开局主线与战前通牒国策均实现 100% 专属高水准叙事事件覆盖**：
* **文学质感与 YDJ 全面对齐**：大幅加强文本厚度与场景临场感，融入水磨石走廊、红木门、紫砂保温杯、苯类油漆挥发浓雾、液氮超算机柜蜂鸣与试卷油墨香等极其细腻的微观细节与荒诞现实主义讽刺；
* **融入多地域特色方言**：
  * **京味大院与燕京官场切口**：西单官僚的“得嘞”、“门儿清”、“局气”、“大院规矩是老祖宗立下的”、“底儿掉”、“没褶儿了”、“外省叫驴”；
  * **山河四省老农做题家悲叹**：华北平原与冀鲁豫校长的“弄啥嘞”、“作孽啊”、“手冻得跟胡萝卜似的”、“庄稼地的娃”；
  * **川蜀蓉城方言尖锐对峙**：在兵临锦江合围盐道街（`ebs_focus_event.33`）时，老盐中广播高呼“北京来的督学懂个铲铲”、“骑在老盐中脑壳上搞大一统”、“问问九眼桥下头滔滔江水答不答应”；
* **全面引入 YDJ 式长篇翻页机制 (Pagination Form)**：对于文本量宏大、矛盾复杂的关键转折（开局专署成立 `ebs_event.1`、四大经典危机事件、交织危机链 1~5 全流程、四大政治路线终局大结局、中枢决裂 `ebs_focus_event.1`、合围盐道街 `ebs_focus_event.33` 与太和殿万世圣典 `ebs_focus_event.34`），全面采用 YDJ 专属的“第一页铺陈场景 ➜ `下一页 →` 按钮 ➜ 第二页迎来戏剧高潮与政策抉择”的翻页架构，杜绝弹窗文字溢出，带来小说级别的连贯阅读享受；
* **神圣红线约束**：东三省名校路线（路线 E：奉系入关、长沈哈铁血同盟、高炉夜读营等）全套代码与文案**严格保持原版不变**！

## 6. 中枢路线多阶段交织危机事件链 (Interwoven Crisis Event Chain)

中枢政治路线的决战**彻底摒弃单次弹窗与生硬标签**，深度复刻 TLB/YDJ 高质量多阶段政治叙事与翻页规范：
* **严控选项防重叠**：危机事件严格限制为 **每个事件翻页后恰好 2 个选项**，彻底消除原版弹窗选项挤压重叠的 UI 缺陷；
* **去除人名与阶段编号**：选项中绝不生硬出现领导人名（以行政、机构与政策动作替代），标题全面采用长篇沉浸式叙事标题（如《西单保密室的撬痕》、《绿漆操场上的刺鼻晨雾》）；
* **数理决算单一定局**：危机积累的变量最终在决算点动态结算，**只触发唯一的胜出事件（单选项确立统治）**，不可再手动逆转胜败；
* **TLB/YDJ 级超长篇双页叙事**：每篇事件扩充至 500~800 字双页，多段落构建官僚、校园与做题家的现实讽刺巨作。

"""

updated_text = text[:idx_start] + new_content + text[idx_end:]
with open(path, "w", encoding="utf-8") as f:
    f.write(updated_text)

print("[SUCCESS] README_EBS.md updated successfully!")
