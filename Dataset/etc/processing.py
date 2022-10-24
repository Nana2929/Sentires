import json
import argparse
import logging
from typing import Final, List, Dict


def main(args):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    filepath = f'../{args.dataset}/{args.split}.json'
    outfilepath = f'../{args.dataset}/{args.split}_proc.json'
    # filepath = './Dataset/Laptop/Train.json'
    # outfilepath = f'./Dataset/Laptop/Train_proc.json'
    with open(filepath, 'r') as f:
        data = json.load(f)

    logger.info(f'file keys: {data[0].keys()}')
    textlikes: Final[List] = ['sentence', 'reviewtext', 'text', 'review']
    reviewid_likes: Final[List] = ['review_id',
                                   'reviewid', 'id', 'itemid', 'item_id']
    userid_likes: Final[List] = [
        'reviewer_id', 'reviewerid', 'userid', 'user_id']
    ratings_like: Final[List] = ['rating', 'star', 'ratings', 'overall']

    # ==========UNIFORM============
    TEXT: Final[str] = 'text'
    REVIEWID: Final[str] = 'reviewid'
    USERID: Final[str] = 'userid'
    RATING: Final[str] = 'rating'
    KeyMapping = {}
    for key in data[0].keys():
        # ====== matching key =======
        if key.lower() in textlikes:
            KeyMapping[TEXT] = key
        if key.lower() in reviewid_likes:
            KeyMapping[REVIEWID] = key
        if key.lower() in userid_likes:
            KeyMapping[USERID] = key
        if key.lower() in ratings_like:
            KeyMapping[RATING] = key

    logger.info(f'key mapping: {KeyMapping}')
    proc_examples = []

    for example_id, example in enumerate(data):

        if TEXT not in KeyMapping:
            raise ValueError(f'No text found in example {example_id}.')
        if RATING not in KeyMapping:
            fake_rating = -100  # no rating
        proc_example = {
            TEXT: example[KeyMapping[TEXT]],
            REVIEWID: example[KeyMapping[REVIEWID]] if REVIEWID in KeyMapping else example_id,
            USERID: example[KeyMapping[USERID]] if USERID in KeyMapping else example_id,
            RATING: example[KeyMapping[RATING]] if RATING in KeyMapping else fake_rating,
        }
        other_keys = set(data[0].keys()) - set(KeyMapping.values())
        # adding back the other extra keys
        for okey in other_keys:
            proc_example[okey] = example[okey]
        proc_examples.append(proc_example)

    with open(outfilepath, 'w') as f:
        json.dump(proc_examples, f, ensure_ascii=False, indent=4)
    logger.info('sucessfully written into file: {}'.format(outfilepath))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-dset', '--dataset', default='Laptop', type=str)
    parser.add_argument('-s', '--split', default='Train', type=str)
    args = parser.parse_args()
    main(args)
