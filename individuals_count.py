import datetime as dt
import readata as rd
import pandas as pd
import numpy as np

def for_sorting(output):
    return (output['datetime']-datetime.datetime(1970,1,1)).total_seconds()

td_min=4
site='Riederalp'
# site='Lucomagno'

delta=dt.timedelta(minutes=td_min)

if site=='Lucomagno':
    devs=['LM1','LM2','LM3']
else:
    devs=['LM4','LM5','LM6']


data=rd.read_data("./csv/Lagmut.csv")
place=data.loc[data[site.upper()]].copy()

output=pd.DataFrame(columns=['device', 'datetime','call'])
for main_dev in devs[:-1]:
    main_dev_data=data.loc[data['DEVICE']==main_dev].copy()
    place=place.drop(index=main_dev_data.index)
    for i_main_dev_data, row in main_dev_data.iterrows():
        t_main_dev_data=row['DATETIME']
        dist=place['DATETIME']-t_main_dev_data
        distance_abs=np.abs(dist)
        in_range=place.loc[distance_abs<delta]
        if not in_range.empty:
            if not i_main_dev_data in output.index:
                output=output.append(pd.DataFrame([[main_dev,t_main_dev_data,row['MANUAL ID*']]],columns=['device', 'datetime','call'],index=[i_main_dev_data]))
                # output=output.append({'index':i_main_dev_data,'device':main_dev,'datetime':t_main_dev_data},ignore_index=True)
            for i, ot in in_range.iterrows():
                if not i in output.index:
                    output=output.append(pd.DataFrame([[ot['DEVICE'],ot['DATETIME'],ot['MANUAL ID*']]],columns=['device', 'datetime','call'],index=[i]))
                    # output=output.append({'index':i,'device':ot['DEVICE'],'datetime':ot['DATETIME']},ignore_index=True)

sorted_out=output.sort_values(by='datetime').reset_index()

out_path='/home/plaf2000/Documenti/Lagmut_Lyrtet/csv/'+site+'_'+str(td_min)+'min.csv'
sorted_out.to_csv(out_path)

for s_i, s_r in sorted_out.iterrows():
    if s_i-1>0:
        if np.abs(s_r['datetime']-sorted_out['datetime'].iloc[s_i-1])>=delta:
            print()
    print(s_r['device'],s_r['datetime'].strftime('%d.%m %H:%M:%S.%f'),s_r['call'])
