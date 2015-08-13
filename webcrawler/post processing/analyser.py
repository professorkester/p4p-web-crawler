import csv
import operator

class analyser():
    def __init__(self, filename):
        self.filename = filename

    def print_dict_to_csv(self, myDict, filename):
        f = open(filename, "wb")
        writer = csv.writer(f)
        for field in myDict:
            writer.writerow([str(field),str(myDict[field])])

    def count_field(self, col_name, split_by_comma=False, print_to_file=False):
        with open(self.filename, 'rb') as f:
            reader = csv.reader(f)
            column_names = reader.next()
            col_num = -1

            for i in range(0, len(column_names)):
                if column_names[i] == col_name:
                    col_num = i

            count_dict = {}
            rownum = 1

            if col_num != -1:
                for row in reader:
                    try:
                        field = row[col_num]
                    except IndexError as e:
                        print rownum

                    if (split_by_comma):
                        field_array = field.strip().split(",")
                        for f in field_array:
                            if f in count_dict:
                                count_dict[f] += 1
                            else:
                                count_dict[f] = 1
                    else:
                        if field in count_dict:
                                count_dict[field] += 1
                        else:
                                count_dict[field] = 1
                    rownum += 1

            sorted_dict = sorted(count_dict.items(), key=operator.itemgetter(1), reverse=True)
            if print_to_file:
                self.print_dict_to_csv(sorted_dict, col_name + '_count.csv')
            return count_dict


    def count_two_fields(self, first_col, second_col, split_by_comma=False, print_to_file=False):
        """ gets all cols for certain field"""
        with open(self.filename, 'rb') as f:
            reader = csv.reader(f)
            column_names = reader.next()
            first_col_num = -1
            second_col_num = -1

            for i in range(0, len(column_names)):
                if column_names[i] == first_col:
                    first_col_num = i
                if column_names[i] == second_col:
                    second_col_num = i

            count_dict = {}
            rownum = 1

            if first_col_num is not -1 and second_col_num is not -1:
                for row in reader:
                    try:
                        first_field = row[first_col_num]
                        second_field = row[second_col_num]
                    except IndexError as e:
                        print rownum
                    if first_field in count_dict:
                        count_dict[first_field].append(second_field)
                    else:
                        count_dict[first_field] = [second_field]

            if print_to_file:
                self.print_dict_to_csv(count_dict, str(first_col) + '_' + str(second_col) + '_' + 'Count.csv')
            return count_dict
