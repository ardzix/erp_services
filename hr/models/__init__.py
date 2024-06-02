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
    
    last_location = models.PointField(null=True, blank=True, help_text=_(
        "Coordinates where the employee currently located"))

    basic_salary = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        help_text=_("Enter the employee's basic salary amount")
    )
    bank_account_number = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        help_text=_("Enter the employee's bank account number")
    )

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


class LocationTracker(BaseModelGeneric):
    employee = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.CASCADE, help_text=_("The employee being traked"))
    location = models.PointField(null=True, help_text=_(
        "Coordinates where the employee located"))

    def __str__(self):
        return _("Track #{id32} - {name} on {created_at}").format(id32=self.id32, name=self.employee.user.username, created_at=self.created_at)
    
    def save(self, *args, **kwargs):
        if not self.employee:
            self.employee = Employee.objects.get(user=self._current_user)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Location Tracker")
        verbose_name_plural = _("Location Trackers")

class Salary(BaseModelGeneric):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        help_text="Select the employee associated with this salary record"
    )
    pay_date = models.DateField(
        help_text="Enter the date when the salary was paid"
    )
    salary = models.DecimalField(
        max_digits=19, 
        decimal_places=2, 
        help_text="Enter the total gross salary amount"
    )
    incentive = models.DecimalField(
        max_digits=19, 
        decimal_places=2, 
        default=0,
        help_text="Enter the additional incentive amount"
    )
    operational_cost = models.DecimalField(
        max_digits=19, 
        decimal_places=2, 
        default=0,
        help_text="Enter the operational costs deducted"
    )
    bonus = models.DecimalField(
        max_digits=19, 
        decimal_places=2, 
        default=0,
        help_text="Enter the bonus amount awarded"
    )

    @property
    def total(self):
        return self.salary + self.bonus + self.incentive + self.operational_cost

    def __str__(self):
        return f"Salary for {self.employee.user.get_full_name()} on {self.pay_date}"
    
    class Meta:
        ordering = ['-id']
        verbose_name = _("Location Tracker")
        verbose_name_plural = _("Location Trackers")