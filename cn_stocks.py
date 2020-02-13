import pandas as pd
from sqlalchemy import create_engine

# current_date = '2020-02-09'
current_date = '2020-02-12'

engine = create_engine('mysql+pymysql://root:jkl@localhost:3306/stocks')

sql = '''
    select * from cn_base where `日期` = '{0}';
'''.format(current_date)

df = pd.read_sql_query(sql, engine)

# df['PE分'] = df.sort_values(['PE-TTM(扣非)'], ascending=True).cumcount()
df.sort_values(by=['PE-TTM(扣非)'], inplace=True)
df['PE分'] = df.reset_index().index.map(lambda x: 100-x)
df.sort_values(by=['PB(不含商誉)'], inplace=True)
df['PB分'] = df.reset_index().index.map(lambda x: 100-x)
df.sort_values(by=['股息率(%)'], ascending=0, inplace=True)
df['DY分'] = df.reset_index().index.map(lambda x: 100-x)

df['总分'] = df['PE分'] + df['PB分'] + df['DY分']
df.sort_values(by=['总分'], ascending=0, inplace=True)

df['行业重复'] = df.groupby(['行业'])['总分'].rank(ascending=0, method='first')

print(df)

df = df[df['行业重复']<=1].iloc[0:30]
df.to_excel('./test.xlsx', index=False)
# print(df)