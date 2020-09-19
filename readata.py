import pandas as pd
import datetime as dt

def read_data(f):
    df=pd.read_csv(f)
    df['DATETIME']=pd.to_datetime(df['DATETIME'],format="%Y-%m-%d %H:%M:%S.%f")
    df['DATE']=df['DATETIME'].dt.date
    return df
