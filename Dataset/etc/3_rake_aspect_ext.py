#%%
from rake_nltk import Rake
from nltk.corpus import wordnet as wn
from rake_nltk import Metric
import argparse
import json
import string
from collections import Counter, defaultdict
from typing import List, Dict, Final, Tuple
from bisect import insort_left



ADJ:Final[str] = 'a'
NOUN:Final[str]= 'n'
VERB: Final[str]= 'v'
ADV:Final[str]= 'r'
LikelyAspects = [NOUN]
TEXTCOL:Final[str] = 'text'
ASPECTCOL:Final[str] = 'aspects'

def read_file(path:str):
    with open(path, 'r') as f:
        read_data = json.load(f)
    return read_data

# use wordnet pos filtering?
# To get keyword phrases ranked highest to lowest with scores.
def wordnet_maxpos(term):
    synsets = wn.synsets(term)
    counter = Counter([syns.pos() for syns in synsets])
    return counter.most_common(1)[0] if len(counter) > 0 else None



def wn_filter(terms:List[Tuple[int,str]], kargs:Dict):


    _empty = 0
    _notinwn = 0
    _incorrectpos = 0
    sorted_by_scores = []

    for term_score, term in terms:
        # filtering by punctuations
        term = term.translate(str.maketrans('', '', string.punctuation))
        if len(term) == 0:
            _empty+= 1; continue
        term_pos = wordnet_maxpos(term)
        if not term_pos:
            _notinwn += 1; continue
        term_pos = term_pos[0]
        if term_pos not in LikelyAspects:
            _incorrectpos += 1; continue

        # ===== adding the term to the list =====

        insort_left(sorted_by_scores, (term_score, term), key = lambda x: x[0])
    print(f'\t# Not in wordnet: {_notinwn}')
    print(f'\t# Puncts dummy words: {_empty}')
    print(f'\t# Incorrect POS: {_incorrectpos}')

    if len(kargs.keys() & {'keepsize', 'keepratio'}) != 1:
        raise ValueError('One keyword argument is required: specify only keepsize, or keepratio')
    if 'keepsize' in kargs:
        keepsize = kargs['keepsize']
        if keepsize == -1:
            keepsize = len(sorted_by_scores)
    else: keepsize = int(len(terms) * kargs['keepratio'])

    keepsize = min(keepsize, len(sorted_by_scores))

    sbs = sorted_by_scores[::-1]
    print(f'\t# Keeping {keepsize} terms')
    return sbs[:keepsize]

#%%
from typing import List
def v2_tokens_alignment(sub_seq: List, seq: List) -> List[List[int]]:
    """ map sub_sequence to sequence (find its best contiguous position)
    Returns:
        List[List[int]]: the index of sub_sequence:sequence mapping
    For multiple occurrences of the subseq,
    it returns only the last occurrence's token indices
    eg.
    x = 'boost time is super fast boost time'
    y = 'boost time'
    return: [[0, 5], [1, 6]]
    """
    row = len(sub_seq)
    col = len(seq)
    NULL = -100

    alignment_tables = [[0]*(col+1) for _ in range(row+1)]

    result = [[i, 0] for i in range(0, row)]

    for r in range(row-1, -1, -1):

        ali_v, ali_idx = 0, NULL

        for c in range(col-1, -1, -1):
            if seq[c] == sub_seq[r]:
                alignment_tables[r][c] = 1 + alignment_tables[r+1][c+1]

            if alignment_tables[r][c] > ali_v:
                ali_v, ali_idx = alignment_tables[r][c], c

        result[r][-1] = ali_idx
    mapped_idx = [i[-1] for i in result]
    if NULL in mapped_idx: return None
    return mapped_idx

# sub_seq = [2009, 2064, 2175, 2119, 3971, 1012, 2057, 2035, 4797, 1012, 2009, 2003, 2054, 2017, 2079, 2007, 2009, 2008, 5609, 1012]
# seq = [2009, 2064, 2175, 2119, 3971, 1012, 2057, 2035, 4797, 1012, 2009, 2003, 2054, 2017, 2079, 2007, 2009, 2008, 5609, 1012]
# x = 'boost time is super fast boost time'
# y = 'time is super'
# x = x.strip().split()
# y = y.strip().split()
# result = v2_tokens_alignment(y, x)
# print(result)
#%%



def seqlabel(keywords:set, sentence:str)->List:

    """label the keyword index position within the sentence

    Returns:
        List: the aspect fields in the form of List[Dict]
        # "aspects": [i
        #             {
        #                 "term": [
        #                     "cord"
        #                 ],
        #                 "polarity": "neutral",
        #                 "from": 9,
        #                 "to": 10
        #             },
        #             {
        #                 "term": [
        #                     "battery",
        #                     "life"
        #                 ],
        #                 "polarity": "positive",
        #                 "from": 16,
        #                 "to": 18
        #             }
        #         ],
    """

    aspects_field = []
    sentence = sentence.strip().split()
    tokens = set(x.strip() for x in sentence)
    hit_keywords = tokens.intersection(keywords)
    if len(hit_keywords) == 0:
        return
    for keyword in hit_keywords:
        keyword = keyword.strip().split()
        match = v2_tokens_alignment(sub_sequence = keyword,
                sequence = sentence)
        if match:
            aspects_field.append(
            {
                "term": keyword,
                "polarity": "not-labeld", # this is not labeld; default value as "not-labeled"
                "from": match[0],
                "to": match[-1] + 1 # the end index is exclusive
            }
        )
    return aspects_field


def main(args, kargs):
    print(f'* RAKE & Wordnet filter *')
    print(f'\tinput: {args.input}')
    readdata = read_file(args.input)
    sentences = [d[TEXTCOL] for d in readdata]
    r = Rake()
    r.extract_keywords_from_sentences(sentences)
    phscores = r.get_ranked_phrases_with_scores()
    MINL, MAXL = 1, 3
    # dfratio_r = Rake(ranking_metric = Metric.DEGREE_TO_FREQUENCY_RATIO)
    fr = Rake(ranking_metric = Metric.WORD_FREQUENCY, punctuations = string.punctuation,
            min_length = MINL, max_length = MAXL)

    # ph_ratio = r.get_ranked_phrases()
    fr.extract_keywords_from_sentences(sentences)
    ph_freq = fr.get_ranked_phrases_with_scores()
    ph_freq = set(ph_freq)
    print(f'\t# Extracting keywords: {len(ph_freq)}')
    ftrd_phrases = wn_filter(ph_freq, kargs)
    print(*ftrd_phrases[:5], sep = '\n')
    keyword_set = set([p[1] for p in ftrd_phrases])
    aspect_relabeled_data = []
    for data in readdata:
        relabeled_aspect_fields = seqlabel(keyword_set, data[TEXTCOL])
        data[ASPECTCOL] = relabeled_aspect_fields #might be an empty list
        aspect_relabeled_data.append(data)
    with open(args.output, 'w') as f:
        json.dump(aspect_relabeled_data, f, ensure_ascii = False, indent = 4)

    print(f'\tDone relabeling. Output file: {args.output}')

if __name__ == "__main__":
    # (base) nanaeilish@nanaeilish-MS-7D59:~/projects/Github/Sentires-Guide/Dataset/etc$ python3 3_rake.py -i ../Laptop/Train_proc.json
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='../Laptop/Train_proc.json')
    parser.add_argument('-o', '--output', type=str, default='../Laptop/Train_proc_rake.json')
    parser.add_argument('-k', '--keepsize', type=int, default=300)
    args = parser.parse_args()
    print(args)
    main(args, {'keepsize': args.keepsize})

# %%
# x = 'boost time is super fast boost time'
# y = 'time is super'
# x = x.strip().split()
# y = y.strip().split()
# result = tokens_alignment(y, x)
# print(result)
