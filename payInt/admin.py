from django.contrib import admin

from payInt.models import PayrollCenterUsers, PayrollItemsMatched, EmployeesMatched

admin.site.register(PayrollCenterUsers)
admin.site.register(PayrollItemsMatched)
admin.site.register(EmployeesMatched)
