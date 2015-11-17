# coding: utf-8
__author__ = 'Andrew'

import csv, sys
import docclass

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Chapter 6\\"
train_file = working_path + 'train.csv'
test_file = working_path + 'test.csv'

def show_test_data(blocked=1):
    with open(test_file, 'rb') as csvf:
        reader = csv.reader(csvf, quotechar='"')
        # skip header
        reader.next()
        for index, row in enumerate(reader):
            title = row[3].decode("utf-8")
            desc = row[4].decode("utf-8")
            is_blocked = int(row[8])

            if is_blocked != blocked:
                continue

            print is_blocked, (title + ' ' + desc).encode(sys.stdout.encoding, errors='replace')


def train(cl):
    raw_data = []
    with open(train_file, 'rb') as csvf:
        reader = csv.reader(csvf, quotechar='"')
        # skip header
        reader.next()
        for index, row in enumerate(reader):
            title = row[3].decode("utf-8")
            desc = row[4].decode("utf-8")
            is_blocked = int(row[8])

            raw_data.append(((title + ' ' + desc).encode(sys.stdout.encoding, errors='replace'), is_blocked))
    for text, l in [x for x in raw_data if x[1] == 0]:
        cl.train(text,'good' if l == 0 else 'bad')

# show_test_data()

cl = docclass.fisherclassifier(docclass.getwords)
train(cl)
print cl.classify(u'Услуги психолога, онлайн Консультация психолога — это действительно универсальное средство психологической помощи. Проблемы в общении, принятии себя, жизненные кризисы, неуверенность в себе, страхи, стресс — во всех этих и многих других ситуациях помощь психолога неоценима. ^p Часто к психологу обращаются для решения не только личных, но и семейных проблем и трудностей во взаимоотношениях — в таких ситуациях более эффективно семейное консультирование и консультирование пар. ^p Помощь, консультации психолога ОНЛАЙН! Низкие цены. Все вопросы направляйте на электронную почту.')
