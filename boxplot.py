import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import readlagmut as data_lagmut
import readlyrtet as data_lyrtet

# lagmut_lucomagno=lagmut.loc(lucomagno['FOLDER'])
fig, axes = plt.subplots(1, 1)
sns.boxplot(data=data_lyrtet.lyrtet_riederalp, x='DATE', y='SECONDS', ax=axes)
plt.xticks(rotation=90)
plt.show()

'''
fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
for name, ax in zip(['Lucomagno', 'Riederalp', 'Both'], axes):
    sns.boxplot(data=opsd_daily, x='Month', y='TIME', ax=ax)
    ax.set_ylabel('GWh')
    ax.set_title(name)
    # Remove the automatic x-axis label from all but the bottom subplot
    if ax != axes[-1]:
        ax.set_xlabel('')
'''
