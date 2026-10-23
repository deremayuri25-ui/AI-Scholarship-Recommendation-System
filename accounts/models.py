from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Personal Information
    full_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    taluka = models.CharField(max_length=50)
    city_village = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Education Information
    education_level = models.CharField(max_length=50)
    university_board = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100)
    college = models.CharField(max_length=150)
    current_year = models.CharField(max_length=30)
    percentage_cgpa = models.DecimalField(
        max_digits=5, decimal_places=2)
    percentage_type = models.CharField(max_length=20)
    admission_type = models.CharField(max_length=30)

    # Financial & Eligibility
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30)
    parent_occupation = models.CharField(max_length=100)
    family_members = models.IntegerField()
    disability_status = models.CharField(max_length=10)
    residence_type = models.CharField(max_length=30)
    domicile_state = models.CharField(max_length=50)

    # Scholarship Preference
    scholarship_type = models.CharField(max_length=50)

    # Documents
   
    def __str__(self):
        return self.full_name
     
     
class Scholarship(models.Model):

    name = models.CharField(max_length=200)
    department = models.CharField(max_length=150)
    description = models.TextField()

    category = models.CharField(max_length=50)

    minimum_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    maximum_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    education_level = models.CharField(max_length=100)
    

    state = models.CharField(max_length=100)

    last_date = models.DateField(
        null=True,
        blank=True
    )

    official_link = models.URLField(
        blank=True
    )
    
    required_document = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name