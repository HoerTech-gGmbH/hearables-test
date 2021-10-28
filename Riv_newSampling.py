# Script to produce one mixed dataset (for each subject) from data collected with Dopple hearables while moving
# (generates the input files for classification with river ML)
# Author: Alexandra Illiger
#
# This script expects all csv files for every participant to lie in a dedicated folder and this script to lie next
# to this folders. Any additional folders starting with '.' are ignored when creating a list of folder content.
# For Input the script expects to find multiple csv files in the participants folders, one csv for every activity.
# For output you get one csv file for each participant witch combines all their csv files in one but with data randomly
# sampled in chunks with window size. The Output file consists of four columns: x-,y-,z_acceleration_g
# and int_activity (same integer for same activity over all subjects)

import pandas as pd
import os
import random
import pathlib

window = 4000  # data will be cut in chunks of 5 sec, which will be randomly sampled

path = pathlib.Path().resolve()
project_folder = path.__str__() + '\\'
print(project_folder)


def sample_data(folder, window):
    print(folder)
    # This function cuts all csv files in the participants folder into window-sized chunks,
    # appends them into one list, randomly samples the chunks and writes them to one csv file.
    list_chunks = []
    data = [i for i in os.listdir(folder) if i.startswith('raw_accelerometer')]
    for csv_file_name in data:
        CSVs = pd.read_csv(folder + csv_file_name, float_precision='round_trip', index_col=False, header=0)
        print('read ' + csv_file_name)
        # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        chunks = [CSVs[j:j + window] for j in range(0, len(CSVs), window)]
        for chunk in chunks:
            list_chunks.append(chunk)

    mixed_chunks = random.sample(list_chunks, len(list_chunks))
    mixed_data = pd.concat(mixed_chunks)
    mixed_data['int_activity'] = mixed_data['activity'] # producing copy from col 'activity' with name 'int_activity'
    # replace activity labels in 'int_activity' with int from dict, use regex to match occurrences with spaces
    mixed_data['int_activity'].replace(
        {' *jog.*': 1,  # 'jogging', but also 'joggen' and variants including space or other characters before and after
         ' *lying *': 2,
         ' *reading *': 3,
         ' *reading_out *': 4,
         ' *sitting *': 5,
         ' *talking *': 6,
         ' *walk.*': 7},
        inplace=True, regex=True)
    print(mixed_data)

    # codes, uniques = pd.factorize(mixed_data.activity)   # create unique integers for each unique activity
    # mixed_data['int_activity'] = codes   # write integer labells in new column 'int_activity
    mixed_data = mixed_data.drop(columns=['time_s', 'timestamp_s', 'status', 'activity'])  # drop unnecessary columns
    mixed_data.to_csv(folder + 'Mixed_data.csv', index=False, sep=',')



def sample_data_subjectwise():
    # This function loops through all the participant folders in the project folder and
    # executes the function 'sample_data()' for them.

    # discard hidden folders starting with . & this script
    all_files = [f for f in os.listdir(project_folder) if not f.startswith('.') and not f.endswith('py')]
    for subject_folder in all_files:
        sample_data(folder=project_folder + subject_folder + '\\', window=window)
        print("We are done with sample_data_subjectwise")


sample_data_subjectwise()
