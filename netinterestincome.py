import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#задаем датафреймы
assets = pd.DataFrame({
    'name': ['Loan to A', 'Loan to B', 'Mortgage', 'Interbank loan', 'OFZ-floater', 'OFZ-fixed'],
    'amount, mln. Rub': np.array([500, 300, 800, 200, 400, 300]),
    'rate, %': np.array([0.12, 0.105, 0.095, 0.08, 0.078, 0.085]),
    'type': ['fixed', 'fixed', 'fixed', 'floating(1M)', 'floating(3M)', 'fixed']
}
)

liabilities = pd.DataFrame({
    'name': ['Deposits', 'Cash', 'Interbank credit', 'Bonds'],
    'amount, mln. Rub': np.array([1200, 400, 500, 300]),
    'rate, %': np.array([0.07, 0.02, 0.075, 0.08]),
    'type': ['fixed', 'fixed', 'floating(1M)', 'fixed']
}
)

#Считаем Капитал
equity = assets['amount, mln. Rub'].sum() - liabilities['amount, mln. Rub'].sum()
#Расчет NII, NIM
interest_income = (assets['amount, mln. Rub']*assets['rate, %']).sum()
interest_expense = (liabilities['amount, mln. Rub']*liabilities['rate, %']).sum()
NII_base = (interest_income - interest_expense)
Net_Interest_Margin = NII_base/(assets['amount, mln. Rub'].sum())

#Расчет шоковых ставок для флоутеров и датафрейма для флоутеров
shock_rates_assets = np.zeros(len(assets['rate, %']))
floating_assets = pd.DataFrame(columns=[
    'name',
    'amount, mln. Rub',
    'rate, %',
    'shock rate, %'
])

for i, row in assets.iterrows():
    if 'floating' in row['type']:
        shock_rates_assets[i] = assets['rate, %'][i] + 0.02
        floating_assets.loc[i] = {
            'name': row['name'],
            'amount, mln. Rub': row['amount, mln. Rub'],
            'rate, %': row['rate, %'],
            'shock rate, %': shock_rates_assets[i] 
        }
    else:
        shock_rates_assets[i] = assets['rate, %'][i]
assets['shock rate, %'] = shock_rates_assets

#Расчет шоковых ставок для флоутеров и датафрейма
shock_rates_liabilities = np.zeros(len(liabilities['rate, %']))
floating_liabilities = pd.DataFrame(columns=[
    'name',
    'amount, mln. Rub',
    'rate, %',
    'shock rate, %'
])

for i, row in liabilities.iterrows():
    if 'floating' in row['type']:
        shock_rates_liabilities[i] = liabilities['rate, %'][i] + 0.02
        floating_liabilities.loc[i] = {
            'name': row['name'],
            'amount, mln. Rub': row['amount, mln. Rub'],
            'rate, %': row['rate, %'],
            'shock rate, %': shock_rates_liabilities[i] 
        }
    else:
        shock_rates_liabilities[i] = liabilities['rate, %'][i]
liabilities['shock rate, %'] = shock_rates_liabilities

#Расчет стрессовых показателей
interest_income_stress = (assets['amount, mln. Rub']*assets['shock rate, %']).sum()
interest_expense_stress = (liabilities['amount, mln. Rub']*liabilities['shock rate, %']).sum()
NII_stress = interest_income_stress - interest_expense_stress
Net_Interest_Margin_stress = NII_stress/(assets['amount, mln. Rub']).sum()

#Расчетов через repricing gap
gap = floating_assets['amount, mln. Rub'].sum()-floating_liabilities['amount, mln. Rub'].sum()
Delta_NII = gap*0.02


#Принты

print(f"Активы: \n {assets}")

print(f"Обязательства: \n {liabilities}")
 
print(f"Equity: {equity}, Процентный доход: {interest_income}, Процентный расход: {interest_expense}, NII: {NII_base: .2f}, NIM: {Net_Interest_Margin: .2%}")
print(f"Процентный доход при стрессе: {interest_income_stress}, Процентный расход при стрессе: {interest_expense_stress}, NII stress: {NII_stress: .2f}, NIM stress: {Net_Interest_Margin_stress: .2%}")
print(f"delta NII: {NII_stress-NII_base}. NII увеличился на 2 миллиона ввиду большего обьема активов, подверженных изменению процентных ставок(флоутеров) нежели обязательств. Таким образом рост ставок на 200 базисных пунктов обеспечил приток процентных дохов на 12 миллионов рублей, отток же увеличился на 10 миллионов. Банку сценарий повышения ставок оказался выгоден.")
print(f"Дельта NII через repriceing gap: {np.isclose(Delta_NII, (NII_stress-NII_base))}")

#Визуализация
assets_viz = assets[['name', 'rate, %']].copy()
assets_viz['side'] = 'assets'

liabilities_viz = liabilities[['name', 'rate, %']].copy()
liabilities_viz['rate, %'] = -liabilities_viz['rate, %']
liabilities_viz['side'] = 'liabilities'

combined = pd.concat([assets_viz, liabilities_viz]).reset_index(drop = True)
combined = combined.sort_values('rate, %')

colors = ['red' if s == 'liabilities' else 'green' for s  in combined['side']]
plt.barh(combined['name'], combined['rate, %'], color = colors)
plt.axvline(0, color = 'black', linewidth = 0.5)
plt.xlabel('Процентный доход/Расход, млн. рублей')
plt.title('Структура NII по инструментам')
plt.tight_layout()
plt.show()