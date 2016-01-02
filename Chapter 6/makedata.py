__author__ = 'Andrew'
import csv, sys

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Chapter 6\\"

def take_from_dataset(count=1000, skip=1, input_file_name='avito_train.tsv', output_file_name='train.csv', rate=None):
    if count is not None and rate is not None:
        good_count = int(rate * count)
        bad_count = count - good_count


        with open(working_path + output_file_name, 'wb') as outputcsv:
            writer = csv.writer(outputcsv)
            with open(working_path + input_file_name, 'rb') as inputcsv:
                reader = csv.reader(inputcsv, delimiter='\t')
                good_index = 0
                bad_index = 0
                index = 0
                for row in reader:
                    if index < skip:
                        index += 1
                        continue

                    is_blocked = int(row[8])

                    if is_blocked == 1 and bad_index < bad_count:
                        writer.writerow(row)
                        bad_index += 1

                    if is_blocked == 0 and good_index < good_count:
                        writer.writerow(row)
                        good_index += 1

                    if bad_index >= bad_count and good_index >= good_count:
                        break
    else:
        with open(working_path + output_file_name, 'wb') as outputcsv:
            writer = csv.writer(outputcsv)
            with open(working_path + input_file_name, 'rb') as inputcsv:
                reader = csv.reader(inputcsv, delimiter='\t')
                index = 0
                for row in reader:
                    if index < skip:
                        index += 1
                        continue

                    writer.writerow(row)
                    if count is not None and index == count + skip:
                        break
                    else:
                        index += 1

def show_top_rows(f, top=10, tsv=True):
    with open(working_path + f, 'rb') as csvf:
        if tsv:
            reader = csv.reader(csvf, delimiter='\t')
        else:
            reader = csv.reader(csvf)

        for index, row in enumerate(reader):
            if index > top:
                break

            for f in row:
                str = f.decode("utf-8")
                print str.encode(sys.stdout.encoding, errors='replace'),
            print

# print "Avito tsv"
# show_top_rows('avito_test.tsv')
#
# print "Avito csv"
# show_top_rows('avito_test.csv', tsv=False)


# take_from_dataset(count=50000, output_file_name='train_eq.csv', rate=0.5)
# take_from_dataset(count=50000)
# take_from_dataset(skip=50000, count=1000, output_file_name='test.csv')
take_from_dataset(skip=50000, count=1000, output_file_name='test_eq.csv', rate=0.5)
# take_from_dataset(count=None, input_file_name='avito_test.tsv', output_file_name='avito_test.csv')