#from datetime import datetime
from Preparation import prep
from FeatureExtraction import extract
from NB_Classifier import NB

#startTime = datetime.now()

partic= 'AI\\' # insert name of the participants folder with the raw data in it

prep(partic)
extract(partic)
NB(partic)

#print( datetime.now() - startTime)
