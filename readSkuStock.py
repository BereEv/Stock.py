import pandas as pd
import warnings


warnings.simplefilter('ignore')

# noinspection PyArgumentList
if 'main' == 'name':
    'name'

#  Читаем файл себестоимости, апка на 6 - й строке
def read_stock() -> [print('read Stock')]:
    df = pd.read_excel('data/stock.xlsx', header=6, decimal=',', engine='openpyxl')
    #  Убираем из названия столбца пробелы до и после названия, переименоваем столбцы
    df = df.rename(columns=lambda x: x.strip()).rename(
        columns={'Номенклатура.Артикул': 'Артикул'}).drop_duplicates(subset='Артикул')
    # Узнаем стоимость 1 ед товара
    df['Стоимость'] = df['Стоимость общая'] / df['Остаток']
    df = df.filter(items=['Артикул', 'Стоимость'])
    #  Запишем результат в эксэль
    df.to_excel('log/stock.xlsx')
    return df


def stockShort():
    """Отделяем от артикула размер и цвет чтобы если по полному артикулу нет стоимости можно было искать по модели"""
    df1 = (read_stock()).copy()
    df1[['Art1', 'Art2']] = df1['Артикул'].str.split('-', n=1, expand=True)
    df1 = df1.drop(columns=['Артикул', 'Art2']).dropna().rename(columns={'Стоимость': 'Стоимость1'})
    df1 = df1.groupby(['Art1']).mean(['Стоимость1']).reset_index()
    df1.to_excel('log/stockShort.xlsx'), print('save to log/stockShort.xlsx')
    print('save to log/stock.xlsx')
    return df1


# noinspection PyArgumentList

#  Читаем файл с отчетом по штрихкодами т.к. там есть вся номенклатура
def read_Sku() -> [print('read sku')]:
    sku = pd.read_excel('data/sku-list.xlsx', header=0, engine='openpyxl')
    # убираем пробелы до и после названия столбца, убираем дубликаты артикулов, сбрасываем ненужные столбцы
    sku = sku.rename(columns=lambda x: x.strip()).drop_duplicates('Артикул').drop(columns=['Код ТНВЭД'])
    #  убираем пустые значения в артикулах чтобы номенклатура не лезла в услуги
    sku = sku.dropna(subset={'Артикул', 'Марка (бренд)'})
    sku = sku.astype({'Штрихкод': str})
    #  Отделяем от артикула размер и цвет чтобы если по полному артикулу нет стоимости можно было искать по модели
    sku[['Art1', 'Art2']] = sku['Артикул'].str.split('-', n=1, expand=True)
    sku['Штрихкод'] = sku['Штрихкод'].str.strip()
    return sku


def Join_DFStock() -> [print('join sku and stock')]:
    """объединяем sku и stock"""
    sku = read_Sku().join(
        read_stock().set_index('Артикул'), on='Артикул').join(stockShort().set_index('Art1'), on='Art1')
    sku = sku.fillna(value={'Стоимость': 0, 'Стоимость1': 0})
    sku.loc[sku['Стоимость'] == 0, 'Стоимость'] = sku['Стоимость1'] - sku['Стоимость']
    sku = sku.loc[sku['Стоимость'] != 0]
    #sku = sku.drop(columns=['Стоимость1'])
    sku = sku.astype({'Штрихкод': 'str'})
    sku.to_excel('log/sku.xlsx')
    print('save to log/sku.xlsx')
    return sku
