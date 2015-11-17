__author__ = 'Andrew'
import csv

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Chapter 6\\"

def take_from_dataset(number=1000, input_file_name='avito_train.tsv', output_file_name='train.csv'):
    with open(working_path + output_file_name, 'wb') as outputcsv:
        writer = csv.writer(outputcsv)
        with open(working_path + input_file_name, 'rb') as inputcsv:
            reader = csv.reader(inputcsv, delimiter='\t')
            count = 0
            for row in reader:
                writer.writerow(row)
                if count == number:
                    break
                else:
                    count += 1

take_from_dataset()