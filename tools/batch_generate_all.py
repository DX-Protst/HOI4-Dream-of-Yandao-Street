"""
Batch generator and integrator for all missing HOI4 Focus and Idea Icons.
Uses local ComfyUI workflow (Qwen-MOSS + Chroma Key Despill).
"""

import os
import sys
import json
import time
import urllib.request
import numpy as np
from PIL import Image, ImageFilter

COMFY_API_URL = "http://127.0.0.1:8188"
COMFY_OUT_DIR = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8\ComfyUI\output"

TASKS = [
    # ================= 14 FOCUS ICONS (100x100 max) =================
    {
        "type": "focus",
        "name": "GFX_focus_YDS_campus_asset_inventory",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一本厚重泛黄的物资登记账簿与金色放大镜，背景堆叠整齐的校园储物箱与课桌椅图标，金色齿轮与资产清单徽记，细腻手绘油画质感与金属光泽，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_school_canteen_monopoly",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台红白色复古自动售货机与冰镇玻璃瓶汽水，环绕着金币与钥匙锁链徽章，象征商业垄断与物资管制，复古手绘钢铁雄心图章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_overhead_corridor_network",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两栋现代化教学楼之间横跨的钢铁与玻璃风雨连廊，连廊上方有雨伞与顺畅通行的金色箭头徽标，带有工业与建筑蓝图质感，手绘国策图标风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_sports_room_requisition",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两柄交叉的加固扫把木柄与实心铅球，前方挂着一把厚重的黄铜挂锁与治安管制封条，金属反光，象征后勤器材军用化，钢铁雄心手绘勋章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_craft_class_armory",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，劳技课木工车床与齿轮流水线，传送带上整齐排列着防暴木棍与简易防暴盾牌，木屑与金属火花微光，手绘军工厂国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_print_shop_overdrive",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台高速运转喷吐纸张的工业印刷复印机，洁白的教辅试卷堆积如山，周围环绕着象征超频运转的金色闪电与机械齿轮，手绘工业国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_chemistry_lab_reagents",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两只盛满鲜艳红色墨水与深紫红色化学试剂的玻璃平底烧瓶与试管，冒出细腻气泡，背后衬托着交叉的玻璃搅拌棒与原子轨道图案，手绘科技国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_handicraft_standardization",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台经典的复古黑色脚踏缝纫机，整齐折叠的深色学生校服与鲜红色的纠察队袖标，金色剪刀与量尺交叉，手绘工业标准化国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_campus_logistics_gigafactory",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，宏伟的巨型校园后勤综合联合体大楼，巨大的金色工业齿轮、运输箱与铁砧，两侧环绕金色麦穗，象征终极后勤工业巨无霸，庄重恢弘手绘国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_gaokao_war_mobilization",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，悬挂着全国战时总动员深红横幅的宏伟校园大门，背景为冲锋号角与金色战斗警钟，钢笔如利刃刺刀般整齐排列，决战氛围，手绘总动员国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_exam_hall_tactics",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一个正在精准倒计时的金色机械秒表，压在画有严密战术进攻红色箭头的答题卡方阵之上，象征严苛的考场心理压迫与战术推演，手绘战术国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_break_repeater_siege",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一柄巨大的金色锋利长剑将象征包围圈的厚重试卷锁链与铁丝网齐齐斩断，碎片与金色火花飞溅，象征突破重围与锐利突穿，手绘战争突围国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_all_front_counterattack",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张展开的羊皮纸作战地图，多道醒目的红色大反攻箭头从中心席卷而出，前方矗立着一面迎风招展的校旗，手绘全面进攻国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "focus",
        "name": "GFX_focus_YDS_all_china_educational_hegemony",
        "outdir": "gfx/interface/goals",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一顶镶嵌红蓝宝石的华丽金色帝国桂冠与帝冕，高悬在一份盖有朱红大印的高考金榜卷轴之上，周围环绕着耀眼的金色胜利光芒与橄榄枝，至高霸权手绘国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # ================= 16 YDS IDEA ICONS (64x64) =================
    {
        "type": "idea",
        "name": "yds_academic_ivory_tower_bias",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一座高耸巍峨洁白的象牙石塔，塔顶环绕着复杂的数学积分符号与金色圆规，基座下方断裂倾斜的生锈齿轮与工兵铲，象征偏科脱节实操，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_campus_gigafactory_idea",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一个巨大的金色工业齿轮正中央包裹着一栋校园后勤大厦，四周点缀着麦穗、木工箱与红墨水瓶，金色与深蓝厚涂质感，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_canteen_monopoly_idea",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一瓶插着吸管的冰镇玻璃瓶橙色汽水，前方叠着几枚闪亮的金币与挂锁，象征校园垄断经济与资金充沛，手绘国家精神图章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_chem_reagents_idea",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一只盛着鲜红色发光药剂与微小气泡的化学平底烧瓶，斜插着一根玻璃搅拌棒与原子环形轨道图案，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_olympiad_elite_training_spirit",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一枚燃烧着金色与蓝色炽烈火焰的高难度奥林匹克竞赛奖牌，中央刻有西格玛求和符号∑与原子核，严谨深邃，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_olympiad_well_rounded_focus",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一座古铜色平衡天平，两端分别托着厚厚的教科书与社团艺术调色盘，橄榄枝环绕，象征德智体全面平衡，手绘国家精神图章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_sports_armory_idea",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一柄加粗实木扫把柄与一柄重型钢制标尺在铁砧上交叉，前方立着一枚防暴盾牌与黑铁铅球，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_ivory_tower_hegemony",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一座悬浮在璀璨光环中的华丽金色象牙塔尖，散发着刺眼的蓝色电弧与学术灵光，周身环绕着保送保密卷轴，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_repeater_coalition_pact",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，多只紧紧握在一起的学生拳头，手腕缠绕着铁链与红色复读必胜头带，同仇敌忾，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_repeater_underdog_spirit",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一面迎着暴风雨烈烈燃烧的深红战旗，旗帜上写着大大的“必胜”毛笔金字，身后无数金色钢笔如标枪刺破阴霾，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_exam_hall_tactics_spirit",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一块正在急促倒计时的金色机械怀表秒表，指针正指向最后关头，压在红蓝交错的军用态势推演图上，手绘国家精神图章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_break_siege_spirit",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一柄金色的利剑将厚重的铁丝网与锁链一斩两段，迸发出耀眼的断裂火星，象征摧枯拉朽突破重围，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_national_exam_hegemony",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一顶耀眼夺目的黄金帝国皇冠，嵌满祖母绿与红宝石，稳稳戴在一份全国高考状元大红喜报卷轴之上，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_school_resistance_debuff",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一只潜伏在阴影中的紫色神秘眼睛，正在警惕地窥视着校门与铁栅栏，四周弥漫着象征流言与抵制的暗紫色雾气，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_elite_schools_united",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，三枚闪烁着金色、银色与深蓝色光辉的顶尖名校盾徽整齐排列并拢，上方有一顶统摄全局的金色月桂冠，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "yds_regular_schools_united",
        "outdir": "gfx/interface/ideas/YDS",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，三柄并列向下的礼仪佩剑与三本打开的外语辞典，下方由一条金色的同盟丝带紧紧系在一起，象征外围多元名校合流，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },

    # ================= 4 TLB IDEA ICONS (64x64) =================
    {
        "type": "idea",
        "name": "tlb_class_6_discord",
        "outdir": "gfx/interface/ideas/TLB",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一张圆桌上被撕成数瓣的班级花名册，几只颜色各异的手分别抓向不同的碎片，暗藏机锋，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "tlb_tongba_movement",
        "outdir": "gfx/interface/ideas/TLB",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一只高高举起紧握铅笔与折断戒尺的铁拳，背景伴有熊熊燃烧的起义火炬与红旗，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "tlb_hegemon_of_sichuan",
        "outdir": "gfx/interface/ideas/TLB",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一尊威风凛凛的铜梁巴中金铜狮子印章，威严地盖在全川行政地图的正中央，手绘国家精神图章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "type": "idea",
        "name": "tlb_chongqing_autonomous_zone",
        "outdir": "gfx/interface/ideas/TLB",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4国家精神圆形徽章图标，正面居中，一座巍峨的现代化山城立体桥梁与两江交汇微缩图标，上方悬挂着代表教育特区自治权的金色盾牌徽章，手绘国家精神图章风格，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    }
]

def build_workflow_payload(prompt_text, seed=None, steps=25, cfg=3.0):
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
                "steps": steps,
                "cfg": cfg,
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
                "filename_prefix": "hoi4_asset_raw"
            }
        }
    }

def cutout_green_screen(raw_img_path):
    img = Image.open(raw_img_path).convert('RGB')
    rgb = np.array(img, dtype=np.float32)

    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]

    max_rb = np.maximum(r, b)
    green_diff = g - max_rb

    lower_th = 15.0
    upper_th = 60.0
    alpha = np.clip(1.0 - (green_diff - lower_th) / (upper_th - lower_th), 0.0, 1.0)

    # Protect dark colors & non-bright greens
    is_bright_green = (g > 100) & (g > r * 1.15) & (g > b * 1.15)
    alpha = np.where(is_bright_green, alpha, 1.0)

    # Despill: neutralize green spill
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
    os.makedirs(outdir, exist_ok=True)
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

def process_idea_icon(cutout, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    bbox = cutout.getbbox()
    if bbox:
        cropped = cutout.crop(bbox)
        bw, bh = cropped.width, cropped.height
        # fit within 62x62 and center in 64x64 canvas
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
    print(f"[Done] Idea Icon saved: {out_file} (size: {canvas.size})")
    return out_file

def generate_one(task):
    name = task["name"]
    outdir = task["outdir"]
    target_path = os.path.join(outdir, f"{name}.png")

    if os.path.exists(target_path):
        print(f"[*] Skipping {name} - already exists at {target_path}")
        return target_path

    payload = build_workflow_payload(task["prompt"])
    post_data = json.dumps({"prompt": payload}).encode('utf-8')
    req = urllib.request.Request(f"{COMFY_API_URL}/prompt", data=post_data, headers={'Content-Type': 'application/json'})

    print(f"[*] Submitting prompt for [{task['type']}] {name}...")
    resp = urllib.request.urlopen(req)
    prompt_id = json.loads(resp.read().decode('utf-8'))['prompt_id']

    start_t = time.time()
    while True:
        time.sleep(2)
        elapsed = int(time.time() - start_t)
        try:
            h_req = urllib.request.urlopen(f"{COMFY_API_URL}/history/{prompt_id}")
            h_data = json.loads(h_req.read().decode('utf-8'))
            if prompt_id in h_data:
                item = h_data[prompt_id]
                images = item.get('outputs', {}).get('9', {}).get('images', [])
                if not images:
                    raise RuntimeError("No output image returned from node 9")
                filename = images[0]['filename']
                subfolder = images[0].get('subfolder', '')
                raw_path = os.path.join(COMFY_OUT_DIR, subfolder, filename)
                print(f"[*] ComfyUI rendered in {elapsed}s: {raw_path}")

                cutout = cutout_green_screen(raw_path)
                if task["type"] == "focus":
                    return process_focus_icon(cutout, outdir, name)
                else:
                    return process_idea_icon(cutout, outdir, name)
            else:
                if elapsed % 6 == 0:
                    print(f"[*] Waiting for ComfyUI... ({elapsed}s)")
        except Exception as e:
            if "No output image" in str(e):
                raise e
            pass

        if elapsed > 180:
            raise TimeoutError(f"Generation timed out for {name} (180s)")

def main():
    total = len(TASKS)
    print(f"==================================================")
    print(f"[*] Master Batch Generation Started: {total} Assets")
    print(f"==================================================")

    for i, task in enumerate(TASKS, 1):
        print(f"\n[{i}/{total}] Processing {task['type']}: {task['name']}...")
        try:
            generate_one(task)
        except Exception as e:
            print(f"[!] Error generating {task['name']}: {e}")
            time.sleep(2)
        time.sleep(1)

    print("\n[✓] All asset generations completed!")

if __name__ == '__main__':
    main()
