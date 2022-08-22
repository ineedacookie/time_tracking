from django.conf import settings
from django.shortcuts import render, redirect
from .forms import ItemFormSet, EmployeeFormSet, FileForm, ExtractFileForm
from .models import PayrollItemsMatched, PayrollCenterUsers, EmployeesMatched
from .support_methods import *


def index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        pay_int = PayrollCenterUsers.objects.get(owner=request.user.id)

        payroll_items = False
        employee_list = False
        timeclick_extract_file = False
        export = False
        emp_matched = False
        item_matched = False
        file = ''
        if pay_int.payroll_items:
            payroll_items = True
        if pay_int.employee_list:
            employee_list = True
        if pay_int.timeclick_extract_file:
            timeclick_extract_file = True
        if pay_int.export:
            export = True

        # try to check if items and employees are matched
        try:
            emp_matched = check_employees_matched(EmployeesMatched.objects.filter(owner=pay_int))
            item_matched = check_items_matched(PayrollItemsMatched.objects.filter(owner=pay_int))
        except:
            print("EXCEPTION TRIGGERED")

        if timeclick_extract_file:
            file = str(pay_int.timeclick_extract_file).split('/')[1]

        if request.method == 'POST':
            form = ExtractFileForm(request.POST, request.FILES)
            if timeclick_extract_file:
                for field in form:
                    field.exists = True
                    field.file = file

            if 'upload_file' in request.POST:
                if form.is_valid():
                    i = form.clean_file(form, 'timeclick_extract_file')

                    if not i == 'Error' or not i:
                        pay_int.timeclick_extract_file = i
                        pay_int.save()

                        # add employees to the employeesmatched model
                        exist_emp = EmployeesMatched.objects.filter(owner=pay_int)
                        tc_names = parse_extract_names(pay_int.timeclick_extract_file)
                        if exist_emp:
                            # activated if there are existing employees
                            new_employees = compare_names(tc_names, exist_emp)
                            print(new_employees)

                            if new_employees:
                                for emp in new_employees:
                                    EmployeesMatched.objects.create(tc_name=(emp['first'] + ' ' + emp['last']),
                                                                    owner=pay_int)
                                return redirect('/employees')
                        else:
                            for emp in tc_names:
                                EmployeesMatched.objects.create(tc_name=(emp['first'] + ' ' + emp['last']),
                                                                owner=pay_int)
                            return redirect('/employees')
            elif 'generate_file' in request.POST:
                pay_items = PayrollItemsMatched.objects.filter(owner=pay_int)
                emp_list = EmployeesMatched.objects.filter(owner=pay_int)
                path = create_export(pay_int.timer_header, pay_items, emp_list, pay_int.timeclick_extract_file,
                                     request.user.id)
                pay_int.export.name = path
                pay_int.save()

            return redirect('/')
        else:
            form = ExtractFileForm()
            if timeclick_extract_file:
                for field in form:
                    field.exists = True
                    field.file = file

        if export:
            export_file = pay_int.export
        else:
            export_file = '#'

        return render(request, 'main_page.html',
                      {'payroll_items': payroll_items, 'employee_list': employee_list, 'form': form, 'export': export,
                       'timeclick_extract_file': timeclick_extract_file, 'emp_matched': emp_matched,
                       'items_matched': item_matched, 'export_file': export_file})


def register(request):
    return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


def files_upload(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        obj = PayrollCenterUsers.objects.filter(owner=request.user.id)[0]

        if request.method == 'POST':
            form = FileForm(request.POST, request.FILES)
            if form.is_valid():
                error = False
                for field in form:
                    i = form.clean_file(form, field.name)
                    if i and i != 'Error':
                        if field.name == 'timer_header':
                            obj.timer_header = i
                        elif field.name == 'employee_list':
                            obj.employee_list = i
                        elif field.name == 'payroll_items':
                            obj.payroll_items = i
                        else:
                            field.error = "Error: the file you uploaded is not valid"
                            file_exists(form, obj)
                            print("This should not really be triggered ever")
                            error = True
                    elif i == 'Error':
                        field.error = "Invalid file name or file extension. Please check that you have uploaded the correct file."
                        print(
                            "The file that was entered is not what was expected. either the name, file type, or upload category don't line up.")
                        file_exists(form, obj)
                        error = True
                if error:
                    return render(request, 'upload_page.html', {'form': form})
                else:
                    try:
                        obj.company = get_company(obj.timer_header)
                    except:
                        pass

                    obj.save()
                    return redirect('/items')
            return render(request, 'upload_page.html', {'form': form})
        else:
            form = FileForm()
            file_exists(form, obj)

            return render(request, 'upload_page.html', {'form': form})


def product_list(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        pay_int = PayrollCenterUsers.objects.get(owner=request.user.id)

        if not pay_int.payroll_items:
            return redirect('/upload/')

        if request.method == 'POST':
            formset = ItemFormSet(request.POST, queryset=PayrollItemsMatched.objects.filter(owner=pay_int))

            qb_item_list = parse_payroll(pay_int.payroll_items)
            choices = [(None, 'Select a Payroll Item'), ('Not Used', 'Not Used')]
            qb_item_list.sort()
            for i in qb_item_list:
                j = (i, i)
                choices.append(j)

            for form in formset:
                form.fields['qb_item'].choices = choices

            if formset.is_valid():
                formset.save()
                return redirect('/')
            else:
                print(formset.errors)
                for i in formset.errors:
                    if i:
                        i['qb_item'] = 'Please select a payroll item from the list'
                return render(request, 'item_list_page.html', {'formset': formset})
        else:
            if pay_int.payroll_items:
                qb_item_list = parse_payroll(pay_int.payroll_items)
                choices = [(None, 'Select a Payroll Item'), ('Not Used', 'Not Used')]
                qb_item_list.sort()
                for i in qb_item_list:
                    j = (i, i)
                    choices.append(j)
            else:
                return files_upload(request)
            # If there are no entries then this will throw an exception.
            try:
                formset = ItemFormSet(queryset=PayrollItemsMatched.objects.filter(owner=pay_int))
                for form in formset:
                    form.fields['qb_item'].choices = choices
            except Exception as e:
                print("ERROR:" + str(e))
                return render(request, 'item_list_page.html', {'formset': None})

        return render(request, 'item_list_page.html', {'formset': formset})


def employee_list(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        pay_int = PayrollCenterUsers.objects.get(owner=request.user.id)

        if not pay_int.employee_list:
            return redirect('/upload/')

        if request.method == 'POST':
            formset = EmployeeFormSet(request.POST, queryset=EmployeesMatched.objects.filter(owner=pay_int))

            qb_name_list = parse_employee(pay_int.employee_list)
            choices = [(None, 'Select a name'), ('Remove Employee', 'Remove Employee*')]
            qb_name_list.sort()
            for i in qb_name_list:
                j = (i, i)
                choices.append(j)

            for form in formset:
                form.fields['qb_name'].choices = choices

            if formset.is_valid():
                formset.save()
                return redirect('/')
            else:
                print(formset.errors)
                for i in formset.errors:
                    if i:
                        i['qb_name'] = 'Please select a name from the list'
                return render(request, 'employee_list_page.html', {'formset': formset})
        else:

            qb_name_list = parse_employee(pay_int.employee_list)
            choices = [(None, 'Select a name'), ('Remove Employee', 'Remove Employee*')]
            qb_name_list.sort()
            for i in qb_name_list:
                j = (i, i)
                choices.append(j)

            # If there are no entries then this will throw an exception.
            try:
                formset = EmployeeFormSet(queryset=EmployeesMatched.objects.filter(owner=pay_int))
                for form in formset:
                    form.fields['qb_name'].choices = choices
            except Exception as e:
                print("ERROR:" + str(e))
                return render(request, 'employee_list_page.html', {'formset': None})

        return render(request, 'employee_list_page.html', {'formset': formset})
