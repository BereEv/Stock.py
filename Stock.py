# -*- coding: utf-8 -*-


import glob
import pathlib as pl

import warnings
import pandas as pd
import requests

import Curents
from readSkuStock import Join_DFStock

#  ключи кабинетов для Api Ozon
headers = {"Client-Id": "", "Api-Key": ""}



#  Берем из сайта ЦБ.рф курсы евро
Curents
# noinspection PyArgumentList


def curents():
    #  Берем курс цб РФ из файла созданный скриптом Curents
    dfc = pd.read_excel('log/curents.xlsx', decimal=',').drop(columns=['Unnamed: 0', 'Id', 'Nominal'])
    print(dfc[-7:])
    #  Спрашиваем как пользователь хочет считать курс
    print('Выбираем дату из списка или вводим в ручную?')
    answer = {'Д', 'Н'}
    #  исключаем ошибку при введении неверного значения
    while answer != 'Д' and answer != 'Н':
        answer = input('Введите Д/Н:    ')
        answer = answer.upper()
        continue
    if answer == 'Д':
        date = input('На какую дату считать курс из списка дд.мм.гггг?  ')
        date = date.replace(',', '.')
        #  Если нет курса на понедельник берем на ближайшую дату до него
        dfc.loc[dfc['Date'] != date] = dfc.iloc[[-1]]
        dfc.loc[dfc['Date'] == date]
        dfc = dfc.dropna().reset_index().drop(columns=['index'])
        dfc = dfc['Value'][0]
        print(dfc)
    elif answer == 'Н':
        dfc = float(input('Введите курс:   '))
        print(dfc)
    return dfc


# noinspection PyArgumentList

#  Читаем файл себестоимости, апка на 6 - й строке

# noinspection PyArgumentList
def read_sales() -> [print('read sales')]:
    #  читаем и объединяем файлы по отчету продаж
    warnings.simplefilter("ignore")
    dfs = [pd.read_excel(f, header=0) for f in pl.Path.cwd().glob('sales/*.xlsx')]
    sales = pd.concat(dfs, keys=glob.glob1('sales', '*xlsx')).reset_index(level=0).reindex(
    ).rename(columns={'level_0': 'Name'})
    #  Собираем в один столбец данные по логистике
    #  sales.info()
    sales['Логистика'] = sales.iloc[:, 14:23].sum(axis=1) * -1
    #  данный столбец нужен для продаж и возврата
    sales['Кол-во'] = 0
    sales.loc[sales['Тип начисления'] == 'Получение возврата, отмены, невыкупа от покупателя', 'Кол-во'] = -1
    sales.loc[sales['Тип начисления'] == 'Доставка покупателю', 'Кол-во'] = 1
    sales['Кол-во'] = sales['Кол-во'] * sales['Количество']
    #  считаем кол-во операций по организации
    sales_c = sales['Name'].value_counts().rename_axis('Name').reset_index(name='Count')
    sales = sales.join(sales_c.set_index('Name'), on='Name')
    # считаем сумму логистики по организации
    salesl = sales.groupby('Count').sum('Логистика').reset_index().rename(
        columns={'Логистика': 'SumLog',
                 'Количество': 'Кол-во по орг'}).filter(items={'Count', 'SumLog', 'Кол-во по орг'})
    salesl.to_excel('log/sumlog.xlsx')
    # считаем кол-во операций без продаж
    salesNonsale = sales.loc[sales['Тип начисления'] == 'Доставка и обработка возврата, отмены, невыкупа']
    salesNonsale = salesNonsale.groupby(['Name']).count().reset_index(
    ).filter(items=['Name', 'Count']).rename(columns={'Count': 'Count1'})
    salesNonsale.to_excel('log/nonsales.xlsx')
    #  salesNonsale1 = sales.loc[sales['Тип начисления'] == 'Получение возврата, отмены, невыкупа от покупателя']
    #  salesNonsale1 = salesNonsale1.groupby(['Name']).count().reset_index(
    #  ).filter(items=['Name', 'Count']).rename(columns={'Count': 'Count2'})
    sales = sales.join(salesl.set_index('Count'), on='Count')
    sales = sales.join(salesNonsale.set_index('Name'), on='Name')
    #  sales = sales.join(salesNonsale1.set_index('Name'), on='Name')
    sales = sales.fillna(value={'Count1': 0})
    #  считаем среднюю доставку по кабинету
    try:
        sales['Logistic'] = sales['SumLog'] / (
                    sales['Count'] - sales['Count1'] - (sales['Count'] - sales['Кол-во по орг']))
    except KeyError:
        sales['Кол-во по орг'] = 0
        sales['Logistic'] = 0
    sales['К перечислению - комиссия и логистика'] = sales[
                                                         'За продажу или возврат до вычета комиссий и услуг'] - sales[
                                                         'Logistic'] + sales['Комиссия за продажу']
    sales.loc[sales['Кол-во'] == 0, 'К перечислению - комиссия и логистика'] = 0
    sales.to_excel('log/sale.xlsx')
    return sales


def transaction(name_headers):
    """Берем из Api данные по РРЦ из метода: Получить список товаров по идентификаторам"""
    try:
        #  берем из отчета по продажам список SKU как индефикатор товара
        data = read_sales()['SKU'].dropna().astype(int)
        data = data.to_list()
        #  print(data)
        data1 = {'sku': data}
        request = requests.post('https://api-seller.ozon.ru/v2/product/info/list', headers=name_headers, json=data1)
        #  print(request.content)
        request = pd.json_normalize(request.json(
        )['result']['items']).melt(id_vars=['id', 'name', 'offer_id', 'barcode', 'buybox_price', 'category_id',
                                            'created_at', 'images', 'marketing_price', 'min_ozon_price', 'old_price',
                                            'premium_price',
                                            'price', 'recommended_price', 'min_price', 'sources', 'errors', 'vat',
                                            'visible', 'price_index', 'images360', 'color_image', 'primary_image',
                                            'state',
                                            'service_type', 'stocks.coming', 'stocks.present', 'stocks.reserved',
                                            'visibility_details.has_price', 'visibility_details.has_stock',
                                            'visibility_details.active_product', 'status.state', 'status.state_failed',
                                            'status.moderate_status', 'status.decline_reasons',
                                            'status.validation_state',
                                            'status.state_name', 'status.state_description', 'status.is_failed',
                                            'status.is_created', 'status.state_tooltip', 'status.item_errors',
                                            'status.state_updated_at']).dropna(subset=['value']).fillna(value=0)
        request = request.rename(columns={'value': 'sku'})
        return request
    except ValueError:
        pass
    except KeyError:
        print(request.status_code, request.content, name_headers)
        pass


dfs = (transaction(headers),

pd.concat(dfs, keys=['transaction(headers)',
                     ]).reset_index().drop(columns=['level_1']).to_excel('log/prod.xlsx')


# noinspection PyArgumentList


def join_sales_product_STOCK():
    prod = pd.read_excel('log/prod.xlsx')
    prod = pd.DataFrame(prod).rename(columns={'sku': 'SKU'}).dropna(subset='SKU')
    prod = read_sales().join(prod.set_index('SKU'), on='SKU').rename(
        columns={'offer_id': 'Артикул1'}).join(Join_DFStock().set_index('Артикул'), on='Артикул')
    prod[['Art1', 'Art2']] = prod['Артикул'].str.split('-', n=1, expand=True).fillna(value='N-a')
    prodShortIndex = Join_DFStock()[['Art1', 'Стоимость', 'Марка (бренд)', 'Вид номенклатуры', 'Товарная категория',
                                     'Номенклатура']]
    prodShortIndex[['Модель', 'Цвет', 'Размер']] = prodShortIndex['Номенклатура'].str.rsplit(';', n=2, expand=True)
    prodShortIndex = prodShortIndex.drop(columns=['Номенклатура', 'Товарная категория', 'Цвет', 'Размер'])
    prodShortIndex = prodShortIndex.drop_duplicates(subset='Art1')
    prodShortIndex.info()
    prod = prod.join(prodShortIndex.set_index('Art1'), on='Art1', rsuffix='_sh')
    prod['Курс'] = curents()
    prod = prod.fillna(value={'Марка (бренд)': prod['Марка (бренд)_sh'],
                              'Номенклатура': prod['Модель'],
                              'Вид номенклатуры': prod['Вид номенклатуры_sh'],
                              'Стоимость': prod['Стоимость_sh']})
    prod['Себестоимость_руб'] = prod['Стоимость'] * prod['Курс'] * prod['Кол-во']
    name_columns = 'Себестоимость_руб', 'old_price', 'К перечислению - комиссия и логистика'
    prod.loc[prod['Кол-во'] == 0, name_columns] = 0
    prod = prod.drop(columns=['Count', 'SumLog', 'Кол-во по орг', 'Count1', 'Unnamed: 0', 'images', 'vat',
                              'service_type', 'stocks.coming', 'stocks.present', 'stocks.reserved', 'barcode',
                              'status.moderate_status', 'status.decline_reasons', 'status.validation_state', 'sources',
                              'errors', 'visible', 'price_index', 'images360', 'color_image', 'primary_image', 'state',
                              'visibility_details.has_price', 'visibility_details.has_stock', 'created_at', 'level_0',
                              'visibility_details.active_product', 'status.state', 'status.state_failed',
                              'status.state_name', 'status.state_description', 'status.is_failed', 'status.is_created',
                              'status.state_tooltip', 'status.item_errors', 'status.state_updated_at', 'variable'])
    prod.to_excel('log/q1.xlsx', float_format='%.2f')


join_sales_product_STOCK()
