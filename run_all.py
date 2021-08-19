#from datetime import datetime
from Preparation import prep
from FeatureExtraction import extract
from NB_Classifier import NB
import os

#startTime = datetime.now()


partic= 'D:\DoppleDaten\Backup_Aug12_subjects\\'  # insert name of the participants folder with the raw data in it
def classify_subwise():
    """
    Goes through folders in the data containing the activities sorted by subject no.
    Performs preparation of data, feature extraction and classification for every subject independently (external scripts)
    Output given by classifier script:
    """
    for folder in os.listdir(partic):
        prep(str(partic+folder+'\\'))
        extract(str(partic+folder+'\\'))
        NB((str(partic+folder+'\\')),folder)

classify_subwise()


#print( datetime.now() - startTime)

