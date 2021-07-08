def prep(partic):
    import os
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler

    RawData = [i for i in os.listdir(partic) if i.startswith('raw_accelerometer')]

    # read all 12 CSV-files and for each file:
    # calculate 3STD and write NaN where its over or under 3STD
    # delete all the rows containing NANs

    for i in RawData:
        CSV = pd.read_csv(partic + i, float_precision='round_trip', index_col=False, header=0)

        # remove Outliers (outlier = over or under 3 STD)
        x = CSV['x_acceleration_g']
        xSTD = np.std(x)
        xMEAN = np.mean(x)
        CSV['x_acceleration_g'] = np.where((x > (xMEAN - 3 * xSTD)) & (x < (xMEAN + 3 * xSTD)), x, np.nan)

        y = CSV['y_acceleration_g']
        ySTD = np.std(y)
        yMEAN = np.mean(y)
        CSV['y_acceleration_g'] = np.where((y > (yMEAN - 3 * ySTD)) & (y < (yMEAN + 3 * ySTD)), y, np.nan)

        z = CSV['z_acceleration_g']
        zSTD = np.std(z)
        zMEAN = np.mean(z)
        CSV['z_acceleration_g'] = np.where((z > (zMEAN - 3 * zSTD)) & (z < (zMEAN + 3 * zSTD)), z, np.nan)

        # delete all rows with NaNs
        CSV.dropna(inplace=True)

        # write CSVs with removed Outliers
        name = CSV['activity'].iloc[0]
        CSV.to_csv(str(partic + 'noOutlier_' + name + '.csv'), index=False, sep=',')

    # find length of shortest CSV
    noOutlierLength = [i for i in os.listdir(partic) if i.startswith('noOutlier')]
    length = []
    for i in noOutlierLength:
        CSV = pd.read_csv(partic + i, float_precision='round_trip', index_col=False, header=0)
        # get length of shortest CSV
        length.append(len(CSV.index))
        shortest = min(length)

    # Balance and scale
    # cut to length of shortest CSV and scale
    noOutlier = [i for i in os.listdir(partic) if i.startswith('noOutlier')]
    for i in noOutlier:
        CSV = pd.read_csv(partic + i, float_precision='round_trip', index_col=False, header=0)
        CSV = CSV.head(n=shortest)
        # Scale 0-1
        x = CSV[['x_acceleration_g', 'y_acceleration_g', 'z_acceleration_g']]
        y = CSV[['time_s', 'status', 'timestamp_s', 'activity']]
        scaler = MinMaxScaler()
        x = scaler.fit_transform(x)
        x = pd.DataFrame.from_records(x, columns=['x_acceleration_g', 'y_acceleration_g', 'z_acceleration_g'])
        normalized = pd.concat([y, x], axis=1)
        name = normalized.activity[1]
        normalized.to_csv(str(partic + 'cleaned_' + name + '.csv'), index=False, sep=',')

