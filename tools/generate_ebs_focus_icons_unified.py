"""
HOI4 Focus Icon Unified Master Pipeline for EBS (Education Bureaucracy System).
Strictly enforces:
1. National Macro-Style (Clausewitz 1930s-1940s vintage gouache illustration, heavy brass framing, Prussian blue/crimson palette).
2. Branch Micro-Styles (8 distinct branch aesthetic matrices).
3. Immutable Style Lock Clause in every prompt.
Supports both ComfyUI text-to-image (with auto VRAM kill) and Banana / subagent prompt book generation.
"""

import os
import sys
import json
import time
import argparse
import subprocess
import urllib.request
import urllib.error
import numpy as np
from PIL import Image, ImageFilter
import psutil

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOAL_OUT_DIR = os.path.join(PROJECT_ROOT, "gfx", "interface", "goals", "EBS")
os.makedirs(GOAL_OUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. STRICT STYLE LOCK DEFINITIONS
# -------------------------------------------------------------

NATIONAL_MACRO_STYLE_LOCK = (
    "【强制国家级大风格约束·绝对不可更改或省略】：Hearts of Iron IV 钢铁雄心4官方国策图标水粉宣传画艺术风格"
    "（Clausewitz 1930s-1940s vintage gouache & propaganda illustration），宏观基底：深普鲁士蓝与权威古典黄铜浮雕装帧，"
    "统一金色月桂/齿轮/绶带黄金构件外框锚点，庄严厚重金属光泽与手绘笔触，45度左上方温暖戏剧性主光与边缘高光，"
    "纯净平整单色绿幕背景（chroma key #00FF00 green screen background），平光棚拍，干净无毛刺剪影。"
    "【严格负向锁定】：严禁任何扁平矢量极简图形、严禁现代3D塑料CG感、严禁现实照片真人混贴、严禁画面出现任何文本/英文字母/汉字/数字印记。"
)

BRANCH_MICRO_STYLES = {
    "PHASE_1": {
        "name": "最高督导巡视局总干线",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：朱印公文与深红火漆档案风格（Crimson Wax Seal & Ministerial Dossier）。"
            "专属视觉图腾与材质：朱红火漆印章、黄铜双管放大镜、红头保密档案袋、丝绒封签、正义黄铜天平、红木法槌。"
            "微观调色盘：辰砂红、深红木褐、档案陈金色。"
        )
    },
    "BRANCH_A": {
        "name": "陈专员公署 (海淀贵胄与世卿保送)",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：汉白玉罗马浮雕与镀金特权学院风格（Ivory Marble Relief & Neoclassical Academy）。"
            "专属视觉图腾与材质：罗马多立克石柱、汉白玉浮雕群、纯金锻铁旋转拱门、金色强基钥匙、紫丝绒博士兜帽、重金百合纹章。"
            "微观调色盘：汉白玉象牙白、皇家紫罗兰、高光纯金。"
        )
    },
    "BRANCH_B": {
        "name": "怀总工实验室 (赛博考务与AI算力分流)",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：柴油朋克真空管与复古继电器数控风格（Dieselpunk Cybernetics & Brass Oscilloscopes）。"
            "专属视觉图腾与材质：发光橙色真空管、黄铜示波器阴极射线、机械打孔纸带、铜质继电器、跳跃电弧、金属齿轮算盘。"
            "微观调色盘：真空管炽橙、示波器青蓝、哑光枪钢色。"
        )
    },
    "BRANCH_C": {
        "name": "周总导督察部 (绿化率与突击迎检)",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：秒表、涂料喷枪与刺目迎检警报风格（Chrome Stopwatches, Lawn Paint & Inspection Sirens）。"
            "专属视觉图腾与材质：镀铬倒计时秒表、高压草坪涂料喷枪、水泥喷覆鲜绿涂层、铁质文件夹带血红打勾复核表、旋转探照警报灯。"
            "微观调色盘：工矿铬绿、警示斑马黄、镀铬精钢银。"
        )
    },
    "BRANCH_D": {
        "name": "双王黑金政权 (校服校餐与特长生意)",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：黑金钞券、天价校服与金库黑市风格（Black Gold Banknotes, Vaults & Fabric Cartels）。"
            "专属视觉图腾与材质：扎捆的连号纸钞、溢出金条的鳄鱼皮公文箱、镀金体育优胜杯标价签、昂贵校服布料呢绒卷、茅台酒高脚杯。"
            "微观调色盘：沥青玄黑、金库金、钞券浅绿、深宝蓝。"
        )
    },
    "BRANCH_E": {
        "name": "东三省名校联合公社 (铁锈重工做题家起义)",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：苏式构成主义重工业与工农钢笔齿轮风格（Constructivist Heavy Industry & Steel Grinders）。"
            "专属视觉图腾与材质：交叉的重型锻压铁锤与钢尖蘸水笔、咬合在教科书上的生铁巨齿轮、高炉通红钢水飞溅、红旗工学齿轮徽。"
            "微观调色盘：生铁铸造黑灰、高炉熔融烈橙、苏维埃赤红。"
        )
    },
    "EXAM_INDUSTRY": {
        "name": "考工委印卷垄断与重工业基建",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：国家机密轮转印机与军工重备风格（Confidential Rotary Presses & Military-Industrial Complex）。"
            "专属视觉图腾与材质：飞速吞吐试卷的高速双滚筒轮转印刷机、装甲防暴押运车厢、带刺铁丝网、1938钢印重钢轨、炮弹木箱。"
            "微观调色盘：军工机械橄榄绿、铅字油墨灰、弹壳黄铜。"
        )
    },
    "WAR_CLIMAX": {
        "name": "全国统考圣战与盐道街终局",
        "lock": (
            "【强制分支专有小风格约束·绝对不可更改或省略】：统帅部作战地图、上膛刺刀与大一统圣旨风格（Supreme War Room Map & Syllabus Ultimatum）。"
            "专属视觉图腾与材质：交叉元帅权杖横跨全国考纲作战沙盘、插穿考卷的毛瑟刺刀、抓握大一统圣旨的金雕、直指盐道街的攻城重炮。"
            "微观调色盘：参谋部野战灰、进军箭头血红、帝国至尊金。"
        )
    }
}

# -------------------------------------------------------------
# 2. FULL 82 FOCUSES DATA REGISTRY WITH IMMUTABLE LOCKED PROMPTS
# -------------------------------------------------------------

EBS_FOCUS_REGISTRY = [
    # --- PHASE 1 (5) ---
    {
        "id": "EBS_supreme_inspection_bureau",
        "name": "最高教育巡视督导专员公署成立",
        "branch": "PHASE_1",
        "focal": "一枚硕大厚重的八角形中央督学青铜巡按盾徽，盾心刻有深红火漆立柱与两把交叉的黄铜羽毛笔，盾顶盘绕金色月桂枝，背后垂下两条深红金边督导绶带。"
    },
    {
        "id": "EBS_inspectors_general_assembly",
        "name": "全国督学常务全席会议",
        "branch": "PHASE_1",
        "focal": "一张深色红木半圆议事桌，正中摆放镀金议长木槌与展开的全国督导红头法令，两盏铸铜台灯照亮整齐码放的牛皮纸会议公文夹与沉重官印。"
    },
    {
        "id": "EBS_balance_bureaucratic_interests",
        "name": "平衡部内诸派既得利益",
        "branch": "PHASE_1",
        "focal": "一架精密的黄铜机械天平，左盘盛放着象征学术特权的汉白玉柱与紫绶带，右盘盛放着象征工业配额的铁齿轮与钞票夹，中间由一枚雕刻精细的官僚金印牢牢镇住支点。"
    },
    {
        "id": "EBS_uncover_internal_corruption",
        "name": "暗中收集各派腐败黑料",
        "branch": "PHASE_1",
        "focal": "一只戴着黑色皮手套的隐秘之手正用黄铜手电筒照亮暗处半开的铁皮保险柜，光柱聚焦在一份用深红火漆重新密封的密级绝密档案袋上，露出一张带黑印的照片角与微型放大镜。"
    },
    {
        "id": "EBS_the_council_schism",
        "name": "部务核心分歧：总督学的抉择",
        "branch": "PHASE_1",
        "focal": "一块被中央闪电裂纹精确劈裂的红木官印座，左侧裂片缠绕着海淀金丝与计算机光缆，右侧裂片堆叠着草坪绿化喷枪与重工钢轨，一把悬空落下的沉重裁决钢刃。"
    },

    # --- BRANCH A (10) ---
    {
        "id": "EBS_chen_absolutism",
        "name": "陈专员太上皇权威确立",
        "branch": "BRANCH_A",
        "focal": "一座汉白玉雕琢的威严太上皇高背御座，椅背雕刻着四百强基大学圆顶浮雕，扶手为两头纯金雄狮，椅面上端放着一枚盖有朱红部令大印的免试金册。"
    },
    {
        "id": "EBS_squeeze_classroom_moisture",
        "name": "全国课堂挤水分运动",
        "branch": "BRANCH_A",
        "focal": "一只沉重的黄铜工业挤压螺旋手轮，正在强力拧绞一本厚重的各省高考复习大纲，淡蓝色的水分被挤出化作蒸汽，压榨出泛着金光的极度浓缩核心考点结晶。"
    },
    {
        "id": "EBS_strengthen_beijing_admissions",
        "name": "强化京城直属校录取特权",
        "branch": "BRANCH_A",
        "focal": "两座巍峨对峙的汉白玉华表柱拱卫着一道敞开的纯金宫门，门内透出温暖的象牙塔金色光辉，一条铺着紫丝绒的直通录取红地毯笔直延伸至门内。"
    },
    {
        "id": "EBS_fortify_haidian_bastion",
        "name": "海淀贵胄堡垒深度固化",
        "branch": "BRANCH_A",
        "focal": "一座由厚重花岗岩与汉白玉堆砌的星形学院要塞城堡，垛口插满象征顶尖名校的深蓝金边校旗，要塞城墙上悬挂着一条刻满奥赛特等奖金字的防卫铁锁链。"
    },
    {
        "id": "EBS_tibet_airdrop_express",
        "name": "进藏生名额直通车特许",
        "branch": "BRANCH_A",
        "focal": "一架复古的双翼运输机在雪山之巅抛下一个带有降落伞的坚固黄铜保险箱，箱体上盖有醒目的绿色‘特许绿色通道进藏生’封签，雪山下映射出金色直通路线。"
    },
    {
        "id": "EBS_central_inspectorate_permanent",
        "name": "中央巡视常态化进驻防线",
        "branch": "BRANCH_A",
        "focal": "一顶坚固的军用帆布中央督导帐篷扎根在大理石台阶前，门前立着一具带有黄铜长矛尖的哨兵立牌，上面挂着一具锁闭的24小时机要检举铸铁信箱。"
    },
    {
        "id": "EBS_monopolize_special_pathways",
        "name": "垄断强基破格自招暗道",
        "branch": "BRANCH_A",
        "focal": "一扇雕花精美的铸铁镀金旋转暗门，门缝中透出幽微的密室金色光芒，一把镶嵌红宝石的纯金特长特许钥匙正悄然插在隐秘的机关锁孔中。"
    },
    {
        "id": "EBS_bureaucratic_iron_stamp",
        "name": "部令红头铁印一票否决权",
        "branch": "BRANCH_A",
        "focal": "一枚极具份量的铸铁方形大官印重重砸在一叠地方公文上，印底留下鲜红如血的‘一票否决’朱砂正方印记，四溅的暗红色墨迹震裂了桌面的红木纹理。"
    },
    {
        "id": "EBS_the_untouchable_nobility",
        "name": "不可动摇之名门贵胄特权",
        "branch": "BRANCH_A",
        "focal": "一座高耸入云的汉白玉方尖碑，基座雕刻着京城八大名校族徽，四周环绕着带倒刺的纯金铸铁荆棘栏杆，雷电与暴雨在栏杆外被金色护盾无形消解。"
    },
    {
        "id": "EBS_imperial_examination_throne",
        "name": "应试帝国太上皇法统",
        "branch": "BRANCH_A",
        "focal": "一顶由千百支镀金钢笔尖与朱砂印泥盒堆砌而成的金色帝王冠冕，冠冕正前方镶嵌着一枚完美无瑕的八角形高考大纲晶石，散发着君临天下的庄严金芒。"
    },

    # --- BRANCH B (9) ---
    {
        "id": "EBS_huai_technocratic_coup",
        "name": "怀总工的技术官僚政变",
        "branch": "BRANCH_B",
        "focal": "一把镀铬的电子工程游标卡尺与一把复古烙铁交叉，强行别开一扇锈蚀的传统官僚木门，门后露出一排排跳动着幽蓝电光的真空管控制面板。"
    },
    {
        "id": "EBS_fiber_optic_exam_backbone",
        "name": "光纤考务全国骨干网",
        "branch": "BRANCH_B",
        "focal": "一束从重型铸铁地下井口破土而出的多股发光光纤电缆束，耀眼的金色与青蓝色脉冲信号在玻璃管内奔流，如电光蛛网般延伸向四周的微型金属地图。"
    },
    {
        "id": "EBS_ai_proctoring_neurolink",
        "name": "脑机生物考场监考矩阵",
        "branch": "BRANCH_B",
        "focal": "一具精密的黄铜半球形头戴式脑电波探测仪，带有三根柔性铜质吸盘电极，中心仪表面板上是一只发出琥珀色警示辉光的无机机械复眼。"
    },
    {
        "id": "EBS_tsinghua_supercomputer_grid",
        "name": "清华超算考务中心联网",
        "branch": "BRANCH_B",
        "focal": "一座庞大的复古机房塔楼矩阵，无数排闪烁着规律绿光的继电器柜整齐排列，顶部矗立着一座正在向阴云密布的长空发射高频同步无线电波的环形特斯拉线圈发射塔。"
    },
    {
        "id": "EBS_quantum_grading_datacenter",
        "name": "量子拟合试卷批改集群",
        "branch": "BRANCH_B",
        "focal": "一个悬浮在充油冷却玻璃圆筒中的复杂齿轮差分机核心，数千张微缩试卷如同数据流环绕核心飞速旋舞，数道青蓝色的激光束瞬间将试卷解析为打孔数据。"
    },
    {
        "id": "EBS_algorithmic_credit_system",
        "name": "全国学生行为算法积分系统",
        "branch": "BRANCH_B",
        "focal": "一张厚重的穿孔牛皮纸学生档案卡，正面被打孔机压出一排排精密的机械孔洞，背景中巨大的青铜算筹滚轮正将分数转化为带锁链的信用齿轮。"
    },
    {
        "id": "EBS_predictive_drop_out_model",
        "name": "前瞻性早培与分流预测模型",
        "branch": "BRANCH_B",
        "focal": "一台复古机械示波器屏幕，绿色的荧光曲线上显示着一条急剧分叉的命运走势：上方通往象牙塔金顶，下方被一把冰冷的黑色铁剪无情剪断并盖上红叉。"
    },
    {
        "id": "EBS_algorithm_determines_destiny",
        "name": "算法即命运：无机专制",
        "branch": "BRANCH_B",
        "focal": "一只由精密青铜齿轮与真空管组成的机械神明巨手，指尖垂下一根根金色数据导线，操控着下方木偶般的微缩考生人偶走向两座标有升学与分流的钢铁闸门。"
    },
    {
        "id": "EBS_silicon_curriculum_singularity",
        "name": "硅基考纲奇点大一统",
        "branch": "BRANCH_B",
        "focal": "一颗巨大的多面体黑色硅晶石核心悬浮在半空，表面蚀刻着金色的数理化公式电路，万千本传统课本在它强大的引力光环中被分解并重组为永恒的计算晶格。"
    },

    # --- BRANCH C (9) ---
    {
        "id": "EBS_zhou_evaluation_frenzy",
        "name": "周总导大迎检权威确立",
        "branch": "BRANCH_C",
        "focal": "一枚镀铬的五星特别迎检巡按徽章，背后交叉着一支带有红墨水笔痕的硬木指挥棒与一把钢质直尺，徽章正中镶嵌着一块写满‘迎检必胜’的珐琅铭牌。"
    },
    {
        "id": "EBS_five_day_shock_inspection",
        "name": "五天突击大迎检极限动员",
        "branch": "BRANCH_C",
        "focal": "一块金属秒表，指针正指向最后的倒计时血红刻度，表盘后方是三辆风驰电掣冲出校门的黑色迎检吉普车剪影，车顶亮着刺目的旋转黄色探照警灯。"
    },
    {
        "id": "EBS_nationwide_lawn_greening",
        "name": "全国校区草坪一夜刷漆绿化",
        "branch": "BRANCH_C",
        "focal": "一支重工业压铸喷漆枪正猛烈喷射出一道极其浓厚鲜艳的翠绿涂料，将干枯灰暗的操场泥土与枯草瞬间覆盖成一片刺目的完美几何绿茵，地面放着绿漆铁桶。"
    },
    {
        "id": "EBS_midnight_paperwork_mobilization",
        "name": "中小学教师连夜补教案运动",
        "branch": "BRANCH_C",
        "focal": "一盏罩着墨绿色铁皮灯罩的白炽台灯照亮凌乱的书桌，厚如城墙的整齐教学教案堆积如山，数支写得磨平笔尖的红蓝铅笔和空了的速溶咖啡杯散落一旁。"
    },
    {
        "id": "EBS_model_school_showcase",
        "name": "示范校夜景立面粉饰工程",
        "branch": "BRANCH_C",
        "focal": "一座原本斑驳古旧的教学楼外墙前，工人们正架起脚手架给立面粉刷一层薄如纸片的纯白大理石仿石漆，数道刺眼的聚光灯将这面伪装门面照耀得光彩夺目。"
    },
    {
        "id": "EBS_evaluation_or_shutdown",
        "name": "迎检不合格即刻停办反思",
        "branch": "BRANCH_C",
        "focal": "一张盖有鲜红督导局钢印的巨大白色交叉封条，狠狠贴在一座被粗大铁链锁死的高中大铁门上，门锁上挂着一把冷酷的黑色铸铁挂锁。"
    },
    {
        "id": "EBS_punitive_disciplinary_tribunal",
        "name": "督导严惩特别巡回法庭",
        "branch": "BRANCH_C",
        "focal": "一座黑漆审判台，上面摆放着一本摊开的《违规办学处罚条例》，一柄坚硬的黑石法槌重重落下，将一块刻有‘全国百强中学’的铜质荣誉校牌砸成两段。"
    },
    {
        "id": "EBS_total_inspection_state",
        "name": "全权示范帝国官道迎检大成",
        "branch": "BRANCH_C",
        "focal": "一条纤尘不染、用白石灰画出绝对笔直边界线的校园迎检主干道，道路两旁整齐划一地伫立着标兵般的红绿迎检旗帜，天空晴朗却带着一丝不可呼吸的严酷秩序。"
    },
    {
        "id": "EBS_perpetual_inspection_mobilization",
        "name": "永久突击迎检总体战",
        "branch": "BRANCH_C",
        "focal": "一只永远在疯狂运转的发条秒表，表盘上的指针已经融合成一道银色光环，底座与一台永不停歇的督导广播大喇叭齿轮死死铆接，喷吐出连绵不绝的检查号令。"
    },

    # --- BRANCH D (10) ---
    {
        "id": "EBS_wang_commercial_consortium",
        "name": "王司长与王总管黑金同盟",
        "branch": "BRANCH_D",
        "focal": "两只戴着纯金劳力士手表的肥硕手掌在虚空中紧紧相握，背景中是一张由各省教育后勤采购合同拼贴而成的黑金网状底盘，一枚金币在握手上方闪耀。"
    },
    {
        "id": "EBS_sports_quota_black_market",
        "name": "国家二级运动员特长黑市",
        "branch": "BRANCH_D",
        "focal": "一只摆在黑天鹅绒托盘上的金色田径运动奖杯，杯身上粗暴地贴着一张带有手写美元符号与高额标价的当铺质押标签，旁边散落着盖有假红印的测试记录册。"
    },
    {
        "id": "EBS_school_canteen_cartel",
        "name": "全国中小学校餐预制垄断财阀",
        "branch": "BRANCH_D",
        "focal": "一只巨大的军绿色重型工业预制菜蒸笼铁箱，箱体上用白色油漆喷着‘统一集中配餐’字样，周围堆满了铁皮罐头与锁紧的铁链，箱盖上坐着一只饕餮金兽。"
    },
    {
        "id": "EBS_privatized_varsity_franchise",
        "name": "特长加分与校外牌照特许",
        "branch": "BRANCH_D",
        "focal": "一张装裱在重金雕花相框内的‘全国艺术体育加分特许经营执照’，印泥鲜红，右下角盖有纯金压印，数枚沉甸甸的金币正被整齐地码放在执照边缘。"
    },
    {
        "id": "EBS_exclusive_uniform_procurement",
        "name": "天价校服强制统一定点采购",
        "branch": "BRANCH_D",
        "focal": "一卷粗劣却泛着塑料化纤光泽的深蓝色中学生校服布料卷轴，周围缠绕着一道金色的皮尺，皮尺末端咬着一张数额惊人的天价采购发票。"
    },
    {
        "id": "EBS_athletic_darwinism",
        "name": "校园足球特许与特长达尔文主义",
        "branch": "BRANCH_D",
        "focal": "一只由坚硬铸铁与黑金皮革缝制而成的沉重足球，球面上凸起着尖锐的金属鞋钉，足球碾碎了下方一本普通的物理教科书，顶端顶着一顶胜利桂冠。"
    },
    {
        "id": "EBS_banquet_diplomacy_network",
        "name": "千席茅台宴请与关系网密织",
        "branch": "BRANCH_D",
        "focal": "一只经典的白瓷红带酱香酒瓶立在深色酒桌正中，周围环绕着八只晶莹剔透、盛满金色玉液的高脚玻璃酒杯，酒杯下方垫着各省招生办主任的签单便笺。"
    },
    {
        "id": "EBS_educational_slush_funds",
        "name": "教育黑金金库与资金洗白",
        "branch": "BRANCH_D",
        "focal": "一座深藏在地下的重型金库防爆圆形钢铁大门，门轴由沉重的齿轮带动半开，露出里面堆积如山的成捆钞票砖与被金漆涂装的学杂费收费箱。"
    },
    {
        "id": "EBS_educational_plutocracy",
        "name": "金钱即考分：教育财阀极权",
        "branch": "BRANCH_D",
        "focal": "一枚由纯金铸造的巨大硬币，硬币正面雕刻着满分‘750’的立体数字，背后浮雕着一座私立贵族学校的城堡轮廓，周围环绕着‘价高者得’的罗马拉丁文铭文。"
    },
    {
        "id": "EBS_the_unrestricted_exam_market",
        "name": "全国高考名额证券化现货市场",
        "branch": "BRANCH_D",
        "focal": "一块黑色的复古交易所行情报价黑板，上方用白色粉笔密密麻麻标写着‘京籍指标：涨停’、‘藏籍名额：大宗交易’，下方是一把敲定拍卖交易的金色小锤。"
    },

    # --- BRANCH E (11) ---
    {
        "id": "EBS_dongbei_conspiracy_active",
        "name": "风暴前夜：东三省名校暗流",
        "branch": "BRANCH_E",
        "focal": "冰封雪原上一座彻夜通明的红砖苏式高中教学楼，窗户透出昏黄的做题灯光，近处雪地中一双穿着大头皮鞋的脚旁插着一柄铁锹和一份带血红指印的同盟书。"
    },
    {
        "id": "EBS_secret_alliance_of_three_provinces",
        "name": "关东三省学运钢铁秘密结盟",
        "branch": "BRANCH_E",
        "focal": "三只粗糙长满老茧的年轻手掌在重型铸造台上死死握在一起，手腕上绑着红白相间的工学纠察队布条，背景中是黑吉辽三省的钢铁浮雕地图。"
    },
    {
        "id": "EBS_placate_dongbei_normal",
        "name": "东北师范大学教研先锋动员",
        "branch": "BRANCH_E",
        "focal": "一本巨大的硬皮《高等数学与高考命题解析》，书脊上焊接着用角铁焊制的简易冲锋枪枪托，书本封面烫金印着东北师大的雄伟校门与一颗闪耀的红星。"
    },
    {
        "id": "EBS_furnace_night_study_battalions",
        "name": "高炉钢水旁的通宵做题突击营",
        "branch": "BRANCH_E",
        "focal": "一座奔涌着滚烫橙红色铁水的高炉出铁口，旁边简陋的木板桌上，几名年轻工人戴着焊工护目镜正在雪白的模拟卷上飞速演算，火星在头顶绚烂飞溅。"
    },
    {
        "id": "EBS_armored_exam_trains",
        "name": "满铁装甲押题列车",
        "branch": "BRANCH_E",
        "focal": "一列通体披挂双层铆接钢板的黑色装甲蒸汽火车，车头大灯如利剑般劈开呼啸的暴风雪，车头挂着‘绝密押运·绝不出错’的厚重铁制牌匾。"
    },
    {
        "id": "EBS_mukden_express_to_beijing",
        "name": "奉天特快进京：包围教育部",
        "branch": "BRANCH_E",
        "focal": "一根烧红的铁道转辙器手柄被重重扳向南方，背景中一条笔直伸向关内的双轨铁路线在寒夜中闪耀着金属寒光，数千支高举的钢笔在列车旁如林矗立。"
    },
    {
        "id": "EBS_worker_student_syndicate_councils",
        "name": "工学联合苏维埃代表会议",
        "branch": "BRANCH_E",
        "focal": "一枚红色的齿轮胸章，齿轮内圈镶嵌着一柄锋利的工业活动扳手与一支交叉的金尖蘸水钢笔，下方系着迎风飘扬的红色领巾。"
    },
    {
        "id": "EBS_dongbei_takes_over_moe",
        "name": "攻占西单教育部大楼",
        "branch": "BRANCH_E",
        "focal": "教育部大楼宏伟的灰色正门石阶上，两扇沉重的雕花实木大门被暴力撞开，一面巨大的工农学联红旗插上了门楣，红旗上印着巨大的金色圆规与铁锤。"
    },
    {
        "id": "EBS_incinerate_aristocratic_archives",
        "name": "焚毁海淀贵胄特权免试档案",
        "branch": "BRANCH_E",
        "focal": "一口巨大的铸铁焚化炉前，厚厚的贵族私立学校加分档案与免试保送生名册正在烈火中化为灰烬，翻飞的黑灰中露出一把烧红的拨火铁棍。"
    },
    {
        "id": "EBS_heavy_industry_exam_equality",
        "name": "重工做题家全国考纲大平权",
        "branch": "BRANCH_E",
        "focal": "一把巨大的工业重型锻压落锤重重砸下一张刻满特权分数线的青铜模具，将其彻底砸平为一张全国统一、分毫不差的水平钢板标尺。"
    },
    {
        "id": "EBS_absolute_meritocracy_republic",
        "name": "铁血唯分数平权共和国",
        "branch": "BRANCH_E",
        "focal": "一座由纯黑生铁铸造的崇高纪念碑，碑顶是一只展开铁翼的钢铁雄鹰，雄鹰怀中抱持着一张刻有‘唯分数论·不问门第’的钢铁大宪章。"
    },

    # --- EXAM & INDUSTRY (19) ---
    {
        "id": "EBS_seize_central_printing_press",
        "name": "接管全国统考试卷印刷总厂",
        "branch": "EXAM_INDUSTRY",
        "focal": "一座戒备森严的红砖印钞级工厂大门，门前拉起三道带刺铁丝网拒马，两名持枪保密卫兵驻守两侧，烟囱中吐出象征试卷正在印刷的滚滚黑烟。"
    },
    {
        "id": "EBS_rig_informatics_syllabus",
        "name": "垄断全国信息学奥赛考纲与保送",
        "branch": "EXAM_INDUSTRY",
        "focal": "一块刻满精细电路铜线的印刷电路板母盘，被放置在一个带有双锁保密盒内，中央一颗闪烁着红光的控制晶体管牢牢卡住数据总线接口。"
    },
    {
        "id": "EBS_suppress_southern_olympiad",
        "name": "铁腕取缔南方数学奥林匹克联赛",
        "branch": "EXAM_INDUSTRY",
        "focal": "一只戴着铆钉铁手套的军靴猛烈踩碎一块刻有‘南方奥数集训营’的镀银招牌，破碎的招牌旁散落着被折断的圆规与画满红叉的竞赛草稿纸。"
    },
    {
        "id": "EBS_manipulate_national_exam_board",
        "name": "全国高考命题院最高法统定位",
        "branch": "EXAM_INDUSTRY",
        "focal": "一枚雕刻精湛的八角形绝密命题院钢印，正上方是一枚微缩的国家教育徽章，下方交叉着两柄未开封的保密裁纸钢刀，周围环绕着厚重的密级铅封锁。"
    },
    {
        "id": "EBS_lock_ivory_tower_top3",
        "name": "焊死全国前三象牙塔招生大门",
        "branch": "EXAM_INDUSTRY",
        "focal": "三座象征最高学府的宏伟罗马拱门，拱门正前方被交叉焊接上了粗壮的工字型重型钢梁，电焊飞溅的耀眼火花正将两扇大门永久性封死焊牢。"
    },
    {
        "id": "EBS_industrial_backbone",
        "name": "国家统考重工业基石保障",
        "branch": "EXAM_INDUSTRY",
        "focal": "一座巨大的重工业厂区剪影前，三个巨大的啮合钢齿轮托起一本展开的全国教学计划大纲，齿轮轴心渗出润滑油，坚不可摧。"
    },
    {
        "id": "EBS_central_printing_industrialization",
        "name": "印卷厂百万级轮转印刷工业化",
        "branch": "EXAM_INDUSTRY",
        "focal": "一台庞大的双联立式报业轮转印刷机，滚筒飞速旋转，雪白崭新的试卷如瀑布般从出纸口倾泻而出，流水线旁是整齐码放的牛皮纸封装木箱。"
    },
    {
        "id": "EBS_beijing_tianjin_railway_artery",
        "name": "京津保密押运铁路线",
        "branch": "EXAM_INDUSTRY",
        "focal": "两根重型淬火钢轨笔直向前延伸穿透山川，中间由带有‘教育部专线’编号的混凝土轨枕支撑，一盏亮着绿光的铁路信号灯指引通往京津的道路。"
    },
    {
        "id": "EBS_northeast_rust_belt_integration",
        "name": "东北铁锈工业基地教育统筹",
        "branch": "EXAM_INDUSTRY",
        "focal": "一片森林般的工厂烟囱与起重机吊臂背景下，一幅带有红色网格的东北重工业规划图纸被一枚带有教育部大印的重型黄铜镇纸死死压在绘图桌上。"
    },
    {
        "id": "EBS_tianjin_bohai_chemical_refinery",
        "name": "天津渤海试卷特种纸与油墨化工厂",
        "branch": "EXAM_INDUSTRY",
        "focal": "三个银光闪闪的巨型化工反应釜与复杂的管道系统，管道下方龙头正流淌出浓黑发亮的高级防伪印卷油墨，注入漆有黄黑警戒线的铁桶中。"
    },
    {
        "id": "EBS_rehe_chahar_mineral_prospecting",
        "name": "热河察哈尔铅笔石墨与特种矿开采",
        "branch": "EXAM_INDUSTRY",
        "focal": "两支交叉的重型地质勘探地质镐，正砸开一块带有金属银灰光泽的天然高纯度石墨原矿石，矿石旁整齐排列着几支印着‘2B统考专用’的未削原木铅笔。"
    },
    {
        "id": "EBS_anshan_heavy_steel_foundry",
        "name": "鞍山重钢考场防暴铁栅栏铸造厂",
        "branch": "EXAM_INDUSTRY",
        "focal": "一扇刚刚从冷却水槽中吊起、表面还在散发白热蒸汽的重型带尖刺铸钢防暴铁栅栏，上方行车吊钩悬挂着铸造厂的钢铁标牌。"
    },
    {
        "id": "EBS_shenyang_arsenal_mobilization",
        "name": "沈阳造兵所防暴安检设备军工转产",
        "branch": "EXAM_INDUSTRY",
        "focal": "一条军工厂的兵工组装线上，工人们正在装配带有军工品质的步枪刺刀与手持金属探测安检仪，枪托旁陈列着印有军工红星的信号屏蔽设备箱。"
    },
    {
        "id": "EBS_harbin_locomotive_heavy_chassis",
        "name": "哈尔滨重型机车考场屏蔽车辆底盘",
        "branch": "EXAM_INDUSTRY",
        "focal": "一具巨大的六轴重型特种装甲车辆底盘，履带由坚实的碳钢铸造，底盘上方架设着带有旋转天线的电磁全频段压制干扰仪。"
    },
    {
        "id": "EBS_dalian_naval_dockyard_expansion",
        "name": "大连造船厂海上保密考务船坞",
        "branch": "EXAM_INDUSTRY",
        "focal": "一座巨大的干船坞内，一艘通体涂刷海军灰色迷彩的巨型特种船体正在建造，龙骨旁悬挂着‘海上全封闭命题保密基地’的白字横幅。"
    },
    {
        "id": "EBS_changchun_precision_instrument_works",
        "name": "长春光学与考务仪器仪表精工制造",
        "branch": "EXAM_INDUSTRY",
        "focal": "一台放在天鹅绒木盒里的高精度光学测微仪，透镜反射出紫绿色的多层镀膜光泽，精密调节手轮旁放着标有‘0.01毫米容差’的金属校准量块。"
    },
    {
        "id": "EBS_wartime_industrial_stockpile",
        "name": "国家高考战备工业原料战略储备",
        "branch": "EXAM_INDUSTRY",
        "focal": "一座深山洞库掩体内，整齐堆叠至库顶的原木纸浆纸卷、成箱铅笔与密封在木板箱里的军粮罐头，洞库大门是一道防核爆级别的铸铅钢铁重门。"
    },
    {
        "id": "EBS_national_defense_technical_polytechnic",
        "name": "国防七子特种军工工程技术学院",
        "branch": "EXAM_INDUSTRY",
        "focal": "一枚带有国防科技风格的盾形校徽，校徽中心是一枚翱翔的火箭弹与交叉的圆规，背景是一座带有风洞实验室与雷达天线的现代化学院主楼。"
    },
    {
        "id": "EBS_the_invincible_exam_industrial_complex",
        "name": "坚不可摧的国家应试军工复合体",
        "branch": "EXAM_INDUSTRY",
        "focal": "一尊由钢铁齿轮、高炉、试卷印刷滚筒与重炮炮膛熔铸结合而成的庞大工业巨兽图腾，昂首向天，巨兽胸口镶嵌着一枚闪耀金光的至高应试国徽。"
    },

    # --- WAR CLIMAX (9) ---
    {
        "id": "EBS_dispatch_final_syllabus_ultimatum",
        "name": "向全国各省发送统一考纲最后通牒",
        "branch": "WAR_CLIMAX",
        "focal": "一份被卷成卷轴的朱红色加急最后通牒文书，上面盖有教育部与统帅部联合火漆大印，文书斜插在一把入木三分的毛瑟军用匕首旁，匕首钉穿了一张泛黄的全国地图。"
    },
    {
        "id": "EBS_curb_southern_resistance",
        "name": "铁腕压制南方高校自主命题叛乱",
        "branch": "WAR_CLIMAX",
        "focal": "一只沉重的军用皮靴狠狠踩碎一册封面上印有‘南方诸大学自主命题联考大纲’的蓝色线装书，碎纸残页在风中零落，靴后是一列整齐荷枪实弹的宪兵队列。"
    },
    {
        "id": "EBS_coopt_provincial_collaborators",
        "name": "分化拉拢地方实力派与督学总会",
        "branch": "WAR_CLIMAX",
        "focal": "一张铺在作战室案头的军事地图上，两名将军样式的军官正用木质沙盘推杆将代表地方军阀的蓝色棋子推倒，换插上代表中央督察特派员的鲜红旗帜。"
    },
    {
        "id": "EBS_war_mobilization_1938",
        "name": "1938年战时全国高考总动员",
        "branch": "WAR_CLIMAX",
        "focal": "一尊巨大的青铜战时警钟被一根巨大的撞木猛烈撞击，钟身上浮雕着‘1938·全员应试’的醒目大字，滚滚音波震荡着天地，下方是无数荷枪步枪与背着书包的行军剪影。"
    },
    {
        "id": "EBS_pacify_shanhe_coalition",
        "name": "踏平山河四省高考大冤种互助同盟",
        "branch": "WAR_CLIMAX",
        "focal": "两支重型履带铁甲车正轰鸣着跨过一条干涸的黄河河床裂谷，履带后方将代表地方互助协议的脆弱木制界碑无情碾碎，远方山河轮廓笼罩在晨曦血色中。"
    },
    {
        "id": "EBS_subjugate_huazhong_hbe",
        "name": "平定华中黄冈黄梅应试同盟",
        "branch": "WAR_CLIMAX",
        "focal": "一座由万册密密麻麻的《黄冈密卷》搭建而成的坚固纸质堡垒，正被中央教育部重炮发射的高爆穿甲弹击中正中，漫天纸屑在浓烟与烈焰中四散炸裂。"
    },
    {
        "id": "EBS_strike_east_and_south",
        "name": "横扫江浙沪奥赛资本集团",
        "branch": "WAR_CLIMAX",
        "focal": "一把巨大的锋利战刀横空斩下，精准斩断一条串联着无数昂贵奥数金牌与汇票支票的金锁链，被斩断的链条化作金色碎片散落一地。"
    },
    {
        "id": "EBS_final_siege_of_yandao",
        "name": "最终围城：进逼盐道街中学大本营",
        "branch": "WAR_CLIMAX",
        "focal": "一门巨大的重型围城列车炮，炮口正严阵以待瞄准远方夜色中一座巍峨古朴、挂着‘盐道街’匾额的钟楼大门，无数道探照灯交织在城楼顶端，决战一触即发。"
    },
    {
        "id": "EBS_nationwide_educational_dominion",
        "name": "天下大一统：颁布统考至高圣旨",
        "branch": "WAR_CLIMAX",
        "focal": "展开的一卷金丝织锦、宽达三尺的国家至高教育一统圣旨，两端为雕花纯金玉轴，正中央盖着一枚巨大的‘奉天应试·受命永昌’方正传国玉玺朱红大印，万道金光破开云雾普照神州。"
    }
]

def build_full_locked_prompt(entry):
    """Assembles the immutable 3-tier locked prompt."""
    branch_key = entry["branch"]
    branch_info = BRANCH_MICRO_STYLES[branch_key]
    branch_lock = branch_info["lock"]
    
    full_prompt = (
        f"{NATIONAL_MACRO_STYLE_LOCK}\n\n"
        f"{branch_lock}\n\n"
        f"【国策核心专属图腾与隐喻构图】：国策名称《{entry['name']}》（ID: {entry['id']}）。{entry['focal']}"
    )
    return full_prompt

def export_prompt_books():
    """Exports structured JSON and Markdown prompt books for subagents/Banana/Gemini."""
    export_data = []
    for entry in EBS_FOCUS_REGISTRY:
        full_p = build_full_locked_prompt(entry)
        export_data.append({
            "id": entry["id"],
            "name": entry["name"],
            "branch": entry["branch"],
            "branch_name": BRANCH_MICRO_STYLES[entry["branch"]]["name"],
            "focal": entry["focal"],
            "locked_prompt": full_p
        })
        
    json_path = os.path.join(PROJECT_ROOT, "tools", "ebs_focus_prompts_unified.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Exported unified prompt book to {json_path} ({len(export_data)} focuses)")
    return json_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOI4 EBS Unified Focus Icon Pipeline with Immutable Macro & Micro Style Locks")
    parser.add_argument("--export", action="store_true", help="Export unified prompt books (JSON & Markdown)")
    parser.add_argument("--list", action="store_true", help="List all 82 focuses and their branches")
    parser.add_argument("--branch", type=str, default="", help="Filter by branch (e.g. PHASE_1, BRANCH_A, etc.)")
    args = parser.parse_args()

    if args.list:
        print("=" * 60)
        print("  EBS 82 National Focuses - Unified Style Registry")
        print("=" * 60)
        for i, item in enumerate(EBS_FOCUS_REGISTRY):
            bname = BRANCH_MICRO_STYLES[item["branch"]]["name"]
            if not args.branch or args.branch.upper() in item["branch"].upper():
                print(f"{i+1:2d}. [{item['branch']}] {item['id']} -> {item['name']}")
        sys.exit(0)

    # Default action: Export prompt book and verify
    export_prompt_books()
