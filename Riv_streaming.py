# Script to generate/load River Model to classify data collected with Dopple hearables while moving
# Author: Alexandra Illiger
#
# This script expects one csv file with whole data from one participant to lie in a dedicated folder and this script to
# lie next to the subject folders. Any additional folders starting with '.' are ignored when creating a list of folder
# content. The expected csv-file should have three columns: x-, y-, z_acceleration_g and int_activity.
# For output you get a trained Naive Bayes Model for each subject and a csv-File with the accuracy.
# Mean, Standard Deviation and Correlation between the channels are used features. Data is scaled before processed from
# model.

import pandas as pd
import pathlib
import os
import math
import pickle
from river import compose
from river import preprocessing
from river import metrics
from river import stats
from river import stream
from river import naive_bayes

xypearson = stats.PearsonCorr()
xzpearson = stats.PearsonCorr()
yzpearson = stats.PearsonCorr()
# we need one object for every feature, we cannot reuse the same object, because it has internal state!
window_size = 400
xmean = stats.RollingMean(window_size=window_size)
ymean = stats.RollingMean(window_size=window_size)
zmean = stats.RollingMean(window_size=window_size)

xvar = stats.Var()
yvar = stats.Var()
zvar = stats.Var()

path = pathlib.Path().resolve()
project_folder = path.__str__() + '\\'
print(project_folder)


# defining functions to create features

def corr_xy(x):
    xy_corr = xypearson.update(x['x_acceleration_g'], x['y_acceleration_g']).get()
    return {'xy_corr': xy_corr, **x}  # **x writes the new feature into the old dict without overwriting the input(x)
    # https://riverml.xyz/dev/api/compose/FuncTransformer/


def corr_xz(x):
    xz_corr = xzpearson.update(x['x_acceleration_g'], x['z_acceleration_g']).get()
    return {'xz_corr': xz_corr, **x}


def corr_yz(x):
    yz_corr = yzpearson.update(x['y_acceleration_g'], x['z_acceleration_g']).get()
    return {'yz_corr': yz_corr, **x}


def mean_x(x):
    x_mean = xmean.update(x['x_acceleration_g']).get()
    return {'x_mean': x_mean, **x}


def mean_y(x):
    y_mean = ymean.update(x['y_acceleration_g']).get()
    return {'y_mean': y_mean, **x}


def mean_z(x):
    z_mean = zmean.update(x['z_acceleration_g']).get()
    return {'z_mean': z_mean, **x}


def std_x(x):
    x_std = math.sqrt(xvar.update(x['x_acceleration_g']).get())
    return {'x_std': x_std, **x}


def std_y(x):
    y_std = math.sqrt(yvar.update(x['y_acceleration_g']).get())
    return {'y_std': y_std, **x}


def std_z(x):
    z_std = math.sqrt(zvar.update(x['z_acceleration_g']).get())
    return {'z_std': z_std, **x}


# function containing model pipeline, data streaming, predicting, learning, saving/loading model
def modelling(dataset_path, folder):
    # setting up model pipeline
    model = compose.Pipeline(
        compose.FuncTransformer(corr_xy),
        compose.FuncTransformer(corr_xz),
        compose.FuncTransformer(corr_yz),
        compose.FuncTransformer(mean_x),
        compose.FuncTransformer(mean_y),
        compose.FuncTransformer(mean_z),
        compose.FuncTransformer(std_x),
        compose.FuncTransformer(std_y),
        compose.FuncTransformer(std_z),
        # compose.Discard('x_acceleration_g','y_acceleration_g','z_acceleration_g'),
        preprocessing.StandardScaler(),
        naive_bayes.GaussianNB()
    )
    print('Composed pipeline')
    # preparing data stream
    data_stream = stream.iter_csv(
        dataset_path,
        converters={
            'int_activity': int,
            'x_acceleration_g': float,
            'y_acceleration_g': float,
            'z_acceleration_g': float
        },
        target='int_activity'
    )
    print('Prepared data stream')

    # model = pickle.load(open(folder+'Riv_M_Steaming.pickle', 'rb'))
    metric = metrics.Accuracy()

    acc_list = []  # creating empty list for accuracy
    # use model pipeline for each sample, predict and learn
    for x, y in data_stream:
        y_pred = model.predict_one(x)
        accuracy = metric.update(y, y_pred).get()
        acc_list.append(accuracy)
        model = model.learn_one(x, y)

    print(acc_list)
    print(metric.update(y, y_pred))
    acc = pd.DataFrame(acc_list)
    acc.to_csv(folder + 'Accuracy.csv')

    # report = model.debug_one(x)
    # print(report)

    # save new model
    with open(folder + 'Riv_M_Steaming.pickle', "wb") as output_file:
        pickle.dump(model, output_file)


def models_for_subjects():
    # This function loops through all the participant folders in the project folder and
    # executes the function 'modelling()' for them.

    # discard hidden folders starting with . & this script
    all_files = [f for f in os.listdir(project_folder) if not f.startswith('.') and not f.endswith('py')]
    for subject_folder in all_files:
        print('The data folder is called ' + subject_folder + ' and we iterate through Mixed_data.csv now')
        modelling(dataset_path=project_folder + subject_folder + '\Mixed_data.csv',
                  folder=project_folder + subject_folder + '\\')


models_for_subjects()
