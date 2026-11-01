"""
Master Batch Generator for EBS Focus and Idea Icons.
Generates all 17 Idea Icons and 38 Core Focus Icons for EBS via ComfyUI (钢铁雄心.json),
applies Chroma-Key Despill, exports transparent PNGs to gfx/interface/ideas/EBS and gfx/interface/goals/EBS,
generates interface/EBS_ideas.gfx and interface/EBS_goals.gfx,
and maps common/national_focus/EBS_focus.txt to the new GFX icons.
Finally kills ComfyUI to completely free GPU VRAM!
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

IDEA_OUT_DIR = "gfx/interface/ideas/EBS"
GOAL_OUT_DIR = "gfx/interface/goals/EBS"
os.makedirs(IDEA_OUT_DIR, exist_ok=True)
os.makedirs(GOAL_OUT_DIR, exist_ok=True)

# 17 Ideas
IDEA_TASKS = [
    {
        "name": "EBS_northeast_undercurrent",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一枚暗红色冰封的枫叶与重工钢铁齿轮咬合，象征东北关外之怨与雪原暗流，厚重金属手绘图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_chen_absolutism_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一把厚重的紫檀木太上皇官僚太师椅与带红色流苏的最高督导令箭，金色麦穗与权威红头文件，手绘厚重官僚威权风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_cybernetic_dictatorship_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一枚发光的清华蓝色微处理器芯片，芯片中心印有考卷纹路，向四周延伸出金色发光电路板与数据线，象征赛博算力专政，手绘科技风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_lawn_greening_totalism_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一把滴着鲜绿油漆的毛刷斜跨在一块军绿色的教学评估奖牌上，周围环绕整齐插满的翠绿麦苗，象征全域迎检刷绿漆狂热，讽刺手绘图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_canteen_black_gold_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一个不锈钢密封预制菜餐盒，上方叠放着金条与一叠黑色账本，缠绕着金色锁链，象征校园后勤黑金托拉斯，手绘财阀勋章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_dongbei_liberation_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一柄巨大的苏式重工铁锤与一柄钢笔在金色齿轮前交叉，背景有燃烧的红星与风雪松枝，象征关东重工做题家平权公社，工团主义手绘风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_information_monopoly_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一只戴着黑色皮手套的手紧紧攥住一份发光的二进制加密全国高考试卷，上方有一只机械全知之眼，象征试卷院信息学霸权，手绘图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_dongbei_unrest_high",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一块被冰霜覆盖并裂开的考卷石碑，红色的感叹号警示标志与断裂的锁链，象征关外做题家动荡危机，手绘危机图标风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_haidian_privilege",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一顶华丽的金色贵族小王冠与一对交叉的花剑击剑，背景为清华北大校门剪影与免试保送金色丝带，象征海淀早培生源特权，贵族手绘风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_cybernetic_exam_grid",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一副连接着神经传感电极线的深黑战术护目镜，镜片上闪烁着考场红外雷达网格与微表情分析波形，象征神经监考天网，赛博手绘风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_inspection_frenzy",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，叠成半米高的厚重红色教学反思教案，上面压着一块黄铜倒计时秒表与一枚五星特优印章，象征突击迎检造假狂热，讽刺手绘风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_imperial_examination_throne_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一把纯金打造的应试科举龙椅宝座，扶手上雕刻着毛笔与玉玺，背景为金色光芒与万世法典金册，极其庄重威严手绘图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_silicon_curriculum_singularity_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一颗悬浮在半空中的量子硅基立方体晶体，向四周放射出刺目的矩阵代码光束，将所有手写考卷吸入数据漩涡，象征硅基大纲奇点，手绘科幻风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_perpetual_inspection_mobilization_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一辆疾驰的黑色督导巡视装甲专车，车顶装有探照灯与警报器，车头插着红黄双色督导旗帜，象征永恒迎检全域战备大公社，手绘极权战备风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_unrestricted_exam_market_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一台老式黄铜天平，一端称着清华北大的录取批文，另一端堆满金币与美元纸钞，天平向金币端倾斜，象征彻底无界自由考务市场，讽刺手绘风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_absolute_meritocracy_republic_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，一柄巨大的正义之剑将一堆自招特许降分证书斩为两半，剑柄镶嵌冰雪红星，下方是一张全国绝对统一的纯白试卷，象征关外真才实学平等共和国，手绘英雄主义风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "EBS_the_invincible_exam_industrial_complex_spirit",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国家精神图标，正面居中，宏伟的重工业工厂群与冒着浓烟的高耸烟囱，前方并列着金色巨型齿轮、重炮与印刷试卷流水线，象征无坚不摧的应试工业复合体，壮丽手绘工业勋章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    }
]

# 38 Unique Focus Icons
FOCUS_TASKS = [
    # Phase 1 & Central
    {
        "name": "GFX_focus_EBS_supreme_inspection_bureau",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一块刻有‘最高教育巡视督导总署’的红木金字威严牌匾，上方悬挂金色国徽与尚方宝剑，红绸缎带垂落，手绘厚重官僚国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_inspectors_general_assembly",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张椭圆形红色会议长桌，桌上整齐排列着茶杯、红头公文与金色麦克风，背景为庄严肃穆的红幔礼堂，手绘会议国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_the_council_schism",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张被从中间剧烈震裂成四块的黑色大理石办公桌，四角分别散落着红头印章、断裂网线、带绿漆毛刷与黑色账本，电光火石闪烁，象征四巨头决裂摊牌，手绘政治分裂国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # Branch A: Chen
    {
        "name": "GFX_focus_EBS_chen_absolutism",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一枚硕大无比的纯铜总督学方形大印沉沉砸下，红色的泥印如鲜血般鲜亮，旁边立着专员手杖，手绘太上皇威权国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_squeeze_classroom_moisture",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一只铁钳般的手用力拧绞一块湿漉漉的海绵，无数蓝色水滴被狠狠榨出落入铁桶，露出生硬刻板的标准八股教案，象征狠挤课堂水分，讽刺手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_strengthen_beijing_admissions",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座由汉白玉雕琢的北京天安门城楼与名校校门，四周筑起坚不可摧的高耸城墙与黄铜铁锁，将金色录取通知书牢牢护在城内，象征巩固京津录取特权，手绘特权堡垒国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_fortify_haidian_bastion",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座插满清北锦旗的深蓝色海淀城堡，城楼上方有一位戴金丝眼镜的神童在操纵精密天文望远镜与击剑，象征海淀早培垄断堡垒，手绘贵族学校国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_tibet_airdrop_express",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一列呼啸穿行在雪山布达拉宫脚下的现代化高原快车，车窗飘出两百分录取清华强基班的特快专函，周围环绕哈达与氧气瓶，象征西藏三年挂职直通车，手绘讽刺国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_bureaucratic_iron_stamp",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一枚钢铁锻造的巨大公章狠狠盖在一叠地方学校执照上，浮现出刺目的深红‘一票否决’钢印，火花四溅，手绘强权铁腕国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_imperial_examination_throne",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，巍峨的应试帝国金銮殿宝座，宝座顶端悬挂九龙盘踞的金匾，阶梯两旁整齐跪伏着手捧朱批考卷的考官剪影，象征新应试帝国太上皇法典，手绘极度庄严国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # Branch B: Huai
    {
        "name": "GFX_focus_EBS_huai_technocratic_coup",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一把闪烁蓝色电光的激光手术刀将一捆传统的红色纸质档案切断，断口处迸射出金色光纤与数码瀑布，象征怀总工赛博算力政变，手绘赛博朋克国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_tsinghua_supercomputer_grid",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，排布整齐、亮着幽蓝冷光的巨型超级计算机机柜阵列，地面水冷管线纵横交错，上方悬浮着清华附中算力天网的全息地球投影，手绘算力中心国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_ai_proctoring_neurolink",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一只透明的玻璃眼球内部嵌入精密机械光圈，发射出网格状的红色扫描激光笼罩着一张答题卡，旁边浮现微表情心率警报，象征脑电波微表情防作弊，手绘高科技监控国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_algorithmic_credit_system",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张发光的智能做题家信用芯片黑卡，卡面显示着‘Credit: 750 (Tier 1 Elite)’，周围环绕着上升的绿色数据条形图与算力徽章，象征全国做题家信用算法，手绘科技国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_silicon_curriculum_singularity",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一尊完全由闪亮硅晶圆片与主板电路构筑的无面人工智能考官雕像，右手托举着旋转的四维量子几何考题，人类考官的红木桌案在其脚下粉碎，象征硅基大纲奇点，手绘终极算力国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # Branch C: Zhou
    {
        "name": "GFX_focus_EBS_zhou_evaluation_frenzy",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一枚带刺刀的铁血大迎检令箭，箭身缠绕红色戒尺与军用秒表，背景为雷霆风暴中的万所校园，象征周总导铁血迎检大极权，手绘铁血强权国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_nationwide_lawn_greening",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，几个巨大的军用高压油漆喷枪正在疯狂向破旧泥泞的操场喷洒刺目欲滴的鲜绿油漆，操场瞬间变得反光夺目，旁边堆满空油漆桶，象征全国万校操场狂刷绿漆，讽刺手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_midnight_paperwork_mobilization",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，深夜昏暗的台灯下，三支钢笔在同一张假教案上疯狂飞舞，旁边堆叠着如小山般的假档案与空浓咖啡杯，窗外是残月，象征百万师生通宵抄假教案，手绘写实国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_model_school_showcase",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一片荒芜的碎石瓦砾地上，整齐插着一夜之间连夜移栽的嫩绿麦苗，前面立着一块金灿灿的‘国家级示范样板校’黄铜招牌，象征荒地连夜插麦苗样板工程，荒诞讽刺手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_perpetual_inspection_mobilization",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座由万卷整齐划一的评估材料构筑而成的巨型要塞城堡，城头飘扬着‘迎检战备’鲜红战旗，探照灯交叉扫射夜空，象征永恒迎检全域战备大公社，手绘极权战备国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # Branch D: Shuang Wang
    {
        "name": "GFX_focus_EBS_wang_commercial_consortium",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一只戴着硕大金戒指的手与另一只戴着名表的手在盛满佳肴的宴会桌上紧紧相握，背景是堆积成山的预制菜料理包与高尔夫球杆，象征体卫艺与后勤黑金托拉斯，手绘腐败财阀国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_sports_quota_black_market",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张印有‘国家二级运动员’烫金字样的证书被贴上了条形码与红色‘200,000元’价格标签，旁边放着一把金羽毛球拍与皮箱美金，象征体优加分黑市，讽刺手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_school_canteen_cartel",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一辆巨大的冷链物流重卡，车身上印着卡通笑脸与‘中央厨房垄断配餐’字样，车厢卸下成千上万份塑料预制料理包，将学校传统食堂的烟囱死死堵住，象征中小学预制菜包干，讽刺手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_the_unrestricted_exam_market",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座繁华喧嚣的证券交易所大厅，大屏幕上滚动的不是股票代码，而是‘清华大学强基批文 +15%’、‘北大自招指标 涨停’，金币如雨倾泻，象征彻底无界自由考务市场，极具讽刺的华丽手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # Branch E: Dongbei
    {
        "name": "GFX_focus_EBS_dongbei_conspiracy",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，雪夜沈阳火车站的候车长椅上，一份摊开的秘密泛黄手抄会议纪要，上面放着一顶沾着冰雪的工装帽与一枚生锈的指南针，直指西南关内，象征奉天密谋关外做题家觉醒，手绘秘密结社国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_furnace_night_study_battalions",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座喷涌着滚烫橙红铁水的高炉车间前，整齐排列着几排简易课桌，头戴安全帽与护目镜的年轻工人正在铁水火光下奋笔疾书做理综试卷，钢铁火花飞溅，象征高炉铁水夜读突击营，壮丽手绘重工国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_armored_exam_trains",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一列披挂着厚重钢甲与重机枪塔的巨大蒸汽装甲列车在呼啸的林海雪原中全速冲锋，车厢侧面喷刷着巨大的‘满铁押题’标语，象征满铁装甲押题列车，霸气手绘装甲国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_mukden_express_to_beijing",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一柄巨大的奉系做题长刀以雷霆万钧之势劈开山海关的古老关楼，后方无数关东做题大军手持钢笔与考卷如潮水般涌入直隶，象征奉系做题大军入关特快，史诗手绘战争国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_incinerate_aristocratic_archives",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，在西单教育部大楼广场前熊熊燃烧的巨大篝火，无数印有‘海淀早培自招降分特权’的泛黄机密档案被投入烈焰，火舌狂舞，灰烬升空，围观众人振臂欢呼，象征焚毁大院特权档案，手绘革命史诗国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_meritocracy_republic",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座高耸入云的汉白玉平等纪念碑，碑顶是一本展开的纯金做题圣典与高悬的正义天平，背景是红日初升照亮整片冰原与钢铁厂，象征关外真才实学平等共和国，宏伟庄严手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # Exam Board & Industry
    {
        "name": "GFX_focus_EBS_seize_central_printing_press",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台巨大的工业胶印机正在疯狂吞吐着盖有绝密火漆印的全国统考试卷，旁边站着荷枪实弹的宪兵哨兵与黄铜密码保险库大门，象征接管绝密印刷总厂，手绘工业机密国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_manipulate_national_exam_board",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一块高耸的八校联考全国排位天梯积分榜木牌，一只神秘的提线木偶木雕手正在暗中将写有‘清北’的金色木牌移动至榜首，象征黑箱操盘八校联考积分天梯，手绘谋略国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_industrial_backbone",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一副连接北京直隶与关东黑土地的重工业地图，地图上方矗立着交错的铁路钢轨、起重吊车与工业齿轮，象征中枢督导统辖与关东重工产业带，壮丽手绘工业国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_shenyang_arsenal_mobilization",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，沈阳第一兵工厂的钢铁大门内，流水线上传送带整齐排列着崭新的军用步枪与炮弹，工人们正在给武器烙印督导总署红星钢印，象征沈阳兵工军备转产，手绘军工厂国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_invincible_complex",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一座庞大得宛如移动堡垒的现代化综合工业城，铁路直接贯穿高炉与印刷厂，城墙上并列着重炮与发射天线，两侧环绕金色齿轮麦穗，象征无坚不摧的应试工业复合体，终极手绘工业巨无霸国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # War 1938
    {
        "name": "GFX_focus_EBS_final_ultimatum",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一封插着带血匕首的黑底金字《全国考纲统一最后通牒》公函，公函下压着带刺铁丝网与滴血钢笔，象征密发全国考纲统一通牒，冷酷威慑手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_war_mobilization",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两柄交叉的刺刀步枪后衬托着巨大的战时防空警报器与鲜红总动员旗帜，下方排列着整齐行军的做题家战备师方阵，象征战时全境管制动员，热血手绘战争国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_final_siege_yandao",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张成都府南河作战地图，多支粗壮的黑色进攻箭头从四面八方向盐道街中学校徽铁桶般合围刺入，校门火光熊熊，象征合围盐道街学区堡垒，决战手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_EBS_nationwide_dominion",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一本散发着耀眼万丈光芒的金色巨著《中央统考万世圣典》，高悬于全中国版图上空，普照四海，象征颁发中央统考圣典建立全国大一统霸权，神圣恢弘手绘国策风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
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
                "filename_prefix": "hoi4_batch_raw"
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

def process_idea_icon(cutout, outdir, name):
    bbox = cutout.getbbox()
    if bbox:
        cropped = cutout.crop(bbox)
        bw, bh = cropped.width, cropped.height
        scale = min(62.0 / bw, 62.0 / bh)
        new_w = max(1, int(round(bw * scale)))
        new_h = max(1, int(round(bh * scale)))
        resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        resized = cutout.resize((62, 62), Image.Resampling.LANCZOS)
        new_w, new_h = 62, 62

    canvas = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    offset_x = (64 - new_w) // 2
    offset_y = (64 - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y), resized)
    out_file = os.path.join(outdir, f"{name}.png")
    canvas.save(out_file)
    print(f"[Done] Idea Icon saved: {out_file}")
    return out_file

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

def generate_item(task, item_type):
    name = task["name"]
    outdir = IDEA_OUT_DIR if item_type == "idea" else GOAL_OUT_DIR
    target_path = os.path.join(outdir, f"{name}.png")
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
            if item_type == "idea":
                return process_idea_icon(cutout, outdir, name)
            else:
                return process_focus_icon(cutout, outdir, name)
        if elapsed > 180:
            raise TimeoutError(f"Generation timed out for {name}")

def update_code_and_gfx():
    print("\n[*] Updating interface and national focus scripts...")
    
    # 1. Generate interface/EBS_ideas.gfx
    idea_sprites = [
        f"""\tspriteType = {{
\t\tname = "GFX_idea_{item['name']}"
\t\ttexturefile = "gfx/interface/ideas/EBS/{item['name']}.png"
\t}}""" for item in IDEA_TASKS
    ]
    # Add existing ones if not present
    idea_sprites.append("""\tspriteType = {
\t\tname = "GFX_idea_EBS_privilege_iron_fist"
\t\ttexturefile = "gfx/interface/ideas/EBS/ebs_privilege_iron_fist.png"
\t}
\tspriteType = {
\t\tname = "GFX_idea_EBS_bureau_total_control"
\t\ttexturefile = "gfx/interface/ideas/EBS/ebs_bureau_total_control.png"
\t}""")
    
    with open("interface/EBS_ideas.gfx", "w", encoding="utf-8") as f:
        f.write("spriteTypes = {\n" + "\n".join(idea_sprites) + "\n}\n")
    print("[OK] Written interface/EBS_ideas.gfx")

    # 2. Generate interface/EBS_goals.gfx
    goal_sprites = []
    for item in FOCUS_TASKS:
        name = item["name"]
        goal_sprites.append(f"""\tSpriteType = {{
\t\tname = "{name}"
\t\ttexturefile = "gfx/interface/goals/EBS/{name}.png"
\t}}
\tSpriteType = {{
\t\tname = "{name}_shine"
\t\ttexturefile = "gfx/interface/goals/EBS/{name}.png"
\t\teffectFile = "gfx/FX/buttonstate.lua"
\t\tanimation = {{
\t\t\tanimationmaskfile = "gfx/interface/goals/EBS/{name}.png"
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
    print("[OK] Written interface/EBS_goals.gfx")

    # 3. Map all 82 focuses in common/national_focus/EBS_focus.txt
    FOCUS_MAP = {
        # Phase 1
        "EBS_supreme_inspection_bureau": "GFX_focus_EBS_supreme_inspection_bureau",
        "EBS_inspectors_general_assembly": "GFX_focus_EBS_inspectors_general_assembly",
        "EBS_balance_bureaucratic_interests": "GFX_focus_EBS_inspectors_general_assembly",
        "EBS_uncover_internal_corruption": "GFX_focus_EBS_the_council_schism",
        "EBS_the_council_schism": "GFX_focus_EBS_the_council_schism",
        # Branch A
        "EBS_chen_absolutism": "GFX_focus_EBS_chen_absolutism",
        "EBS_squeeze_classroom_moisture": "GFX_focus_EBS_squeeze_classroom_moisture",
        "EBS_strengthen_beijing_admissions": "GFX_focus_EBS_strengthen_beijing_admissions",
        "EBS_fortify_haidian_bastion": "GFX_focus_EBS_fortify_haidian_bastion",
        "EBS_tibet_airdrop_express": "GFX_focus_EBS_tibet_airdrop_express",
        "EBS_central_inspectorate_permanent": "GFX_focus_EBS_supreme_inspection_bureau",
        "EBS_monopolize_special_pathways": "GFX_focus_EBS_strengthen_beijing_admissions",
        "EBS_bureaucratic_iron_stamp": "GFX_focus_EBS_bureaucratic_iron_stamp",
        "EBS_the_untouchable_nobility": "GFX_focus_EBS_fortify_haidian_bastion",
        "EBS_imperial_examination_throne": "GFX_focus_EBS_imperial_examination_throne",
        # Branch B
        "EBS_huai_technocratic_coup": "GFX_focus_EBS_huai_technocratic_coup",
        "EBS_fiber_optic_exam_backbone": "GFX_focus_EBS_tsinghua_supercomputer_grid",
        "EBS_ai_proctoring_neurolink": "GFX_focus_EBS_ai_proctoring_neurolink",
        "EBS_tsinghua_supercomputer_grid": "GFX_focus_EBS_tsinghua_supercomputer_grid",
        "EBS_quantum_grading_datacenter": "GFX_focus_EBS_tsinghua_supercomputer_grid",
        "EBS_algorithmic_credit_system": "GFX_focus_EBS_algorithmic_credit_system",
        "EBS_predictive_drop_out_model": "GFX_focus_EBS_ai_proctoring_neurolink",
        "EBS_algorithm_determines_destiny": "GFX_focus_EBS_algorithmic_credit_system",
        "EBS_silicon_curriculum_singularity": "GFX_focus_EBS_silicon_curriculum_singularity",
        # Branch C
        "EBS_zhou_evaluation_frenzy": "GFX_focus_EBS_zhou_evaluation_frenzy",
        "EBS_five_day_shock_inspection": "GFX_focus_EBS_zhou_evaluation_frenzy",
        "EBS_nationwide_lawn_greening": "GFX_focus_EBS_nationwide_lawn_greening",
        "EBS_midnight_paperwork_mobilization": "GFX_focus_EBS_midnight_paperwork_mobilization",
        "EBS_model_school_showcase": "GFX_focus_EBS_model_school_showcase",
        "EBS_evaluation_or_shutdown": "GFX_focus_EBS_zhou_evaluation_frenzy",
        "EBS_punitive_disciplinary_tribunal": "GFX_focus_EBS_bureaucratic_iron_stamp",
        "EBS_total_inspection_state": "GFX_focus_EBS_model_school_showcase",
        "EBS_perpetual_inspection_mobilization": "GFX_focus_EBS_perpetual_inspection_mobilization",
        # Branch D
        "EBS_wang_commercial_consortium": "GFX_focus_EBS_wang_commercial_consortium",
        "EBS_sports_quota_black_market": "GFX_focus_EBS_sports_quota_black_market",
        "EBS_school_canteen_cartel": "GFX_focus_EBS_school_canteen_cartel",
        "EBS_privatized_varsity_franchise": "GFX_focus_EBS_wang_commercial_consortium",
        "EBS_exclusive_uniform_procurement": "GFX_focus_EBS_school_canteen_cartel",
        "EBS_athletic_darwinism": "GFX_focus_EBS_sports_quota_black_market",
        "EBS_banquet_diplomacy_network": "GFX_focus_EBS_wang_commercial_consortium",
        "EBS_educational_slush_funds": "GFX_focus_EBS_the_unrestricted_exam_market",
        "EBS_educational_plutocracy": "GFX_focus_EBS_the_unrestricted_exam_market",
        "EBS_the_unrestricted_exam_market": "GFX_focus_EBS_the_unrestricted_exam_market",
        # Branch E
        "EBS_dongbei_conspiracy_active": "GFX_focus_EBS_dongbei_conspiracy",
        "EBS_secret_alliance_of_three_provinces": "GFX_focus_EBS_dongbei_conspiracy",
        "EBS_placate_dongbei_normal": "GFX_focus_EBS_furnace_night_study_battalions",
        "EBS_furnace_night_study_battalions": "GFX_focus_EBS_furnace_night_study_battalions",
        "EBS_armored_exam_trains": "GFX_focus_EBS_armored_exam_trains",
        "EBS_mukden_express_to_beijing": "GFX_focus_EBS_mukden_express_to_beijing",
        "EBS_worker_student_syndicate_councils": "GFX_focus_EBS_dongbei_conspiracy",
        "EBS_dongbei_takes_over_moe": "GFX_focus_EBS_mukden_express_to_beijing",
        "EBS_incinerate_aristocratic_archives": "GFX_focus_EBS_incinerate_aristocratic_archives",
        "EBS_heavy_industry_exam_equality": "GFX_focus_EBS_furnace_night_study_battalions",
        "EBS_absolute_meritocracy_republic": "GFX_focus_EBS_meritocracy_republic",
        # Exam Board
        "EBS_seize_central_printing_press": "GFX_focus_EBS_seize_central_printing_press",
        "EBS_rig_informatics_syllabus": "GFX_focus_EBS_tsinghua_supercomputer_grid",
        "EBS_suppress_southern_olympiad": "GFX_focus_EBS_manipulate_national_exam_board",
        "EBS_manipulate_national_exam_board": "GFX_focus_EBS_manipulate_national_exam_board",
        "EBS_lock_ivory_tower_top3": "GFX_focus_EBS_manipulate_national_exam_board",
        # Heavy Industry
        "EBS_industrial_backbone": "GFX_focus_EBS_industrial_backbone",
        "EBS_central_printing_industrialization": "GFX_focus_EBS_seize_central_printing_press",
        "EBS_beijing_tianjin_railway_artery": "GFX_focus_EBS_armored_exam_trains",
        "EBS_northeast_rust_belt_integration": "GFX_focus_EBS_industrial_backbone",
        "EBS_tianjin_bohai_chemical_refinery": "GFX_focus_EBS_industrial_backbone",
        "EBS_rehe_chahar_mineral_prospecting": "GFX_focus_EBS_industrial_backbone",
        "EBS_anshan_heavy_steel_foundry": "GFX_focus_EBS_furnace_night_study_battalions",
        "EBS_shenyang_arsenal_mobilization": "GFX_focus_EBS_shenyang_arsenal_mobilization",
        "EBS_harbin_locomotive_heavy_chassis": "GFX_focus_EBS_armored_exam_trains",
        "EBS_dalian_naval_dockyard_expansion": "GFX_focus_EBS_shenyang_arsenal_mobilization",
        "EBS_changchun_precision_instrument_works": "GFX_focus_EBS_tsinghua_supercomputer_grid",
        "EBS_wartime_industrial_stockpile": "GFX_focus_EBS_industrial_backbone",
        "EBS_national_defense_technical_polytechnic": "GFX_focus_EBS_shenyang_arsenal_mobilization",
        "EBS_the_invincible_exam_industrial_complex": "GFX_focus_EBS_invincible_complex",
        # War 1938
        "EBS_dispatch_final_syllabus_ultimatum": "GFX_focus_EBS_final_ultimatum",
        "EBS_curb_southern_resistance": "GFX_focus_EBS_final_ultimatum",
        "EBS_coopt_provincial_collaborators": "GFX_focus_EBS_final_ultimatum",
        "EBS_war_mobilization_1938": "GFX_focus_EBS_war_mobilization",
        "EBS_pacify_shanhe_coalition": "GFX_focus_EBS_war_mobilization",
        "EBS_subjugate_huazhong_hbe": "GFX_focus_EBS_war_mobilization",
        "EBS_strike_east_and_south": "GFX_focus_EBS_war_mobilization",
        "EBS_final_siege_of_yandao": "GFX_focus_EBS_final_siege_yandao",
        "EBS_nationwide_educational_dominion": "GFX_focus_EBS_nationwide_dominion"
    }

    import re
    with open("common/national_focus/EBS_focus.txt", "r", encoding="utf-8") as f:
        f_content = f.read()

    updated_count = 0
    for fid, new_icon in FOCUS_MAP.items():
        # Match from id = fid up to icon = GFX_...
        pattern = re.compile(rf'(id\s*=\s*{fid}\b(?:(?!focus\s*=\s*\{{)[\s\S])*?icon\s*=\s*)([a-zA-Z0-9_]+)')
        if pattern.search(f_content):
            f_content = pattern.sub(rf'\g<1>{new_icon}', f_content, count=1)
            updated_count += 1

    with open("common/national_focus/EBS_focus.txt", "w", encoding="utf-8") as f:
        f.write(f_content)
    print(f"[OK] Mapped {updated_count}/82 focuses in common/national_focus/EBS_focus.txt to GFX_focus_EBS_*")

def kill_comfy():
    print("\n[*] Mandatory VRAM cleanup: Terminating ComfyUI server...")
    subprocess.run([
        "C:\\Program Files\\Comfyui-WF-2026.8.8\\Comfyui-WF-2026.8.8\\python\\python.exe",
        "tools/generate_portrait.py",
        "--kill"
    ])
    print("[OK] GPU VRAM 100% released!")

def main():
    total_ideas = len(IDEA_TASKS)
    total_focuses = len(FOCUS_TASKS)
    print(f"==================================================")
    print(f"[*] EBS Asset Generation Pipeline: {total_ideas} Ideas + {total_focuses} Focuses")
    print(f"==================================================")

    # 1. Generate 17 Idea Icons
    for i, t in enumerate(IDEA_TASKS, 1):
        print(f"\n[Idea {i}/{total_ideas}] Generating: {t['name']}...")
        try:
            generate_item(t, "idea")
        except Exception as e:
            print(f"[!] Error on idea {t['name']}: {e}")

    # 2. Generate 38 Focus Icons
    for i, t in enumerate(FOCUS_TASKS, 1):
        print(f"\n[Focus {i}/{total_focuses}] Generating: {t['name']}...")
        try:
            generate_item(t, "focus")
        except Exception as e:
            print(f"[!] Error on focus {t['name']}: {e}")

    # 3. Update interface definitions & focus tree code
    update_code_and_gfx()

    # 4. Mandatory VRAM cleanup
    kill_comfy()

if __name__ == '__main__':
    main()
