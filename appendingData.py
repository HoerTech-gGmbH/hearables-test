import pandas as pd
import os

new = pd.DataFrame(columns=['time[s]', ' x-acceleration [g]', ' y-acceleration [g]', ' z-acceleration [g]', ' status', ' timestamp[s]', 'activity'])
RawData=[i for i in os.listdir() if i.startswith('raw_accelerometer_data_')]
for i in RawData:
    CSVs = pd.read_csv(i,float_precision='round_trip')
    new = new.append(CSVs)
new.to_csv('DATA_with_Activity_new.csv',index=False)
