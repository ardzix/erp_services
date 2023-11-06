from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User


class Department(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_("The name of the department"))

    def __str__(self):
        return _("Department #{dept_id} - {dept_name}").format(dept_id=self.id32, dept_name=self.name)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")


class Employee(BaseModelGeneric):
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text=_(
        "The associated user of the employee"))
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True,
                                   blank=True, help_text=_("The department the employee belongs to"))

    def __str__(self):
        return _("Employee #{emp_id} - {emp_name}").format(emp_id=self.id32, emp_name=self.user.username)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")


class Leave(BaseModelGeneric):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, help_text=_(
        "The employee who requested the leave"))
    leave_type = models.CharField(
        max_length=100, help_text=_("The type of leave"))
    start_date = models.DateField(help_text=_("Start date of the leave"))
    end_date = models.DateField(help_text=_("End date of the leave"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        help_text=_("The status of the leave request")
    )

    def __str__(self):
        return _("Leave #{leave_id} - {leave_emp}").format(leave_id=self.id32, leave_emp=self.employee)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Leave")
        verbose_name_plural = _("Leaves")


class Attendance(BaseModelGeneric):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, help_text=_(
        "The employee whose attendance is recorded"))
    clock_in = models.DateTimeField(help_text=_(
        "Clock-in time and date of the employee"))
    clock_out = models.DateTimeField(null=True, blank=True, help_text=_(
        "Clock-out time and date of the employee"))
    clock_in_location = models.PointField(null=True, blank=True, help_text=_(
        "Coordinates where the employee clocked in"))
    clock_out_location = models.PointField(null=True, blank=True, help_text=_(
        "Coordinates where the employee clocked out"))
    able_checkout = models.BooleanField(default=False)

    def __str__(self):
        return _("Attendance #{att_id} - {att_emp}").format(att_id=self.id32, att_emp=self.employee)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")


class Performance(BaseModelGeneric):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, help_text=_("The employee being reviewed"))
    rating = models.PositiveIntegerField(choices=((1, _('Poor')), (2, _('Fair')), (3, _('Good')), (4, _(
        'Very Good')), (5, _('Excellent'))), help_text=_("Rating given to the employee's performance"))
    review = models.TextField(
        blank=True, help_text=_("Additional review notes"))

    def __str__(self):
        return _("Performance #{perf_id} - {perf_emp}").format(perf_id=self.id32, perf_emp=self.employee)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Performance")
        verbose_name_plural = _("Performances")
