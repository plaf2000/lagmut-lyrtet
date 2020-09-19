import pandas as pd
import datetime as dt
import intervals as iv

df=pd.read_csv("./csv/Lagmut_definitivo.csv")
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

df['TO_INCLUDE']=df.T.apply(lambda x:  iv.intervals[dt.datetime.strftime(x['DATETIME'],'%d-%m-%Y')].loc['inter_start_dt'] <= x['DATETIME'] <= iv.intervals[dt.datetime.strftime(x['DATETIME'],'%d-%m-%Y')].loc['inter_end_dt'])

df=df.drop(['DATE-12','TIME-12','HOUR-12','ORGID','USERID','REVIEW ORGID','REVIEW USERID'], axis = 1)

df['DEVICE']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[0]
df['COORDX']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[-1].str.split('-').str[0]
df['COORDY']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[-1].str.split('-').str[1]

bool_gt1=None
multi_calls=df['MANUAL ID*'].str.contains('calls')
calls=['CALL_1','CALL_2','CALL_3','CALL_4','FEMALE']

for call_name in calls:
    df[call_name]=0
    pat=call_name.lower().replace('_','')
    df.loc[df['MANUAL ID*'].str.contains(pat),call_name]= 1
    if call_name!='FEMALE':
        call_num=call_name.split("_")[1]
        df.loc[multi_calls,call_name]=df.loc[multi_calls,'MANUAL ID*'].str.split(pat='_').str[-1].str.count(call_num)

df['INDIVIDUALS']=df[calls].sum(axis=1)



if __name__=="__main__":
    df.to_csv("./csv/Lagmut.csv")
