#%%
# =========== checking Sentires Result ==========
import pickle
trainpath = './English-Jar/lei/output/Laptop-Train_reviews.pickle'
testpath = './English-Jar/lei/output/Laptop-Test_reviews.pickle'
with open(trainpath, 'rb') as f:
    train_sentires = pickle.load(f)
with open(testpath, 'rb') as f:
    test_sentires = pickle.load(f)

TRIPLETS = 'sentence'
TEXT = 'text'
REVIEWID = 'item'
# %%
poldict = {1: 'positive', 0:'neutral', -1:'negative'}
trainsent_vis_output = './English-Jar/lei/output/Laptop-Train_sentires_vis.txt'
with open(trainsent_vis_output, 'w') as f:
    for data in train_sentires:
        if data.get(TRIPLETS, None):
            print("============", file = f)
            print(f'review id: {data[REVIEWID]}', file = f)
            print(f'text: {data[TEXT]}', file = f)
            for sentence in data[TRIPLETS]:
                aspect, opinion, text, pol = sentence
                print(f'\taspect: {aspect}\n\topinion: {opinion}', file = f)
                print(f'\t{poldict[pol]}', file = f)

# %%
# =========== Loading the data back ===========
import json
from typing import Dict, List, Tuple
from collections import defaultdict
dsetdir = './Dataset/Laptop'
traindatapath = f'{dsetdir}/Train_proc.json'
pairing:Dict[int, Dict]= defaultdict(lambda:{'sentires':None, 'labeled':None})
TrueAspects = set()
DetectAspects = set()
with open(traindatapath, 'r') as f:
    trainset = json.load(f)
for sdata in train_sentires:
    pairing[sdata[REVIEWID]]['sentires'] = sdata
    if sdata.get(TRIPLETS, None):
        for sentence in sdata[TRIPLETS]:
            aspect, opinion, text, pol = sentence
            print(aspect)
            DetectAspects.add(aspect)
#%%
# ====== SemEval 14 SB1: aspect extraction Eval Metrics ========
for exid in range(len(trainset)):
    tdata = trainset[exid]
    assert tdata['reviewid'] == exid
    pairing[exid]['labeled'] = tdata
    labeled_aspects = set(' '.join(tok for tok in asp['term']) for asp in tdata['aspects'])
    TrueAspects = TrueAspects.union(labeled_aspects)
    print(f'{len(labeled_aspects)}')

#%%
def calcPR(S:set, G:set)->Tuple[float, float]:
    """return precision, recall for the S, G

    Args:
        S (set): system detected aspect terms for the whole dataset
        G (set): gold-labeled aspect terms for the whole dataset (split)

    Returns:
        Tuple[float, float]: Precision, Recall
    """
    P = len(S.intersection(G))/len(S)
    R = len(S.intersection(G))/len(G)
    return P, R
calcPR(S = DetectAspects, G = TrueAspects)
#(0.5555555555555556, 0.0048216007714561235)




