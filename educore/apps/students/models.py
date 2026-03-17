from django.db import models
from apps.core.models import User, Section, AcademicYear


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE   = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER  = 'O', 'Other'

    class BloodGroup(models.TextChoices):
        A_POS  = 'A+',  'A+'
        A_NEG  = 'A-',  'A-'
        B_POS  = 'B+',  'B+'
        B_NEG  = 'B-',  'B-'
        O_POS  = 'O+',  'O+'
        O_NEG  = 'O-',  'O-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'

    # Identity
    user             = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    admission_no     = models.CharField(max_length=20, unique=True)
    first_name       = models.CharField(max_length=100)
    last_name        = models.CharField(max_length=100)
    date_of_birth    = models.DateField()
    gender           = models.CharField(max_length=1, choices=Gender.choices)
    blood_group      = models.CharField(max_length=3, choices=BloodGroup.choices, blank=True)
    photo            = models.ImageField(upload_to='students/', blank=True, null=True)
    aadhaar_no       = models.CharField(max_length=12, blank=True)

    # Academics
    section          = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='students')
    admission_date   = models.DateField()
    academic_year    = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    roll_number      = models.CharField(max_length=10, blank=True)

    # Parent/Guardian
    father_name      = models.CharField(max_length=150)
    mother_name      = models.CharField(max_length=150, blank=True)
    guardian_name    = models.CharField(max_length=150, blank=True)
    parent_phone     = models.CharField(max_length=15)
    parent_email     = models.EmailField(blank=True)
    parent_occupation= models.CharField(max_length=100, blank=True)

    # Address
    address          = models.TextField()
    city             = models.CharField(max_length=100)
    pincode          = models.CharField(max_length=10)

    # Status
    is_active        = models.BooleanField(default=True)
    remarks          = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['section', 'roll_number', 'last_name']

    def __str__(self):
        return f'{self.full_name} ({self.admission_no})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def current_class(self):
        return str(self.section)
