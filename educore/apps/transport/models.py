from django.db import models
from apps.core.models import User
from apps.students.models import Student


class Vehicle(models.Model):
    class Status(models.TextChoices):
        ACTIVE      = 'active',      'Active'
        MAINTENANCE = 'maintenance', 'Under Maintenance'
        INACTIVE    = 'inactive',    'Inactive'

    registration_no = models.CharField(max_length=20, unique=True)
    vehicle_type    = models.CharField(max_length=50, default='Bus')
    capacity        = models.PositiveSmallIntegerField()
    make_model      = models.CharField(max_length=100, blank=True)
    year            = models.PositiveSmallIntegerField(null=True, blank=True)
    status          = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    fitness_expiry  = models.DateField(null=True, blank=True)
    insurance_expiry= models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.registration_no} ({self.vehicle_type})'


class Driver(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    license_no     = models.CharField(max_length=30, unique=True)
    license_expiry = models.DateField()
    experience_yrs = models.PositiveSmallIntegerField(default=0)
    is_active      = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name()


class Route(models.Model):
    name          = models.CharField(max_length=200)
    code          = models.CharField(max_length=20, unique=True)
    vehicle       = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    driver        = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    morning_start = models.TimeField()
    evening_start = models.TimeField()
    is_active     = models.BooleanField(default=True)
    description   = models.TextField(blank=True)

    def __str__(self):
        return f'{self.code} — {self.name}'

    @property
    def student_count(self):
        return self.student_routes.filter(is_active=True).count()


class RouteStop(models.Model):
    route      = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    stop_name  = models.CharField(max_length=200)
    order      = models.PositiveSmallIntegerField()
    pickup_time= models.TimeField()
    drop_time  = models.TimeField()
    latitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering        = ['route', 'order']
        unique_together = ('route', 'order')

    def __str__(self):
        return f'{self.route.code} — Stop {self.order}: {self.stop_name}'


class StudentRoute(models.Model):
    student    = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_routes')
    route      = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='student_routes')
    stop       = models.ForeignKey(RouteStop, on_delete=models.SET_NULL, null=True)
    is_active  = models.BooleanField(default=True)
    assigned_on= models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'route')

    def __str__(self):
        return f'{self.student.full_name} — {self.route.name}'
