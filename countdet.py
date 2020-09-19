import readata
import pandas as pd



sof=pd.read_csv("./csv/Lyrtet_soffio_orig.csv")
rug=pd.read_csv("./csv/Lyrtet_rugolio_orig.csv")
fem=pd.read_csv("./csv/Lyrtet_female_orig.csv")
lyr = pd.concat([sof,rug,fem])
lyr.append(pd.read_csv("./csv/Lyrtet_rugolio_orig.csv"))
lyr.append(pd.read_csv("./csv/Lyrtet_female_orig.csv"))
print(lyr.shape)
lyr['DEVICE']=lyr['FOLDER'].str.split(pat='\\').str[1].str.split('_').str[0]

print(lyr['DEVICE'].value_counts())