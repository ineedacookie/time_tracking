from django.forms import modelformset_factory, ModelForm
from django import forms
from .models import PayrollCenterUsers, PayrollItemsMatched, EmployeesMatched


class ItemForm(ModelForm):
    qb_item = forms.ChoiceField(choices=[])

    class Meta:
        model = PayrollItemsMatched
        exclude = ('owner',)


class EmployeeForm(ModelForm):
    qb_name = forms.ChoiceField(choices=[])

    class Meta:
        model = EmployeesMatched
        exclude = ('owner',)


class ExtractFileForm(ModelForm):
    """
    Validates the files received. It is specific to the name of the file, the type, and the file upload slot.
    """

    def clean_file(self, form, name):
        file = form.cleaned_data[name]
        if file:
            filename, filetype = file.name.split('.')
            if filetype == 'csv' or filetype == 'CSV':
                return file

            return 'Error'

        else:
            return None

    class Meta:
        model = PayrollCenterUsers
        fields = ('timeclick_extract_file',)


class FileForm(ModelForm):
    """
    Validates the files received. It is specific to the name of the file, the type, and the file upload slot.
    """

    def clean_file(self, form, name):
        file = form.cleaned_data[name]
        if file:
            filename, filetype = file.name.split('.')
            if name == 'employee_list' and filetype == 'IIF':
                return file
            if name == 'timer_header' and filetype == 'IIF':
                return file
            if name == 'payroll_items' and (filetype == 'csv' or filetype == 'CSV'):
                return file

            return 'Error'

        else:
            return None

    class Meta:
        model = PayrollCenterUsers
        fields = ('timer_header', 'employee_list', 'payroll_items')


"""
    Formsets allow multiple database entries to be displayed on one form.
    It has been used in this case to list employees with their respective matches, and payroll items.
"""
ItemFormSet = modelformset_factory(PayrollItemsMatched, form=ItemForm)
EmployeeFormSet = modelformset_factory(EmployeesMatched, form=EmployeeForm)
