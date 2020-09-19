import datetime as dt
import readlagmut as data
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

fig, axes = plt.subplots(2, 1,figsize=(20, 20),sharex=False)

x_start,x_end=[],[]

for name, ax in zip(['Riederalp','Lucomagno'], axes):
    if name=='Riederalp':
        maxh=11
        lagmut=data.lagmut_riederalp
    elif name=='Lucomagno':
        maxh=11
        lagmut=data.lagmut_lucomagno
    start=lagmut['DATETIME'].iloc[0].date()
    end=lagmut['DATETIME'].iloc[-1].date()+dt.timedelta(days=2)
    x_start.append(start)
    x_end.append(end)
    x=np.arange(start, end, dt.timedelta(days=1)).astype(dt.datetime)

    y=np.arange(3,maxh)
    z=np.zeros((len(y),len(x)))
    lagmut=lagmut.set_index('DATE')

    index_date=0
    for d in x[:-1]:
        date=d.date()
        try:
            this_date=lagmut.loc[date]
            if type(this_date['HOUR']) is not np.int64:
                count=this_date['HOUR'].value_counts()
            for i in count.index:
                index_time=i-3
                if index_time<z.shape[0]:
                    z[index_time,index_date]=count.loc[i]
        except KeyError:
            print(date)
        index_date+=1
    ax.set_ylabel('Hour')
    ax.set_title(name)


    if ax == axes[-1]:
        ax.set_xlabel('Date')
    else:
        labels =['']*len(x)
        ax.get_xaxis().set_ticks([])


    ax.pcolor(x,y,z,cmap='Greys')

'''
start, end=[],[]

'''
global_start=max(x_start)
global_end=min(x_end)
global_x=np.arange(global_start, global_end, dt.timedelta(days=1)).astype(dt.datetime)

for ax in axes:
    ax.set_xlim([global_start,global_end])
# x=np.arange(max(start),min(end),dt.timedelta(days=1)).astype(dt.datetime)

plt.xticks(global_x,rotation=90)
# plt.xticks(x)
plt.show()
