
import pandas as pd


a = pd.read_excel('log\\sku-list.xlsx')
# убираем пробелы до и после названия 
a = a.rename(columns=lambda x: x.strip())
# считаем дубли
a1 = a['Артикул'].value_counts().rename_axis('Артикул').reset_index(name='counter')
a1 = a.join(a1.set_index('Артикул'), on='Артикул')
a1 = a1.groupby(['Артикул', 'Штрихкод']).mean('counter').reset_index().fillna(value='n-a')
a1 = a1.pivot_table(
    index='Артикул', values='Штрихкод', columns='counter', aggfunc=lambda x: 'разделитель'.join(x.dropna()))
a1['ColumnA'] = a1[0:].apply(lambda x: ''.join(x.dropna()), axis=1)
new_df = a1['ColumnA'].str.split(
    'разделитель', expand=True).rename(columns=lambda x: x+1).add_prefix('Штрихкод_').reset_index()
new_df = new_df.join(a.set_index('Артикул'), on='Артикул').drop(columns=['Штрихкод']).drop_duplicates('Артикул')
new_df.info()
#  assert isinstance(new_df.to_excel, object)
new_df.to_excel('log/result_sku.xlsx')
