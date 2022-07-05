import requests
import pandas as pd

headers_Ultra = {"Client-Id": "53484", "Api-Key": "07c6065d-a04f-4150-8a9c-e883275961e5"}
headers_Lester = {"Client-Id": "3933", "Api-Key": "6d969891-d7c5-4845-b740-7260842dbd28"}
headers_TopSale = {"Client-Id": "129321", "Api-Key": "57bf369a-7434-4e4e-8035-b9cf9c9ef7d1"}
headers_RkRasha = {'Client-id': '227466', 'Api-Key': '0fea6dc8-0bd2-4a70-86a8-fe09d5333897'}
headers_Svell = {'Client-id': '22359', 'Api-Key': '037df650-7701-4085-ba6e-19d367876578'}

date_from = input('Введите начало периода ГГГГ-ММ-ДД    ') + "T00:00:00.000Z"
date_to = input('Введите конец периода ГГГГ-ММ-ДД     ') + "T00:00:00.000Z"


def transaction(name_headers):
    data = {"filter": {"date": {"from": date_from, "to": date_to},
                       "transaction_type": "all"}, "page": 1, "page_size": 1000}
    r = requests.post('https://api-seller.ozon.ru/v3/finance/transaction/list', headers=name_headers, json=data)
    try:
        tr = pd.json_normalize(r.json()['result']['operations'], ['items'], meta=[
            'operation_id', 'operation_type', 'operation_date', 'operation_type_name', 'delivery_charge',
            'return_delivery_charge', 'accruals_for_sale', 'sale_commission', 'amount', 'type'])
        #  posting = pd.json_normalize(r.json()['result']['operations'], meta=['posting'])
        tc = pd.json_normalize(r.json()['result']['operations'])
        tr = pd.DataFrame(tr)
        #print(tr['sku'])
        tr.to_excel('log/d.xlsx')
        tc.to_excel('log/c.xlsx')

        data1 = {'sku': list(tr['sku'])}
        request = requests.post('https://api-seller.ozon.ru/v2/product/info/list', headers=name_headers, json=data1)
        # print(request.content)
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
                                            'status.state_updated_at'])
        request = request.rename(columns={'value': 'sku'})
        return request
        request.to_excel('log/r.xlsx')

    except KeyError:
        pass


def get_info_product(name_headers):
    url = 'https://api-seller.ozon.ru/v2/product/info'
    data = {"offer_id": "",
            "product_id": 0,
            "sku": list['sku']}
    r = requests.post(url, headers=name_headers, json=data)
    print(r.status_code, r.content)


dfs = (transaction(headers_Ultra),
       transaction(headers_Lester),
       transaction(headers_TopSale),
       transaction(headers_RkRasha),
       transaction(headers_Svell))
pd.concat(dfs, keys=['transaction(headers_Ultra)',
                     'transaction(headers_Lester)',
                     'transaction(headers_TopSale)',
                     'transaction(headers_RkRasha)',
                     'transaction(headers_Svell)']).reset_index().drop(columns=['level_1']).to_excel('log/prod.xlsx')
