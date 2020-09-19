import pandas as pd
import datetime as dt

intervals=pd.read_csv("./csv/intervalli_registrazione_VS_TI.csv")
intervals=intervals.set_index('Data')




intervals.loc['inter_start_dt']=pd.to_datetime(intervals.loc['inter_start'].index+" "+intervals.loc['inter_start'],format='%d-%m-%Y %H:%M')
intervals.loc['inter_end_dt']=pd.to_datetime(intervals.loc['inter_end'].index+" "+intervals.loc['inter_end'],format='%d-%m-%Y %H:%M')
