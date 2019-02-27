# -*- coding: utf-8 -*-

__author__ = 'Administrator'

import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, DateTime, MetaData, ForeignKey, UniqueConstraint, Index, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import config

# 创建数据基类
Base = declarative_base()

# 创建mysql数据库引擎
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False)

# 创建数据库会话类
Session = sessionmaker(bind=engine)


# 股票代码表
class Instrument(Base):
    __tablename__ = "instrument"

    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)  # 代码
    name = Column(String(32), nullable=False)  # 名称
    industry = Column(String(32))  # 所属行业
    area = Column(String(32))  # 地区
    pe = Column(Float)  # 市盈率
    outstanding = Column(Float)  # 流通股本(亿)
    totals = Column(Float)  # 总股本(亿)
    total_assets = Column(Float)  # 总资产(万)
    liquid_assets = Column(Float)  # 流动资产
    fixed_assets = Column(Float)  # 固定资产
    reserved = Column(Float)  # 公积金
    reserved_per_share = Column(Float)  # 每股公积金
    esp = Column(Float)  # 每股收益
    bvps = Column(Float)  # 每股净资
    pb = Column(Float)  # 市净率
    time_2_market = Column(String(16))  # 上市日期
    undp = Column(Float)  # 未分利润
    perundp = Column(Float)  # 每股未分配
    rev = Column(Float)  # 收入同比(%)
    profit = Column(Float)  # 利润同比(%)
    gpr = Column(Float)  # 毛利率(%)
    npr = Column(Float)  # 净利润率(%)
    holders = Column(Integer)  # 股东人数
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, name, industry, area, pe, outstanding, totals, total_assets, liquid_assets, fixed_assets,
                 reserved, reserved_per_share, esp, bvps, pb, time_2_market, undp, perundp, rev, profit, gpr, npr,
                 holders):
        self.code = code
        self.name = name
        self.industry = industry
        self.area = area
        self.pe = pe
        self.outstanding = outstanding
        self.totals = totals
        self.total_assets = total_assets
        self.liquid_assets = liquid_assets
        self.fixed_assets = fixed_assets
        self.reserved = reserved
        self.reserved_per_share = reserved_per_share
        self.esp = esp
        self.bvps = bvps
        self.pb = pb
        self.time_2_market = time_2_market
        self.undp = undp
        self.perundp = perundp
        self.rev = rev
        self.profit = profit
        self.gpr = gpr
        self.npr = npr
        self.holders = holders
        self.update_time = datetime.datetime.now()


# 财务报表
class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    eps = Column(Float)  # 每股收益
    eps_yoy = Column(Float)  # 每股收益同比(%)
    bvps = Column(Float)  # 每股净资产
    roe = Column(Float)  # 净资产收益率(%)
    epcf = Column(Float)  # 每股现金流量(元)
    net_profits = Column(Float)  # 净利润(万元)
    profits_yoy = Column(Float)  # 净利润同比(%)
    report_date = Column(String(16))  # 发布日期
    year = Column(Integer, nullable=False)  # 财报年份
    season = Column(Integer, nullable=False)  # 财报季度
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, eps, eps_yoy, bvps, roe, epcf, net_profits, profits_yoy,
                 report_date, year, season):
        self.code = code
        self.eps = eps
        self.eps_yoy = eps_yoy
        self.bvps = bvps
        self.roe = roe
        self.epcf = epcf
        self.net_profits = net_profits
        self.profits_yoy = profits_yoy
        self.report_date = report_date
        self.year = year
        self.season = season
        self.update_time = datetime.datetime.now()


#
class SelfSelectedStock(Base):
    __tablename__ = 'self_selected_stock'

    __table_args__ = (
        UniqueConstraint('email', 'code', name='uix_email_code'),
        Index('ix_email_code', 'email', 'code'),
    )

    id = Column(Integer, primary_key=True)
    email = Column(String(128), nullable=False)
    code = Column(String(8), nullable=False)
    labels = Column(String(128))
    deleted = Column(Integer, default=False, nullable=False)
    update_time = Column(DateTime, nullable=False)

    def __init__(self, email, code, labels, deleted):
        self.code = code
        self.email = email
        self.labels = labels
        self.deleted = deleted
        self.update_time = datetime.datetime.now()

# 板块分类
class StockCluster(Base):
    __tablename__ = 'stock_cluster'

    id = Column(Integer, primary_key=True)
    section = Column(String(16), nullable=False)  # 板块
    code = Column(String(8), nullable=False)
    name = Column(String(32), nullable=False)  # 名称
    update_time = Column(DateTime, nullable=False)

    def __init__(self, section, code, name):
        self.code = code
        self.name = name
        self.section = section
        self.update_time = datetime.datetime.now()


class StockClusterItem(Base):
    __tablename__ = 'stock_cluster_item'

    id = Column(Integer, primary_key=True)
    section = Column(String(16), nullable=False)  # 板块
    parent_code = Column(String(8), nullable=False)
    code = Column(String(8), nullable=False)
    name = Column(String(32), nullable=False)  # 名称
    corr = Column(Float, nullable=False)
    update_time = Column(DateTime, nullable=False)

    def __init__(self, section, parent_code, code, name, corr):
        self.section = section
        self.parent_code = parent_code
        self.code = code
        self.name = name
        self.corr = corr
        self.update_time = datetime.datetime.now()


class StockPrediction(Base):
    '''
    股票预测结果表
    '''
    __tablename__ = 'stock_prediction'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    name = Column(String(32),  index=True, nullable=False, comment=u"股票名称")  # 名称
    accu_rate = Column(Float, nullable=False, comment=u"精确度")
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, name, accu_rate):
        self.code = code
        self.name = name
        self.accu_rate = accu_rate
        self.update_time = datetime.datetime.now()


class StockProfitReport(Base):
    '''
    盈利能力报告
    '''
    __tablename__ = 'stock_profit_report'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    name = Column(String(32),  index=True, nullable=False, comment=u"股票名称")
    roe = Column(Float, nullable=True, comment=u"净资产收益率(%)")
    net_profit_ratio = Column(Float, nullable=True, comment=u"净利率(%)")
    gross_profit_rate = Column(Float, nullable=True, comment=u"毛利率(%)")
    net_profits = Column(Float, nullable=True, comment=u"净利润(万元)")
    eps = Column(Float, nullable=True, comment=u"每股收益")
    business_income = Column(Float, nullable=True, comment=u"营业收入(百万元)")
    bips = Column(Float, nullable=True, comment=u"每股主营业务收入(元)")
    year = Column(Integer, nullable=False, comment=u"财报年份")
    season = Column(Integer, nullable=False, comment=u"财报季度")
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, name, roe, net_profit_ratio, gross_profit_rate, net_profits, eps, business_income, bips,
                 year, season):
        self.code = code
        self.name = name
        self.update_time = datetime.datetime.now()
        self.roe = roe
        self.net_profit_ratio = net_profit_ratio
        self.gross_profit_rate = gross_profit_rate
        self.net_profits = net_profits
        self.eps = eps
        self.business_income = business_income
        self.bips = bips
        self.year = year
        self.season = season


class StockOperationReport(Base):
    '''
    运营能力报告
    '''
    __tablename__ = 'stock_operation_report'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    name = Column(String(32),  index=True, nullable=False, comment=u"股票名称")
    arturnover = Column(Float, nullable=True, comment=u"应收账款周转率(次)")
    arturndays = Column(Float, nullable=True, comment=u"应收账款周转天数(天)")
    inventory_turnover = Column(Integer, nullable=True, comment=u"存货周转率(次)")
    inventory_days = Column(Integer, nullable=True, comment=u"存货周转天数(天)")
    currentasset_turnover = Column(Integer, nullable=True, comment=u"流动资产周转率(次)")
    currentasset_days = Column(Integer, nullable=True, comment=u"流动资产周转天数(天)")
    year = Column(Integer, index=True, nullable=False, comment=u"财报年份")
    season = Column(Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, name, arturnover, arturndays, inventory_turnover, inventory_days, currentasset_turnover,
                 currentasset_days, year, season):
        self.code = code
        self.name = name
        self.update_time = datetime.datetime.now()
        self.arturnover = arturnover
        self.arturndays = arturndays
        self.inventory_turnover = inventory_turnover
        self.inventory_days = inventory_days
        self.currentasset_days = currentasset_days
        self.currentasset_turnover = currentasset_turnover
        self.year = year
        self.season = season


class StockGrowthReport(Base):
    '''
    成长能力报告
    '''
    __tablename__ = 'stock_growth_report'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    name = Column(String(32),  index=True, nullable=False, comment=u"股票名称")
    mbrg = Column(Float, nullable=True, comment=u"主营业务收入增长率(%)")
    nprg = Column(Float, nullable=True, comment=u"净利润增长率(%)")
    nav = Column(Float, nullable=True, comment=u"净资产增长率")
    targ = Column(Float, nullable=True, comment=u"总资产增长率")
    epsg = Column(Float, nullable=True, comment=u"每股收益增长率")
    seg = Column(Float, nullable=True, comment=u"股东权益增长率")
    year = Column(Integer, index=True, nullable=False, comment=u"财报年份")
    season = Column(Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, name, mbrg, nprg, nav, targ, epsg, seg, year, season):
        self.code = code
        self.name = name
        self.update_time = datetime.datetime.now()
        self.mbrg = mbrg
        self.nprg = nprg
        self.nav = nav
        self.targ = targ
        self.epsg = epsg
        self.seg = seg
        self.year = year
        self.season = season


class StockDebtPayingReport(Base):
    '''
    偿债能力报告
    '''
    __tablename__ = 'stock_debtpaying_report'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    name = Column(String(32),  index=True, nullable=False, comment=u"股票名称")
    currentratio = Column(Float, nullable=True, comment=u"流动比率")
    quickratio = Column(Float, nullable=True, comment=u"速动比率")
    cashratio = Column(Float, nullable=True, comment=u"现金比率")
    icratio = Column(Float, nullable=True, comment=u"利息支付倍数")
    sheqratio = Column(Float, nullable=True, comment=u"股东权益比率")
    adratio = Column(Float, nullable=True, comment=u"股东权益增长率")
    year = Column(Integer, index=True, nullable=False, comment=u"财报年份")
    season = Column(Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, name, currentratio, quickratio, cashratio, icratio, sheqratio, adratio, year, season):
        self.code = code
        self.name = name
        self.update_time = datetime.datetime.now()
        self.currentratio = currentratio
        self.quickratio = quickratio
        self.cashratio = cashratio
        self.icratio = icratio
        self.sheqratio = sheqratio
        self.adratio = adratio
        self.year = year
        self.season = season


class StockCashFlowReport(Base):
    '''
    现金流量报告
    '''
    __tablename__ = 'stock_cashflow_report'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    name = Column(String(32),  index=True, nullable=False, comment=u"股票名称")
    cf_sales = Column(Float, nullable=True, comment=u"经营现金净流量对销售收入比率")
    rateofreturn = Column(Float, nullable=True, comment=u"资产的经营现金流量回报率")
    cf_nm = Column(Float, nullable=True, comment=u"经营现金净流量与净利润的比率")
    cf_liabilities = Column(Float, nullable=True, comment=u"经营现金净流量对负债比率")
    cashflowratio = Column(Float, nullable=True, comment=u"现金流量比率")
    year = Column(Integer, index=True, nullable=False, comment=u"财报年份")
    season = Column(Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = Column(DateTime, nullable=False)

    def __init__(self, code, name, cf_sales, rateofreturn, cf_nm, cf_liabilities, cashflowratio, year, season):
        self.code = code
        self.name = name
        self.update_time = datetime.datetime.now()
        self.cf_sales = cf_sales
        self.rateofreturn = rateofreturn
        self.cf_nm = cf_nm
        self.cf_liabilities = cf_liabilities
        self.cashflowratio = cashflowratio
        self.year = year
        self.season = season

"""
DROP TABLE IF EXISTS `stock_indicator`;
CREATE TABLE `stock_indicator` (
  `id` int(4) primary key not null auto_increment,
  `org_type` TINYINT not null COMMENT '组织类型, 1-4',
  `indicator_type` varchar(16) not null COMMENT '指标类型, indicator(一般指标), income(利润表), balance(资产负债表), cash(现金流量表), special(特殊指标)',
  `en_name` varchar(32) not null COMMENT '指标英文名称',
  `cn_name` varchar(64) not null COMMENT '指标中文名称',
  `update_time` timestamp NOT NULL COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""
class StockIndicator(Base):
    """
    股票财务指标字典表
    """
    __tablename__ = 'stock_indicator'

    id = Column(Integer, primary_key=True)
    org_type = Column(Integer, nullable=False, comment=u"组织类型, 1-4")
    indicator_type = Column(String(16), nullable=False, comment=u"指标类型, indicator(一般指标), income(利润表), balance(资产负债表), cash(现金流量表), special(特殊指标)")
    en_name = Column(String(32),  index=True, nullable=False, comment=u"指标英文名称")
    cn_name = Column(String(64), nullable=True, comment=u"指标中文名称")
    update_time = Column(DateTime, nullable=False)


class StockFinanceFactor(Base):
    """
    股票财务因子表
    """
    __tablename__ = 'stock_finance_factor'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    name = Column(String(32),  index=True, nullable=False, comment=u"股票名称")
    report_date = Column(Integer, nullable=True, comment=u"报告年度") # "报告年度",
    report_name = Column(String(20), nullable=True, comment=u"报告名称") # "报告名称",
    total_revenue = Column(Float, nullable=True, comment=u"营业收入") # "营业收入",
    operating_income_yoy = Column(Float, nullable=True, comment=u"营业收入同比增长") #: "营业收入同比增长",
    net_profit_atsopc = Column(Float, nullable=True, comment=u"净利润") #"净利润",
    net_profit_atsopc_yoy = Column(Float, nullable=True, comment=u"净利润同比增长") #"净利润同比增长",
    net_profit_after_nrgal_atsolc = Column(Float, nullable=True, comment=u"扣非净利润") #"扣非净利润",
    np_atsopc_nrgal_yoy = Column(Float, nullable=True, comment=u"扣非净利润同比增长") #"扣非净利润同比增长",
    basic_eps = Column(Float, nullable=True, comment=u"每股收益") #"每股收益",
    np_per_share = Column(Float, nullable=True, comment=u"每股净资产") #"每股净资产",
    capital_reserve = Column(Float, nullable=True, comment=u"每股资本公积金") #"每股资本公积金",
    undistri_profit_ps = Column(Float, nullable=True, comment=u"每股未分配利润") #"每股未分配利润",
    operate_cash_flow_ps = Column(Float, nullable=True, comment=u"每股经营现金流") #"每股经营现金流",
    avg_roe = Column(Float, nullable=True, comment=u"净资产收益率") #"净资产收益率",
    ore_dlt = Column(Float, nullable=True, comment=u"净资产收益率-摊薄") #"净资产收益率-摊薄",
    net_interest_of_total_assets = Column(Float, nullable=True, comment=u"总资产报酬率") #"总资产报酬率",
    rop = Column(Float, nullable=True, comment=u"人力投入回报率") #"人力投入回报率",
    gross_selling_rate = Column(Float, nullable=True, comment=u"销售毛利率") #"销售毛利率",
    net_selling_rate = Column(Float, nullable=True, comment=u"销售净利率") #"销售净利率",
    asset_liab_ratio = Column(Float, nullable=True, comment=u"资产负债率") #"资产负债率",
    current_ratio = Column(Float, nullable=True, comment=u"流动比率") #"流动比率",
    quick_ratio = Column(Float, nullable=True, comment=u"速动比率") #"速动比率",
    equity_multiplier = Column(Float, nullable=True, comment=u"权益乘数") #"权益乘数",
    equity_ratio = Column(Float, nullable=True, comment=u"产权比率") #"产权比率",
    holder_equity = Column(Float, nullable=True, comment=u"股东权益比率") #"股东权益比率",
    ncf_from_oa_to_total_liab = Column(Float, nullable=True, comment=u"现金流量比率") #"现金流量比率",
    inventory_turnover_days = Column(Integer, nullable=True, comment=u"存货周转天数") #"存货周转天数",
    receivable_turnover_days = Column(Integer, nullable=True, comment=u"应收账款周转天数") #"应收账款周转天数",
    accounts_payable_turnover_days = Column(Integer, nullable=True, comment=u"应付账款周转天数") #"应付账款周转天数",
    cash_cycle = Column(Integer, nullable=True, comment=u"现金循环周期") #"现金循环周期",
    operating_cycle = Column(Integer, nullable=True, comment=u"营业周期") #"营业周期",
    total_capital_turnover = Column(Float, nullable=True, comment=u"总资产周转率") #"总资产周转率",
    inventory_turnover = Column(Float, nullable=True, comment=u"存货周转率") #"存货周转率",
    account_receivable_turnover = Column(Float, nullable=True, comment=u"应收账款周转率") #"应收账款周转率",
    accounts_payable_turnover = Column(Float, nullable=True, comment=u"应付账款周转率") #"应付账款周转率",
    current_asset_turnover_rate = Column(Float, nullable=True, comment=u"流动资产周转率") #"流动资产周转率",
    fixed_asset_turnover_ratio = Column(Float, nullable=True, comment=u"固定资产周转率") #"固定资产周转率"
    update_time = Column(DateTime, nullable=False, comment=u"更新时间")

    def __init__(self, code, name, report_date, report_name):
        self.code = code
        self.name = name
        self.report_date = report_date
        self.report_name = report_name
        self.update_time = datetime.datetime.now()


class XueQiuReportInfo(Base):
    __tablename__ = 'xueqiu_report_info'

    id = Column(Integer, primary_key=True)
    security_code = Column(String(8), index=True, nullable=False, comment=u"股票代码")
    security_name = Column(String(8), index=True, nullable=False, comment=u"股票名称")
    report_type = Column(Integer, nullable=False, comment=u"报表类型 0: 资产负债表 1: 利润分配表 2: 现金流量表")
    report_data = Column(Text, nullable=False, comment=u"报表内容，json格式")
    update_time = Column(DateTime, nullable=False, comment=u"更新时间")

    def __init__(self, security_code, security_name, report_type, report_data):
        self.security_code = security_code
        self.security_name = security_name
        self.update_time = datetime.datetime.now()
        self.report_type = report_type
        self.report_data = report_data


class StrategyResultInfo(Base):
    __tablename__ = 'strategy_result_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True, nullable=False, comment=u"策略名称")
    buy_list = Column(Text, nullable=True, comment=u"买入列表")
    sell_list = Column(Text, nullable=True, comment=u"卖出列表")
    create_time = Column(DateTime, nullable=False, comment=u"创建时间")
    update_time = Column(DateTime, nullable=False, comment=u"更新时间")

    def __init__(self, name, buy_list, sell_list):
        self.name = name
        self.buy_list = buy_list
        self.sell_list = sell_list
        self.create_time = datetime.datetime.now()
        self.update_time = datetime.datetime.now()

if __name__ == '__main__':
    Base.metadata.create_all(engine) 
