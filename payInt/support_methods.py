import csv
from django.conf import settings
import time
import os
from datetime import datetime


# These are utility methods for reading files, parsing names, and checking if a file exists.


def file_exists(form, obj):
    for field in form:
        field.exists = False
        if field.name == 'timer_header':
            if obj.timer_header:
                field.exists = True
        if field.name == 'employee_list':
            if obj.employee_list:
                field.exists = True
        if field.name == 'payroll_items':
            if obj.payroll_items:
                field.exists = True


def parse_timer(timer_header):
    """
    parses the timer list file and returns the first two lines the header as a list of lists
    :param timer_header:
    :return:
    """
    csv_file = open(timer_header.path, 'r')
    file_reader = csv.reader(csv_file, delimiter='\t')
    x = 0
    result = []
    try:
        for row in file_reader:
            contents = []
            for cell in row:
                contents.append(str(cell))
            if x < 2:
                result.append(contents)
                x += 1
            else:
                break

        # makes it look like it came from a quickbooks pro timer
        result[1][5] = 'Y'

    except Exception as e:
        print(e)
        csv_file.close()
        return None
    csv_file.close()
    return result


def get_company(timer_header):
    """
        parses the timer list file and returns the first two lines the header as a list of lists
        :param timer_header:
        :return:
        """
    csv_file = open(timer_header.path, 'r')
    file_reader = csv.reader(csv_file, delimiter='\t')
    x = 0
    result = None
    for row in file_reader:
        if x == 1:
            result = row[3]
        x += 1
    return result


def parse_employee(employee_list):
    """
    parses the list of employees and returns an employee list
    :param employee_list:
    :return:
    """
    csv_file = open(employee_list.path, 'r')
    file_reader = csv.reader(csv_file, delimiter='\t')

    result = []

    try:
        for row in file_reader:
            if row[0] == 'EMP' and row[-2] == 'N':
                result.append(row[1])
    except Exception as e:
        print(e)
        csv_file.close()
        return None
    csv_file.close()
    return result


def parse_payroll(payroll_items):
    """
    parses the list of payroll items and returns a payroll item list
    :param payroll_items:
    :return:
    """
    csv_file = open(payroll_items.path, 'r')
    file_reader = csv.reader(csv_file, delimiter=',')
    result = []

    try:
        for row in file_reader:
            if row[2] == "Hourly Wage":
                result.append(row[1])
    except Exception as e:
        print(e)
        csv_file.close()
        return None
    csv_file.close()
    return result


def parse_extract_names(extract):
    # This reader modifies any null values that exist in the csv extract file. Otherwise it throws an exception
    csv_file = open(extract.path)
    file_reader = csv.reader(x.replace('\0', '') for x in csv_file)
    result = []
    try:
        for row in file_reader:
            if row[3] == 'EOT':
                first = row[2].strip()
                last = row[1].strip()
                result.append({'first': first, 'last': last})
    except Exception as e:
        print(e)
        csv_file.close()
        return None
    csv_file.close()
    return result


def split_name(emp_name):
    middle_name = None
    try:
        first_name, middle_name, last_name = emp_name.split()
    except:
        first_name, last_name = emp_name.split()

    if middle_name:
        result = {'first': first_name, 'last': last_name, 'middle': middle_name}
        return result
    else:
        result = {'first': first_name, 'last': last_name}
        return result


def sort_by_last_name(name_list):
    temp = []
    result = []
    for i in name_list:
        temp.append(split_name(i))
    temp = sorted(temp, key=lambda l: l['last'], reverse=False)

    for i in temp:
        try:
            result.append(i['first'] + ' ' + i['middle'] + ' ' + i['last'])
        except:
            result.append(i['first'] + ' ' + i['last'])

    return result


def compare_names(tc_names, ex_names):
    result = []

    for t_emp in tc_names:
        matched = False
        for e_emp in ex_names:
            if e_emp.tc_name == t_emp['first'] + ' ' + t_emp['last']:
                matched = True
                break
        if matched:
            pass
        else:
            result.append(t_emp)
    return result


def create_export(timer_header, payroll_items, employee_list, extract, user_id):
    header = parse_timer(timer_header)
    current_time = time.time()
    pay_dict = prepare_list(payroll_items, 'item')
    emp_dict = prepare_list(employee_list, 'name')

    content = organize_rows(pay_dict, emp_dict, extract)
    header.append(settings.QB_HEADER)
    for i in content:
        header.append(i)

    path = os.path.join(settings.MEDIA_ROOT, 'user_' + str(user_id),
                        'QuickBooks-Employee-Hrs-Import.IIF')

    f = open(path, 'w', newline='')

    # wipe existing content
    f.truncate()

    # Writes the header
    csv_writer = csv.writer(f, delimiter=',', quotechar='"')
    csv_writer.writerows(header)

    f.close()

    return path


def organize_rows(pay_dict, emp_dict, extract):
    csv_file = open(extract.path)
    file_reader = csv.reader(x.replace('\0', '') for x in csv_file)
    result = []
    BEGIN = 'TIMEACT'
    date = datetime.now()
    total_times = []
    overtime = '0:00'
    first_row = True

    try:
        for row in file_reader:
            strip_row = []
            for i in row:
                strip_row.append(i.strip())
            row = strip_row
            if first_row:
                first_row = False
            else:
                input_date = row[4].strip() + ', ' + row[5].strip()
            try:
                date = datetime.strptime(input_date, '%m/%d, %Y')
            except:
                pass
            if row[3] == 'DTT':
                if not emp_dict[row[2] + ' ' + row[1]] == "Remove Employee":
                    try:
                        if row[8] == '0:00' or not row[8] or row[8] == '00:00':
                            # if there is not daily overtime on the day
                            day_total = row[6]
                            if total_times:
                                # if there were total time actions within the day like sick, pto, vacation
                                for entry in total_times:
                                    day_total = sub_hr_min(row[6], entry['duration'])
                                    if not pay_dict[entry['type']] == "Not Used":
                                        result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                            row[2] + ' ' + row[1]], '', pay_dict[entry['type']], entry[
                                                          'duration'], '', '', 'Y', 0]
                                        result.append(result_row)
                                    else:
                                        pass
                                total_times = []
                                if not day_total == '0:00' and not day_total == '00:00':
                                    if not pay_dict['REGULAR'] == "Not Used":
                                        result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                            row[2] + ' ' + row[1]], '', pay_dict['REGULAR'], day_total, '', '', 'Y', 0]
                                        result.append(result_row)
                            else:
                                # if there are no tt actions
                                if not pay_dict['REGULAR'] == "Not Used":
                                    result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                        row[2] + ' ' + row[1]], '', pay_dict['REGULAR'], day_total, '', '', 'Y', 0]
                                    result.append(result_row)
                        else:
                            # if there is daily overtime on the day
                            day_total = sub_hr_min(row[6], row[8])

                            # for the REGULAR hour entry
                            if not pay_dict['REGULAR'] == "Not Used":
                                result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                    row[2] + ' ' + row[1]], '', pay_dict['REGULAR'], day_total, '', '', 'Y', 0]
                                result.append(result_row)

                            # for the OVERTIME hour entry
                            if not pay_dict['OVERTIME'] == "Not Used" and not row[8] == '00:00' and not row[
                                                                                                            8] == '0:00':
                                result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                    row[2] + ' ' + row[1]], '', pay_dict['OVERTIME'], row[8], '', '', 'Y', 0]
                                result.append(result_row)
                            overtime = add_hr_min(overtime, row[8])

                    except:
                        # This is to catch exceptions where the field that would contain overtime within the daily totals is empty or null
                        if not pay_dict['REGULAR'] == "Not Used":
                            result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                row[2] + ' ' + row[1]], '', pay_dict['REGULAR'], row[6], '', '', 'Y', 0]
                            result.append(result_row)

            elif row[3] == 'EOT':
                if not emp_dict[row[2] + ' ' + row[1]] == "Remove Employee":
                    # this is for catching weekly overtime if it exists
                    left_over_overtime = sub_hr_min(overtime, row[6])
                    if left_over_overtime == '0:00':
                        pass
                    elif left_over_overtime[0] == '-':
                        left_over_overtime = left_over_overtime[1:len(left_over_overtime)]

                        result[-1][6] = sub_hr_min(result[-1][6], left_over_overtime)

                        if not pay_dict[
                                   'OVERTIME'] == "Not Used" and not left_over_overtime == '00:00' and not left_over_overtime == '0:00':
                            result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                row[2] + ' ' + row[1]], '', pay_dict['OVERTIME'], left_over_overtime, '', '', 'Y', 0]
                            result.append(result_row)
                    else:
                        result[-1][6] = sub_hr_min(result[-1][6], left_over_overtime)

                        if not pay_dict[
                                   'OVERTIME'] == "Not Used" and not left_over_overtime == '00:00' and not left_over_overtime == '0:00':
                            result_row = [BEGIN, date.strftime('%m/%d/%Y'), '', emp_dict[
                                row[2] + ' ' + row[1]], '', pay_dict['OVERTIME'], left_over_overtime, '', '', 'Y', 0]
                            result.append(result_row)
                    overtime = '0:00'

            elif row[3] == 'DET' and row[7] == 'T':
                if not emp_dict[row[2] + ' ' + row[1]] == "Remove Employee":
                    if row[8] == 'Sick' or row[8] == 'SICK':
                        action_type = "SICK"
                    elif row[8] == 'PTO' or row[8] == 'Pto':
                        action_type = "PTO"
                    elif row[8] == 'VACATION' or row[8] == 'Vacation':
                        action_type = "VACATION"
                    elif row[8] == 'HOLIDAY' or row[8] == 'Holiday':
                        action_type = "HOLIDAY"
                    elif row[8] == 'BEREAVEMENT' or row[8] == 'Bereavement' or row[8] == 'BEREAVMENT' or row[
                        8] == 'Bereavment':
                        action_type = "BEREAVEMENT"
                    else:
                        action_type = "OTHER"
                    total_times.append({'duration': row[6], 'type': action_type})

    except Exception as e:
        print(e)
        csv_file.close()
        return None
    csv_file.close()
    return result


def prepare_list(query_set, entry_type):
    result = {}

    if entry_type == 'name':
        for entry in query_set:
            result[entry.tc_name] = entry.qb_name

    else:
        for entry in query_set:
            result[entry.tc_item] = entry.qb_item
    return result


def sub_hr_min(i, j):
    i_hr, i_min = i.split(':')
    j_hr, j_min = j.split(':')
    i_hr = int(i_hr)
    i_min = int(i_min)
    j_hr = int(j_hr)
    j_min = int(j_min)
    i_hr_min = i_hr * 60 + i_min
    j_hr_min = j_hr * 60 + j_min
    result_hr_min = i_hr_min - j_hr_min
    result_min = int(abs(result_hr_min) % 60)
    result_hr = int(result_hr_min / 60)
    result = str(result_hr) + ':' + "{:02d}".format(result_min)
    return result


def add_hr_min(i, j):
    i_hr, i_min = i.split(':')
    j_hr, j_min = j.split(':')
    i_hr = int(i_hr)
    i_min = int(i_min)
    j_hr = int(j_hr)
    j_min = int(j_min)
    i_hr_min = i_hr * 60 + i_min
    j_hr_min = j_hr * 60 + j_min
    result_hr_min = i_hr_min + j_hr_min
    result_min = int(result_hr_min % 60)
    result_hr = int(result_hr_min / 60)
    result = str(result_hr) + ':' + "{:02d}".format(result_min)
    return result


def check_employees_matched(employees):
    for emp in employees:
        if not emp.qb_name:
            return False
    return True


def check_items_matched(items):
    for item in items:
        if not item.qb_item:
            return False
    return True
