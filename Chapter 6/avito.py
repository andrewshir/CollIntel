# coding: utf-8
__author__ = 'Andrew'

import csv, sys
import docclass

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Chapter 6\\"
train_file = working_path + 'train.csv'
test_file = working_path + 'test.csv'

def get_test_data(blocked=None):
    result = []
    with open(test_file, 'rb') as csvf:
        reader = csv.reader(csvf, quotechar='"')
        # skip header
        reader.next()
        for index, row in enumerate(reader):
            title = row[3].decode("utf-8")
            desc = row[4].decode("utf-8")
            is_blocked = int(row[8])

            if blocked is not None and is_blocked != blocked:
                continue
            result.append(((title + ' ' + desc).encode(sys.stdout.encoding, errors='replace'), is_blocked))
    return result

def get_train_data():
    result = []
    with open(train_file, 'rb') as csvf:
        reader = csv.reader(csvf, quotechar='"')
        # skip header
        reader.next()
        for index, row in enumerate(reader):
            title = row[3].decode("utf-8")
            desc = row[4].decode("utf-8")
            is_blocked = int(row[8])

            result.append(((title + ' ' + desc).encode(sys.stdout.encoding, errors='replace'), is_blocked))
    return result

def train(cl):
    train_data = get_train_data()
    for text, l in [x for x in train_data]:
        cl.train(text,'good' if l == 0 else 'bad')

def test(cl):
    test_data = get_test_data()
    right = 0
    wrong = 0
    for text, l in [x for x in test_data]:
        res = cl.classify(text)
        if res == 'good' and l == 0:
            right += 1
        else:
            wrong += 1

    return (right, wrong)



cl = docclass.fisherclassifier(docclass.getwords)

print "Start training"
train(cl)
print "Start testing"
right, wrong = test(cl)
print "Right:", right
print "Wrong:", wrong
print "Rate:", round(float(right)/(right + wrong), 2)
