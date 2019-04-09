# -*- coding: utf-8 -*-

# project/models.py


import datetime
from app import db, bcrypt
from flask_login import UserMixin

import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String(256), nullable=True)

    def __init__(self, email, password, confirmed,
                 admin=False, confirmed_on=None,
                 password_reset_token=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.password_reset_token = password_reset_token


# 精选股票数据
class SpecialStock(db.Model):
    __tablename__ = 'business_stock'

    code = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(32))
    turnoverratio = db.Column(db.Float)
    per = db.Column(db.Float)
    pb = db.Column(db.Float)
    mktcap = db.Column(db.Float)
    roe = db.Column(db.Float)
    close = db.Column(db.Float)
    wma10 = db.Column(db.Float)
    update_time = db.Column(db.Date)

    def __init__(self, code=None, name=None):
        self.code = code
        self.name = name


# 标签数据
class StockLabels(db.Model):
    __tablename__ = 'stock_labels'
    code = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(32))
    labels = db.Column(db.String(128))

    def __init__(self, code, name, labels):
        self.code = code
        self.name = name
        self.labels = labels


# 自选股数据
class SelfSelectedStock(db.Model):
    __tablename__ = 'self_selected_stock'

    __table_args__ = (
        db.UniqueConstraint('email', 'code', name='uix_email_code'),
        db.Index('ix_email_code', 'email', 'code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(8), nullable=False)
    labels = db.Column(db.String(128))
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    update_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, code, labels, deleted=False):
        self.code = code
        self.email = email
        self.labels = labels
        self.deleted = deleted
        self.update_time = datetime.datetime.now()

    def to_json(self):
        result = {}
        result['email'] = self.email
        result['code'] = self.code
        result['labels'] = self.labels
        result['deleted'] = self.deleted

        return result


# 股票代码表
class Instrument(db.Model):
    __tablename__ = "instrument"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False)  # 代码
    name = db.Column(db.String(32), nullable=False)  # 名称
    industry = db.Column(db.String(32))  # 所属行业
    area = db.Column(db.String(32))  # 地区
    pe = db.Column(db.Float)  # 市盈率
    outstanding = db.Column(db.Float)  # 流通股本(亿)
    totals = db.Column(db.Float)  # 总股本(亿)
    total_assets = db.Column(db.Float)  # 总资产(万)
    liquid_assets = db.Column(db.Float)  # 流动资产
    fixed_assets = db.Column(db.Float)  # 固定资产
    reserved = db.Column(db.Float)  # 公积金
    reserved_per_share = db.Column(db.Float)  # 每股公积金
    esp = db.Column(db.Float)  # 每股收益
    bvps = db.Column(db.Float)  # 每股净资
    pb = db.Column(db.Float)  # 市净率
    time_2_market = db.Column(db.String(16))  # 上市日期
    undp = db.Column(db.Float)  # 未分利润
    perundp = db.Column(db.Float)  # 每股未分配
    rev = db.Column(db.Float)  # 收入同比(%)
    profit = db.Column(db.Float)  # 利润同比(%)
    gpr = db.Column(db.Float)  # 毛利率(%)
    npr = db.Column(db.Float)  # 净利润率(%)
    holders = db.Column(db.Integer)  # 股东人数
    update_time = db.Column(db.DateTime, nullable=False)

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
class Report(db.Model):
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False)
    eps = db.Column(db.Float)  # 每股收益
    eps_yoy = db.Column(db.Float)  # 每股收益同比(%)
    bvps = db.Column(db.Float)  # 每股净资产
    roe = db.Column(db.Float)  # 净资产收益率(%)
    epcf = db.Column(db.Float)  # 每股现金流量(元)
    net_profits = db.Column(db.Float)  # 净利润(万元)
    profits_yoy = db.Column(db.Float)  # 净利润同比(%)
    report_date = db.Column(db.String(16))  # 发布日期
    year = db.Column(db.Integer, nullable=False)  # 财报年份
    season = db.Column(db.Integer, nullable=False)  # 财报季度
    update_time = db.Column(db.DateTime, nullable=False)

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


# 板块分类
class StockCluster(db.Model):
    __tablename__ = 'stock_cluster'

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(16), nullable=False)  # 板块
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(32), nullable=False)  # 名称
    update_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, section, code, name):
        self.code = code
        self.name = name
        self.section = section
        self.update_time = datetime.datetime.now()


class StockClusterItem(db.Model):
    __tablename__ = 'stock_cluster_item'

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(16), nullable=False)  # 板块
    parent_code = db.Column(db.String(8), nullable=False)
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(32), nullable=False)  # 名称
    corr = db.Column(db.Float, nullable=False)
    update_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, section, parent_code, code, name, corr):
        self.section = section
        self.parent_code = parent_code
        self.code = code
        self.name = name
        self.corr = corr
        self.update_time = datetime.datetime.now()


class StockPrediction(db.Model):
    '''
    股票预测结果表
    '''
    __tablename__ = 'stock_prediction'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), index=True, nullable=False, comment=u"股票代码")
    name = db.Column(db.String(32),  index=True, nullable=False, comment=u"股票名称")  # 名称
    accu_rate = db.Column(db.Float, nullable=False, comment=u"精确度")
    update_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, code, name, accu_rate):
        self.code = code
        self.name = name
        self.accu_rate = accu_rate
        self.update_time = datetime.datetime.now()


class StockReportBasic():
    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


class StockProfitReport(db.Model, StockReportBasic):
    '''
    盈利能力报告
    '''
    __tablename__ = 'stock_profit_report'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), index=True, nullable=False, comment=u"股票代码")
    name = db.Column(db.String(32),  index=True, nullable=False, comment=u"股票名称")
    roe = db.Column(db.Float, nullable=True, comment=u"净资产收益率(%)")
    net_profit_ratio = db.Column(db.Float, nullable=True, comment=u"净利率(%)")
    gross_profit_rate = db.Column(db.Float, nullable=True, comment=u"毛利率(%)")
    net_profits = db.Column(db.Float, nullable=True, comment=u"净利润(万元)")
    eps = db.Column(db.Float, nullable=True, comment=u"每股收益")
    business_income = db.Column(db.Float, nullable=True, comment=u"营业收入(百万元)")
    bips = db.Column(db.Float, nullable=True, comment=u"每股主营业务收入(元)")
    year = db.Column(db.Integer, nullable=False, comment=u"财报年份")
    season = db.Column(db.Integer, nullable=False, comment=u"财报季度")
    update_time = db.Column(db.DateTime, nullable=False)

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


class StockOperationReport(db.Model, StockReportBasic):
    '''
    运营能力报告
    '''
    __tablename__ = 'stock_operation_report'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), index=True, nullable=False, comment=u"股票代码")
    name = db.Column(db.String(32),  index=True, nullable=False, comment=u"股票名称")
    arturnover = db.Column(db.Float, nullable=True, comment=u"应收账款周转率(次)")
    arturndays = db.Column(db.Float, nullable=True, comment=u"应收账款周转天数(天)")
    inventory_turnover = db.Column(db.Integer, nullable=True, comment=u"存货周转率(次)")
    inventory_days = db.Column(db.Integer, nullable=True, comment=u"存货周转天数(天)")
    currentasset_turnover = db.Column(db.Integer, nullable=True, comment=u"流动资产周转率(次)")
    currentasset_days = db.Column(db.Integer, nullable=True, comment=u"流动资产周转天数(天)")
    year = db.Column(db.Integer, index=True, nullable=False, comment=u"财报年份")
    season = db.Column(db.Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = db.Column(db.DateTime, nullable=False)

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


class StockGrowthReport(db.Model, StockReportBasic):
    '''
    成长能力报告
    '''
    __tablename__ = 'stock_growth_report'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), index=True, nullable=False, comment=u"股票代码")
    name = db.Column(db.String(32),  index=True, nullable=False, comment=u"股票名称")
    mbrg = db.Column(db.Float, nullable=True, comment=u"主营业务收入增长率(%)")
    nprg = db.Column(db.Float, nullable=True, comment=u"净利润增长率(%)")
    nav = db.Column(db.Float, nullable=True, comment=u"净资产增长率")
    targ = db.Column(db.Float, nullable=True, comment=u"总资产增长率")
    epsg = db.Column(db.Float, nullable=True, comment=u"每股收益增长率")
    seg = db.Column(db.Float, nullable=True, comment=u"股东权益增长率")
    year = db.Column(db.Integer, index=True, nullable=False, comment=u"财报年份")
    season = db.Column(db.Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = db.Column(db.DateTime, nullable=False)

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


class StockDebtPayingReport(db.Model, StockReportBasic):
    '''
    偿债能力报告
    '''
    __tablename__ = 'stock_debtpaying_report'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), index=True, nullable=False, comment=u"股票代码")
    name = db.Column(db.String(32),  index=True, nullable=False, comment=u"股票名称")
    currentratio = db.Column(db.Float, nullable=True, comment=u"流动比率")
    quickratio = db.Column(db.Float, nullable=True, comment=u"速动比率")
    cashratio = db.Column(db.Float, nullable=True, comment=u"现金比率")
    icratio = db.Column(db.Float, nullable=True, comment=u"利息支付倍数")
    sheqratio = db.Column(db.Float, nullable=True, comment=u"股东权益比率")
    adratio = db.Column(db.Float, nullable=True, comment=u"股东权益增长率")
    year = db.Column(db.Integer, index=True, nullable=False, comment=u"财报年份")
    season = db.Column(db.Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = db.Column(db.DateTime, nullable=False)

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


class StockCashFlowReport(db.Model, StockReportBasic):
    '''
    现金流量报告
    '''
    __tablename__ = 'stock_cashflow_report'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), index=True, nullable=False, comment=u"股票代码")
    name = db.Column(db.String(32),  index=True, nullable=False, comment=u"股票名称")
    cf_sales = db.Column(db.Float, nullable=True, comment=u"经营现金净流量对销售收入比率")
    rateofreturn = db.Column(db.Float, nullable=True, comment=u"资产的经营现金流量回报率")
    cf_nm = db.Column(db.Float, nullable=True, comment=u"经营现金净流量与净利润的比率")
    cf_liabilities = db.Column(db.Float, nullable=True, comment=u"经营现金净流量对负债比率")
    cashflowratio = db.Column(db.Float, nullable=True, comment=u"现金流量比率")
    year = db.Column(db.Integer, index=True, nullable=False, comment=u"财报年份")
    season = db.Column(db.Integer, index=True, nullable=False, comment=u"财报季度")
    update_time = db.Column(db.DateTime, nullable=False)

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


class XueQiuReportInfo(db.Model):
    __tablename__ = 'xueqiu_report_info'

    id = db.Column(db.Integer, primary_key=True)
    security_code = db.Column(db.String(8), index=True, nullable=False, comment=u"股票代码")
    security_name = db.Column(db.String(8), index=True, nullable=False, comment=u"股票名称")
    report_type = db.Column(db.Integer, nullable=False, comment=u"报表类型 0: 资产负债表 1: 利润分配表 2: 现金流量表")
    report_data = db.Column(db.Text, nullable=False, comment=u"报表内容，json格式")
    update_time = db.Column(db.DateTime, nullable=False, comment=u"更新时间")

    def __init__(self, security_code, security_name, report_type, report_data):
        self.security_code = security_code
        self.security_name = security_name
        self.update_time = datetime.datetime.now()
        self.report_type = report_type
        self.report_data = report_data


class InvestmentKnowledge(db.Model):
    __tablename__ = 'investment_knowledge'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), index=True, nullable=False, comment=u"标题")
    category = db.Column(db.String(32), index=True, nullable=True, comment=u"股票名称")
    content = db.Column(db.Text, nullable=False, comment=u"内容")
    priority = db.Column(db.Integer, nullable=False, comment=u"排序优先级")
    create_time = db.Column(db.DateTime, nullable=False, comment=u"创建时间")
    update_time = db.Column(db.DateTime, nullable=False, comment=u"更新时间")

    def __init__(self, title, category, content, priority):
        self.title = title
        self.category = category
        self.create_time = datetime.datetime.now()
        self.update_time = datetime.datetime.now()
        self.content = content
        self.priority = priority