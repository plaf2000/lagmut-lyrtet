import datetime as dt
import readata as rd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import sunriseset as srst
from importlib import reload
import matplotlib.dates as mdates


register_matplotlib_converters()

fig, axes = plt.subplots(2, 1,figsize=(50, 200),sharex=False)

x_start,x_end=[],[]

frac_h=1/12
hstart=3
hend=11
restr=True
call_filter='call 4'

data=rd.read_data("./csv/Lagmut.csv")

cf=None

if type(call_filter) is str and call_filter!='':
    cf=call_filter.upper().replace(" ","_")
    if cf in data.columns:
        data=data.loc[data[cf]>0]

if cf is None:
    cf = 'INDIVIDUALS'



for name, ax in zip(['Riederalp','Lucomagno'], axes):
    if name=='Riederalp':
        loc=srst.loc_astral(name,'Valais',46.39536, 8.04805, elevation=2300)
    elif name=='Lucomagno':
        loc=srst.loc_astral(name,'Ticino',46.55321, 8.78278, elevation=2300)

    lagmut=data.loc[data[name.upper()]].copy()

    start=lagmut['DATETIME'].iloc[0].date()
    end=lagmut['DATETIME'].iloc[-1].date()+dt.timedelta(days=2)
    x_start.append(start)
    x_end.append(end)
    x=np.arange(start, end, dt.timedelta(days=1)).astype(dt.datetime)

    lagmut['FRAC_HOUR']=lagmut['HOUR'].astype(float)+(lagmut['DATETIME'].dt.minute/(60*frac_h)).astype(int)*frac_h


    y=np.arange(hstart,hend,step=frac_h)
    z=np.zeros((len(y),len(x)))
    lagmut=lagmut.set_index('DATE')

    index_date=0
    for d in x[:-1]:
        date=d.date()
        try:
            this_date=lagmut.loc[date]
            if type(this_date['FRAC_HOUR']) is not np.float64:
                count=this_date[['FRAC_HOUR',cf]].groupby(['FRAC_HOUR']).sum()
                # count=this_date['FRAC_HOUR'].value_counts()
                for i in count.index:
                    index_time=int((i-hstart)*(1/frac_h))
                    if index_time<z.shape[0]:
                        z[index_time,index_date]=count.loc[i]
        except KeyError:
            print(date)
        index_date+=1
    ax.set_ylabel('Hour')
    ax.set_title(name)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))


    if ax == axes[-1]:
        ax.set_xlabel('Date', labelpad=20)
    else:
        labels =['']*len(x)
        ax.get_xaxis().set_ticks([])

    print(z.max())
    ax.pcolor(x,y,z,cmap='Greys',vmax=27)


'''
start, end=[],[]

'''
global_start=min(x_start)
global_end=max(x_end)
xlim=[global_start,global_end]
global_x=np.arange(global_start, global_end, dt.timedelta(days=1)).astype(dt.datetime)+dt.timedelta(hours=12)

sunrises=[]

srs_start=global_start-dt.timedelta(days=1)
srs_end=global_end+dt.timedelta(days=1)
sunrises_x=np.arange(srs_start, srs_end, dt.timedelta(days=1)).astype(dt.datetime)+dt.timedelta(hours=12)

for date in sunrises_x:
    sr=loc.sunrise(date)
    sr=sr.hour+sr.minute/60
    sunrises.append(sr)


for ax in axes:
    # ax.plot(global_x,sunrises)
    ax.fill_between(sunrises_x, sunrises, ax.get_ylim()[1],facecolor='yellow', alpha=0.075)
    ax.fill_between(sunrises_x, sunrises, ax.get_ylim()[0],facecolor='blue', alpha=0.075)
    # ax.set_xlim([global_start,global_end])
    ax.set_xlim(xlim)
# x=np.arange(max(start),min(end),dt.timedelta(days=1)).astype(dt.datetime)
subtitle=call_filter if type(call_filter) is str and call_filter!='' else 'all calls'
plt.suptitle(r"$\bf{Rock\ ptarmigan\ }$"+r"$\it{Lagopus\ muta}$"+'\n'+subtitle,fontsize=18)
plt.subplots_adjust(bottom=0.15, top=0.85)
plt.xticks(global_x,rotation=90)
# plt.xticks(x)
plt.show()
