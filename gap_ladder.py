import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

assets = pd.DataFrame({
    'type': ['Overnight МБК', 'Корп. кредит А', 'Корп. кредит Б', 'ОФЗ 26207', 'Корп. кредит В', 'Ипотечный транш 1', 'Корп. бонд X', 'ОФЗ 26212', 'Ипотечный транш 2', 'Корп. кредит Г', 'ОФЗ 26230', 'Ипотечный транш 3'],
    'amount': np.array([150, 200, 300,500, 400, 800, 350, 600, 1200, 450, 700, 900]),
    'maturity': ['2026.10.26', '2026.10.30', '2026.11.17', '2026.12.22', '2027.01.22', '2027.03.17', '2027.06.12', '2027.10.25', '2028.04.17', '2029.01.12', '2030.06.17', '2032.05.22']
})

assets['maturity'] = pd.to_datetime(assets['maturity'], format='%Y.%m.%d')
today = pd.to_datetime('2026.10.25', format='%Y.%m.%d')

delta_time_assets = pd.to_timedelta(assets['maturity'] - today).dt.days

buckets_edjes = [0, 1, 7, 30, 90, 180, 365, 720, 1825, float('inf')]
buckets_labels = ['O/N', '2D-7D', '8D-1M', '1M-3M', '3M-6M', '6M-1Y', '1Y-2Y', '2Y-5Y', '>5Y']
buckets_assets = pd.cut(
    delta_time_assets,
    buckets_edjes,
    labels=buckets_labels
)
assets['buckets'] = buckets_assets

liability = pd.DataFrame({
    'type': ['Текущие счета физлиц', 'Overnight МБК привлечённый', 'Срочные вклады 3M', 'Срочные вклады 6M', 'Срочные вклады 1Y', 'МБК привлечённый 3M', 'Выпущенные облигации 2Y', 'Выпущенные облигации 3Y', 'Выпущенные облигации 5Y', 'Субординированный долг'],
    'amount': np.array([2000, 300, 800, 600, 500, 400, 500, 400, 300, 250]),
    'maturity': ['2026.11.26', '2026.10.27', '2027.01.25', '2027.04.25', '2027.10.25', '2027.04.25', '2027.01.25', '2029.10.25', '2031.10.25', '2033.10.25']
})
liability['maturity'] = pd.to_datetime(liability['maturity'], format='%Y.%m.%d')
delta_time_liabilities = pd.to_timedelta(liability['maturity'] - today).dt.days

buckets_liability = pd.cut(
    delta_time_liabilities,
    buckets_edjes,
    labels= buckets_labels
)
liability['buckets'] = buckets_liability

assets_by_bucket = assets.groupby('buckets')['amount'].sum()
liability_by_bucket = liability.groupby('buckets')['amount'].sum()

gap_ladder = pd.DataFrame({
    'assets in bucket': assets_by_bucket,
    'liabilities in bucket': liability_by_bucket,
    'cumulative assets': assets_by_bucket.cumsum(),
    'cumulative liabilities': liability_by_bucket.cumsum(),
    'gap in bucket': assets_by_bucket - liability_by_bucket,
    'cumulative gap': (assets_by_bucket-liability_by_bucket).cumsum()
})

short_term_buckets = ['O/N', '2D-7D', '8D-1M']

st_assets = 0
st_liabilities = 0
for i in range(0, 3):
    st_assets += gap_ladder['assets in bucket'][i]
    st_liabilities += gap_ladder['liabilities in bucket'][i]

st_gap = st_assets - st_liabilities

year_gap = 0
for i in range(0, 6):
    year_gap += (gap_ladder['assets in bucket'].iloc[i] - gap_ladder['liabilities in bucket'].iloc[i])

lt_gap = 0
for i in range(6, 9):
    lt_gap += (gap_ladder['assets in bucket'].iloc[i] - gap_ladder['liabilities in bucket'].iloc[i])

for i in range(len(gap_ladder)):
    if gap_ladder['cumulative gap'].iloc[i] < 0:
        print(gap_ladder.iloc[[i]])

print(st_gap, year_gap, lt_gap)
print(np.isclose(lt_gap+year_gap, assets['amount'].sum()-liability['amount'].sum()))
print(f"Активы: \n {assets}")
print(f"Обязательства: \n {liability}")
print(f"Ликвидность: \n {gap_ladder}" )


