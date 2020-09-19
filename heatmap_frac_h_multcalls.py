import datetime as dt
import readata as rd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import sunriseset as srst
from importlib import reload
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd

register_matplotlib_converters()

fig, axes = plt.subplots(2, 1,figsize=(50, 200),sharex=False)

x_start,x_end=[],[]

frac_h=1/12
hstart=3
hend=11
restr=True
color_calls={

    'CALL_1': [1 ,0 ,0 ,1 ],
    'CALL_2': [0 ,0 ,1 ,1 ],
    'CALL_3': [0 ,1 ,0 ,1 ],
    'CALL_4': [0 ,1 ,1 ,1 ],
    'FEMALE': [0 ,0 ,1 ,1 ]

}

data=rd.read_data("./csv/Lagmut.csv")




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
    lagmut=lagmut.set_index('DATE')
    z_calls={}
    z_max={'abs':0}

    for call in color_calls:
        z=np.zeros((len(y),len(x)))
        # z[:,:]=np.nan
        index_date=0
        for d in x[:-1]:
            date=d.date()
            try:
                this_date=lagmut.loc[date]
                if type(this_date['FRAC_HOUR']) is not np.float64:
                    count=this_date[['FRAC_HOUR',call]].groupby(['FRAC_HOUR']).sum()
                    # count=this_date['FRAC_HOUR'].value_counts()
                    for i in count.index:
                        index_time=int((i-hstart)*(1/frac_h))
                        if index_time<z.shape[0]:
                            z[index_time,index_date]=count.loc[i]
                else:
                    index_time=int((this_date['FRAC_HOUR']-hstart)*(1/frac_h))
                    z[index_time,index_date]=this_date[call]
            except KeyError:
                print(date)
            index_date+=1
        z_max[call]=z.max()
        z_max['abs']=z_max[call] if z_max[call]>z_max['abs'] else z_max['abs']
        # z=np.ma.masked_array(z, z==10)
        z_calls[call]=z

    ax.set_ylabel('Hour')
    ax.set_title(name)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))


    if ax == axes[-1]:
        ax.set_xlabel('Date', labelpad=20)
    else:
        labels =['']*len(x)
        ax.get_xaxis().set_ticks([])


    for call in ['CALL_1','CALL_2']:
        c=color_calls[call]
        # cmp=getattr(plt.cm,c)
        # cmp.set_under(color="white", alpha="0")
        ncolors = int(z_max['abs'])

        color_array=np.zeros((ncolors,4))
        for i in range(len(c)):
            ch_start=c[i]/3# if i<3 else .9
            color_array[:,i]=np.linspace(ch_start,c[i],ncolors)

        # rang_colors=
        # color_array = plt.get_cmap(c)(rang_colors)
        # color_array=np.linspace(0.25,1,ncolors)
        #
        #
        # color_array[:,-1] = np.linspace(0.25,1,ncolors)
        color_array[0,-1] =0
        # alpha=LinearSegmentedColormap.from_list(name=c+'_alpha',colors=color_array)
        # plt.register_cmap(cmap=alpha)
        cmp=ListedColormap(color_array)
        heatmap=ax.pcolormesh(x,y,z_calls[call],cmap=cmp,vmin=0,vmax=z_max['abs'])

        cbar=fig.colorbar(heatmap, ax=ax,fraction=.05,pad=0.01)
        if ax == axes[-1]:
            call_label=call.capitalize().replace("_"," ")
            cbar.ax.set_xlabel(call_label, rotation=270)


'''
start, end=[],[]

'''
global_start=min(x_start)
global_end=max(x_end)
xlim=[global_start,global_end]
global_x=np.arange(global_start, global_end, dt.timedelta(days=1)).astype(dt.datetime)+dt.timedelta(hours=12)

sunrises=[]
dawns=[]

srs_start=global_start-dt.timedelta(days=1)
srs_end=global_end+dt.timedelta(days=1)
sunrises_x=np.arange(srs_start, srs_end, dt.timedelta(days=1)).astype(dt.datetime)+dt.timedelta(hours=12)

sunrises_dt=pd.to_datetime(loc.sunrise(sunrises_x))
sunrises=sunrises_dt.hour.values+sunrises_dt.minute.values/60


dawns_dt=pd.to_datetime(loc.dawn(sunrises_x))
dawns=dawns_dt.hour.values+dawns_dt.minute.values/60


for ax in axes:
    ax.plot(sunrises_x,sunrises,color='yellow',linestyle=':')
    ax.plot(sunrises_x,dawns,color='black',linestyle=':')
    # ax.fill_between(sunrises_x, sunrises, ax.get_ylim()[1],facecolor='yellow', alpha=0.075)
    # ax.fill_between(sunrises_x, sunrises, ax.get_ylim()[0],facecolor='gray', alpha=0.075)
    # ax.set_xlim([global_start,global_end])
    ax.set_xlim(xlim)
# x=np.arange(max(start),min(end),dt.timedelta(days=1)).astype(dt.datetime)
# subtitle=call_filter if type(call_filter) is str and call_filter!='' else 'all calls'
subtitle='all calls'
plt.suptitle(r"$\bf{Rock\ ptarmigan\ }$"+r"$\it{Lagopus\ muta}$"+'\n'+subtitle,fontsize=18)
plt.subplots_adjust(bottom=0.15, top=0.85)
plt.xticks(global_x,rotation=90)
# plt.xticks(x)
plt.show()
