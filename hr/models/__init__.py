from django.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User

class Department(BaseModelGeneric):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"Department #{self.id62} - {self.name}"

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")


class Employee(BaseModelGeneric):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    # Add any other fields specific to your employee model

    def __str__(self):
        return f"Employee #{self.id62} - {self.user.get_full_name()}"

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")


class Leave(BaseModelGeneric):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    # Add any other fields specific to your leave model

    def __str__(self):
        return f"Leave #{self.id62} - {self.employee}"

    class Meta:
        verbose_name = _("Leave")
        verbose_name_plural = _("Leaves")


class Attendance(BaseModelGeneric):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    clock_in_time = models.TimeField()
    clock_out_time = models.TimeField()
    # Add any other fields specific to your attendance model

    def __str__(self):
        return f"Attendance #{self.id62} - {self.employee}"

    class Meta:
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")


class Performance(BaseModelGeneric):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=((1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')))
    review = models.TextField(blank=True)
    # Add any other fields specific to your performance model

    def __str__(self):
        return f"Performance #{self.id62} - {self.employee}"

    class Meta:
        verbose_name = _("Performance")
        verbose_name_plural = _("Performances")
