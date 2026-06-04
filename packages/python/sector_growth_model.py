from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from packages.python.data.real_collectors import load_market_data
from packages.python.strategies.resonance import build_theme_heat_map


MODEL_VERSION = "sector-growth-v0.2"

POLICY_SOURCES = [
    {
        "name": "2025 年政府工作报告重点任务",
        "url": "https://english.www.gov.cn/news/202503/05/content_WS67c7b134c6d0868f4e8f0591.html",
        "note": "提出推动商业航天、低空经济等新兴产业安全健康发展，培育生物制造、量子科技、具身智能、6G 等未来产业。",
    },
    {
        "name": "工信部等七部门《关于推动未来产业创新发展的实施意见》解读",
        "url": "https://www.miit.gov.cn/zwgk/zcjd/art/2024/art_668516c79842469eaacad07738bf6408.html",
        "note": "明确未来制造、未来信息、未来材料、未来能源、未来空间、未来健康等方向。",
    },
    {
        "name": "工信部等七部门《关于推动未来产业创新发展的实施意见》",
        "url": "https://wap.miit.gov.cn/jgsj/kjs/wjfb/art/2024/art_a9950c3b3cbe47b4b45519ce4a376687.html",
        "note": "列出人形机器人、量子计算机、脑机接口、6G、超大规模新型智算中心、先进高效航空装备等标志性产品。",
    },
    {
        "name": "工信部《人形机器人创新发展指导意见》解读",
        "url": "https://www.miit.gov.cn/zwgk/zcjd/art/2023/art_e3f5686c2f0d49f9968b7ae011d558e1.html",
        "note": "提出人形机器人到 2027 年产业加速规模化发展，应用场景更加丰富。",
    },
]


@dataclass(frozen=True)
class CompanyProfile:
    name: str
    symbol: str
    market: str
    role: str
    rationale: str
    exposure_score: float
    maturity_score: float
    risk_note: str


@dataclass(frozen=True)
class GrowthTrack:
    track_id: str
    sector: str
    segment: str
    horizon: str
    keywords: tuple[str, ...]
    policy_score: float
    demand_score: float
    tech_readiness_score: float
    ecosystem_score: float
    localization_score: float
    commercialization_score: float
    capital_efficiency_score: float
    risk_score: float
    growth_drivers: tuple[str, ...]
    risk_factors: tuple[str, ...]
    companies: tuple[CompanyProfile, ...]
    evidence_tags: tuple[str, ...]


@dataclass(frozen=True)
class EarlyAlphaTrack:
    track_id: str
    sector: str
    segment: str
    horizon: str
    keywords: tuple[str, ...]
    penetration_inflection_score: float
    inference_pull_score: float
    supply_bottleneck_score: float
    business_catalyst_score: float
    underowned_score: float
    ecosystem_score: float
    tech_readiness_score: float
    commercialization_score: float
    capital_efficiency_score: float
    risk_score: float
    maturity_penalty: float
    crowding_penalty: float
    accumulation_window: str
    trigger_events: tuple[str, ...]
    growth_drivers: tuple[str, ...]
    risk_factors: tuple[str, ...]
    companies: tuple[CompanyProfile, ...]
    evidence_tags: tuple[str, ...]


TRACK_UNIVERSE: tuple[GrowthTrack, ...] = (
    GrowthTrack(
        track_id="ai_infra",
        sector="AI 基础设施",
        segment="AI 算力、光模块、液冷、国产 AI 芯片",
        horizon="1-3 年",
        keywords=("人工智能", "AI", "算力", "光模块", "服务器", "液冷", "芯片", "智算"),
        policy_score=92,
        demand_score=95,
        tech_readiness_score=82,
        ecosystem_score=88,
        localization_score=90,
        commercialization_score=88,
        capital_efficiency_score=76,
        risk_score=58,
        growth_drivers=(
            "大模型训练和推理推动算力、互连、存储、散热持续扩容。",
            "国产算力和自主可控链条具备政策与产业双重牵引。",
            "云厂商、运营商、政企智算中心形成多层需求来源。",
        ),
        risk_factors=(
            "光模块和服务器链条有订单周期与价格下行风险。",
            "高端芯片受制于先进制程、HBM、EDA 和出口管制。",
            "短期估值容易受海外 AI 资本开支波动影响。",
        ),
        companies=(
            CompanyProfile("中际旭创", "300308", "A股", "高速光模块", "800G/1.6T 光模块弹性核心环节。", 92, 88, "外需和客户集中度较高。"),
            CompanyProfile("新易盛", "300502", "A股", "高速光模块", "海外 AI 集群光互连需求直接受益。", 90, 84, "订单节奏和毛利率波动较大。"),
            CompanyProfile("天孚通信", "300394", "A股", "光器件", "高速光模块上游精密光器件代表。", 86, 84, "受光模块景气传导影响。"),
            CompanyProfile("工业富联", "601138", "A股", "AI 服务器", "AI 服务器整机制造和云端硬件交付能力强。", 84, 86, "利润率受代工模式约束。"),
            CompanyProfile("浪潮信息", "000977", "A股", "AI 服务器", "国内服务器和智算基础设施代表。", 82, 82, "供应链与行业订单波动。"),
            CompanyProfile("寒武纪", "688256", "A股", "AI 芯片", "国产 AI 加速芯片稀缺标的。", 82, 62, "商业化和盈利验证压力高。"),
            CompanyProfile("海光信息", "688041", "A股", "国产 CPU/GPU", "国产高端处理器和服务器生态代表。", 78, 72, "技术迭代和生态适配仍需验证。"),
            CompanyProfile("中科曙光", "603019", "A股", "智算中心", "高性能计算、服务器和算力集成能力较完整。", 76, 80, "政府和行业项目节奏影响收入确认。"),
        ),
        evidence_tags=("人工智能+", "超大规模新型智算中心", "新型数字基础设施"),
    ),
    GrowthTrack(
        track_id="semiconductor_equipment",
        sector="半导体国产替代",
        segment="设备、材料、先进封装、Chiplet",
        horizon="2-5 年",
        keywords=("半导体", "集成电路", "芯片", "先进封装", "材料", "设备", "Chiplet"),
        policy_score=95,
        demand_score=88,
        tech_readiness_score=72,
        ecosystem_score=84,
        localization_score=96,
        commercialization_score=78,
        capital_efficiency_score=64,
        risk_score=66,
        growth_drivers=(
            "AI、汽车电子、工业控制提升高端芯片和先进封装需求。",
            "国产设备材料在成熟制程和部分关键工艺持续渗透。",
            "外部约束强化自主可控投入的持续性。",
        ),
        risk_factors=(
            "先进制程突破周期长，研发投入强度高。",
            "半导体资本开支有明显周期性。",
            "核心零部件和材料仍存在供应约束。",
        ),
        companies=(
            CompanyProfile("北方华创", "002371", "A股", "半导体设备", "刻蚀、薄膜、清洗等平台型设备龙头。", 92, 88, "估值与晶圆厂扩产周期相关。"),
            CompanyProfile("中微公司", "688012", "A股", "刻蚀/MOCVD", "刻蚀设备国产替代核心公司。", 90, 86, "先进工艺验证周期较长。"),
            CompanyProfile("拓荆科技", "688072", "A股", "薄膜设备", "PECVD/ALD 等薄膜设备代表。", 84, 78, "客户集中和产线验证影响节奏。"),
            CompanyProfile("华海清科", "688120", "A股", "CMP 设备", "CMP 设备国产化代表。", 82, 80, "设备订单受晶圆厂资本开支影响。"),
            CompanyProfile("长电科技", "600584", "A股", "先进封装", "先进封装和 Chiplet 产业链代表。", 80, 82, "封测景气和价格竞争影响盈利。"),
            CompanyProfile("通富微电", "002156", "A股", "先进封装", "CPU/GPU 封测和先进封装能力较强。", 78, 78, "海外大客户需求波动。"),
            CompanyProfile("江丰电子", "300666", "A股", "靶材", "半导体高纯溅射靶材国产化代表。", 76, 78, "材料认证周期长。"),
            CompanyProfile("沪硅产业", "688126", "A股", "硅片", "大硅片国产供应链代表。", 72, 70, "价格周期和盈利能力承压。"),
        ),
        evidence_tags=("集成电路", "产业基础再造", "自主可控"),
    ),
    GrowthTrack(
        track_id="embodied_ai_robotics",
        sector="具身智能",
        segment="人形机器人、执行器、传感器、控制系统",
        horizon="2-5 年",
        keywords=("机器人", "人形机器人", "具身智能", "伺服", "减速器", "传感器", "灵巧手"),
        policy_score=94,
        demand_score=86,
        tech_readiness_score=66,
        ecosystem_score=82,
        localization_score=84,
        commercialization_score=62,
        capital_efficiency_score=70,
        risk_score=70,
        growth_drivers=(
            "AI 大模型提升机器人感知、规划和交互能力。",
            "制造业、物流、特种作业和家庭服务构成长期场景。",
            "执行器、减速器、传感器等零部件先于整机放量。",
        ),
        risk_factors=(
            "整机量产成本、可靠性和应用 ROI 仍需验证。",
            "主题热度高，短期订单兑现可能低于预期。",
            "供应链标准和产品形态尚未完全稳定。",
        ),
        companies=(
            CompanyProfile("三花智控", "002050", "A股", "执行器/热管理", "机器人执行器与热管理潜在受益链条。", 84, 86, "机器人业务占比仍需跟踪。"),
            CompanyProfile("拓普集团", "601689", "A股", "执行器/结构件", "汽车零部件能力可迁移至机器人执行器。", 82, 84, "下游量产进度不确定。"),
            CompanyProfile("绿的谐波", "688017", "A股", "谐波减速器", "精密减速器是机器人核心部件。", 84, 74, "竞争加剧和价格压力。"),
            CompanyProfile("鸣志电器", "603728", "A股", "电机/控制", "控制电机和运动控制链条代表。", 78, 74, "订单弹性依赖整机放量。"),
            CompanyProfile("汇川技术", "300124", "A股", "工业自动化", "伺服、控制和工业自动化能力完整。", 76, 88, "机器人主题弹性弱于小市值部件股。"),
            CompanyProfile("埃斯顿", "002747", "A股", "工业机器人", "工业机器人整机和控制系统代表。", 74, 72, "盈利修复和海外竞争压力。"),
            CompanyProfile("柯力传感", "603662", "A股", "传感器", "力传感器在人形机器人中具备增量空间。", 72, 68, "机器人收入占比需验证。"),
            CompanyProfile("禾川科技", "688320", "A股", "运动控制", "伺服系统和运动控制部件供应商。", 70, 66, "规模和客户结构仍在成长。"),
        ),
        evidence_tags=("人形机器人", "具身智能", "智能终端"),
    ),
    GrowthTrack(
        track_id="low_altitude",
        sector="低空经济",
        segment="eVTOL、无人机、低空空管、运营服务",
        horizon="2-5 年",
        keywords=("低空经济", "无人机", "eVTOL", "航空", "空管", "通航", "飞行汽车"),
        policy_score=92,
        demand_score=82,
        tech_readiness_score=68,
        ecosystem_score=76,
        localization_score=78,
        commercialization_score=58,
        capital_efficiency_score=58,
        risk_score=72,
        growth_drivers=(
            "城市空中交通、应急、物流、巡检等场景逐步试点。",
            "政策推动空域、适航、基础设施和地方示范协同推进。",
            "空管系统、无人机整机和运营服务具备多环节机会。",
        ),
        risk_factors=(
            "空域管理、适航认证和安全责任决定商业化速度。",
            "eVTOL 规模化运营的单位经济性仍未完全证明。",
            "地方项目容易形成概念先行、订单后置。",
        ),
        companies=(
            CompanyProfile("中无人机", "688297", "A股", "无人机整机", "大型固定翼无人机平台代表。", 82, 74, "军民需求节奏波动。"),
            CompanyProfile("航天彩虹", "002389", "A股", "无人机", "无人机系统和特种应用代表。", 78, 72, "订单确认不确定。"),
            CompanyProfile("莱斯信息", "688631", "A股", "空管系统", "低空空管和指挥调度系统潜在关键环节。", 80, 74, "项目制交付影响收入节奏。"),
            CompanyProfile("四川九洲", "000801", "A股", "空管/北斗", "空管、导航和低空基础设施链条代表。", 76, 70, "业务结构复杂，主题纯度需拆分。"),
            CompanyProfile("万丰奥威", "002085", "A股", "通航/eVTOL", "通航和飞行汽车主题代表。", 78, 66, "主题波动和兑现节奏风险较高。"),
            CompanyProfile("中信海直", "000099", "A股", "通航运营", "通航运营和低空服务场景代表。", 74, 70, "运营利润率和需求密度待提升。"),
            CompanyProfile("纵横股份", "688070", "A股", "工业无人机", "工业无人机在巡检测绘等场景有应用基础。", 70, 62, "规模和盈利能力仍偏早期。"),
            CompanyProfile("宗申动力", "001696", "A股", "航空动力", "低空飞行器动力链条代表。", 68, 66, "低空相关收入占比需验证。"),
        ),
        evidence_tags=("低空经济", "先进高效航空装备", "新场景示范"),
    ),
    GrowthTrack(
        track_id="commercial_space",
        sector="商业航天",
        segment="卫星互联网、火箭配套、遥感导航、地面终端",
        horizon="2-5 年",
        keywords=("商业航天", "卫星", "北斗", "航天", "遥感", "导航", "地面站"),
        policy_score=90,
        demand_score=78,
        tech_readiness_score=70,
        ecosystem_score=80,
        localization_score=84,
        commercialization_score=60,
        capital_efficiency_score=56,
        risk_score=68,
        growth_drivers=(
            "卫星互联网、遥感、北斗应用和空天地一体通信带来长期需求。",
            "商业火箭发射和卫星批产有望打开制造端规模。",
            "国防、应急、交通、农业、海事等行业应用逐步扩展。",
        ),
        risk_factors=(
            "发射节奏、星座建设和订单确认周期长。",
            "多数公司项目制属性强，利润弹性不稳定。",
            "技术门槛高且部分需求受政策采购节奏影响。",
        ),
        companies=(
            CompanyProfile("中国卫星", "600118", "A股", "卫星制造/应用", "卫星制造和空间应用传统代表。", 82, 80, "央企属性强，利润弹性有限。"),
            CompanyProfile("航天电子", "600879", "A股", "航天电子配套", "航天电子设备和配套链条代表。", 78, 78, "业务分散，商业航天弹性需拆分。"),
            CompanyProfile("铖昌科技", "001270", "A股", "相控阵芯片", "卫星通信相控阵射频芯片代表。", 78, 68, "客户和产品集中度较高。"),
            CompanyProfile("上海沪工", "603131", "A股", "卫星部件", "卫星部组件和航天装备主题代表。", 72, 62, "主题波动较大。"),
            CompanyProfile("海格通信", "002465", "A股", "卫星通信/北斗", "无线通信、北斗和卫星通信应用链条。", 76, 76, "订单节奏影响短期表现。"),
            CompanyProfile("华测导航", "300627", "A股", "高精度定位", "北斗高精度定位应用代表。", 74, 82, "更多偏应用端，星座制造弹性较弱。"),
            CompanyProfile("航天环宇", "688523", "A股", "航天结构件", "航天产品配套和结构件代表。", 70, 64, "规模较小，项目波动。"),
            CompanyProfile("震有科技", "688418", "A股", "卫星核心网", "卫星互联网通信网络设备主题代表。", 70, 58, "盈利和订单兑现压力较高。"),
        ),
        evidence_tags=("商业航天", "未来空间", "6G 空天地一体"),
    ),
    GrowthTrack(
        track_id="solid_state_storage",
        sector="新型储能",
        segment="固态电池、大储、钠电、储能系统",
        horizon="1-4 年",
        keywords=("储能", "固态电池", "锂电", "钠电", "新能源", "电池"),
        policy_score=86,
        demand_score=90,
        tech_readiness_score=72,
        ecosystem_score=86,
        localization_score=88,
        commercialization_score=76,
        capital_efficiency_score=62,
        risk_score=64,
        growth_drivers=(
            "新能源并网、电力市场化和数据中心用电提升储能配置需求。",
            "固态电池有望改善安全性和能量密度，打开高端车和低空飞行器场景。",
            "中国电池材料、设备和系统集成产业链完整。",
        ),
        risk_factors=(
            "电池材料价格和产能周期影响盈利。",
            "固态电池路线仍有量产良率、成本和安全验证。",
            "大储价格竞争激烈，项目收益率承压。",
        ),
        companies=(
            CompanyProfile("宁德时代", "300750", "A股", "动力/储能电池", "全球电池龙头，储能和新技术平台能力强。", 90, 92, "体量大，主题弹性相对分散。"),
            CompanyProfile("亿纬锂能", "300014", "A股", "动力/储能电池", "动力、储能和消费电池业务覆盖广。", 82, 84, "产能和价格周期影响盈利。"),
            CompanyProfile("国轩高科", "002074", "A股", "动力/储能电池", "磷酸铁锂和储能链条代表。", 78, 74, "竞争和盈利修复压力。"),
            CompanyProfile("鹏辉能源", "300438", "A股", "储能电池", "储能电池弹性标的。", 76, 68, "价格竞争和客户结构风险。"),
            CompanyProfile("当升科技", "300073", "A股", "正极材料", "高镍和固态相关材料链条代表。", 74, 76, "材料价格周期影响利润。"),
            CompanyProfile("容百科技", "688005", "A股", "正极材料", "三元正极和新材料方向代表。", 72, 72, "产能和价格波动。"),
            CompanyProfile("先导智能", "300450", "A股", "锂电设备", "电池设备平台型供应商。", 74, 82, "设备订单受扩产周期影响。"),
            CompanyProfile("科达利", "002850", "A股", "电池结构件", "电池结构件龙头，受益电池出货增长。", 72, 84, "客户集中和价格压力。"),
        ),
        evidence_tags=("未来能源", "新型储能", "绿色低碳"),
    ),
    GrowthTrack(
        track_id="bio_manufacturing",
        sector="生物制造",
        segment="合成生物、发酵工程、生物基材料",
        horizon="3-5 年",
        keywords=("生物制造", "合成生物", "生物基", "发酵", "医药", "材料"),
        policy_score=88,
        demand_score=76,
        tech_readiness_score=66,
        ecosystem_score=72,
        localization_score=78,
        commercialization_score=58,
        capital_efficiency_score=66,
        risk_score=66,
        growth_drivers=(
            "生物法有望在化工、食品、医药和材料环节替代传统工艺。",
            "绿色低碳和供应链安全提升生物基材料战略价值。",
            "菌种设计、发酵放大和分离纯化构成核心壁垒。",
        ),
        risk_factors=(
            "从实验室到大规模发酵放大存在较高工艺风险。",
            "产品价格受传统化工路线和大宗商品影响。",
            "部分公司收入仍集中在少数产品。",
        ),
        companies=(
            CompanyProfile("华恒生物", "688639", "A股", "合成生物制造", "氨基酸和生物基产品产业化代表。", 82, 78, "产品价格和扩产节奏影响盈利。"),
            CompanyProfile("凯赛生物", "688065", "A股", "生物基材料", "长链二元酸和生物基聚酰胺代表。", 80, 76, "下游需求培育周期较长。"),
            CompanyProfile("川宁生物", "301301", "A股", "抗生素中间体/合成生物", "发酵产能和合成生物平台延展性。", 76, 74, "传统业务周期性仍存在。"),
            CompanyProfile("金丹科技", "300829", "A股", "乳酸/PLA", "乳酸和可降解材料链条代表。", 70, 68, "可降解需求和价格波动。"),
            CompanyProfile("嘉必优", "688089", "A股", "营养强化剂", "微生物发酵营养产品代表。", 68, 68, "市场空间和竞争格局需验证。"),
            CompanyProfile("华熙生物", "688363", "A股", "生物活性物", "透明质酸等生物活性物产业化代表。", 66, 76, "消费端需求波动。"),
        ),
        evidence_tags=("生物制造", "未来健康", "绿色制造"),
    ),
    GrowthTrack(
        track_id="innovative_medicine",
        sector="创新药与未来健康",
        segment="创新药、细胞基因治疗、AI 制药",
        horizon="2-5 年",
        keywords=("创新药", "生物医药", "细胞", "基因", "AI制药", "医疗"),
        policy_score=84,
        demand_score=88,
        tech_readiness_score=70,
        ecosystem_score=78,
        localization_score=72,
        commercialization_score=66,
        capital_efficiency_score=54,
        risk_score=74,
        growth_drivers=(
            "老龄化和支付结构升级支撑长期医疗需求。",
            "国产创新药出海和 license-out 提升行业天花板。",
            "AI 制药、细胞基因治疗推动研发范式变化。",
        ),
        risk_factors=(
            "研发失败、临床周期、医保控费和监管不确定性高。",
            "海外合规和地缘因素影响 CXO 与创新药出海。",
            "现金流和融资环境对早期公司影响明显。",
        ),
        companies=(
            CompanyProfile("恒瑞医药", "600276", "A股", "创新药平台", "国产创新药龙头，管线和商业化能力较强。", 84, 88, "创新药放量和集采压力并存。"),
            CompanyProfile("百济神州", "688235", "A股", "创新药平台", "全球化创新药平台代表。", 86, 78, "研发销售投入大，盈利节奏需跟踪。"),
            CompanyProfile("信达生物", "01801", "港股", "生物创新药", "肿瘤和慢病创新药代表。", 80, 76, "港股流动性和管线进度风险。"),
            CompanyProfile("康方生物", "09926", "港股", "双抗/创新药", "双抗平台和出海交易代表。", 80, 72, "临床和商业化不确定性较高。"),
            CompanyProfile("药明康德", "603259", "A股", "CXO/研发服务", "全球研发服务平台，受益创新药研发外包。", 74, 82, "海外政策和订单不确定。"),
            CompanyProfile("金斯瑞生物科技", "01548", "港股", "细胞治疗/生命科学", "细胞治疗和生命科学工具代表。", 72, 68, "亏损和产品放量风险。"),
            CompanyProfile("复星医药", "600196", "A股", "综合医药", "创新药、器械和医疗服务多元平台。", 68, 78, "业务复杂，主题纯度较低。"),
        ),
        evidence_tags=("未来健康", "生物制造", "AI 制药"),
    ),
    GrowthTrack(
        track_id="industrial_ai_software",
        sector="AI 应用与数据要素",
        segment="工业软件、办公 AI、数据资产、智能制造",
        horizon="1-3 年",
        keywords=("AI应用", "人工智能", "工业软件", "数据", "办公", "智能制造", "数字经济"),
        policy_score=88,
        demand_score=84,
        tech_readiness_score=78,
        ecosystem_score=80,
        localization_score=82,
        commercialization_score=72,
        capital_efficiency_score=78,
        risk_score=62,
        growth_drivers=(
            "AI 从基础模型转向办公、制造、研发、客服和行业流程。",
            "数据要素制度和国央企数字化提升软件本地化机会。",
            "工业软件和智能制造装备存在长期国产替代空间。",
        ),
        risk_factors=(
            "AI 应用付费率、降本增效 ROI 和渠道转化仍需验证。",
            "软件公司受企业 IT 预算周期影响。",
            "同质化大模型接入容易压低壁垒。",
        ),
        companies=(
            CompanyProfile("金山办公", "688111", "A股", "办公 AI", "办公软件和 AI 助手商业化代表。", 84, 88, "估值对 AI 付费转化敏感。"),
            CompanyProfile("科大讯飞", "002230", "A股", "AI 应用平台", "语音、教育、办公和行业 AI 应用代表。", 80, 78, "商业化效率和费用控制需验证。"),
            CompanyProfile("宝信软件", "600845", "A股", "工业软件/IDC", "钢铁信息化、工业软件和数据中心平台。", 76, 86, "行业资本开支影响增长。"),
            CompanyProfile("中控技术", "688777", "A股", "工业自动化软件", "流程工业控制系统和工业软件代表。", 78, 84, "制造业投资周期影响订单。"),
            CompanyProfile("用友网络", "600588", "A股", "企业软件", "企业管理软件和云服务代表。", 72, 74, "利润修复压力。"),
            CompanyProfile("中科创达", "300496", "A股", "端侧智能软件", "智能终端、汽车和边缘 AI 软件代表。", 72, 76, "汽车和 IoT 订单波动。"),
            CompanyProfile("润和软件", "300339", "A股", "开源鸿蒙/金融 IT", "国产软件生态和行业 IT 代表。", 68, 68, "主题弹性高但业绩验证压力大。"),
            CompanyProfile("广联达", "002410", "A股", "建筑软件", "建筑数字化和造价软件代表。", 66, 78, "地产链压力影响需求。"),
        ),
        evidence_tags=("人工智能+", "数据要素", "下一代操作系统"),
    ),
    GrowthTrack(
        track_id="six_g_network",
        sector="6G 与下一代通信",
        segment="空天地一体、卫星通信、光通信、核心网",
        horizon="3-6 年",
        keywords=("6G", "通信", "卫星通信", "光通信", "空天地", "核心网", "网络设备"),
        policy_score=86,
        demand_score=72,
        tech_readiness_score=52,
        ecosystem_score=76,
        localization_score=82,
        commercialization_score=45,
        capital_efficiency_score=58,
        risk_score=76,
        growth_drivers=(
            "6G 标准、空天地一体网络和卫星通信构成长期技术方向。",
            "运营商、设备商和光通信链条具备产业基础。",
            "车联网、工业互联网、低空经济对高可靠连接提出新需求。",
        ),
        risk_factors=(
            "6G 仍处于标准和技术验证期，商用周期较长。",
            "资本开支启动时间不确定。",
            "通信设备竞争和海外市场环境复杂。",
        ),
        companies=(
            CompanyProfile("中兴通讯", "000063", "A股", "通信设备", "通信主设备和核心网代表。", 80, 88, "运营商资本开支周期影响增长。"),
            CompanyProfile("中国移动", "600941", "A股", "运营商/算力", "运营商网络、算力和 6G 研发资源代表。", 72, 92, "成长弹性相对稳定但不高。"),
            CompanyProfile("亨通光电", "600487", "A股", "光通信/海缆", "光通信和通信基础设施链条。", 72, 78, "周期和价格竞争影响利润。"),
            CompanyProfile("烽火通信", "600498", "A股", "光网络设备", "光网络和通信设备代表。", 70, 76, "订单和毛利率波动。"),
            CompanyProfile("信科移动", "688387", "A股", "无线通信设备", "移动通信网络设备研发代表。", 68, 62, "盈利和商用节奏压力。"),
            CompanyProfile("海能达", "002583", "A股", "专网通信", "专网通信和应急通信应用代表。", 64, 66, "海外合规和竞争风险。"),
        ),
        evidence_tags=("6G网络设备", "空天地一体", "新型数字基础设施"),
    ),
    GrowthTrack(
        track_id="quantum_technology",
        sector="量子科技",
        segment="量子通信、量子计算、量子测量",
        horizon="4-8 年",
        keywords=("量子", "量子科技", "量子计算", "量子通信", "量子测量"),
        policy_score=90,
        demand_score=62,
        tech_readiness_score=40,
        ecosystem_score=62,
        localization_score=72,
        commercialization_score=34,
        capital_efficiency_score=44,
        risk_score=82,
        growth_drivers=(
            "量子信息是明确的未来产业方向，具备国家战略属性。",
            "量子通信和量子测量有较早应用，量子计算是更长周期期权。",
            "科研投入、标准和试点应用有望提升产业化基础。",
        ),
        risk_factors=(
            "多数方向仍处于科研和早期试点阶段。",
            "商业化路径长，收入规模和利润弹性不稳定。",
            "主题估值容易远领先于产业兑现。",
        ),
        companies=(
            CompanyProfile("国盾量子", "688027", "A股", "量子通信", "量子通信设备和系统代表。", 78, 58, "收入规模小，项目节奏波动。"),
            CompanyProfile("科大国创", "300520", "A股", "数据智能/量子生态", "科大系科技生态和数据智能代表。", 58, 62, "量子业务纯度较低。"),
            CompanyProfile("神州信息", "000555", "A股", "金融科技/量子安全", "金融 IT 与量子安全应用主题。", 54, 66, "量子相关收入占比需验证。"),
            CompanyProfile("光迅科技", "002281", "A股", "光器件", "光通信器件能力可延展至量子通信链条。", 54, 76, "量子主题非主业。"),
        ),
        evidence_tags=("量子科技", "量子计算机", "量子信息标准"),
    ),
    GrowthTrack(
        track_id="future_power_grid",
        sector="未来能源与智能电网",
        segment="虚拟电厂、特高压、源网荷储、氢能",
        horizon="1-5 年",
        keywords=("智能电网", "虚拟电厂", "特高压", "氢能", "电力", "储能", "新能源"),
        policy_score=84,
        demand_score=86,
        tech_readiness_score=76,
        ecosystem_score=84,
        localization_score=86,
        commercialization_score=74,
        capital_efficiency_score=70,
        risk_score=60,
        growth_drivers=(
            "新能源占比提升推动电网调度、储能和灵活性资源建设。",
            "电力设备更新、特高压和配网数字化具备确定性投资。",
            "虚拟电厂和源网荷储提升需求侧响应价值。",
        ),
        risk_factors=(
            "电网投资节奏和招标价格影响盈利。",
            "虚拟电厂商业模式和电力市场规则仍在完善。",
            "氢能经济性和补贴依赖度仍需观察。",
        ),
        companies=(
            CompanyProfile("国电南瑞", "600406", "A股", "电网自动化", "电网自动化和调度系统龙头。", 86, 90, "成长弹性相对稳健。"),
            CompanyProfile("阳光电源", "300274", "A股", "逆变器/储能系统", "新能源电力电子和储能系统代表。", 84, 88, "海外需求和价格竞争风险。"),
            CompanyProfile("南网科技", "688248", "A股", "储能/电网技术服务", "电网侧技术服务和储能应用代表。", 78, 72, "项目制收入波动。"),
            CompanyProfile("许继电气", "000400", "A股", "电力设备", "特高压、配网和电力装备代表。", 76, 82, "招标价格和交付周期影响利润。"),
            CompanyProfile("东方电气", "600875", "A股", "能源装备/氢能", "传统能源装备向风光氢储延展。", 72, 82, "传统业务周期影响估值。"),
            CompanyProfile("亿华通", "688339", "A股", "氢燃料电池", "燃料电池系统代表。", 66, 54, "氢能经济性和补贴依赖高。"),
            CompanyProfile("华光环能", "600475", "A股", "环保能源/氢能", "能源环保和氢能设备主题。", 62, 70, "氢能业务弹性需验证。"),
        ),
        evidence_tags=("未来能源", "源网荷储", "绿色低碳"),
    ),
)


EARLY_ALPHA_UNIVERSE: tuple[EarlyAlphaTrack, ...] = (
    EarlyAlphaTrack(
        track_id="edge_inference_ai_device",
        sector="端侧 AI 推理",
        segment="AI PC、AI 手机、端侧 Agent、低功耗 NPU/SoC",
        horizon="6-24 个月",
        keywords=("端侧AI", "AI PC", "AI手机", "NPU", "边缘AI", "SoC", "端侧推理", "智能终端"),
        penetration_inflection_score=92,
        inference_pull_score=90,
        supply_bottleneck_score=68,
        business_catalyst_score=84,
        underowned_score=78,
        ecosystem_score=76,
        tech_readiness_score=80,
        commercialization_score=72,
        capital_efficiency_score=82,
        risk_score=62,
        maturity_penalty=42,
        crowding_penalty=34,
        accumulation_window="AI PC/AI 手机换机周期启动前，优先跟踪端侧模型适配和出货指引。",
        trigger_events=(
            "Windows/Android 端侧 Agent 功能进入主流机型。",
            "NPU TOPS 成为消费电子新机型核心卖点。",
            "端侧小模型、RAG、本地隐私助手出现高频付费场景。",
        ),
        growth_drivers=(
            "推理从云端向个人设备下沉，低时延、隐私和成本成为关键变量。",
            "端侧模型压缩、量化和多模态交互改善，使本地 Agent 有商业化基础。",
            "换机周期一旦叠加 AI 功能，SoC、存储、声学、摄像头和端侧软件都可能重估。",
        ),
        risk_factors=(
            "端侧 AI 应用如果不能提升用户付费或换机意愿，硬件弹性会弱化。",
            "A 股公司多数是间接受益，需警惕 AI 纯度不足。",
            "消费电子需求本身仍有周期波动。",
        ),
        companies=(
            CompanyProfile("中科创达", "300496", "A股", "端侧智能软件", "端侧操作系统、智能终端和汽车软件可承接本地 AI Agent。", 82, 76, "汽车和 IoT 订单波动。"),
            CompanyProfile("虹软科技", "688088", "A股", "视觉 AI 软件", "端侧多模态和视觉算法有望受益 AI 手机/AI PC。", 78, 68, "商业化和终端出货需验证。"),
            CompanyProfile("全志科技", "300458", "A股", "边缘 SoC", "低功耗 SoC 可覆盖端侧智能硬件和边缘推理。", 76, 66, "产品 ASP 和竞争格局有压力。"),
            CompanyProfile("瑞芯微", "603893", "A股", "AIoT SoC", "AIoT 芯片和 NPU 能力适合边缘推理设备。", 78, 72, "消费和行业终端需求波动。"),
            CompanyProfile("恒玄科技", "688608", "A股", "智能音频芯片", "可穿戴和音频端侧 AI 交互入口。", 70, 72, "下游消费电子周期影响。"),
            CompanyProfile("乐鑫科技", "688018", "A股", "低功耗物联网芯片", "边缘联网节点和轻量 AI 推理潜在受益。", 68, 76, "AI 推理弹性仍需产品验证。"),
        ),
        evidence_tags=("端侧推理", "AI PC", "AI 手机", "本地 Agent"),
    ),
    EarlyAlphaTrack(
        track_id="private_inference_appliance",
        sector="企业私有化推理",
        segment="本地推理一体机、私有 Agent、行业模型部署",
        horizon="6-18 个月",
        keywords=("私有化", "一体机", "行业大模型", "AI服务器", "推理", "Agent", "信创"),
        penetration_inflection_score=88,
        inference_pull_score=92,
        supply_bottleneck_score=74,
        business_catalyst_score=86,
        underowned_score=72,
        ecosystem_score=82,
        tech_readiness_score=78,
        commercialization_score=76,
        capital_efficiency_score=70,
        risk_score=64,
        maturity_penalty=48,
        crowding_penalty=42,
        accumulation_window="央国企和金融、能源、制造业从 PoC 转向生产部署前。",
        trigger_events=(
            "企业从大模型试点进入预算化采购。",
            "国产算力+行业模型+私有知识库形成标准化交付包。",
            "推理成本下降，使中小企业本地部署 ROI 变得可算。",
        ),
        growth_drivers=(
            "企业数据安全和延迟要求决定大量推理不会完全放在公有云。",
            "行业模型、RAG 和工作流 Agent 需要本地知识库、权限、审计和持续运维。",
            "硬件一次性销售之外，软件订阅、运维和模型服务可能带来更高利润弹性。",
        ),
        risk_factors=(
            "企业 AI 从试点到规模部署的预算节奏可能慢于预期。",
            "硬件集成商利润率容易被竞争压缩。",
            "行业模型效果和数据治理决定复购率。",
        ),
        companies=(
            CompanyProfile("中科曙光", "603019", "A股", "智算/私有云", "高性能计算、智算中心和私有化交付能力完整。", 82, 80, "项目制交付影响节奏。"),
            CompanyProfile("紫光股份", "000938", "A股", "企业网络/私有云", "企业 IT、网络和私有云基础设施入口。", 78, 82, "硬件业务利润率弹性有限。"),
            CompanyProfile("浪潮信息", "000977", "A股", "AI 服务器", "服务器和行业算力交付基础强。", 78, 82, "供应链与订单波动。"),
            CompanyProfile("软通动力", "301236", "A股", "企业 AI 实施", "软件外包和行业数字化实施可切入企业 Agent 落地。", 72, 70, "人力服务属性影响利润弹性。"),
            CompanyProfile("拓尔思", "300229", "A股", "语义检索/行业 AI", "政企语义检索、知识图谱和行业大模型应用。", 74, 64, "订单兑现和产品化能力需验证。"),
            CompanyProfile("星环科技", "688031", "A股", "数据平台", "大数据平台和 AI 数据底座受益私有化推理部署。", 70, 58, "亏损和客户预算压力。"),
        ),
        evidence_tags=("私有化推理", "行业 Agent", "本地 AI 一体机", "RAG"),
    ),
    EarlyAlphaTrack(
        track_id="inference_memory_wall",
        sector="推理内存墙",
        segment="HBM、DDR5、存储模组、先进封装材料",
        horizon="12-30 个月",
        keywords=("HBM", "DDR5", "存储", "内存", "先进封装", "Chiplet", "封装材料", "推理"),
        penetration_inflection_score=86,
        inference_pull_score=94,
        supply_bottleneck_score=90,
        business_catalyst_score=78,
        underowned_score=62,
        ecosystem_score=76,
        tech_readiness_score=76,
        commercialization_score=74,
        capital_efficiency_score=66,
        risk_score=68,
        maturity_penalty=56,
        crowding_penalty=60,
        accumulation_window="存储价格回调或 HBM/DDR5 国产链条验证节点前。",
        trigger_events=(
            "长上下文、多 Agent 并发和 MoE 推理推高显存/内存带宽需求。",
            "HBM4、先进封装和高速互连进入新一轮供应链验证。",
            "国产 AI 芯片对高带宽内存和封装材料形成刚性配套需求。",
        ),
        growth_drivers=(
            "推理不只是算力问题，长上下文和高并发会持续卡在内存容量、带宽和封装互连。",
            "训练链条涨过之后，推理工作负载会把增量转向存储、封装和系统带宽。",
            "国产替代约束下，材料、模组、封测和配套设备有持续验证机会。",
        ),
        risk_factors=(
            "存储本身强周期，价格下行会压制估值。",
            "HBM 核心供应仍集中于海外龙头，A 股多为间接配套。",
            "若模型架构快速降内存需求，弹性会被削弱。",
        ),
        companies=(
            CompanyProfile("江波龙", "301308", "A股", "存储模组", "存储模组和企业级存储可受益 AI 终端与边缘推理。", 76, 72, "存储价格周期影响盈利。"),
            CompanyProfile("佰维存储", "688525", "A股", "存储模组", "存储产品组合覆盖嵌入式和企业级场景。", 74, 66, "价格和库存周期波动。"),
            CompanyProfile("香农芯创", "300475", "A股", "存储分销/模组", "高端存储供应链弹性标的。", 72, 62, "业务模式和价格波动风险较高。"),
            CompanyProfile("雅克科技", "002409", "A股", "半导体材料", "封装和存储相关材料链条代表。", 70, 76, "材料认证和需求周期影响。"),
            CompanyProfile("深科技", "000021", "A股", "存储封测/制造", "存储制造和封测配套能力。", 68, 72, "业务结构复杂，AI 纯度需拆分。"),
            CompanyProfile("通富微电", "002156", "A股", "先进封装", "先进封装可受益 AI 芯片推理量产。", 70, 78, "封测景气和客户需求波动。"),
        ),
        evidence_tags=("内存墙", "HBM", "长上下文推理", "先进封装"),
    ),
    EarlyAlphaTrack(
        track_id="inference_power_cooling",
        sector="推理电力与液冷",
        segment="高密度机柜、电源、液冷、微模块数据中心",
        horizon="6-24 个月",
        keywords=("液冷", "电源", "数据中心", "机柜", "温控", "IDC", "储能", "算力"),
        penetration_inflection_score=84,
        inference_pull_score=88,
        supply_bottleneck_score=88,
        business_catalyst_score=80,
        underowned_score=66,
        ecosystem_score=80,
        tech_readiness_score=84,
        commercialization_score=80,
        capital_efficiency_score=72,
        risk_score=58,
        maturity_penalty=52,
        crowding_penalty=52,
        accumulation_window="AI 机柜功耗密度继续上行、液冷从试点转标准配置前。",
        trigger_events=(
            "单机柜功耗提升推动冷板/浸没式液冷渗透。",
            "推理集群全天候运行带来电源效率、热管理和储能需求。",
            "云厂商和运营商智算中心从训练扩建转向推理运营。",
        ),
        growth_drivers=(
            "推理是持续运营负载，电费、散热和 PUE 会直接影响每 token 成本。",
            "高密度 AI 机柜提高液冷、电源、配电和储能系统价值量。",
            "相比 GPU，电力温控链条可能有更长订单尾部和更低技术替代风险。",
        ),
        risk_factors=(
            "液冷价格竞争和客户议价会影响利润率。",
            "数据中心资本开支若放缓，订单节奏会后移。",
            "部分公司 AI 相关收入占比仍需验证。",
        ),
        companies=(
            CompanyProfile("英维克", "002837", "A股", "数据中心温控", "机房温控和液冷链条代表。", 82, 82, "液冷竞争和价格压力。"),
            CompanyProfile("申菱环境", "301018", "A股", "温控/液冷", "数据中心和工业温控设备供应商。", 78, 72, "项目制订单波动。"),
            CompanyProfile("科华数据", "002335", "A股", "UPS/数据中心", "电源、IDC 和微模块基础设施。", 76, 78, "IDC 业务利润率和资本开支压力。"),
            CompanyProfile("科士达", "002518", "A股", "UPS/电源", "UPS、电源和数据中心配套代表。", 72, 76, "新能源业务波动影响估值。"),
            CompanyProfile("佳力图", "603912", "A股", "机房空调", "数据中心温控和机房空调弹性标的。", 68, 64, "规模和订单稳定性较弱。"),
            CompanyProfile("依米康", "300249", "A股", "数据中心温控", "机房温控和工程服务主题。", 64, 58, "盈利波动和主题弹性风险高。"),
        ),
        evidence_tags=("推理能耗", "液冷", "高密度机柜", "每 token 成本"),
    ),
    EarlyAlphaTrack(
        track_id="rag_data_infra",
        sector="RAG 与数据底座",
        segment="向量检索、知识图谱、数据治理、语料资产",
        horizon="6-18 个月",
        keywords=("RAG", "向量", "知识图谱", "数据治理", "语料", "数据要素", "大模型"),
        penetration_inflection_score=90,
        inference_pull_score=86,
        supply_bottleneck_score=76,
        business_catalyst_score=84,
        underowned_score=82,
        ecosystem_score=70,
        tech_readiness_score=74,
        commercialization_score=70,
        capital_efficiency_score=86,
        risk_score=66,
        maturity_penalty=38,
        crowding_penalty=30,
        accumulation_window="企业大模型从问答 Demo 转向业务系统接入前，数据治理订单先行。",
        trigger_events=(
            "RAG 成为企业 Agent 标配，知识库建设从一次性项目转为持续运营。",
            "数据要素、数据授权和行业语料资产形成可计费产品。",
            "模型效果瓶颈从参数规模转向数据质量、权限和检索准确率。",
        ),
        growth_drivers=(
            "企业推理真正落地，需要私有知识、权限、审计和检索增强。",
            "数据治理和知识库建设资本开支低于硬件，但可能带来高毛利软件收入。",
            "A 股市场对 GPU 更敏感，对数据底座和 RAG 中间层的定价仍不充分。",
        ),
        risk_factors=(
            "项目型软件公司产品化能力差异大。",
            "开源工具会压低通用向量数据库和中间件壁垒。",
            "客户数据质量差会拖慢交付和复购。",
        ),
        companies=(
            CompanyProfile("拓尔思", "300229", "A股", "语义检索/知识图谱", "政企语义检索、知识图谱和行业语料经验。", 82, 64, "订单兑现和产品化能力需验证。"),
            CompanyProfile("星环科技", "688031", "A股", "大数据平台", "数据平台、湖仓和分析底座适配企业 AI。", 76, 58, "亏损和销售周期压力。"),
            CompanyProfile("海天瑞声", "688787", "A股", "训练/评测数据", "语料、数据标注和模型评测可延展到推理质量运营。", 74, 56, "收入规模和订单稳定性较弱。"),
            CompanyProfile("每日互动", "300766", "A股", "数据智能", "数据智能和行业数据服务潜在受益数据要素。", 68, 62, "数据合规和商业化压力。"),
            CompanyProfile("云赛智联", "600602", "A股", "数据中心/数据服务", "地方数据与算力基础设施结合度较高。", 66, 62, "主题纯度和盈利弹性需验证。"),
            CompanyProfile("东方国信", "300166", "A股", "数据治理/行业软件", "运营商和工业数据治理基础。", 64, 62, "利润修复和客户预算约束。"),
        ),
        evidence_tags=("RAG", "数据治理", "知识图谱", "数据要素"),
    ),
    EarlyAlphaTrack(
        track_id="ai_security_governance",
        sector="推理安全与治理",
        segment="模型安全、隐私计算、内容审计、AI 网关",
        horizon="12-30 个月",
        keywords=("AI安全", "模型安全", "隐私计算", "数据安全", "网关", "审计", "内容安全"),
        penetration_inflection_score=82,
        inference_pull_score=80,
        supply_bottleneck_score=78,
        business_catalyst_score=82,
        underowned_score=88,
        ecosystem_score=70,
        tech_readiness_score=68,
        commercialization_score=62,
        capital_efficiency_score=82,
        risk_score=62,
        maturity_penalty=34,
        crowding_penalty=24,
        accumulation_window="企业推理接入生产系统、监管开始要求模型审计和数据安全前。",
        trigger_events=(
            "企业 Agent 获得业务系统权限后，AI 网关、审计和权限控制需求上升。",
            "模型输出合规、提示词攻击、数据泄漏成为采购项。",
            "隐私计算和可信执行环境用于行业模型推理。",
        ),
        growth_drivers=(
            "推理越接近真实业务，安全和治理就越从可选项变成刚需。",
            "AI 安全目前市场拥挤度低，容易在监管或事故催化下重估。",
            "安全产品具备订阅和续费属性，资本效率优于重资产硬件。",
        ),
        risk_factors=(
            "AI 安全预算可能滞后于大模型应用预算。",
            "产品标准尚未统一，客户采购口径不稳定。",
            "部分安全公司增长已放缓，需要确认新产品贡献。",
        ),
        companies=(
            CompanyProfile("深信服", "300454", "A股", "安全/私有云", "安全、云和企业 IT 入口利于承接 AI 安全网关。", 74, 78, "传统安全增长修复仍需确认。"),
            CompanyProfile("启明星辰", "002439", "A股", "网络安全", "央国企安全客户基础和数据安全产品线。", 72, 76, "行业预算恢复节奏不确定。"),
            CompanyProfile("安恒信息", "688023", "A股", "数据安全", "数据安全和云安全产品可延展到模型治理。", 72, 62, "盈利压力较高。"),
            CompanyProfile("奇安信", "688561", "A股", "网络安全平台", "政企安全平台和终端安全基础。", 70, 64, "亏损和费用压力。"),
            CompanyProfile("三未信安", "688489", "A股", "密码/隐私计算", "密码和隐私计算适配可信推理场景。", 68, 62, "规模较小，订单波动。"),
            CompanyProfile("电科网安", "002268", "A股", "密码安全", "密码安全和政企安全链条代表。", 66, 70, "成长弹性需新场景验证。"),
        ),
        evidence_tags=("AI 安全", "模型治理", "隐私推理", "AI 网关"),
    ),
    EarlyAlphaTrack(
        track_id="physical_ai_edge_inference",
        sector="物理 AI 边缘推理",
        segment="机器视觉、空间感知、机器人边缘控制",
        horizon="12-36 个月",
        keywords=("物理AI", "机器视觉", "空间智能", "边缘推理", "传感器", "机器人", "多模态"),
        penetration_inflection_score=84,
        inference_pull_score=82,
        supply_bottleneck_score=74,
        business_catalyst_score=78,
        underowned_score=78,
        ecosystem_score=74,
        tech_readiness_score=72,
        commercialization_score=66,
        capital_efficiency_score=70,
        risk_score=70,
        maturity_penalty=44,
        crowding_penalty=38,
        accumulation_window="机器人整机订单未放量前，先看视觉/传感/边缘控制进入样机验证。",
        trigger_events=(
            "具身智能从语言控制转向视觉、空间和触觉多模态推理。",
            "工业检测、仓储、安防和机器人在边缘端部署小模型。",
            "3D 视觉、力传感和边缘控制器进入更多整机方案。",
        ),
        growth_drivers=(
            "物理世界应用需要低时延推理，边缘设备和传感器价值量提升。",
            "机器人爆发前，感知和控制部件可能先出现订单和设计定点。",
            "多模态推理将机器视觉从检测工具升级为现场智能入口。",
        ),
        risk_factors=(
            "机器人和工业 AI 量产节奏仍有不确定性。",
            "硬件价格竞争可能压低毛利。",
            "客户验证周期长，收入确认可能滞后。",
        ),
        companies=(
            CompanyProfile("奥比中光", "688322", "A股", "3D 视觉", "3D 视觉传感器适配机器人和空间智能。", 78, 58, "盈利和放量节奏需验证。"),
            CompanyProfile("凌云光", "688400", "A股", "机器视觉", "工业机器视觉和视觉算法平台。", 72, 66, "工业投资周期影响订单。"),
            CompanyProfile("海康威视", "002415", "A股", "视觉 AI/边缘设备", "视觉硬件、边缘 AI 和行业渠道基础强。", 70, 88, "体量大，主题弹性相对有限。"),
            CompanyProfile("大华股份", "002236", "A股", "视觉 AI/边缘设备", "视觉设备和边缘智能应用覆盖广。", 68, 82, "传统安防业务周期影响。"),
            CompanyProfile("柯力传感", "603662", "A股", "力传感器", "力传感器适配机器人触觉和工业控制。", 70, 68, "机器人收入占比需验证。"),
            CompanyProfile("汇川技术", "300124", "A股", "运动控制", "运动控制和伺服系统是物理 AI 执行层基础。", 68, 88, "大市值导致主题弹性较弱。"),
        ),
        evidence_tags=("物理 AI", "边缘推理", "机器视觉", "空间智能"),
    ),
    EarlyAlphaTrack(
        track_id="silicon_photonics_cpo_second_line",
        sector="推理互连二线",
        segment="CPO、硅光、LPO、板级互连与光器件",
        horizon="12-30 个月",
        keywords=("CPO", "硅光", "LPO", "光模块", "光器件", "互连", "交换机", "推理"),
        penetration_inflection_score=82,
        inference_pull_score=90,
        supply_bottleneck_score=86,
        business_catalyst_score=78,
        underowned_score=58,
        ecosystem_score=78,
        tech_readiness_score=70,
        commercialization_score=66,
        capital_efficiency_score=66,
        risk_score=72,
        maturity_penalty=64,
        crowding_penalty=74,
        accumulation_window="一线光模块拥挤后，等待 CPO/硅光订单验证向二线器件扩散。",
        trigger_events=(
            "推理集群东西向流量提升，800G/1.6T 之后继续向 CPO/硅光演进。",
            "交换芯片、光引擎和板级互连成为机柜级瓶颈。",
            "一线光模块估值拥挤后，资金寻找未充分定价的上游器件。",
        ),
        growth_drivers=(
            "多 Agent 和 MoE 推理需要更强机柜内、机柜间通信。",
            "CPO/硅光若进入量产验证，上游光器件和二线供应商弹性可能超过成熟龙头。",
            "互连是推理每 token 成本下降的重要路径。",
        ),
        risk_factors=(
            "CPO 商业化节奏存在技术和客户路线不确定。",
            "光通信链条已经较拥挤，短线波动大。",
            "二线公司客户导入失败会导致预期落空。",
        ),
        companies=(
            CompanyProfile("光迅科技", "002281", "A股", "光器件/硅光", "光器件平台和硅光方向代表。", 76, 76, "弹性受产品结构影响。"),
            CompanyProfile("源杰科技", "688498", "A股", "激光器芯片", "高速光模块上游激光器芯片。", 76, 62, "客户导入和价格压力。"),
            CompanyProfile("仕佳光子", "688313", "A股", "光芯片", "PLC 分路器、AWG 和光芯片方向。", 70, 60, "规模较小，订单波动。"),
            CompanyProfile("联特科技", "301205", "A股", "光模块", "高速光模块二线弹性标的。", 72, 60, "竞争和客户集中风险。"),
            CompanyProfile("太辰光", "300570", "A股", "光器件", "光连接和器件链条代表。", 68, 66, "景气传导和产品升级需验证。"),
            CompanyProfile("剑桥科技", "603083", "A股", "光模块/通信设备", "光通信设备和模块主题弹性。", 66, 64, "订单和毛利波动较大。"),
        ),
        evidence_tags=("CPO", "硅光", "推理互连", "机柜级网络"),
    ),
)


def forecast_sector_growth(
    limit: int = 12,
    include_market_heat: bool = True,
    market_limit: int = 120,
    mode: str = "early_alpha",
) -> dict[str, Any]:
    stocks = []
    market_meta: dict[str, str] = {"source": "disabled", "trade_date": str(date.today())}
    theme_heat: dict[str, dict[str, float | int | bool]] = {}
    if include_market_heat:
        stocks, market_meta = load_market_data(limit=market_limit)
        theme_heat = build_theme_heat_map(stocks)

    normalized_mode = mode if mode in {"early_alpha", "structural"} else "early_alpha"
    if normalized_mode == "structural":
        ranked = [
            _score_track(track, stocks=stocks, theme_heat=theme_heat, include_market_heat=include_market_heat)
            for track in TRACK_UNIVERSE
        ]
        ranked = sorted(ranked, key=lambda item: item["growth_score"], reverse=True)
        methodology = _structural_methodology()
    else:
        ranked = [
            _score_early_alpha_track(track, stocks=stocks, theme_heat=theme_heat, include_market_heat=include_market_heat)
            for track in EARLY_ALPHA_UNIVERSE
        ]
        ranked = sorted(ranked, key=lambda item: item["early_alpha_score"], reverse=True)
        methodology = _early_alpha_methodology()

    return {
        "model_version": MODEL_VERSION,
        "mode": normalized_mode,
        "score_label": "埋伏分" if normalized_mode == "early_alpha" else "增长分",
        "trade_date": market_meta.get("trade_date") or str(date.today()),
        "source_meta": {
            "market_source": market_meta.get("source"),
            "market_heat_enabled": include_market_heat,
            "policy_sources": POLICY_SOURCES,
        },
        "methodology": methodology,
        "items": ranked[: max(1, min(limit, len(ranked)))],
    }


def _score_track(
    track: GrowthTrack,
    stocks: list[Any],
    theme_heat: dict[str, dict[str, float | int | bool]],
    include_market_heat: bool,
) -> dict[str, Any]:
    heat_payload = _market_heat_score(track, stocks, theme_heat) if include_market_heat else {
        "score": 50.0,
        "matched_symbols": [],
        "matched_themes": [],
    }
    market_heat = float(heat_payload["score"])
    structural_score = (
        track.policy_score * 0.18
        + track.demand_score * 0.18
        + track.ecosystem_score * 0.14
        + track.tech_readiness_score * 0.12
        + track.localization_score * 0.12
        + track.commercialization_score * 0.12
        + track.capital_efficiency_score * 0.08
        + market_heat * 0.10
        - track.risk_score * 0.14
        + 7
    )
    growth_score = round(max(0.0, min(100.0, structural_score)), 1)
    confidence_score = round(
        max(
            0.0,
            min(
                100.0,
                track.policy_score * 0.30
                + track.ecosystem_score * 0.22
                + track.commercialization_score * 0.22
                + track.tech_readiness_score * 0.14
                + (100 - track.risk_score) * 0.12,
            ),
        ),
        1,
    )
    companies = _score_companies(track, growth_score, stocks)
    return {
        "track_id": track.track_id,
        "sector": track.sector,
        "segment": track.segment,
        "horizon": track.horizon,
        "growth_score": growth_score,
        "confidence_score": confidence_score,
        "confidence_level": _confidence_level(confidence_score),
        "stage": _stage_label(track),
        "market_heat_score": round(market_heat, 1),
        "matched_market_themes": heat_payload["matched_themes"],
        "matched_market_symbols": heat_payload["matched_symbols"],
        "factor_scores": {
            "policy": track.policy_score,
            "demand": track.demand_score,
            "tech_readiness": track.tech_readiness_score,
            "ecosystem": track.ecosystem_score,
            "localization": track.localization_score,
            "commercialization": track.commercialization_score,
            "capital_efficiency": track.capital_efficiency_score,
            "risk": track.risk_score,
        },
        "growth_drivers": list(track.growth_drivers),
        "risk_factors": list(track.risk_factors),
        "evidence_tags": list(track.evidence_tags),
        "typical_companies": companies,
        "research_note": _research_note(track, growth_score, confidence_score),
    }


def _score_early_alpha_track(
    track: EarlyAlphaTrack,
    stocks: list[Any],
    theme_heat: dict[str, dict[str, float | int | bool]],
    include_market_heat: bool,
) -> dict[str, Any]:
    heat_payload = _market_heat_score(track, stocks, theme_heat) if include_market_heat else {
        "score": 50.0,
        "matched_symbols": [],
        "matched_themes": [],
    }
    market_heat = float(heat_payload["score"])
    low_crowding_bonus = max(0.0, 100.0 - market_heat) * 0.12
    raw_score = (
        track.penetration_inflection_score * 0.18
        + track.inference_pull_score * 0.18
        + track.business_catalyst_score * 0.14
        + track.supply_bottleneck_score * 0.12
        + track.underowned_score * 0.12
        + track.ecosystem_score * 0.08
        + track.tech_readiness_score * 0.08
        + track.commercialization_score * 0.07
        + track.capital_efficiency_score * 0.07
        + low_crowding_bonus
        - track.risk_score * 0.12
        - track.maturity_penalty * 0.09
        - track.crowding_penalty * 0.08
        + 11
    )
    early_alpha_score = round(max(0.0, min(100.0, raw_score)), 1)
    confidence_score = round(
        max(
            0.0,
            min(
                100.0,
                track.tech_readiness_score * 0.24
                + track.commercialization_score * 0.22
                + track.ecosystem_score * 0.18
                + track.business_catalyst_score * 0.18
                + (100 - track.risk_score) * 0.18,
            ),
        ),
        1,
    )
    companies = _score_companies_for_early_alpha(track, early_alpha_score, stocks)
    return {
        "track_id": track.track_id,
        "sector": track.sector,
        "segment": track.segment,
        "horizon": track.horizon,
        "growth_score": early_alpha_score,
        "early_alpha_score": early_alpha_score,
        "confidence_score": confidence_score,
        "confidence_level": _confidence_level(confidence_score),
        "stage": _early_alpha_stage_label(track),
        "market_heat_score": round(market_heat, 1),
        "underowned_score": track.underowned_score,
        "maturity_penalty": track.maturity_penalty,
        "crowding_penalty": track.crowding_penalty,
        "accumulation_window": track.accumulation_window,
        "trigger_events": list(track.trigger_events),
        "matched_market_themes": heat_payload["matched_themes"],
        "matched_market_symbols": heat_payload["matched_symbols"],
        "factor_scores": {
            "penetration_inflection": track.penetration_inflection_score,
            "inference_pull": track.inference_pull_score,
            "supply_bottleneck": track.supply_bottleneck_score,
            "business_catalyst": track.business_catalyst_score,
            "underowned": track.underowned_score,
            "ecosystem": track.ecosystem_score,
            "tech_readiness": track.tech_readiness_score,
            "commercialization": track.commercialization_score,
            "capital_efficiency": track.capital_efficiency_score,
            "risk": track.risk_score,
        },
        "growth_drivers": list(track.growth_drivers),
        "risk_factors": list(track.risk_factors),
        "evidence_tags": list(track.evidence_tags),
        "typical_companies": companies,
        "research_note": _early_alpha_research_note(track, early_alpha_score, confidence_score),
    }


def _market_heat_score(
    track: GrowthTrack,
    stocks: list[Any],
    theme_heat: dict[str, dict[str, float | int | bool]],
) -> dict[str, Any]:
    matched_symbols: list[dict[str, Any]] = []
    matched_themes: list[dict[str, Any]] = []
    keyword_set = tuple(k.lower() for k in track.keywords)

    for theme, item in theme_heat.items():
        haystack = theme.lower()
        if any(keyword in haystack or haystack in keyword for keyword in keyword_set):
            matched_themes.append(
                {
                    "theme": theme,
                    "rank": item.get("rank"),
                    "heat_score": item.get("heat_score"),
                    "is_mainline": item.get("is_mainline"),
                }
            )

    raw_score = 0.0
    for stock in stocks:
        haystack = " ".join(
            [
                str(getattr(stock, "name", "")),
                str(getattr(stock, "symbol", "")),
                str(getattr(stock, "theme", "")),
                str(getattr(stock, "secondary_theme", "")),
                " ".join(getattr(stock, "concepts", []) or []),
            ]
        ).lower()
        if not any(keyword in haystack for keyword in keyword_set):
            continue
        pct_change = float(getattr(stock, "pct_change", 0.0) or 0.0)
        volume_ratio = float(getattr(stock, "volume_ratio", 1.0) or 1.0)
        item_score = max(pct_change, 0.0) * 1.6 + min(volume_ratio * 4, 14)
        if bool(getattr(stock, "is_limit_up", False)):
            item_score += 8
        raw_score += item_score
        if len(matched_symbols) < 8:
            matched_symbols.append(
                {
                    "symbol": getattr(stock, "symbol", ""),
                    "name": getattr(stock, "name", ""),
                    "theme": getattr(stock, "theme", ""),
                    "pct_change": round(pct_change, 2),
                    "volume_ratio": round(volume_ratio, 2),
                }
            )

    theme_bonus = sum(float(item.get("heat_score") or 0.0) for item in matched_themes[:4])
    score = min(100.0, 35.0 + raw_score * 0.55 + theme_bonus * 1.8)
    if not matched_symbols and not matched_themes:
        score = 45.0
    return {
        "score": round(score, 1),
        "matched_symbols": matched_symbols,
        "matched_themes": matched_themes[:6],
    }


def _score_companies(track: GrowthTrack, growth_score: float, stocks: list[Any]) -> list[dict[str, Any]]:
    live_lookup = {
        str(getattr(stock, "symbol", "")): stock
        for stock in stocks
        if getattr(stock, "symbol", "")
    }
    rows: list[dict[str, Any]] = []
    for company in track.companies:
        live = live_lookup.get(company.symbol)
        heat_bonus = 0.0
        live_snapshot = None
        if live:
            pct_change = float(getattr(live, "pct_change", 0.0) or 0.0)
            volume_ratio = float(getattr(live, "volume_ratio", 1.0) or 1.0)
            heat_bonus = min(max(pct_change, 0.0) * 0.6 + volume_ratio * 1.8, 10)
            live_snapshot = {
                "pct_change": round(pct_change, 2),
                "volume_ratio": round(volume_ratio, 2),
                "theme": getattr(live, "theme", ""),
            }
        company_score = round(
            max(
                0.0,
                min(
                    100.0,
                    company.exposure_score * 0.48
                    + company.maturity_score * 0.22
                    + growth_score * 0.22
                    + heat_bonus
                    - _company_risk_penalty(company.risk_note),
                ),
            ),
            1,
        )
        rows.append(
            {
                "name": company.name,
                "symbol": company.symbol,
                "market": company.market,
                "role": company.role,
                "company_score": company_score,
                "exposure_score": company.exposure_score,
                "maturity_score": company.maturity_score,
                "rationale": company.rationale,
                "risk_note": company.risk_note,
                "live_snapshot": live_snapshot,
            }
        )
    return sorted(rows, key=lambda item: item["company_score"], reverse=True)


def _score_companies_for_early_alpha(track: EarlyAlphaTrack, alpha_score: float, stocks: list[Any]) -> list[dict[str, Any]]:
    live_lookup = {
        str(getattr(stock, "symbol", "")): stock
        for stock in stocks
        if getattr(stock, "symbol", "")
    }
    rows: list[dict[str, Any]] = []
    for company in track.companies:
        live = live_lookup.get(company.symbol)
        heat_bonus = 0.0
        live_snapshot = None
        if live:
            pct_change = float(getattr(live, "pct_change", 0.0) or 0.0)
            volume_ratio = float(getattr(live, "volume_ratio", 1.0) or 1.0)
            heat_bonus = min(max(pct_change, 0.0) * 0.35 + volume_ratio * 1.2, 7)
            live_snapshot = {
                "pct_change": round(pct_change, 2),
                "volume_ratio": round(volume_ratio, 2),
                "theme": getattr(live, "theme", ""),
            }
        company_score = round(
            max(
                0.0,
                min(
                    100.0,
                    company.exposure_score * 0.44
                    + company.maturity_score * 0.18
                    + alpha_score * 0.28
                    + track.underowned_score * 0.08
                    + heat_bonus
                    - _company_risk_penalty(company.risk_note),
                ),
            ),
            1,
        )
        rows.append(
            {
                "name": company.name,
                "symbol": company.symbol,
                "market": company.market,
                "role": company.role,
                "company_score": company_score,
                "exposure_score": company.exposure_score,
                "maturity_score": company.maturity_score,
                "rationale": company.rationale,
                "risk_note": company.risk_note,
                "live_snapshot": live_snapshot,
            }
        )
    return sorted(rows, key=lambda item: item["company_score"], reverse=True)


def _company_risk_penalty(note: str) -> float:
    high_risk_terms = ("亏损", "压力", "不确定", "波动", "政策", "纯度较低", "较高")
    return min(8.0, sum(1.4 for term in high_risk_terms if term in note))


def _confidence_level(score: float) -> str:
    if score >= 78:
        return "高"
    if score >= 64:
        return "中"
    return "低"


def _stage_label(track: GrowthTrack) -> str:
    if track.commercialization_score >= 76 and track.demand_score >= 84:
        return "放量成长期"
    if track.commercialization_score >= 62:
        return "场景扩张期"
    if track.tech_readiness_score < 55:
        return "技术验证期"
    return "政策加速期"


def _early_alpha_stage_label(track: EarlyAlphaTrack) -> str:
    if track.penetration_inflection_score >= 88 and track.commercialization_score >= 70:
        return "渗透率拐点前夜"
    if track.underowned_score >= 80:
        return "低拥挤预热期"
    if track.supply_bottleneck_score >= 84:
        return "瓶颈重估期"
    if track.tech_readiness_score < 65:
        return "技术验证期"
    return "催化等待期"


def _research_note(track: GrowthTrack, growth_score: float, confidence_score: float) -> str:
    if growth_score >= 78 and confidence_score >= 70:
        return "结构性成长和产业兑现兼具，适合作为中期重点跟踪赛道。"
    if growth_score >= 70:
        return "成长逻辑较强，但需要持续验证订单、商业化或监管进展。"
    return "更偏远期主题或早期技术期权，适合观察政策和产品突破，不宜只看概念热度。"


def _early_alpha_research_note(track: EarlyAlphaTrack, alpha_score: float, confidence_score: float) -> str:
    if alpha_score >= 78 and track.underowned_score >= 70:
        return "更接近下一波推理扩散方向，适合提前跟踪催化和订单验证。"
    if alpha_score >= 70:
        return "具备推理增量逻辑，但需要等待渗透率、客户预算或产品标准确认。"
    return "偏早期可选方向，先观察触发事件，不宜仅凭概念提前加大暴露。"


def _structural_methodology() -> dict[str, Any]:
    return {
        "score_formula": "结构性成长因子 - 风险惩罚 + 当前市场热度小权重修正",
        "factors": [
            {"factor": "policy_score", "weight": 0.18, "description": "政策支持和未来产业定位强度"},
            {"factor": "demand_score", "weight": 0.18, "description": "下游需求扩张和应用场景确定性"},
            {"factor": "ecosystem_score", "weight": 0.14, "description": "产业链完整度和龙头/配套成熟度"},
            {"factor": "tech_readiness_score", "weight": 0.12, "description": "技术成熟度和产品可交付性"},
            {"factor": "localization_score", "weight": 0.12, "description": "国产替代或自主可控牵引"},
            {"factor": "commercialization_score", "weight": 0.12, "description": "收入确认和规模化商业路径"},
            {"factor": "capital_efficiency_score", "weight": 0.08, "description": "扩张所需资本开支与利润弹性"},
            {"factor": "market_heat_score", "weight": 0.10, "description": "当前 A 股题材热度，仅作小权重修正"},
            {"factor": "risk_score", "weight": -0.14, "description": "技术、监管、估值、周期和商业化风险惩罚"},
        ],
        "disclaimer": "模型用于产业研究和候选赛道筛选，不构成投资建议或收益承诺。",
    }


def _early_alpha_methodology() -> dict[str, Any]:
    return {
        "score_formula": "推理增量 + 渗透率拐点 + 商业催化 + 低拥挤度 - 成熟/拥挤/风险惩罚",
        "factors": [
            {"factor": "penetration_inflection", "weight": 0.18, "description": "渗透率从试点走向规模部署的拐点概率"},
            {"factor": "inference_pull", "weight": 0.18, "description": "AI 推理工作负载对该环节的增量拉动"},
            {"factor": "business_catalyst", "weight": 0.14, "description": "未来 6-24 个月可观测的商业化触发事件"},
            {"factor": "supply_bottleneck", "weight": 0.12, "description": "该环节是否会成为推理扩散瓶颈"},
            {"factor": "underowned", "weight": 0.12, "description": "市场定价不足和资金低拥挤度"},
            {"factor": "ecosystem", "weight": 0.08, "description": "产业链和客户验证基础"},
            {"factor": "tech_readiness", "weight": 0.08, "description": "技术可交付和产品成熟度"},
            {"factor": "commercialization", "weight": 0.07, "description": "订单、收入和付费路径可验证性"},
            {"factor": "capital_efficiency", "weight": 0.07, "description": "轻资产或利润弹性"},
            {"factor": "low_crowding_bonus", "weight": 0.12, "description": "当前市场热度越低，反向给少量预期差加分"},
            {"factor": "risk/maturity/crowding", "weight": "penalty", "description": "风险、已成熟和已拥挤赛道会被降权"},
        ],
        "disclaimer": "early_alpha 模式用于寻找预期差和提前跟踪方向，不代表买入建议；低拥挤方向也可能长期不兑现。",
    }
