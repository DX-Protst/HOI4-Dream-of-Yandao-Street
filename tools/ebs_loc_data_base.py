# -*- coding: utf-8 -*-
"""
EBS Localization Data: Base Systems
Parties, Bookmark, Characters, Traits, Ideas, Focus Titles & Descriptions, Decisions, Tooltips.
Branch E (东三省) content is strictly preserved from original!
"""

DATA_BASE = {
    # PARTIES
    "EBS_paternal_autocrat_party": "巡视督导总署",
    "EBS_paternal_autocrat_party_long": "教育部派驻最高教育巡视督导专员公署",
    "EBS_totalist_party": "铁血督察特使处",
    "EBS_totalist_party_long": "教育部最高铁腕督导特派行动署",
    "EBS_authoritarian_democrat_party": "赛博考务技术总署",
    "EBS_authoritarian_democrat_party_long": "国家教育数字化与AI天网监考总工程师公署",
    "EBS_social_conservative_party": "京津学阀建制派",
    "EBS_social_conservative_party_long": "京津大院特权与校董联合会",
    "EBS_social_liberal_party": "开放学术评议同盟",
    "EBS_social_liberal_party_long": "多元评价与顺义国际部教育同盟",
    "EBS_national_populist_party": "考霸体育达尔文军团",
    "EBS_national_populist_party_long": "全国校园体优加分与军事化考霸突击阵线",
    "EBS_market_liberal_party": "全国校园后勤商会",
    "EBS_market_liberal_party_long": "全国中小学统一营养配餐特许经营总会",
    "EBS_radical_socialist_party": "关外名校平权公社",
    "EBS_radical_socialist_party_long": "东北三省做题家平权与大纲重构总公社",
    "EBS_syndicalist_party": "关东重工做题总工会",
    "EBS_syndicalist_party_long": "东三省重型机械子弟与体训生做题联合工团",
    "EBS_social_democrat_party": "北方开明教研联合会",
    "EBS_social_democrat_party_long": "北方中小学特级教师民主维权公会",

    # 1936 BOOKMARK
    "EBS_GATHERING_STORM_DESC": (
        "坐落于北京大院深处的【最高教育局巡视督导专署】，是统治北方乃至全中国应试帝国的官僚巨兽。它手里死死攥着两件号令天下的权柄：全国统一高考试卷的绝密印厂，以及京津特区压倒全国的外省生源收割特权。\n\n"
        "表面上，督导总署由道貌岸然的陈专员执掌，张口闭口“四个回归、狠挤课堂水分”；而在总署厚重朱红大门的背后，怀总工的AI微表情天网、周总导的“五天刷绿操场”迎检狂潮、王司长的体育加分黑金与王总管的预制菜帝国，正在将应试教育变现为无穷无尽的官僚财富。\n\n"
        "然而，在这座应试堡垒的北方，极寒暴雪中的东三省考霸们已经在蒸汽锅炉前摔碎了茶缸。当权力的贪婪演变为绝对的掠夺，长春、哈尔滨与沈阳的名校已经在暗夜中发出灵魂诘问：“当年大帅能坐专列入关，这教育部龙椅，我们为何不能取而代之？！”"
    ),

    # CHARACTERS & BIOGRAPHIES
    "EBS_leader_chen_zhuanyuan": "陈专员",
    "EBS_leader_chen_zhuanyuan_desc": "最高教育督导专署总专员。常年身着笔挺深灰中山装，胸前佩戴金边校徽，大会发言张口闭口“四个回归、狠挤课堂水分”。曾主导“淘汰水课、打造样板金课”运动，表面上清廉威严，实则是京津大院子弟保送名单的幕后总庄家。他用精密的行政调令挤干了各省的招生名额，将直辖市一本录取率做成了不可撼动的铁壁铜墙。",
    "EBS_huai_zonggong": "怀总工",
    "EBS_huai_zonggong_desc": "国家教育数字化工程院院士、赛博考务总工程师。信奉绝对的理性与唯算力论。在他看来，传统的人工出题与做题早已落后于时代。他主张在全国所有考场架设全景高清微表情摄像头与脑电波生物手环，通过清华附中地下超算中心实时计算全国考生的“忠诚度与升学潜力”，用一行代码决定万千学子的命运。",
    "EBS_zhou_zongdao": "周总导",
    "EBS_zhou_zongdao_desc": "重点中学教学水平五年大评估行动特派司令，民间闻风丧胆的“洲际导弹”。毕生信奉“以评促建，形式也是生产力”。他的名号所到之处，校长们战栗失眠。他能在短短五天内逼得全国所有高中将枯泥操场刷成翠绿、在荒地上连夜插满麦苗伪造科学基地，并让百万师生通宵手抄十年假试卷与假教案，以格式的绝对完美掩盖教学的彻底停滞。",
    "EBS_wang_sichang": "王司长",
    "EBS_wang_sichang_desc": "全国校园球类与艺术特长统筹办公室主任。掌管数百亿专项体卫艺扶持基金，私设数十个秘密小金库。深谙“特长曲线救国”的暴利法则，将国家二级运动员证书与艺术统测免考名额全盘商业化。无论是买卖足球门框还是批发武术段位，每一分钱都在推高着他的体育加分商业帝国。",
    "EBS_wang_zongguan": "王总管",
    "EBS_wang_zongguan_desc": "全国校园宴饮与后勤总管。名言是“早上醒酒听汇报，中午陪餐过流水，晚上会所定调令”。独家垄断各大学区中小学统一配餐特许权，以廉价预制菜筑造了庞大的流动资金池。深谙官场应酬之道，善于用昂贵的宴席与特供教辅将地方督学牢牢捆绑在自己的利益链条上。",
    "EBS_dongbei_council": "东三省名校联合公社",
    "EBS_dongbei_council_desc": "由吉林长春东北师大附中、黑龙江哈尔滨三中、辽宁本溪高中与辽宁省实验中学联合组成的关外做题家最高权力机关。代表着黑土地上千万在零下三十度冰原中苦读的重工业做题学子。他们蔑视北京贵胄的温室骑马作秀，誓要挥师入关踏平教委大楼，夺回被窃取的高考命题权，让教育重归绝对平权！",
    "EBS_enlightened_teachers": "北方开明教研联合会",
    "EBS_enlightened_teachers_desc": "由北方各省数千名一线特级教师、学科带头人与教研员组成的民主自救组织。他们厌倦了高层官员形式主义的大迎检与假教案折腾，痛恨特权阶层对自招名额的瓜分，主张废除假大空评估、让教育回归课堂与育人本质。",
    "EBS_xi_teshi": "郗特使",
    "EBS_xi_teshi_desc": "边疆专项降分通道特派督导使。精通“跨省空挂学籍”大阵，善于利用援藏援疆政策漏洞，让嫡系子弟高中三年足不出京，高考却能在雪域高原享受两百分超低降分直通清北。",
    "EBS_haidian_council": "海淀贵胄委员会",
    "EBS_haidian_council_desc": "以海淀六小强校董与顺义大藤派家长组成的精英游说集团。垄断了自主招生与强基计划命题人席位，将马术、击剑、帆船与南极科考列为“综合素质必备项”，筑起平民学子永世无法逾越的素质壁垒。",

    # TRAITS
    "EBS_the_grand_commissioner": "挤水分的大督学",
    "EBS_the_grand_commissioner_desc": "“要把课堂里的水分彻底挤干！”——虽然挤掉的其实是普通省份的录取名额，但督导组的权威无人敢质疑。",
    "EBS_cybernetic_technocrat": "赛博考务总工程师",
    "EBS_cybernetic_technocrat_desc": "以算法与工程学重构考场，任何微小的作弊或发呆都逃不过人脸微表情算力的无情锁定。",
    "EBS_evaluation_maniac": "五天突击大迎检",
    "EBS_evaluation_maniac_desc": "“以评促建，重在建设！”——只要专家组进校时墙皮是绿的、麦苗是挺的、教案是全的，学校就是全国模范。",
    "EBS_football_czar": "校园足球特许状",
    "EBS_football_czar_desc": "绿茵场上踢的不是球，是数不尽的专项补贴与保送批文。",
    "EBS_plateau_skygate": "三年挂职直通车",
    "EBS_plateau_skygate_desc": "户籍在雪域高原，肉身在海淀六小强。分数线一降到底，寒门学子只能望洋兴叹。",
    "EBS_banquet_mastermind": "醒酒查课总调度",
    "EBS_banquet_mastermind_desc": "酒过三巡，调令自出；后勤流水，源源不断。",
    "EBS_haidian_aristocrat": "早培神话与素质霸权",
    "EBS_haidian_aristocrat_desc": "从幼儿园早培班直通名校，马术与冰球才是最高等级的做题家修养。",
    "EBS_dongbei_equality": "重工做题家平权意志",
    "EBS_dongbei_equality_desc": "黑土地冰雪中熔铸的钢铁意志。誓要打破一切大院特权与暗箱保送，让全国每一个孩子面对同一张试卷！",
    "EBS_enlightened_reform": "渐进理性教研之光",
    "EBS_enlightened_reform_desc": "摒弃形式主义假教案与官僚折腾，以一线师资的真才实学重构科学严谨的教学秩序。",

    # IDEAS / SPIRITS
    "EBS_privilege_iron_fist": "京津高考特权与铁腕巡视",
    "EBS_privilege_iron_fist_desc": "京津地区拥有全国最高的一本录取率与保送特权，红头文件所及之处万校肃立。",
    "EBS_northeast_undercurrent": "关外暗流：东三省之怨",
    "EBS_northeast_undercurrent_desc": "东三省被总署定位为廉价生源供给站与调剂大粮仓。漫天飞雪中，关外各校的怨气正在锅炉管道里剧烈发酵。",
    "EBS_chen_absolutism_spirit": "陈专员太上皇威权",
    "EBS_chen_absolutism_spirit_desc": "官僚总督学独揽大权，红头文件与行政调令凌驾于一切教学规律之上。",
    "EBS_cybernetic_dictatorship_spirit": "赛博算力专政矩阵",
    "EBS_cybernetic_dictatorship_spirit_desc": "清华附中算力天网全面接管全国考务，脑电波算法监控每一位考生的神经突触。",
    "EBS_lawn_greening_totalism_spirit": "全域大迎检与绿漆狂热",
    "EBS_lawn_greening_totalism_spirit_desc": "全国陷入连夜刷绿操场与插麦苗的狂暴整风中，一切生产与教学服务于专家组的视察路线。",
    "EBS_canteen_black_gold_spirit": "校园后勤黑金托拉斯",
    "EBS_canteen_black_gold_spirit_desc": "全国中小学校堂配餐被预制菜财阀垄断，巨额现金流水源源不断注入特许金库。",
    "EBS_dongbei_liberation_spirit": "关东重工做题家平权公社",
    "EBS_dongbei_liberation_spirit_desc": "打破大院垄断！东三省工农学联合执政，全国重工试卷君临天下！",
    "EBS_information_monopoly_spirit": "全国高考试卷院信息学霸权",
    "EBS_information_monopoly_spirit_desc": "清华附中算力中枢对全国信息学赛道施加绝对算力压迫，封锁一切外省选手的夺金通道。",
    "EBS_inspection_frenzy": "突击大迎检与材料造假",
    "EBS_inspection_frenzy_desc": "为了应付突击检查，全校师生停工停课连夜伪造假教案、给操场刷绿漆。表面光鲜亮丽，教学与生产实则停滞。",
    "EBS_cybernetic_exam_grid": "赛博考务天网",
    "EBS_cybernetic_exam_grid_desc": "全国统一的微表情人脸识别与神经监控矩阵。没有人能逃过天网的凝视。",
    "EBS_haidian_privilege": "海淀素质教育特权",
    "EBS_haidian_privilege_desc": "京津大院与海淀名校专属的自招加分渠道，固若金汤。",
    "EBS_dongbei_unrest_high": "关外躁动：为何不能取而代之",
    "EBS_dongbei_unrest_high_desc": "“当年奉系能入关，今天东三省考霸，难道就当不得这教育部的主人？！”关外各校暗中磨刀，准备挥师入关！",
    "EBS_bureau_total_control": "督导总署战时管制体制",
    "EBS_bureau_total_control_desc": "教育部全面军事化运作，考场即战场，准考证即动员令。",

    # NEW NATIONAL SPIRITS
    "EBS_imperial_examination_throne_spirit": "新应试帝国太上皇法典",
    "EBS_imperial_examination_throne_spirit_desc": "陈专员官僚家长制与京津大院特权的终极集权形态。红头调令与一票否决权化作神圣铁律，外省招生名额被制度化抽干，大院贵胄万世不易。",
    "EBS_silicon_curriculum_singularity_spirit": "硅基考务奇点专政",
    "EBS_silicon_curriculum_singularity_spirit_desc": "清华附中超算中心全面覆写传统教育体系。AI大模型自主推演极限试题，千万考生降格为算力节点，二进制代码决定终身社会分工。",
    "EBS_perpetual_inspection_mobilization_spirit": "永恒迎检全域战备大公社",
    "EBS_perpetual_inspection_mobilization_spirit_desc": "全国所有学校永久转入战备迎检状态。操场必须长保荧光绿，教案必须厚达三尺，形式主义的绝对规范成为压倒一切的军事战斗力！",
    "EBS_unrestricted_exam_market_spirit": "全国试卷期货交易财阀",
    "EBS_unrestricted_exam_market_spirit_desc": "教育资本化与特权商业化的极致产物。保送批文在阳光大厅竞价上市，预制菜现金流源源不断，金钱成为唯一的通关硬通货。",
    "EBS_absolute_meritocracy_republic_spirit": "关东铁血唯才平权共和国",
    "EBS_absolute_meritocracy_republic_spirit_desc": "黑土地冰雪淬火的重工做题家平权图腾。彻底踏碎京津大院垄断，焚毁自招保送档案，以红笔卷面分数为天下唯一裁决尺度！",
    "EBS_the_invincible_exam_industrial_complex_spirit": "应试重工产业复合体",
    "EBS_the_invincible_exam_industrial_complex_spirit_desc": "直隶中枢绝密印厂与东三省重工基地全面联通，印刷流水线、钢铁机车与兵工军械形成庞大的应试后勤战备网。",
}
