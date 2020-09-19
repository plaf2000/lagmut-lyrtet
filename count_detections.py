import pandas as pd
import readata as rd


lt=rd.read_data("./csv/Lyrtet.csv")
lm=rd.read_data("./csv/Lagmut.csv")

print(lt[['COOING','HISS','FEMALE']].sum())
print(lm[['CALL_1','CALL_2','CALL_3','CALL_4','FEMALE','INDIVIDUALS']].sum())
