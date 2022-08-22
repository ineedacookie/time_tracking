from django.db import models
from django.contrib.auth.models import User
from payInt.storage import OverwriteStorage


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.owner.id, filename)


class PayrollCenterUsers(models.Model):
    """ The definition of the main table used to store all user information """
    # Fields
    row_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, models.CASCADE)
    company = models.CharField(max_length=100, help_text='Companies name', blank=True)
    timer_header = models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), blank=True)
    employee_list = models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), blank=True)
    payroll_items = models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), blank=True)
    timeclick_extract_file = models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), blank=True)
    export = models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), blank=True)

    # Metadata
    # Sorts the data according to the things selected.
    class Meta:
        ordering = ['-owner']

    # Methods
    def __str__(self):
        return self.company


class PayrollItemsMatched(models.Model):
    """ This table handles all of the matched payroll items, There is a many to one relationship between this and a user """
    # Fields
    # Fields
    owner = models.ForeignKey(PayrollCenterUsers, models.CASCADE)
    tc_item = models.CharField(max_length=100, help_text='TimeClick Item Name', default='')
    qb_item = models.CharField(max_length=100, help_text='QuickBooks Item Name', default='', blank=True)

    # Metadata
    # Sorts the data according to the things selected.
    class Meta:
        ordering = ['-owner']


class EmployeesMatched(models.Model):
    """ This table handles all of the matched employees, There is a many to one relationship between this and a user """
    # Fields
    owner = models.ForeignKey(PayrollCenterUsers, models.CASCADE)
    tc_name = models.CharField(max_length=100, help_text='TimeClick Employee Name', default='')
    qb_name = models.CharField(max_length=100, help_text='QuickBooks Employee Name', default='', blank=True)

    # Metadata
    # Sorts the data according to the things selected.
    class Meta:
        ordering = ['-owner']
