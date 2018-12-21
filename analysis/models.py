# -*- coding: utf-8 -*-

__author__ = 'Administrator'

import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, DateTime, MetaData, ForeignKey, UniqueConstraint, Index
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


if __name__ == '__main__':
    Base.metadata.create_all(engine) 
