"""
Generates dedicated unique focus icons for all remaining EBS focuses,
achieving a strict 1-to-1 mapping where every single focus in EBS_focus.txt
has its own unique icon asset!
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import numpy as np
from PIL import Image, ImageFilter

COMFY_API_URL = "http://127.0.0.1:8188"
COMFY_OUT_DIR = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8\ComfyUI\output"
GOAL_OUT_DIR = "gfx/interface/goals/EBS"
os.makedirs(GOAL_OUT_DIR, exist_ok=True)

REMAINING_TASKS = [
    {
        "id": "EBS_balance_bureaucratic_interests",
        "name": "GFX_focus_EBS_balance_bureaucratic_interests",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张摆满红酒杯的官僚宴会桌上，一把金色蛋糕刀正在将一个印有清华北大自招字样的大蛋糕切分分发给各派系，麦穗与账簿环绕，象征安抚各派既得利益，手绘讽刺国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_uncover_internal_corruption",
        "name": "GFX_focus_EBS_uncover_internal_corruption",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，阴暗的机密档案室中，一只戴着黑色手套的手翻开带有深红火漆印的绝密档案袋，里面滑出标有配餐回扣与自招买卖罪证的照片与金色放大镜，手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_central_inspectorate_permanent",
        "name": "GFX_focus_EBS_central_inspectorate_permanent",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一枚刻有深红五星与双铁剑的最高常驻督导巡按使铜质盾牌，悬挂在省教育厅大门上，旁边设立带铁锁的24小时检举信箱，威严手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_monopolize_special_pathways",
        "name": "GFX_focus_EBS_monopolize_special_pathways",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一扇刻满精密几何纹路的高大纯金旋转门，门上挂着沉重的黄铜密码大锁，一把镀金的强基专属钥匙插在锁孔中，外省考生被铁栅栏阻隔在门外，手绘特权国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_the_untouchable_nobility",
        "name": "GFX_focus_EBS_the_untouchable_nobility",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座由北京二环路地图与汉白玉石狮子环卫的紫禁城角楼，顶端插着金色400分一本锦旗，暴风雨与闪电无法撼动分毫，极其坚固威严手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_fiber_optic_exam_backbone",
        "name": "GFX_focus_EBS_fiber_optic_exam_backbone",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一捆从地下破土而出的巨型多芯发光光缆，金黄色与幽蓝色的激光脉冲沿着光纤向北方各省急速奔驰，穿透崇山峻岭，手绘科技国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_quantum_grading_datacenter",
        "name": "GFX_focus_EBS_quantum_grading_datacenter",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台发光的水冷量子拟合阅卷计算机核心，下方悬浮着数万份正在被激光矩阵瞬间扫描成绿色数字流的高考理综答卷，毫秒级批改，手绘科幻国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_predictive_drop_out_model",
        "name": "GFX_focus_EBS_predictive_drop_out_model",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台闪烁着琥珀色警报红光的神经网络分析仪，屏幕上正在对小学生握笔姿势与骨龄进行扫描，打印出带红色叉号的‘建议中职分流’命运判定单，手绘讽刺科技国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_algorithm_determines_destiny",
        "name": "GFX_focus_EBS_algorithm_determines_destiny",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一尊高耸的金属算法矩阵天平，一边是庞大的芯片算力云端，另一边是数百万考生的档案卡片，天平倾斜，金色数据链锁住命运之轮，手绘赛博国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_five_day_shock_inspection",
        "name": "GFX_focus_EBS_five_day_shock_inspection",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，凌晨破晓时分，一队亮着刺目探照灯的黑色督导巡视越野车队风驰电掣冲入校门，警报器尖叫，秒表倒计时在闪烁，无预警闪电战，手绘突击国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_evaluation_or_shutdown",
        "name": "GFX_focus_EBS_evaluation_or_shutdown",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张带有红头钢印与‘勒令立即停办整顿’字样的白色封条交叉贴在名校紧闭的大铁门上，门前站着两名抱臂冷视的督导宪兵，手绘铁血肃反国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_punitive_disciplinary_tribunal",
        "name": "GFX_focus_EBS_punitive_disciplinary_tribunal",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一把沉重的黄铜法官审判锤狠狠砸在一叠被判定‘抄写不工整’的假教案上，后方高悬深黑督导天平与惩戒戒尺，威严肃杀手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_total_inspection_state",
        "name": "GFX_focus_EBS_total_inspection_state",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座如同积木模型般绝对整齐划一、纤尘不染的空心校园大楼，每扇窗户反射着毫无生气的刺目绿光，地面是一面巨大的假评估示范锦旗，手绘荒诞极权国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_privatized_varsity_franchise",
        "name": "GFX_focus_EBS_privatized_varsity_franchise",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张印有中英双语、盖有火漆金印的贵族私立马术击剑专业特许证书，上面搁着一副高级击剑白手套与纯银马刺，手绘奢华贵族国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_exclusive_uniform_procurement",
        "name": "GFX_focus_EBS_exclusive_uniform_procurement",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一套挂着昂贵‘专营特许 2888元’塑料吊牌的化纤校服，下压着五本强制绑售的泛黄盗版教辅练习册与印钞机，讽刺贪腐手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_athletic_darwinism",
        "name": "GFX_focus_EBS_athletic_darwinism",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，暴雨中的红色塑胶跑道上，一个沉重的生锈铅球砸在终点线上，上方悬挂着巨大的黑色计时钟与盖着‘准考证作废’的红印章，象征残酷体能淘汰，手绘达尔文主义国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_banquet_diplomacy_network",
        "name": "GFX_focus_EBS_banquet_diplomacy_network",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，旋转的水晶宴会大圆桌上摆满高档飞天茅台酒瓶与鲍鱼海参大餐，几只红润油腻的手在碰杯，酒杯下方垫着各省自招指标转让草约，手绘宴饮贪腐国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_educational_slush_funds",
        "name": "GFX_focus_EBS_educational_slush_funds",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一个沉重的黑色密码公文箱在瑞士雪山银行前打开，里面塞满了整捆的美金现钞与加勒比海离岸教育信托债券，缠绕着金色锁链，手绘黑金洗钱国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_educational_plutocracy",
        "name": "GFX_focus_EBS_educational_plutocracy",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张由纯金打造的清华北大录取通知书被夹在一枚巨大的纯金钞票夹中，钞票夹上镶嵌着钻石与贪婪铜币眼，象征教育金权帝国，手绘奢靡财阀国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_dongbei_conspiracy_active",
        "name": "GFX_focus_EBS_dongbei_conspiracy_active",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张摊在沈阳大帅府旧式红木地图桌上的全国考卷分布图，上面压着一枚关东铁军怀表与一柄苏式刺刀，红笔狠狠圈出北京西单，手绘密谋觉醒国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_secret_alliance_of_three_provinces",
        "name": "GFX_focus_EBS_secret_alliance_of_three_provinces",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，四枚分别代表东北师大附中、哈三中、本溪高中、辽宁实验的金属校徽紧密镶嵌在一块钢铁战盾上，四只手紧扣在冰雪盟约羊皮纸上，手绘铁血同盟国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_placate_dongbei_normal",
        "name": "GFX_focus_EBS_placate_dongbei_normal",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一面迎风招展的东北师大附中红旗，旗帜下簇拥着戴着厚棉帽、胸前别着毛笔的青年教师与做题尖子生方阵，后方是长春春城的大烟囱，手绘革命动员国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_worker_student_syndicate_councils",
        "name": "GFX_focus_EBS_worker_student_syndicate_councils",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一柄锻造铁锤与一支金色蘸水钢笔在一枚巨大的工业齿轮中央紧密交叉，下方是一本展开的《工农做题纲领》，红星闪烁，苏式工团主义手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_dongbei_takes_over_moe",
        "name": "GFX_focus_EBS_dongbei_takes_over_moe",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，宏伟的北京教育部大楼门前，东北名校联合公社的赤红战旗高高插上楼顶门楼，门前卫兵换成了身穿苏式防寒大衣的东北做题家工团战士，手绘胜利占领国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_heavy_industry_exam_equality",
        "name": "GFX_focus_EBS_heavy_industry_exam_equality",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一条巨大的重工业钢铁流水线传送带，上面正在以万吨水压机的惊人压力整齐冲压印制出一模一样的全国统一高考大试卷，特权水分被压扁，手绘重工平权国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_absolute_meritocracy_republic",
        "name": "GFX_focus_EBS_absolute_meritocracy_republic",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座高耸入云的汉白玉平等纪念碑，碑顶是一本展开的纯金做题圣典与高悬的正义天平，背景是红日初升照亮整片冰原与钢铁厂，象征关外真才实学平等共和国，宏伟庄严手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_rig_informatics_syllabus",
        "name": "GFX_focus_EBS_rig_informatics_syllabus",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一本被拆开重新装订的全国信息学奥赛大纲，里面嵌入了一枚带有北京后门芯片的黑客电路板，金色二进制代码流正在改写测试用例，手绘黑客篡改国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_suppress_southern_olympiad",
        "name": "GFX_focus_EBS_suppress_southern_olympiad",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一副沉重的精钢手铐将一本厚厚的《南方奥林匹克数学竞赛自招秘籍》与竞赛金牌紧紧锁住，上方盖着‘非法地下竞赛 查封取缔’鲜红大印，手绘打击执法国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_lock_ivory_tower_top3",
        "name": "GFX_focus_EBS_lock_ivory_tower_top3",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，三尊高耸的象牙色古典大学校门汉白玉石柱，被一道布满尖刺的金色铁丝网死死包围，铁丝网上挂着‘仅限大院及直辖市配额’黄铜警示牌，手绘独占垄断国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_central_printing_industrialization",
        "name": "GFX_focus_EBS_central_printing_industrialization",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，幽深庞大的地下工业印钞车间，数十台重型胶印机正在疯狂吐出带有水印防伪线的红色考卷纸带，装甲运输箱在传送带上飞速移动，手绘重工业印刷国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_beijing_tianjin_railway_artery",
        "name": "GFX_focus_EBS_beijing_tianjin_railway_artery",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两条平行发光的钢铁铁路大动脉贯穿华北平原，一列挂有督导专运红色信号灯的重型蒸汽机车在暴风雪中呼啸飞驰，车厢满载押题机密箱，手绘铁路动脉国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_northeast_rust_belt_integration",
        "name": "GFX_focus_EBS_northeast_rust_belt_integration",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台巨型的鞍钢露天起重机与高炉吊钩，正在将一座巨大的军用发电机与教育局机房方舱吊装合体，钢铁支架遍布黑土地，手绘重工整合国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_tianjin_bohai_chemical_refinery",
        "name": "GFX_focus_EBS_tianjin_bohai_chemical_refinery",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，沿海渤海湾畔庞大的化工管道与蒸馏塔群，两座巨大的反应釜正在联产提炼出军用炸药原料与考场防作弊显影墨水试剂，白烟滚滚，手绘化学工业国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_rehe_chahar_mineral_prospecting",
        "name": "GFX_focus_EBS_rehe_chahar_mineral_prospecting",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，荒凉险峻的塞北长城烽火台下，两名身披棉军大衣的地质勘探队员正在架设钻探三角架，从冻土中取出闪烁着黑色金属光泽的钨铁矿石标本，手绘地质采矿国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_anshan_heavy_steel_foundry",
        "name": "GFX_focus_EBS_anshan_heavy_steel_foundry",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，鞍钢巨大的钢水浇铸车间，一整钢包白炽滚烫的钢水倾泻而下，浇铸成厚重的装甲钢板与重型机器底座，火红热浪与火花飞溅，壮丽手绘钢铁重工国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_harbin_locomotive_heavy_chassis",
        "name": "GFX_focus_EBS_harbin_locomotive_heavy_chassis",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，哈尔滨车辆段巨大的装配车间内，一条重型装甲列车与履带底盘被悬挂在龙门吊下，工人们正在用风炮紧固巨大的装甲螺栓，手绘军工机车国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_dalian_naval_dockyard_expansion",
        "name": "GFX_focus_EBS_dalian_naval_dockyard_expansion",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，大连船坞干坞中，一艘披挂着厚重钢甲、带有装甲炮塔的重型巡视押题驱逐舰正在建造，龙门吊与焊枪弧光在蔚蓝波涛前闪烁，手绘海军军工国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_changchun_precision_instrument_works",
        "name": "GFX_focus_EBS_changchun_precision_instrument_works",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，无尘实验室里，一台精密的军用蔡司光学显微镜与高倍防空测距仪，镜片折射出彩虹般的镀膜光芒，旁边放着红外夜视考场抓拍镜头图纸，手绘精密光学科技国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_wartime_industrial_stockpile",
        "name": "GFX_focus_EBS_wartime_industrial_stockpile",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座开凿在花岗岩山体深处的庞大地下掩体仓库，货架上码放着整齐划一的军用压缩干粮箱、弹药箱与绝密考卷铅封铁盒，重型防弹防核大门半开，手绘战备储备国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_national_defense_technical_polytechnic",
        "name": "GFX_focus_EBS_national_defense_technical_polytechnic",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，国防工业大学标志性的齿轮与导弹校徽前，几位身穿白大褂与军装的教授正在风洞测试模型前推演风阻，黑板上写满空气动力学微积分公式，手绘国防科研国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_the_invincible_exam_industrial_complex",
        "name": "GFX_focus_EBS_the_invincible_exam_industrial_complex",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座庞大得宛如移动堡垒的现代化综合工业城，铁路直接贯穿高炉与印刷厂，城墙上并列着重炮与发射天线，两侧环绕金色齿轮麦穗，手绘终极工业国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_dispatch_final_syllabus_ultimatum",
        "name": "GFX_focus_EBS_dispatch_final_syllabus_ultimatum",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一封插着带血匕首的黑底金字《全国考纲统一最后通牒》公函，公函下压着带刺铁丝网与滴血钢笔，象征密发全国考纲统一通牒，冷酷威慑手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_curb_southern_resistance",
        "name": "GFX_focus_EBS_curb_southern_resistance",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一柄漆黑的督导断头铡刀，将几捆印有‘苏南独立卷’、‘浙江自命题’的南方试卷齐齐切断，残页在狂风中飘散，下方是铁铸的‘考纲归一’印模，手绘铁腕镇压国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_coopt_provincial_collaborators",
        "name": "GFX_focus_EBS_coopt_provincial_collaborators",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一只盖满红头章的公文袋里滑出几张‘北京高校地方扩招名额特许状’与一堆金条，递到一位身穿长袍的地方驻京学阀手中，两人露出会心奸笑，手绘统战收买国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_pacify_shanhe_coalition",
        "name": "GFX_focus_EBS_pacify_shanhe_coalition",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，展开的山河四省地图上，一把巨大的督导长剑将象征河北、河南、山东、山西的四个做题军团旗帜全部斩断，太行山脉上空插上督导总署大旗，手绘平定内战国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_subjugate_huazhong_hbe",
        "name": "GFX_focus_EBS_subjugate_huazhong_hbe",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，宏伟的黄鹤楼与黄冈中学大门被铁锁链死死锁住，校门前高高竖起一面巨大的白旗，象征称雄全国数十年的黄冈密卷体系向中央考纲俯首称臣，手绘征服降伏国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_strike_east_and_south",
        "name": "GFX_focus_EBS_strike_east_and_south",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一枚巨大的黑色钢铁重炮炮弹破空呼啸，将象征华东六省一市与华南奥赛联军的锦旗阵地炸成漫天碎片，金牌与奖状四散崩落，手绘横扫千军国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_final_siege_of_yandao",
        "name": "GFX_focus_EBS_final_siege_of_yandao",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张成都府南河作战地图，多支粗壮的黑色进攻箭头从四面八方向盐道街中学校徽铁桶般合围刺入，校门火光熊熊，象征合围盐道街学区堡垒，决战手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "id": "EBS_nationwide_educational_dominion",
        "name": "GFX_focus_EBS_nationwide_educational_dominion",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一本散发着耀眼万丈光芒的金色巨著《中央统考万世圣典》，高悬于全中国版图上空，普照四海，象征颁发中央统考圣典建立全国大一统霸权，神圣恢弘手绘国策图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    }
]

def build_workflow_payload(prompt_text, seed=None):
    if seed is None:
        seed = int(time.time() * 1000) % 4294967295
    return {
        "28": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "moss_image_sft_nvfp4.safetensors",
                "weight_dtype": "default"
            }
        },
        "41": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["28", 0],
                "lora_name": "KOOK-MOSS-SFT-观澜.safetensors",
                "strength_model": 1.0
            }
        },
        "38": {
            "class_type": "SkipLayerGuidanceDiTSimple",
            "inputs": {
                "model": ["41", 0],
                "double_layers": "",
                "single_layers": "22",
                "start_percent": 0.0,
                "end_percent": 0.5
            }
        },
        "30": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3.5_9b_int8_convrot.safetensors",
                "type": "moss_image",
                "device": "default"
            }
        },
        "32": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "flux2-vae.safetensors"
            }
        },
        "71": {
            "class_type": "PrimitiveStringMultiline",
            "inputs": {
                "value": prompt_text
            }
        },
        "80": {
            "class_type": "QwenMossExpander",
            "inputs": {
                "user_prompt": ["71", 0],
                "preset": "MOSS核心版 (快速/推荐 8k上下文)",
                "model_name": "Qwen3.8-9B-Distill-uncensored-heretic.i1-Q6_K.gguf",
                "max_tokens": 1024,
                "temperature": 0.65,
                "top_p": 0.9,
                "seed": seed,
                "auto_unload_vram": True,
                "enable_thinking": False
            }
        },
        "79": {
            "class_type": "PreviewTextNode",
            "inputs": {
                "text": ["80", 0]
            }
        },
        "29": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["30", 0],
                "text": ["79", 0]
            }
        },
        "36": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["30", 0],
                "text": "worst quality, bad anatomy, watermark, text, signature, jpeg artifact, blurry, realistic photo background, complex environment behind object, shadows on green screen, non-green background elements"
            }
        },
        "19": {
            "class_type": "ResolutionSelector",
            "inputs": {
                "aspect_ratio": "1:1 (Square)",
                "megapixels": 1.0,
                "multiple": 8
            }
        },
        "35": {
            "class_type": "EmptyFlux2LatentImage",
            "inputs": {
                "width": ["19", 0],
                "height": ["19", 1],
                "batch_size": 1
            }
        },
        "31": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["38", 0],
                "positive": ["29", 0],
                "negative": ["36", 0],
                "latent_image": ["35", 0],
                "seed": seed,
                "steps": 20,
                "cfg": 3.0,
                "sampler_name": "er_sde",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        "37": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["31", 0],
                "vae": ["32", 0]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["37", 0],
                "filename_prefix": "hoi4_rem_raw"
            }
        }
    }

def cutout_green_screen(raw_path):
    img = Image.open(raw_path).convert('RGB')
    rgb = np.array(img, dtype=np.float32)
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    max_rb = np.maximum(r, b)
    green_diff = g - max_rb
    lower_th = 15.0
    upper_th = 60.0
    alpha = np.clip(1.0 - (green_diff - lower_th) / (upper_th - lower_th), 0.0, 1.0)
    is_bright_green = (g > 100) & (g > r * 1.15) & (g > b * 1.15)
    alpha = np.where(is_bright_green, alpha, 1.0)
    despill_mask = g > max_rb
    g_despilled = np.where(despill_mask, (r + b) * 0.5, g)
    rgba = np.zeros((rgb.shape[0], rgb.shape[1], 4), dtype=np.uint8)
    rgba[:, :, 0] = np.clip(r, 0, 255).astype(np.uint8)
    rgba[:, :, 1] = np.clip(g_despilled, 0, 255).astype(np.uint8)
    rgba[:, :, 2] = np.clip(b, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    cutout = Image.fromarray(rgba, mode='RGBA')
    alpha_blurred = cutout.split()[3].filter(ImageFilter.GaussianBlur(radius=0.7))
    cutout.putalpha(alpha_blurred)
    return cutout

def process_focus_icon(cutout, outdir, name):
    bbox = cutout.getbbox()
    if bbox:
        cropped = cutout.crop(bbox)
        bw, bh = cropped.width, cropped.height
        scale = min(100.0 / bw, 100.0 / bh)
        new_w = max(1, int(round(bw * scale)))
        new_h = max(1, int(round(bh * scale)))
        icon = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        icon = cutout.resize((100, 100), Image.Resampling.LANCZOS)
    out_file = os.path.join(outdir, f"{name}.png")
    icon.save(out_file)
    print(f"[Done] Focus Icon saved: {out_file} (size: {icon.size})")
    return out_file

def generate_one(task):
    name = task["name"]
    target_path = os.path.join(GOAL_OUT_DIR, f"{name}.png")
    if os.path.exists(target_path):
        print(f"[*] Skipping {name} - already exists.")
        return target_path

    payload = build_workflow_payload(task["prompt"])
    post_data = json.dumps({"prompt": payload}).encode('utf-8')
    req = urllib.request.Request(f"{COMFY_API_URL}/prompt", data=post_data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    prompt_id = json.loads(resp.read().decode('utf-8'))['prompt_id']

    start_t = time.time()
    while True:
        time.sleep(2)
        elapsed = int(time.time() - start_t)
        h_req = urllib.request.urlopen(f"{COMFY_API_URL}/history/{prompt_id}")
        h_data = json.loads(h_req.read().decode('utf-8'))
        if prompt_id in h_data:
            item = h_data[prompt_id]
            images = item.get('outputs', {}).get('9', {}).get('images', [])
            if not images:
                raise RuntimeError("No image output")
            raw_path = os.path.join(COMFY_OUT_DIR, images[0].get('subfolder', ''), images[0]['filename'])
            print(f"[*] ComfyUI rendered in {elapsed}s: {raw_path}")
            cutout = cutout_green_screen(raw_path)
            return process_focus_icon(cutout, GOAL_OUT_DIR, name)
        if elapsed > 180:
            raise TimeoutError(f"Generation timed out for {name}")

def update_all_82_focuses():
    print("\n[*] Updating all 82 focuses in common/national_focus/EBS_focus.txt and interface/EBS_goals.gfx...")
    import re
    
    with open("common/national_focus/EBS_focus.txt", "r", encoding="utf-8") as f:
        content = f.read()

    focus_ids = [fid for fid in re.findall(r'id\s*=\s*(EBS_[a-zA-Z0-9_]+)', content) if fid != 'EBS_focus_tree']
    print(f"Total focus nodes: {len(focus_ids)}")

    # Update each focus: id = EBS_xyz -> icon = GFX_focus_EBS_xyz
    for fid in focus_ids:
        new_icon = f"GFX_focus_{fid}"
        pattern = re.compile(rf'(id\s*=\s*{fid}\b(?:(?!focus\s*=\s*\{{)[\s\S])*?icon\s*=\s*)([a-zA-Z0-9_]+)')
        if pattern.search(content):
            content = pattern.sub(rf'\g<1>{new_icon}', content, count=1)
        else:
            print(f"[!] Warning: could not match {fid}")

    with open("common/national_focus/EBS_focus.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Updated common/national_focus/EBS_focus.txt to 1:1 dedicated icon IDs!")

    # Now write interface/EBS_goals.gfx containing all 82 sprite definitions + shine
    goal_sprites = []
    for fid in focus_ids:
        icon_name = f"GFX_focus_{fid}"
        # File path in gfx/interface/goals/EBS/
        tex_path = f"gfx/interface/goals/EBS/{icon_name}.png"
        goal_sprites.append(f"""\tSpriteType = {{
\t\tname = "{icon_name}"
\t\ttexturefile = "{tex_path}"
\t}}
\tSpriteType = {{
\t\tname = "{icon_name}_shine"
\t\ttexturefile = "{tex_path}"
\t\teffectFile = "gfx/FX/buttonstate.lua"
\t\tanimation = {{
\t\t\tanimationmaskfile = "{tex_path}"
\t\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.dds"
\t\t\tanimationrotation = -90.0
\t\t\tanimationlooping = no
\t\t\tanimationtime = 0.75
\t\t\tanimationdelay = 0
\t\t\tanimationblendmode = "add"
\t\t\tanimationtype = "scrolling"
\t\t\tanimationrotationoffset = {{ x = 0.0 y = 0.0 }}
\t\t\tanimationtexturescale = {{ x = 1.0 y = 1.0 }}
\t\t}}
\t\tlegacy_lazy_load = no
\t}}""")

    with open("interface/EBS_goals.gfx", "w", encoding="utf-8") as f:
        f.write("spriteTypes = {\n" + "\n\n".join(goal_sprites) + "\n}\n")
    print(f"[OK] Written interface/EBS_goals.gfx with all {len(focus_ids)} 1:1 sprite + shine definitions!")

def kill_comfy():
    print("\n[*] Mandatory VRAM cleanup: Terminating ComfyUI server...")
    subprocess.run([
        "C:\\Program Files\\Comfyui-WF-2026.8.8\\Comfyui-WF-2026.8.8\\python\\python.exe",
        "tools/generate_portrait.py",
        "--kill"
    ])
    print("[OK] GPU VRAM 100% released!")

def main():
    total = len(REMAINING_TASKS)
    print(f"==================================================")
    print(f"[*] EBS Remaining Focus Icons Generation: {total} Tasks")
    print(f"==================================================")

    for i, t in enumerate(REMAINING_TASKS, 1):
        print(f"\n[{i}/{total}] Generating: {t['name']}...")
        try:
            generate_one(t)
        except Exception as e:
            print(f"[!] Error on {t['name']}: {e}")

    # Update code to 100% 1:1 mapping
    update_all_82_focuses()

    # Kill ComfyUI to completely free VRAM
    kill_comfy()

if __name__ == '__main__':
    main()
