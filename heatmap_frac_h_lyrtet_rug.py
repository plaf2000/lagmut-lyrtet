import datetime as dt
import readlyrtet as data
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import sunriseset as srst
from importlib import reload
import matplotlib.dates as mdates


srst = reload(srst)

register_matplotlib_converters()

fig, axes = plt.subplots(2, 1,figsize=(50, 200),sharex=False)

x_start,x_end=[],[]

frac_h=1/20

for name, ax in zip(['Riederalp','Pian Segno'], axes):
    if name=='Riederalp':
        maxh=11
        lyrtet=data.lyrtet_riederalp.copy()
        loc=srst.loc_astral(name,'Valais',46.38807, 8.03235, elevation=2200)
    elif name=='Pian Segno':
        maxh=11
        lyrtet=data.lyrtet_lucomagno.copy()
        loc=srst.loc_astral(name,'Ticino',46.52078, 8.84335, elevation=1900)
    start=lyrtet['DATETIME'].iloc[0].date()
    end=lyrtet['DATETIME'].iloc[-1].date()+dt.timedelta(days=2)
    x_start.append(start)
    x_end.append(end)
    x=np.arange(start, end, dt.timedelta(days=1)).astype(dt.datetime)

    lyrtet['FRAC_HOUR']=lyrtet['HOUR'].astype(float)+(lyrtet['DATETIME'].dt.minute/(60*frac_h)).astype(int)*frac_h


    y=np.arange(3,maxh,step=frac_h)
    z=np.zeros((len(y),len(x)))
    lyrtet=lyrtet.set_index('DATE')

    index_date=0
    for d in x[:-1]:
        date=d.date()
        try:
            this_date=lyrtet.loc[date]
            if type(this_date['FRAC_HOUR']) is not np.float64:
                count=this_date['FRAC_HOUR'].value_counts()
                for i in count.index:
                    index_time=int((i-3)*(1/frac_h))
                    if index_time<z.shape[0]:
                        z[index_time,index_date]=count.loc[i]
        except KeyError:
            print(date)
        index_date+=1
    ax.set_ylabel('Hour')
    ax.set_title(name)


    if ax == axes[-1]:
        ax.set_xlabel('Date', labelpad=20)
    else:
        labels =['']*len(x)
        ax.get_xaxis().set_ticks([])


    ax.pcolor(x,y,z,cmap='Greys')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))


'''
start, end=[],[]

'''
global_start=min(x_start)
global_end=max(x_end)
xlim=[global_start,global_end]
# xlim=[dt.datetime(2020,4,19,0,0,0),dt.datetime(2020,5,18,0,0,0)]
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

plt.suptitle(r"$\bf{Black\ grouse\ }$"+r"$\it{Lyrurus\ tetrix}$"+"\n\"cooing\" call",fontsize=18)
# plt.suptitle('"cooing" call')
plt.xticks(global_x,rotation=90)
plt.subplots_adjust(bottom=0.15, top=0.85)
# plt.tight_layout()
# plt.xticks(x)
plt.show()
