import datetime as dt
import readata as rd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import sunriseset as srst
from importlib import reload
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches

def h_to_i(m):
    i=int((m-minstart)/min)
    i=i if 0<=i<=imax_min else 0 if i<0 else imax_min
    return i


h_to_i_vec=np.vectorize(h_to_i)

register_matplotlib_converters()



x_start,x_end=[],[]

min=5

frac_h=min/60
hstart=2.5
hend=11
restr=True

figsize=(12, 9)
dpi=100




res_y_min=30
res_x=1

c_start=[.5,0,0,1]
c_end = [.5,0,0,0]

c_start,c_end=c_end,c_start

color={
    'day':      'white',
    'twilight': '#efefef',
    'night':    '#d1d1d1',
    'contour':  'black',
    'dawn':     'black',
    'sunrise':  'black'
}
alpha={
    'day':      1,
    'twilight': 1,
    'night':    1,
    'dawn':     .9,
    'sunrise':  .5
}

basedir_img='/home/plaf2000/Documenti/Lagmut_Lyrtet/Images/stations/'



data=rd.read_data("./csv/Lagmut.csv")
intervals=pd.read_csv("./csv/intervalli_registrazione_VS_TI.csv")
intervals=intervals.set_index('Data')

devices=data['DEVICE'].groupby(data['DEVICE']).groups
region={'Riederalp':'Valais','Lucomagno':'Ticino'}

gen_date_start=dt.datetime.strptime(intervals.columns[0],'%d-%m-%Y')
gen_date_end=dt.datetime.strptime(intervals.columns[-1],'%d-%m-%Y')



hstart_dt=gen_date_start+dt.timedelta(hours=hstart)
hend_dt=gen_date_end+dt.timedelta(hours=hend)

minstart=int(hstart*60)
minend=int(hend*60)

data['FRAC_MIN']=((data['HOUR'].astype(float)*60+data['DATETIME'].dt.minute)).astype(int)

y_mins=np.arange(minstart,minend,step=min)
imax_min=len(y_mins)-1

devices=['LM1']

for dev in devices:
    data_dev=data.loc[data['DEVICE']==dev].copy()

    place=data_dev[['LUCOMAGNO','RIEDERALP']].iloc[0]
    coord=data_dev[['LATITUDE','LONGITUDE']].iloc[0]
    name=place.loc[place].index[0].capitalize()
    loc=srst.loc_astral(
        name,region[name],
        coord['LATITUDE'],
        coord['LONGITUDE'],
        elevation=2300
    )

    starts=pd.to_datetime(intervals.loc[dev+'_start'],format='%H:%M',errors='coerce')
    ends=pd.to_datetime(intervals.loc[dev+'_end'],format='%H:%M',errors='coerce')


    starts=(starts.dt.hour.astype(float,errors='ignore')*60+starts.dt.minute).astype(int,errors='ignore')
    ends=  (ends.dt.hour.astype(float,errors='ignore')*60+ends.dt.minute).astype(int,errors='ignore')


    fig, ax = plt.subplots(1, 1,figsize=figsize,dpi=dpi)


    dates=np.arange(gen_date_start, gen_date_end+dt.timedelta(days=1), dt.timedelta(days=1)).astype(dt.datetime)


    z=np.zeros((len(y_mins),len(dates)))

    first=True
    index_date=0

    for d in dates:
        date=d.date()
        start_min=starts.loc[date.strftime('%d-%m-%Y')]
        end_min=ends.loc[date.strftime('%d-%m-%Y')]
        if not np.isnan(start_min) and not np.isnan(end_min):
            try:
                this_date=data_dev.loc[data_dev['DATE']==date]

                if type(this_date['FRAC_MIN']) is not np.float64:
                    count=this_date[['FRAC_MIN','INDIVIDUALS']].groupby(['FRAC_MIN']).sum()

                    for i in count.index:
                        print(i)
                        index_time=h_to_i(i)
                        if index_time<z.shape[0]:
                            z[index_time,index_date]=count.loc[i,'INDIVIDUALS']
                else:
                    index_time=h_to_i(this_date['FRAC_MIN'])
                    z[index_time,index_date]=this_date['INDIVUDUALS']
            except KeyError:
                # print(date)
                pass

            xs=[date,date+dt.timedelta(days=1)]
            ax.vlines(xs[1],start_min,end_min,color=color['contour'],linestyle=':',linewidth=.5)
            if first:
                ax.vlines(xs[0],start_min,end_min,color=color['contour'],linestyle=':',linewidth=.5)
            ax.hlines([start_min,end_min],xs[0],xs[1],color=color['contour'],linestyle=':',linewidth=.5)

            first=False
        else:
            first=True

        index_date+=1

    pts_x=dates+dt.timedelta(hours=12)
    pts_x=np.insert(pts_x,0,pts_x[0]-dt.timedelta(days=1))
    pts_x=np.append(pts_x,pts_x[-1]+dt.timedelta(days=1))

    sunrises=pd.to_datetime(loc.sunrise(pts_x))
    sunrises_h=sunrises.hour.values*60+sunrises.minute.values+sunrises.second.values/60


    dawns=pd.to_datetime(loc.dawn(pts_x))
    dawns_h=dawns.hour.values*60+dawns.minute.values+dawns.second.values/60



    ax.fill_between(pts_x, sunrises_h, hend,facecolor=color['day'], alpha=alpha['day'], label='Day')
    ax.fill_between(pts_x, dawns_h, sunrises_h,facecolor=color['twilight'], alpha=alpha['twilight'], label='Twilight')
    ax.fill_between(pts_x, hstart, dawns_h,facecolor=color['night'], alpha=alpha['night'], label='Night')

    zmax=int(z.max())
    ncolors = zmax+1

    color_array=np.zeros((ncolors,4))
    for i in range(4):
        color_array[:,i]=np.linspace(c_start[i],c_end[i],ncolors)
    color_array[0,-1] =0

    new_grays=ListedColormap(color_array)

    heatmap=ax.pcolormesh(dates,y_mins,z,cmap=new_grays,vmin=0)

    cbar=fig.colorbar(heatmap,fraction=.05,pad=.025)
    val_sel=np.linspace(0,zmax,zmax+2)
    cbar_labels=np.linspace(0,zmax,zmax+1)
    val_sel+=.5
    cbar.set_ticks(val_sel[:-1])
    cbar.set_ticklabels(cbar_labels.astype(int))
    cbar.ax.set_xlabel(r"$\frac{Calls}{"+str(min)+"\ min}$",fontsize=16)


    ax.plot(pts_x, sunrises_h,color=color['sunrise'],alpha=alpha['sunrise'],linestyle='--',linewidth=.8, label='Sunrise (sun at 0°)')
    ax.plot(pts_x, dawns_h,color=color['dawn'],alpha=alpha['dawn'],linestyle='--',linewidth=.8, label='Dawn (sun at -6°)')

    ax.set_xlim([gen_date_start,gen_date_end+dt.timedelta(days=1)])
    plt.xticks(pts_x[1:-1],rotation=90)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.set_xlabel('Date [dd.mm]', labelpad=10)


    ax.set_ylim([minstart,minend])
    step_min=res_y_min
    step_tdelta=dt.timedelta(minutes=step_min)
    mod=(minend-minstart)%step_min
    add_end=bool(mod/(minend-minstart)>=1.20)
    y_hours_selected=np.arange(minstart,minend+step_min,step_min)
    y_hours_selected=y_hours_selected[y_hours_selected<=minend]
    if add_end:
        y_hours_selected=np.append(y_hours_selected,minend)
    y_hours_selected=y_hours_selected
    hours_label=np.arange(hstart_dt, hend_dt+step_tdelta, step_tdelta).astype(dt.datetime)
    hours_label=hours_label[hours_label<=hend_dt]
    if add_end:
        hours_label=np.append(hours_label,hend_dt)
    hours_label=pd.to_datetime(hours_label)
    hours_label=hours_label.strftime('%H:%M')
    plt.yticks(y_hours_selected,labels=hours_label)
    ax.set_ylabel('Time (UTC+2)', labelpad=10)


    handles, labels = ax.get_legend_handles_labels()
    handles.append(mpatches.Patch(facecolor='white',edgecolor='black',linestyle=':',linewidth=.5))
    labels.append('Recording')
    ax.set_aspect('auto')
    ax.legend()
    ax.legend(handles,labels)





    subtitle=dev+' - All calls'
    ax.set_title(r"$\bf{Rock\ ptarmigan\ }$"+r"$\it{Lagopus\ muta}$"+'\n'+subtitle,fontsize=18,pad=20)
    plt.show()
    fig.tight_layout()
    # fig.savefig(basedir_img+dev+'.png')
    # fig.savefig(basedir_img+dev+'.svg')
