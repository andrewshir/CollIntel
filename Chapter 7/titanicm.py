import csv

work_path = 'C:\\Users\Andrew\\Source\\Repos\\CollIntel\\Chapter 7\\'

def run(predictor, csv_file='train.csv'):
    def get_result(result_dict):
        return "%0.2f" % (float(result_dict['w']) / (result_dict['w'] + result_dict['r']))

    with open(work_path + csv_file, 'rb') as f:
        reader = csv.reader(f)
        # skip header
        reader.next()

        result = {'male': {1: {'r':0, 'w':0}, 2: {'r':0, 'w':0}, 3: {'r':0, 'w':0}},
                'female': {1: {'r':0, 'w':0}, 2: {'r':0, 'w':0}, 3: {'r':0, 'w':0}}}
        right = 0
        wrong = 0

        values = []
        for row in reader:
            v = {'PassengerId': int(row[0]),
                 'Survived': int(row[1]),
                 'Pclass': int(row[2]),
                 'Name': row[3],
                 'Sex': row[4],
                 'Age': float(row[5]) if row[5] is not None and len(row[5]) > 0 else None,
                 'SibSp': int(row[6]) if row[6] is not None and len(row[5]) > 0 else None,
                 'Parch': int(row[7]) if row[7] is not None and len(row[5]) > 0 else None,
                 'Ticket': row[8],
                 'Fare': float(row[9]) if row[9] is not None and len(row[5]) > 0 else None,
                 'Cabin': row[10],
                 'Embarked': row[11]}
            values.append(v)

            predicted = predictor(v)
            r = result[v['Sex']][v['Pclass']]
            if v['Survived'] == predicted:
                r['r'] += 1
                right += 1
            else:
                r['w'] += 1
                wrong += 1

        print "==================================="
        print "Common rate: %0.2f [%d/%d] " % (float(right)/(right + wrong), right, right + wrong)
        print
        print "Error table"
        print "Male", get_result(result['male'][1]), get_result(result['male'][2]), get_result(result['male'][3])
        print "Female", get_result(result['female'][1]), get_result(result['female'][2]), get_result(result['female'][3])


def gender_model(v):
    if v['Sex'] == 'male':
        return 0
    else:
        return 1

def gender_pclass_fare_model(v):
    if v['Sex'] == 'male':
        return 0
    else:
        if v['Pclass'] == 3:
            if v['Fare'] > 20.0:
                return 0
            else:
                return 1
        else:
            return 1

def gender_pclass_fare_age_model(v):
    if v['Sex'] == 'male':
        if v['Pclass'] == 1:
            if v['Age'] is not None and v['Age'] < 18:
                return 1
            else:
                return 0
        else:
            return 0
    else:
        if v['Pclass'] == 3:
            if v['Fare'] > 20.0:
                return 0
            else:
                return 1
        else:
            return 1


def gender_pclass_fare_age_model_title(v):
    if v['Sex'] == 'male':
        # men
        if v['Pclass'] == 1:
            if v['Age'] is not None and v['Age'] < 18:
                return 1
            else:
                return 0
        elif v['Pclass'] == 2:
            if 'Master.' in v['Name']:
                return 1
            else:
                return 0
        else:
            return 0
    else:
        # women
        if v['Pclass'] == 3:
            if v['Fare'] > 20.0:
                return 0
            else:
                return 1
        else:
            return 1


# run(predictor=gender_model)
# run(predictor=gender_pclass_fare_model)
run(predictor=gender_pclass_fare_age_model)
run(predictor=gender_pclass_fare_age_model_title)
