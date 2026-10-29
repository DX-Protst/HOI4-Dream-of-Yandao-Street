"""
Batch generator for the 14 HOI4 Focus Icons using ComfyUI + Chroma Keying Despill.
Skips icons that already exist.
"""

import os
import sys
import time
from generate_focus_icons import generate_one

TASKS = [
    {
        "name": "GFX_focus_YDS_campus_asset_inventory",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一本厚重泛黄的物资登记账簿与金色放大镜，背景堆叠整齐的校园储物箱与课桌椅图标，金色齿轮与资产清单徽记，细腻手绘油画质感与金属光泽，无阴影，干净轮廓，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_school_canteen_monopoly",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台红白色复古自动售货机与冰镇玻璃瓶汽水，环绕着金币与钥匙锁链徽章，象征商业垄断与物资管制，复古手绘钢铁雄心图章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_overhead_corridor_network",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两栋现代化教学楼之间横跨的钢铁与玻璃风雨连廊，连廊上方有雨伞与顺畅通行的金色箭头徽标，带有工业与建筑蓝图质感，手绘国策图标风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_sports_room_requisition",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两柄交叉的加固扫把木柄与实心铅球，前方挂着一把厚重的黄铜挂锁与治安管制封条，金属反光，象征后勤器材军用化，钢铁雄心手绘勋章风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_craft_class_armory",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，劳技课木工车床与齿轮流水线，传送带上整齐排列着防暴木棍与简易防暴盾牌，木屑与金属火花微光，手绘军工厂国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_print_shop_overdrive",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台高速运转喷吐纸张的工业印刷复印机，洁白的教辅试卷堆积如山，周围环绕着象征超频运转的金色闪电与机械齿轮，手绘工业国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_chemistry_lab_reagents",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，两只盛满鲜艳红色墨水与深紫红色化学试剂的玻璃平底烧瓶与试管，冒出细腻气泡，背后衬托着交叉的玻璃搅拌棒与原子轨道图案，手绘科技国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_handicraft_standardization",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一台经典的复古黑色脚踏缝纫机，整齐折叠的深色学生校服与鲜红色的纠察队袖标，金色剪刀与量尺交叉，手绘工业标准化国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_campus_logistics_gigafactory",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，宏伟的巨型校园后勤综合联合体大楼，巨大的金色工业齿轮、运输箱与铁砧，两侧环绕金色麦穗，象征终极后勤工业巨无霸，庄重恢弘手绘国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_gaokao_war_mobilization",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，悬挂着全国战时总动员深红横幅的宏伟校园大门，背景为冲锋号角与金色战斗警钟，钢笔如利刃刺刀般整齐排列，决战氛围，手绘总动员国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_exam_hall_tactics",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一个正在精准倒计时的金色机械秒表，压在画有严密战术进攻红色箭头的答题卡方阵之上，象征严苛的考场心理压迫与战术推演，手绘战术国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_break_repeater_siege",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一柄巨大的金色锋利长剑将象征包围圈的厚重试卷锁链与铁丝网齐齐斩断，碎片与金色火花飞溅，象征突破重围与锐利突穿，手绘战争突围国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_all_front_counterattack",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一张展开的羊皮纸作战地图，多道醒目的红色大反攻箭头从中心席卷而出，前方矗立着一面迎风招展的校旗，手绘全面进攻国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    },
    {
        "name": "GFX_focus_YDS_all_china_educational_hegemony",
        "prompt": "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一个钢铁雄心4风格的国策图标，正面居中，一顶镶嵌红蓝宝石的华丽金色帝国桂冠与帝冕，高悬在一份盖有朱红大印的高考金榜卷轴之上，周围环绕着耀眼的金色胜利光芒与橄榄枝，至高霸权手绘国策风格，无阴影，干净边缘，棚拍均匀平光照明，背景绝对纯绿色"
    }
]

def main():
    outdir = "gfx/interface/goals"
    total = len(TASKS)
    print(f"[*] Starting batch generation of {total} focus icons...")
    
    for i, item in enumerate(TASKS, 1):
        name = item["name"]
        target_path = os.path.join(outdir, f"{name}.png")
        if os.path.exists(target_path):
            print(f"[{i}/{total}] Skipping {name} - already exists.")
            continue
            
        print(f"\n==========================================")
        print(f"[{i}/{total}] Generating {name}...")
        print(f"==========================================")
        generate_one(item["prompt"], outdir, name)
        time.sleep(1)

    print("\n[✓] All 14 focus icons generated successfully!")

if __name__ == "__main__":
    main()
