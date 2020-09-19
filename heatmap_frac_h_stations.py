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

def h_to_i(h,m=0):
    m/=60
    h+=m
    i=int((h-float(hstart))*(1/frac_h))
    i=i if 0<=i<=imax_h else 0 if i<0 else imax_h
    return i

h_to_i_vec=np.vectorize(h_to_i)

register_matplotlib_converters()



x_start,x_end=[],[]

frac_h=1/12
hstart=3
hend=11
restr=True


data=rd.read_data("./csv/Lagmut.csv")
intervals=pd.read_csv("./csv/intervalli_registrazione_VS_TI.csv")
intervals=intervals.set_index('Data')

devices=data['DEVICE'].groupby(data['DEVICE']).groups
region={'Riederalp':'Valais','Lucomagno':'Ticino'}

gen_date_start=dt.datetime.strptime(intervals.columns[0],'%d-%m-%Y')
gen_date_end=dt.datetime.strptime(intervals.columns[-1],'%d-%m-%Y')

data['FRAC_HOUR']=data['HOUR'].astype(float)+(data['DATETIME'].dt.minute/(60*frac_h)).astype(int)*frac_h

y_hours=np.arange(hstart,hend,step=frac_h)
imax_h=len(y_hours)-1

# devices=['LM1']

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

    starts=pd.to_datetime(intervals.loc[dev+'_start'],format='%H:%M',errors='ignore')
    ends=pd.to_datetime(intervals.loc[dev+'_end'],format='%H:%M',errors='coerce')


    starts=starts.dt.hour.astype(float,errors='ignore')+(starts.dt.minute/(60*frac_h)).astype(int,errors='ignore')*frac_h
    ends=ends.dt.hour.astype(float,errors='ignore')+(ends.dt.minute/(60*frac_h)).astype(int,errors='ignore')*frac_h


    dates=np.arange(gen_date_start, gen_date_end+dt.timedelta(days=1), dt.timedelta(days=1)).astype(dt.datetime)


    z=np.zeros((len(y_hours),len(dates)))
    recording=z.copy()

    index_date=0
    for d in dates:
        date=d.date()
        start_h=starts.loc[date.strftime('%d-%m-%Y')]
        end_h=ends.loc[date.strftime('%d-%m-%Y')]
        if not np.isnan(start_h) and not np.isnan(end_h):
            start_i,end_i=h_to_i(start_h),h_to_i(end_h)
            recording[start_i:end_i,index_date]=1
            try:

                this_date=data_dev.loc[data_dev['DATE']==date]

                if type(this_date['FRAC_HOUR']) is not np.float64:
                    count=this_date[['FRAC_HOUR','INDIVIDUALS']].groupby(['FRAC_HOUR']).sum()

                    for i in count.index:
                        index_time=h_to_i(i)
                        if index_time<z.shape[0]:
                            z[index_time,index_date]=count.loc[i,'INDIVIDUALS']
                else:
                    index_time=h_to_i(this_date['FRAC_HOUR'])
                    z[index_time,index_date]=this_date['INDIVUDUALS']
            except KeyError:
                # print(date)
                pass
        else:
            print(date)
            print('start',start_h,np.isnan(start_h))
            print('end',end_h,np.isnan(end_h))
        index_date+=1

    sunrises=pd.to_datetime(loc.sunrise(dates))
    sunrises_h=sunrises.hour.values+sunrises.minute.values/60


    dawns=pd.to_datetime(loc.dawn(dates))
    dawns_h=dawns.hour.values+dawns.minute.values/60



    fig, ax = plt.subplots(1, 1,figsize=(50, 50))

    ax.fill_between(dates, sunrises_h, hend,facecolor='yellow', alpha=0.75)
    ax.fill_between(dates, dawns_h, sunrises_h,facecolor='blue', alpha=0.75)
    ax.fill_between(dates, hstart, dawns_h,facecolor='black', alpha=1)

    trans_white = np.array([[0,0,0,0],[1,1,1,1]])
    cmap_wt=ListedColormap(trans_white)
    heatmap=ax.pcolormesh(dates,y_hours,recording,cmap=cmap_wt)
    # heatmap=ax.contour(dates,y_hours,recording,colors='black',corner_mask=False,levels=0)

    ncolors = z.max()+1

    reds= plt.cm.Reds
    new_reds=reds(np.arange(reds.N))
    new_reds[0,-1] = 0

    new_reds=ListedColormap(new_reds)


    ax.pcolormesh(dates,y_hours,z,cmap=new_reds)

    ax.plot(dates, dawns_h,color='black',linestyle=':')
    ax.plot(dates, sunrises_h,color='blue',linestyle=':')

    # ax.set_xlim([gen_date_start,gen_date_end])
    ax.set_ylim([hstart,hend])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))

    subtitle=dev+' - All calls'
    plt.suptitle(r"$\bf{Rock\ ptarmigan\ }$"+r"$\it{Lagopus\ muta}$"+'\n'+subtitle,fontsize=18)
    plt.xticks(dates-dt.timedelta(days=.5),rotation=90)
    plt.show()






'''
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



# start, end=[],[]


global_start=min(x_start)
global_end=max(x_end)
xlim=[global_start,global_end]
global_x=np.arange(global_start, global_end, dt.timedelta(days=1)).astype(dt.datetime)+dt.timedelta(hours=12)

sunrises=[]
dawns=[]

srs_start=global_start-dt.timedelta(days=1)
srs_end=global_end+dt.timedelta(days=1)
sunrises_x=np.arange(srs_start, srs_end, dt.timedelta(days=1)).astype(dt.datetime)+dt.timedelta(hours=12)

for date in sunrises_x:
    sun_data=loc.get(date)
    sr=sun_data['sunrise']
    sr=sr.hour+sr.minute/60
    dawn=sun_data['dawn']
    dawn=dawn.hour+dawn.minute/60
    sunrises.append(sr)
    dawns.append(dawn)


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
'''
