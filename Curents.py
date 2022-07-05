import pandas as pd

CB = pd.read_xml(
    'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/02/2022&date_req2=28/02/2032&VAL_NM_RQ=R01239')
pd.DataFrame(CB)
#print(CB)
CB.to_excel('log/curents.xlsx')