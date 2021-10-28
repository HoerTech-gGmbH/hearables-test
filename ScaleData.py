# Scale Data
#_____ X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
#_____ X_scaled = X_std * (max - min) + min

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

data = pd.read_csv('snippData.csv',float_precision='round_trip')
x = data[[' x-acceleration [g]',' y-acceleration [g]',' z-acceleration [g]']]
y = data[['time[s]','activity']]

scaler = MinMaxScaler()
x = scaler.fit_transform(x)
x = pd.DataFrame.from_records(x,columns=[' x-acceleration [g]',' y-acceleration [g]',' z-acceleration [g]'])
normalized = pd.concat([y, x], axis=1)
normalized.to_csv('ScaledData.csv', index=False,float_format='%16g')

#print(x[[' z-acceleration [g]']].min())
#print(x[[' z-acceleration [g]']].max())
