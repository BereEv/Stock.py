import glob

import pathlib as pl
import pandas as pd
import warnings

from readSkuStock import read_stock
from readSkuStock import stockShort

warnings
# noinspection PyArgumentList
#  Читаем файл с отчетом по штрихкодами т.к. там есть вся номенклатура


def read_Sku() -> [print('read sku')]:
    files = [pd.read_excel(f, header=0).rename(
        columns=lambda x: x.strip()) for f in pl.Path.cwd().glob('data/sku-list*.xlsx')]
    sku = pd.concat(files)
    sku = sku.drop(columns=['Код ТНВЭД']).drop_duplicates(subset='Штрихкод')
    #  Отделяем от артикула размер и цвет чтобы если по полному артикулу нет стоимости можно было искать по модели
    sku[['Art1', 'Art2']] = sku['Артикул'].str.split('-', n=1, expand=True)
    sku = sku.astype({'Штрихкод': 'str',
                      'Артикул': 'str'})
    sku['Штрихкод'] = sku['Штрихкод'].str.lstrip("'")
    return sku
# noinspection PyArgumentList


def read_files_S(num_header, name_directoty, name_col):
    dfs = [pd.read_excel(f, header=num_header) for f in pl.Path.cwd().glob(name_directoty + '/*xlsx')]
    stock = pd.concat(
        dfs, keys=glob.glob1(name_directoty,  '*xlsx')).reset_index(level=0).rename(columns={'level_0': 'Name'})
    stock = stock.astype({'Баркод': 'str'})
    stock[['Штрихкод', '1']] = stock['Баркод'].str.split('.', n=1, expand=True)
    stock = stock.join(read_Sku().set_index('Штрихкод'), on='Штрихкод', rsuffix='_r')
    stock[['Art1S', 'Art2S', 'Color', 'Size']] = stock['Артикул поставщика'].str.split('/', n=3, expand=True)
    stock['Art1S'] = stock['Art1S'].str.strip('.')
    stock['Art1S'] = stock['Art1S'].str.strip('-2')
    stock = stock.join(read_stock().set_index('Артикул'), on='Артикул', rsuffix='_st')
    stock = stock.join(stockShort().set_index('Art1'), on='Art1', rsuffix='_sh')
    stock = stock.fillna(value={'Стоимость': stock['Стоимость1'],
                                'Марка (бренд)': stock['Бренд'],
                                'Номенклатура_r': stock[name_col],
                                'Вид номенклатуры': stock['Предмет']})
    return stock


read_files_S(1, 'Остатки склад Wb', name_col='Наименование').to_excel(
    'log/stockWB.xlsx', engine='openpyxl', sheet_name='Stock')
with pd.ExcelWriter('log/stockWB.xlsx', engine='openpyxl', mode='a') as writer:
    read_files_S(0, 'ТОвары в пути', name_col='Предмет').to_excel(writer, sheet_name='Items_in_way')
print('Готово !')
