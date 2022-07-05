import glob

import pathlib as pl
import pandas as pd
import warnings

from readSkuStock import *

# noinspection PyArgumentList

dfs = [pd.read_csv(
    f, header=0, sep=';', quotechar='"', doublequote=True) for f in pl.Path.cwd().glob('stock/products*.csv')]
stk = pd.concat(dfs, keys=glob.glob1('stock', '*csv')).reset_index(level=1, drop=True).rename_axis('Names').reset_index()
stk[['Art1', 'Art2']] = stk['Артикул'].str.split(pat='-', n=1, expand=True)
stk['Остаток'] = stk['Доступно на складе Ozon, шт'] + stk['Зарезервировано, шт']
stk = stk.loc[stk['Остаток'] != 0]
stk = stk.join(read_Sku().set_index('Артикул'), on='Артикул', rsuffix='_sku').join(
    stockShort().set_index('Art1'), on='Art1', rsuffix='_Sh').join(
    Join_DFStock().set_index('Артикул'), on='Артикул', rsuffix='_Stk')
stk = stk.fillna(value={'Стоимость': stk['Стоимость1'],
                        'Марка (бренд)_Stk': stk['Марка (бренд)']})
#  stk.loc[stk['Стоимость'] == 0, 'Стоимость1шт'] = stk['Стоимость1ед'] - stk['Стоимость']
stk['Стоимость'] = stk['Остаток'] * stk['Стоимость']
stk.loc[stk['Марка (бренд)_Stk'] == 'n-a', 'Марка (бренд)'] = stk['Бренд']
print('Записываем в log/stk.xlsx')
stk.to_excel('log/stock_Ozon.xlsx', float_format='%.2f')
