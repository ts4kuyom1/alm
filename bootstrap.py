import pandas as pd
import numpy as np
import matplotlib as plt

data = pd.DataFrame({ 
    'maturity': np.array([0.5, 1, 1.5, 2, 2.5]),
    'coupon': np.array([0.05, 0.06, 0.07, 0.075, 0.08]),
    'nominal': np.array([1000, 1000, 1000, 1000, 1000]),
    'price': np.array([998, 1002, 1005, 1000, 995])
})

zero_rates = np.zeros(len(data))

for i, bond in data.iterrows():
    T =float(bond['maturity'])
    N = int(round(2*T))
    coupon_cf = bond['coupon']*bond['nominal']/2
    nominal = bond['nominal']
    price = bond['price']

    pv_known = sum(coupon_cf/(1+(zero_rates[j]/2))**(j+1) for j in range (N-1))
    pv_last = price - pv_known
    cf_last = coupon_cf + nominal

    zero_rates[i] = 2*((cf_last/pv_last)**(1/N) - 1)
data['zero rates'] = zero_rates
data['par rates'] = data['coupon']
data['discount factor'] = (1/(1+data['zero rates']/2)**(2*data['maturity']))
print(data)