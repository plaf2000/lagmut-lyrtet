import pandas as pd
import datetime as dt
import intervals as iv
from importlib import reload
from wgs84ch1903 import coord



sof=pd.read_csv("./csv/Lyrtet_soffio_definitivo.csv")
rug=pd.read_csv("./csv/Lyrtet_rugolio_definitivo.csv")
fem=pd.read_csv("./csv/Lyrtet_female_definitivo.csv")
df=pd.concat([sof,rug,fem])
df['DATETIME']=df['DATE']+" "+df['TIME']
df['DATETIME']=pd.to_datetime(df['DATETIME'],format="%Y-%m-%d %H:%M:%S.%f")
df=df.sort_values(by='DATETIME')
df['DATE']=df['DATETIME'].dt.date
df['DAY']=(df['DATETIME'].dt.month-4)*30+df['DATETIME'].dt.day
df['5_DAY']=(df['DAY']/5).astype(int)*5
# df['SECONDS']=df['DATETIME'].dt.time
df['SECONDS']=df['DATETIME'].dt.hour*3600+df['DATETIME'].dt.minute*60+df['DATETIME'].dt.second+df['DATETIME'].dt.microsecond/10**6

# df['LUCOMAGNO']=df.FOLDER.apply(lambda x: 'Lucomagno' in x)
# df['RIEDERALP']=df.FOLDER.apply(lambda x: 'Riederalp' in x)
df['LUCOMAGNO']=df['FOLDER'].str.contains('Lucomagno')
df['RIEDERALP']=df['FOLDER'].str.contains('Riederalp')

# df['TO_INCLUDE']=df.T.apply(lambda x:  iv.intervals[dt.datetime.strftime(x['DATETIME'],'%d-%m-%Y')].loc['inter_start_dt'] <= x['DATETIME'] <= iv.intervals[dt.datetime.strftime(x['DATETIME'],'%d-%m-%Y')].loc['inter_end_dt'])

df=df.drop(['DATE-12','TIME-12','HOUR-12','ORGID','USERID','REVIEW ORGID','REVIEW USERID'], axis = 1)

df['DEVICE']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[0]
df['COORDX']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[-1].str.split('-').str[0]
df['COORDY']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[-1].str.split('-').str[1]
df['COORDX']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[-1].str.split('-').str[0]
df['COORDY']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[-1].str.split('-').str[1]
coord=df[['COORDX','COORDY']].apply(lambda x: coord(x[1],x[0]).to_wgs().get(),axis=1)
df['LATITUDE']=coord.str[0]
df['LONGITUDE']=coord.str[1]

calls=['COOING','HISS','FEMALE']

calls_label={
    'COOING': 'Lyrtet_rugolio',
    'HISS': 'Lyrtet_soffio',
    'FEMALE': 'Lyrtet_female',
}

for call_name in calls:
    df[call_name]=0
    pat=calls_label[call_name]
    df.loc[df['MANUAL ID*'].str.contains(pat),call_name]= 1





if __name__=="__main__":
    df.to_csv("./csv/Lyrtet.csv")
