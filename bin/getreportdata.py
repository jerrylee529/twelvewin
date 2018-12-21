# -*- coding:utf-8 -*-
__author__ = 'jerry'

import pandas as pd
import tushare as ts
import datetime
from sendmail import sendmail
import commondatadef

report = ts.get_report_data(2017, 3)

report.set_index('code')

#report.sort(columns=['eps'], ascending=False, inplace=True)

quots = ts.get_today_all()

quots.set_index('code')

result = pd.merge(report, quots, on='code')

result['pe'] = result['trade']/result['eps']

result['pb'] = result['pe']*result['roe']/100

result['peg'] = result['pe']/result['eps_yoy']

def get_best_roe(report):
    result = report[(report.eps_yoy>30)&(report.roe>30)]

    result.sort_values(by=['roe'], ascending=[0], inplace=True)

    return result

def get_best_pe(report):
    result = report[(report.eps_yoy>0)&(report.pe<15)&(report.pe>0)]

    result.sort_values(by=['pe'], ascending=[1], inplace=True)

    return result

def get_best_pb(report):
    result = report[(report.eps_yoy>0)&(report.pb<3)&(report.pe>0)]

    result.sort_values(by=['pb'], ascending=[1], inplace=True)

    return result

def get_best_peg(report):
    result = report[(report.peg>0)&(report.pe>0)]

    result.sort_values(by=['peg'], ascending=[1], inplace=True)

    return result

today = datetime.date.today()
outputfile_best_roe = "%s/thebestroe_report_%s.csv" % (commondatadef.resultPath,today.strftime("%Y%m%d"),)
outputfile_best_pe = "%s/thebestpe_report_%s.csv" % (commondatadef.resultPath,today.strftime("%Y%m%d"),)
outputfile_best_pb = "%s/thebestpb_report_%s.csv" % (commondatadef.resultPath,today.strftime("%Y%m%d"),)
outputfile_best_peg = "%s/thebestpeg_report_%s.csv" % (commondatadef.resultPath,today.strftime("%Y%m%d"),)

roe = get_best_roe(result)
roe.to_csv(outputfile_best_roe, encoding='gbk', index=False)

pe = get_best_pe(result)
pe.to_csv(outputfile_best_pe, encoding='gbk', index=False)

pb = get_best_pb(result)
pb.to_csv(outputfile_best_pb, encoding='gbk', index=False)

peg = get_best_peg(result)
peg.to_csv(outputfile_best_peg, encoding='gbk', index=False)

subject = "成长股列表"

sendmail(subject, mailto=['38454880@qq.com'], content="Please check attachment", attachments=[outputfile_best_roe, outputfile_best_pe, outputfile_best_pb, outputfile_best_peg])

# roe 〉30 并且 每股收益增长率〉0
#df[(df.roe>30) & (df.eps_yoy>0)]

#report.to_csv('e:/stock/report.csv', encoding='gbk', index=False)

