# coding: utf-8
__author__ = 'Andrew'

import csv, sys
import docclass
import numpy as np

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Chapter 6\\"
train_file = working_path + 'train.csv'
test_file = working_path + 'test.csv'
avito_test_file = working_path + 'avito_test.csv'
avito_subm_file = working_path + 'avito_subm.csv'

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

def get_train_data(file):
    result = []
    with open(file, 'rb') as csvf:
        reader = csv.reader(csvf, quotechar='"')
        # skip header
        reader.next()
        for index, row in enumerate(reader):
            title = row[3].decode("utf-8")
            desc = row[4].decode("utf-8")
            is_blocked = int(row[8])

            result.append(((title + ' ' + desc), is_blocked))
    return result

def train(cl, file=train_file):
    train_data = get_train_data(file)
    for text, l in [x for x in train_data]:
        cl.train(text,'good' if l == 0 else 'bad')

def test(cl, file=test_file):
    bad_true = 0
    bad_false = 0
    good_true = 0
    good_false = 0
    good = 0
    bad = 0
    v_true = 0
    v_false = 0
    with open(file, 'rb') as csvf:
        reader = csv.reader(csvf, quotechar='"')
        # skip header
        reader.next()
        for index, row in enumerate(reader):
            title = row[3].decode("utf-8")
            desc = row[4].decode("utf-8")
            is_blocked = int(row[8])

            text = title + ' ' + desc
            res, score = cl.classify(text)

            if res == 'good':
                good += 1
                if is_blocked == 0:
                    v_true += 1
                else:
                    v_false += 1
            elif res == 'bad':
                bad += 1
                if is_blocked == 1:
                    v_true += 1
                else:
                    v_false += 1

            if res == 'good':
                if is_blocked == 0:
                    good_true += 1
                else:
                    good_false += 1
            else:
                if is_blocked == 0:
                    bad_false += 1
                else:
                    bad_true += 1

    abs_matrix = [[good_true, good_false], [bad_false, bad_true]]
    total = float(sum([good_true, good_false,bad_false, bad_true]))
    rate_matrix = [[round(good_true / total,3), round(good_false/total,3)],
                   [round(bad_false/total,3), round(bad_true/total,3)]]
    return (abs_matrix, rate_matrix, good, bad, v_true, v_false)

def make_submission(cl, tfile=avito_test_file,sfile = avito_subm_file):
    with open(sfile, 'wb') as csv_output:
        writer = csv.writer(csv_output)
        writer.writerow(['id'])

        result = []
        with open(tfile, 'rb') as csv_input:
            reader = csv.reader(csv_input, quotechar='"')
            # skip header
            reader.next()
            for index, row in enumerate(reader):
                title = row[3].decode("utf-8")
                desc = row[4].decode("utf-8")
                id = int(row[0])

                text = (title + ' ' + desc)
                res,score = cl.classify(text, target_cat='bad')
                result.append((score, id))

        result.sort(key=lambda x: x[0], reverse=True)

        # write results to file
        for score,id in result:
            writer.writerow([id])#, score

# cl = docclass.fisherclassifier(docclass.getwords)
cl = docclass.naivebayes(docclass.getwords)
# cl = docclass.fisherclassifier(docclass.getwords_avito)

# print "Start training"
# train(cl)
train(cl, file=working_path + 'train_eq.csv')

# for cat, fs in cl.get_top_features(20).items():
#     print "Category", cat,
#     for f, x in fs:
#         print '%s[%d]' % (f, x),
#     print

# print "Make submission file"
# make_submission(cl)

print "Start testing"
# abs_matrix, rate_matrix, good, bad, v_true, v_false = test(cl)
abs_matrix, rate_matrix, good, bad, v_true, v_false = test(cl, file=working_path + 'test_eq.csv')
print "Good:", good
print "Bad:", bad

print "Right count:", v_true
print "Wrong count:", v_false


print "Abs values"
print np.array(abs_matrix)
print "Rates"
print np.array(rate_matrix)
