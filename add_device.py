import pandas as pd
import datetime as dt
import intervals as iv
from importlib import reload
from wgs84ch1903 import coord



df=pd.read_csv("./csv/Lagmut_definitivo.csv")
df['DEVICE']=df['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[0]


if __name__=="__main__":
    df.to_csv("./csv/Lagmut_orig_dev.csv")
