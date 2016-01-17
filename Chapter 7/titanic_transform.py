import csv

work_path = 'C:\\Users\Andrew\\Source\\Repos\\CollIntel\\Chapter 7\\'

def traverse_file(row_f, header_f, input_csv_file, output_csv_file, correction):
    with open(work_path + input_csv_file, 'rb') as f_input:
        reader = csv.reader(f_input)
        with open(work_path + output_csv_file, 'wb') as f_output:
            writer = csv.writer(f_output)

            header = reader.next()
            header_f(header, correction)
            writer.writerow(header)

            for row in reader:
                row_f(row, correction)
                writer.writerow(row)

def parse_title(input_csv_file='train.csv', output_csv_file='train_aug.csv', correction=0):
    def row_f(row, correction):
        name = row[3-correction]
        title = 0
        if 'Mr.' in name or 'Don.' in name or 'Dr.' in name or 'Col.' in name or 'Sir.' in name \
            or 'Rev.' in name or 'Jonkheer.' in name or 'Capt.' in name or 'Major.' in name:
            title = 1
        elif 'Mrs.' in name or 'Mme.' in name or 'Lady.' in name or 'Mlle.' in name \
                or ' Countess.' in name or 'Ms.' in name or 'Dona.' in name:
            title = 2
        elif 'Master.' in name:
            title = 3
        elif 'Miss.' in name:
            title = 4
        row.append(str(title))

    def header_f(header, correction):
        header.append('Title')

    traverse_file(row_f, header_f, input_csv_file, output_csv_file, correction)


def build_notalone(input_csv_file='train.csv', output_csv_file='train_aug.csv', correction=0):
    def row_f(row, correction):
        sibsp = int(row[6-correction])
        parch = int(row[7-correction])

        notalone = 0 if sibsp == 0 and parch == 0 else 1
        row.append(str(notalone))

    def header_f(header, correction):
        header.append('Notalone')

    traverse_file(row_f, header_f, input_csv_file, output_csv_file, correction)


parse_title()
build_notalone(input_csv_file='train_aug.csv', output_csv_file='train_aug1.csv')
# parse_title(input_csv_file='test.csv', output_csv_file='test_aug.csv', correction=1)