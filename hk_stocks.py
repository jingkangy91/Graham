import pandas as pd
from sqlalchemy import create_engine

## Parameters define
# current_date = '2020-02-09'
# current_date = '2020-02-13'
current_date = '2020-02-16'

# Profile 1
total_amount = 382315
num_of_stocks = 20
# num_of_stocks = 25
# num_of_stocks = 26
# num_of_stocks = 27
# num_of_stocks = 30
buy_amount = total_amount / num_of_stocks
out_name = current_date + '_hk_stocks.xlsx'

engine = create_engine('mysql+pymysql://root:jkl@localhost:3306/stocks')

# sql = '''
#     select * from cn_base where `日期` = '{0}';
# '''.format(current_date)

sql = '''
    select s.*, i.`最小成交单位` from hk_stock s left join hk_info i on s.`代码`=i.`代码` where s.`日期`='{0}';
'''.format(current_date)

df = pd.read_sql_query(sql, engine)

## Calculate PE, PB, DY and total scores.
# df['PE分'] = df.sort_values(['PE-TTM(扣非)'], ascending=True).cumcount()
df.sort_values(by=['PE-TTM(扣非)'], inplace=True)
df['PE分'] = df.reset_index().index.map(lambda x: 100-x)
df.sort_values(by=['PB(不含商誉)'], inplace=True)
df['PB分'] = df.reset_index().index.map(lambda x: 100-x)
df.sort_values(by=['股息率(%)'], ascending=0, inplace=True)
df['DY分'] = df.reset_index().index.map(lambda x: 100-x)

df['总分'] = df['PE分'] + df['PB分'] + df['DY分']
df.sort_values(by=['总分'], ascending=0, inplace=True)

df['行业重复'] = df.groupby(['行业'])['总分'].rank(ascending=0, method='first').astype(int)

# df = df[df['行业重复']<=1].iloc[0:num_of_stocks]
df = df[df['行业重复']<=2].iloc[0:num_of_stocks]

# print(df)
# df.to_excel('./test.xlsx', index=False)

## Calculate buy amount
df['计划买入'] = buy_amount
df['折合手数'] = round(df['计划买入']/(df['股价'] * df['最小成交单位']),0).astype(int)
df['买入股数'] = df['折合手数'] * df['最小成交单位']
df['实际买入'] = df['买入股数'] * df['股价']

# print(df)
# print(sum(df['实际买入']))
df.to_excel(out_name, index=False)