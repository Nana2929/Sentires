import pickle
import gzip
import re
import argparse
from typing import Final, List, Dict
import json
SUMMARY:Final[str] = 'summary'
REVIEWTEXT:Final[str] = 'text' # 'text'
ITEMID:Final[str] = 'reviewid'
REVIEWERID:Final[str] = 'userid'
RATING:Final[str] = 'rating'


def main(args):
    raw_path = args.input_file # 'input/reviews_Musical_Instruments_5.json.gz'  # path to load raw reviews


    infilename = raw_path.split('/')[-1].split('.')[0]
    # ======================
    # the below names have to be fixed so that the following processing scripts could work
    perrow_path:str = 'input/record.per.row.txt'
    pkl_path:str = 'input/product2json.pickle'
    writer_1 = open(perrow_path, 'w', encoding='utf-8')
    product2text_list = {}
    product2json = {}
    with open(raw_path, 'r') as f:
        reviews = json.load(f)
    for review in reviews:
        text = ''
        if SUMMARY in review:
            summary = review[SUMMARY]
            if summary != '':
                text += summary + '\n'
        text += review[REVIEWTEXT]

        writer_1.write('<DOC>\n{}\n</DOC>\n'.format(text))

        json_doc = {'user': review[REVIEWERID],
                    'item': review[ITEMID],
                    'rating': int(review[RATING]),
                    'text': text}

        if ITEMID in product2json:
            product2json[ITEMID].append(json_doc)
        else:
            product2json[ITEMID] = [json_doc]

        if ITEMID in product2text_list:
            product2text_list[ITEMID].append('<DOC>\n{}\n</DOC>\n'.format(text))
        else:
            product2text_list[ITEMID] = ['<DOC>\n{}\n</DOC>\n'.format(text)]

    with open('input/records.per.product.txt', 'w', encoding='utf-8') as f:
        for (product, text_list) in product2text_list.items():
            f.write(product + '\t' + str(len(text_list)) + '\tfake_URL')
            text = '\n\t' + re.sub('\n', '\n\t', ''.join(text_list).strip()) + '\n'
            f.write(text)
    pickle.dump(product2json, open(pkl_path, 'wb'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type = str, help='path to the raw review file')
    # parser.add_argument('-o', '--output_file', type = 'str', help='path to the output file')
    args = parser.parse_args()
    main(args)