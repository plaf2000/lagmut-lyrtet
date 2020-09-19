import datetime as dt
import readata as rd
import pandas as pd
import numpy as np
import pylab
import matplotlib.pyplot as plt
from matplotlib import ticker
from pandas.plotting import register_matplotlib_converters
import sunriseset as srst
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

min=1

bins_colorbar=5

# Hour range in which to plot data
hstart=2.5
hend=11


figsize=(12, 9)
dpi=300


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

contour_style={
    'linestyle':':',
    'width':.7,
    'solid_capstyle':'round',
    'solid_joinstyle':'round'
}

basedir_img='/home/plaf2000/Documenti/Lagmut_Lyrtet/Images/Lyrtet/'



data=rd.read_data("./csv/Lyrtet.csv")
intervals=pd.read_csv("./csv/intervalli_registrazione_VS_TI.csv")
intervals=intervals.set_index('Data')

devices=data['DEVICE'].groupby(data['DEVICE']).groups
region={'Riederalp':'Valais','Lucomagno':'Ticino'}

gen_date_start=dt.datetime.strptime(intervals.columns[0],'%d-%m-%Y')
gen_date_end=dt.datetime.strptime(intervals.columns[-1],'%d-%m-%Y')


# Hour range in which to plot data, as datetime object
hstart_dt=gen_date_start+dt.timedelta(hours=hstart)
hend_dt=gen_date_end+dt.timedelta(hours=hend)

minstart=int(hstart*60)
minend=int(hend*60)


# Create a 'FRAC_MIN' column which contains the 'minute pixel' value (the value represent the y value of the pixel in minutes)
data['FRAC_MIN']=data['HOUR'].astype(float)*60+data['DATETIME'].dt.minute
data['FRAC_MIN']-=data['FRAC_MIN']%min

# Create y ax for plotting (reference is always in minutes)
y_mins=np.arange(minstart,minend,step=min)
# Last index value of the array
imax_min=len(y_mins)-1


# devices=['LM2']

for dev in devices:

    # Put the data of this device into data_dev
    data_dev=data.loc[data['DEVICE']==dev].copy()

    # Create the loc_astral object (see sunriseset.py) in order to calculate sunrise and dawn later on
    place=data_dev[['LUCOMAGNO','RIEDERALP']].iloc[0]
    coord=data_dev[['LATITUDE','LONGITUDE']].iloc[0]
    name=place.loc[place].index[0].capitalize()
    loc=srst.loc_astral(
        name,region[name],
        coord['LATITUDE'],
        coord['LONGITUDE'],
        elevation=2300
    )

    # Get the recording start and end times, letting empty values not set
    starts=pd.to_datetime(intervals.loc[dev+'_start'],format='%H:%M',errors='coerce')
    ends=pd.to_datetime(intervals.loc[dev+'_end'],format='%H:%M',errors='coerce')

    # Refernce them to minute value
    starts=(starts.dt.hour.astype(int,errors='ignore')*60+starts.dt.minute.astype(int,errors='ignore')+starts.dt.second.astype(float,errors='ignore')/60)
    ends=  (ends.dt.hour.astype(int,errors='ignore')*60+ends.dt.minute.astype(int,errors='ignore')+ends.dt.second.astype(float,errors='ignore')/60)


    fig, ax = plt.subplots(1, 1,figsize=figsize,dpi=dpi)


    # Create a date array with recording dates of all devices (largest time range possible)
    dates=np.arange(gen_date_start, gen_date_end+dt.timedelta(days=1), dt.timedelta(days=1)).astype(dt.datetime)

    # Create heatmap mesh full of 0 values
    z=np.zeros((len(y_mins),len(dates)))

    last_start=False
    last_end=False

    index_date=0

    for d in dates:
        date=d.date()
        start_min=starts.loc[date.strftime('%d-%m-%Y')]
        end_min=ends.loc[date.strftime('%d-%m-%Y')]

        ######## Fill the z mesh ############

        if not np.isnan(start_min) and not np.isnan(end_min):
        # if start and end recording times are not defined, it means it didn't record, so there's no need to do anything, we can skip to next date
            try:
                # Check whether something has been recorded on this thate. If not, skip to next date
                this_date=data_dev.loc[data_dev['DATE']==date]

                if type(this_date['FRAC_MIN']) is not np.float64:
                    # There's more than one detection for this date, so we need to group them by the same 'minute pixel', summing the amount of total individuals
                    count=this_date[['FRAC_MIN','COOING','HISS']].groupby(['FRAC_MIN']).sum()
                    females=this_date[['FRAC_MIN','FEMALE']].groupby(['FRAC_MIN']).sum()
                    # Loop through every 'minute pixel'
                    for i in count.index:
                        #transform the 'minute pixel' into the y index value of the z array mesh
                        index_time=h_to_i(i)
                        if index_time<z.shape[0]:
                            z[index_time,index_date]=count.loc[i,'COOING']+count.loc[i,'HISS']
                else:
                    # There's just one detection for this date. There's no need to sum the individuals.
                    index_time=h_to_i(this_date['FRAC_MIN'])
                    z[index_time,index_date]=this_date['INDIVUDUALS']
            except KeyError:
                pass

            xs=[date,date+dt.timedelta(days=1)]

            ####### Draw recording box ###########

            # Draw vertical line the date after.

            if last_start and last_end and last_start<end_min and last_end>start_min:
                # If no lines were drawn the date before, draw one
                # ax.vlines(xs[0],start_min,last_start,color=color['contour'],linestyle=contour_style['linestyle'])
                # ax.vlines(xs[0],last_end,end_min,color=color['contour'],linestyle=contour_style['linestyle'])
                pass
            else:
                ax.vlines(xs[0],start_min,end_min,color=color['contour'],linestyle=contour_style['linestyle'],linewidth=contour_style['width'])
            # Draw horizontal lines
            ax.hlines([start_min,end_min],xs[0],xs[1],color=color['contour'],linestyle=contour_style['linestyle'],linewidth=contour_style['width'])

            last_start=start_min
            last_end=end_min
        else:
            ax.vlines(date,last_end,last_start,color=color['contour'],linestyle=contour_style['linestyle'],linewidth=contour_style['width'])
            last_start=False
            last_end=False

        index_date+=1

    # New x array for "poin value" (plot and fill_between), so that they remains in the middle of the pixels
    # It also has a wider date range
    pts_x=dates+dt.timedelta(hours=12)
    pts_x=np.insert(pts_x,0,pts_x[0]-dt.timedelta(days=1))
    pts_x=np.append(pts_x,pts_x[-1]+dt.timedelta(days=1))

    # Calculate sunrises
    sunrises=pd.to_datetime(loc.sunrise(pts_x))
    sunrises_h=sunrises.hour.values*60+sunrises.minute.values+sunrises.second.values/60

    # Calculate dawns
    dawns=pd.to_datetime(loc.dawn(pts_x))
    dawns_h=dawns.hour.values*60+dawns.minute.values+dawns.second.values/60


    # Fill day, twilight and night
    # ax.fill_between(pts_x, sunrises_h, hend,facecolor=color['day'], alpha=alpha['day'], label='Day')
    # ax.fill_between(pts_x, dawns_h, sunrises_h,facecolor=color['twilight'], alpha=alpha['twilight'], label='Twilight')
    # ax.fill_between(pts_x, hstart, dawns_h,facecolor=color['night'], alpha=alpha['night'], label='Night')

    zmax=int(z.max())
    ncolors = zmax+1

    # Create a range of n colors. n is the max number of individuals in one pixel +1. The first color will be set to transparent, the other to rapresent the number from 0 to max individuals.
    color_array=np.zeros((ncolors,4))
    for i in range(4):
        color_array[:,i]=np.linspace(c_start[i],c_end[i],ncolors)
    # Set the first color fully transparent
    color_array[0,-1] =0

    cmap=ListedColormap(color_array)
    heatmap=ax.pcolormesh(dates,y_mins,z,cmap=cmap,vmin=0)

    # Draw the colorbar
    cbar=fig.colorbar(heatmap,fraction=.05,pad=.025)

    # Match the ticks with the right value
    bins=bins_colorbar
    val_sel=np.linspace(0,zmax,zmax+2)
    cbar_labels=[''] * (zmax+1)
    cbar_vislabels=np.arange(0,zmax,bins).astype(int)
    for n in cbar_vislabels:
        cbar_labels[n] = n
    val_sel+=.5
    cbar.set_ticks(val_sel[:-1])
    cbar.set_ticklabels(cbar_labels)
    cbar.ax.set_xlabel(r"$\frac{Calls}{"+str(min)+"\ min}$",fontsize=16)

    # Plot females

    females=data_dev.loc[data_dev['FEMALE']>0].copy()
    if not females.empty:
        females_time_min=(females['HOUR'].astype(float)*60+females['DATETIME'].dt.minute+females['DATETIME'].dt.second/60)
        ax.scatter(females['DATETIME'],females_time_min,s=females['FEMALE']*100,marker='*',alpha=.2,edgecolors='none',c='#0000ff',facecolors=None, label='Female')

    # Plot the dawn and sunrise curve.
    ax.plot(pts_x, sunrises_h,color=color['sunrise'],alpha=alpha['sunrise'],linestyle='--',linewidth=.8, label='Sunrise (sun at 0°)')
    ax.plot(pts_x, dawns_h,color=color['dawn'],alpha=alpha['dawn'],linestyle='--',linewidth=.8, label='Dawn (sun at -6°)')

    # Set the xticks so that they're in the middle of the pixels
    ax.set_xlim([gen_date_start,gen_date_end+dt.timedelta(days=1)])
    plt.xticks(pts_x[1:-1],rotation=90)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.set_xlabel('Date [dd.mm]', labelpad=10)

    ##### Set the y ax #######

    ax.set_ylim([minstart,minend])
    step_min=res_y_min
    step_tdelta=dt.timedelta(minutes=step_min)

    # If the last value is far enough, it writes the end time of the y ax range:
    mod=(minend-minstart)%step_min
    add_end=bool(mod/(minend-minstart)>=1.20)

    # Y ticks we want to show, referenced by minute
    y_hours_selected=np.arange(minstart,minend+step_min,step_min)
    # Include last time value
    y_hours_selected=y_hours_selected[y_hours_selected<=minend]
    if add_end:
        y_hours_selected=np.append(y_hours_selected,minend)

    # Y ticks we want to show, as we want them to appear
    hours_label=np.arange(hstart_dt, hend_dt+step_tdelta, step_tdelta).astype(dt.datetime)
    # Include last time value
    hours_label=hours_label[hours_label<=hend_dt]
    if add_end:
        hours_label=np.append(hours_label,hend_dt)
    hours_label=pd.to_datetime(hours_label)
    hours_label=hours_label.strftime('%H:%M')

    plt.yticks(y_hours_selected,labels=hours_label)
    ax.set_ylabel('Time (UTC+2)', labelpad=10)

    #Draw installation of the devices, battery and SD cards changes and take down

    # if name=='Lucomagno':
    #     changes=[
    #         dt.datetime(2020,5,3,12,0)
    #     ]
    # elif name=='Riederalp':
    #     changes=[
    #         dt.datetime(2020,5,3,12,0),
    #         dt.datetime(2020,5,16,12,0)
    #     ]
    #     if dev=='LM4':
    #         changes=[
    #             dt.datetime(2020,5,16,12,0)
    #         ]
    # ax.vlines(inst[name],minstart,minend,label='Installation of the devices',alpha=.25)

    if name=='Lucomagno':
        changes=[
            dt.datetime(2020,5,3+1,0,0)
        ]
    elif name=='Riederalp':
        changes=[
            dt.datetime(2020,5,3+1,0,0),
            dt.datetime(2020,5,16+1,0,0)
        ]
        if dev=='LM4':
            changes=[
                dt.datetime(2020,5,16+1,0,0)
            ]
    ax.vlines(changes,minstart,minend,label='Batteries and SD cards changes',alpha=.25)

    # Draw legend (for Recording boxes create a new one, since they're made of many lines)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(mpatches.Patch(facecolor='white',edgecolor='black',linestyle=contour_style['linestyle'],linewidth=contour_style['width']))
    labels.append('Recording')





    ax.set_aspect('auto')


    #Add title and save files
    subtitle=dev+' ('+name+') - All calls'
    ax.set_title(r"$\bf{Black\ grouse\ }$"+r"$\it{Lyrurus\ tetrix}$"+'\n'+subtitle,fontsize=18,pad=20)
    # plt.show()
    fig.tight_layout()
    png_path=basedir_img+'png/nofill/'+dev+'_nofill.png'
    svg_path=basedir_img+'svg/nofill/'+dev+'_nofill.svg'
    fig.savefig(png_path)
    print(png_path,'Saved')
    fig.savefig(svg_path)
    print(svg_path,'Saved')



fig_legend = plt.figure(figsize=(2,2))
axi = fig_legend.add_subplot(111)
fig_legend.legend(handles, labels, loc='center', scatterpoints = 1)
axi.xaxis.set_visible(False)
axi.yaxis.set_visible(False)
fig_legend.canvas.draw()
# save the two figures to files
ax.legend(handles,labels)
png_path=basedir_img+'png/legend.png'
svg_path=basedir_img+'svg/legend.svg'
# fig.savefig(png_path)
print(png_path,'Saved')
# fig.savefig(svg_path)
print(svg_path,'Saved')
