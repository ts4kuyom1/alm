
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

assets = pd.DataFrame({
    'name': ['Overnight МБК', 'Корп. кредит А', 'Корп. кредит Б', 'ОФЗ 26207', 'Корп. кредит В', 'Ипотечный транш 1', 'Корп. бонд X', 'ОФЗ 26212', 'Ипотечный транш 2', 'Корп. кредит Г', 'ОФЗ 26230', 'Ипотечный транш 3'],
    'amount': np.array([150, 200, 300, 500, 400, 800, 350, 600, 1200, 450, 700, 900]),
    'maturity date': ['2026.10.24', '2026.10.28', '2026.11.15', '2026.12.20', '2027.01.20', '2027.03.15', '2027.06.10', '2027.10.23', '2028.04.15', '2029.01.10', '2030.06.15', '2032.05.20']
})

assets['maturity date'] = pd.to_datetime(assets['maturity date'], format='%Y.%m.%d')

today = pd.to_datetime('2026.10.23', format='%Y.%m.%d')
delta_time = pd.to_timedelta(assets['maturity date'] - today).dt.days

bucket_edges = [0, 1, 7, 30, 90, 180, 365, 730, 1825, float('inf')]
bucket_lables = ['O/N', '2D-7D', '8D-1M', '1M-3M', '3M-6M', '6M-1Y', '1Y-2Y', '2Y-5Y', '>5Y']
buckets = pd.cut(
    delta_time, 
    bucket_edges,
    labels= bucket_lables
    )
assets['bucket'] = buckets

buckets_sums = {
    'O/N': 0,
    '2D-7D': 0,
    '8D-1M': 0,
    '1M-3M': 0,
    '3M-6M': 0,
    '6M-1Y': 0,
    '1Y-2Y': 0,
    '2Y-5Y': 0,
    '>5Y': 0
}

for i, row in assets.iterrows():
    bucket = row['bucket']
    amount = row['amount']

    buckets_sums[bucket] += amount

summary_buckets = pd.Categorical(
    buckets,
    categories= bucket_lables,
    ordered = True
)

summary_assets = pd.DataFrame({
    'Bucket': bucket_lables,
    'amount': [buckets_sums[bucket] for bucket in bucket_lables]
})
summary_assets['cumulative sum'] = summary_assets['amount'].cumsum()

month_assets=0
for i in range(0,3):
    month_assets += summary_assets['amount'].iloc[i]

year_asset=0
for i in range(0,6):
    year_asset += summary_assets['amount'].iloc[i]

WAM = (assets['amount']*delta_time).sum()/(assets['amount']).sum()


print(f"Процент активов погашаемый в течение 30дней: {month_assets/assets['amount'].sum(): .2%}, \n Процент активов погашаемый в течение первого года: {year_asset/assets['amount'].sum(): .2%}, \n Wheighted avarage maturity (days): {WAM: .2f}")

plt.bar(bucket_lables, summary_assets['amount'])
plt.plot(summary_assets['cumulative sum'])
plt.xlabel('Сроки возвращения активов')
plt.ylabel('Сумма активов')
plt.show()