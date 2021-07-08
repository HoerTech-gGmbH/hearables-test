def extract(partic):
    import pandas as pd
    import os
    import numpy as np

    window = 800

    x_mean = []
    y_mean = []
    z_mean = []
    x_std = []
    y_std = []
    z_std = []
    labels = []
    activities = []
    CORRs = pd.DataFrame()

    data = [i for i in os.listdir(partic) if i.startswith('cleaned_')]
    for i in data:
        CSVs = pd.read_csv(partic + i, float_precision='round_trip', index_col=False, header=0).drop(
            columns=['status', 'time_s', 'timestamp_s'])
        chunks = [CSVs[j:j + window] for j in range(0, len(CSVs),
                                                    window)]  # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        for chunk in chunks:
            if len(chunk) == window:
                labels.append(chunk.activity.iloc[1])
                x_mean.append((np.mean(chunk.x_acceleration_g)))
                x_std.append((np.std(chunk.x_acceleration_g)))
                y_mean.append((np.mean(chunk.y_acceleration_g)))
                y_std.append((np.std(chunk.y_acceleration_g)))
                z_mean.append((np.mean(chunk.z_acceleration_g)))
                z_std.append((np.std(chunk.z_acceleration_g)))

                # corr = chunk[['x_acceleration_g', 'y_acceleration_g', 'z_acceleration_g']].corr()
                # CORRs = CORRs.append(corr)
                # labelsCORRs = [chunk['activity'].iloc[0]] * 3
                # activities = activities + labelsCORRs

            MEANsSTDs1 = pd.DataFrame(
                {'x_mean': x_mean, 'y_mean': y_mean, 'z_mean': z_mean, 'x_std': x_std, 'y_std': y_std, 'z_std': z_std,
                 'activity': labels})
            MEANsSTDs1.to_csv(partic + 'mean_std.csv', index=False)

            MEANsSTDs = {'x_mean': x_mean, 'y_mean': y_mean, 'z_mean': z_mean, 'x_std': x_std, 'y_std': y_std,
                         'z_std': z_std,
                         'activity': labels}

            # CORRs['activity'] = activities

    np.save(partic + 'meanfeatures.npy', MEANsSTDs)

    '''
    CORRs.reset_index(drop=True, inplace=True)
    CORRs = CORRs.set_index(
        'activity').stack().reset_index()  # https://stackoverflow.com/questions/34376053/pandas-dataframe-stack-multiple-column-values-into-single-column
    CORRs.columns = ['activity', 'feature', 'value']  # https://stackoverflow.com/questions/11346283/renaming-columns-in-pandas

    MEANsSTDs = MEANsSTDs.set_index('activity').stack().reset_index()
    MEANsSTDs.columns = ['activity', 'feature', 'value']

    Features = pd.concat([CORRs, MEANsSTDs])
    Features = Features.sort_values(by=['activity', 'feature'])
    Features.to_csv('Features.csv', index=False)
    '''

