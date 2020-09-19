import pandas as pd
import datetime as dt
import intervals as iv

lyrtet=pd.read_csv("Lyrtet_rugolio_definitivo.csv")
lyrtet['DATETIME']=lyrtet['DATE']+" "+lyrtet['TIME']
lyrtet['DATETIME']=pd.to_datetime(lyrtet['DATETIME'],format="%Y-%m-%d %H:%M:%S.%f")
lyrtet=lyrtet.sort_values(by='DATETIME')
lyrtet['DATE']=lyrtet['DATETIME'].dt.date
lyrtet['DAY']=(lyrtet['DATETIME'].dt.month-4)*30+lyrtet['DATETIME'].dt.day
lyrtet['5_DAY']=(lyrtet['DAY']/5).astype(int)*5
# lyrtet['SECONDS']=lyrtet['DATETIME'].dt.time
lyrtet['SECONDS']=lyrtet['DATETIME'].dt.hour*3600+lyrtet['DATETIME'].dt.minute*60+lyrtet['DATETIME'].dt.second+lyrtet['DATETIME'].dt.microsecond/10**6

lyrtet['LUCOMAGNO']=lyrtet.FOLDER.apply(lambda x: 'Lucomagno' in x)
lyrtet['RIEDERALP']=lyrtet.FOLDER.apply(lambda x: 'Riederalp' in x)

lyrtet['TO_INCLUDE']


lyrtet_lucomagno=lyrtet[lyrtet['LUCOMAGNO']]
lyrtet_riederalp=lyrtet[lyrtet['RIEDERALP']]
