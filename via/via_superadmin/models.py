from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, Group
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError


# Create your models here.

class Company(models.Model):
    company_name = models.CharField(max_length=100, blank=False,
                                    error_messages={'required': 'Please provide your name'})
    company_address = models.CharField(max_length=300, blank=False,
                                       error_messages={'required': 'Please provide your Address.'},)
    company_phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    company_phone_number = models.CharField(
        validators=[company_phone_regex], max_length=15, blank=True)
    company_logo = models.ImageField(upload_to='logo/%Y%m%d/', blank=True)
    company_country = CountryField(blank_label='(select country)')
    admin_email = models.EmailField(max_length=254, unique=True,
                                    error_messages={'required': 'Please provide your email address.',
                                                    'unique': 'An account with this email exist.'}, )
    # choicesss = (('Invoice', 'Invoice'), ('Receipt', 'Receipt'),
    #              ('Application Form', 'Application Form'),)
    # use_case = MultiSelectField(choices=choicesss, max_choices=3)
    created_date = models.DateTimeField(
        auto_now_add=True)

    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.company_name

    class Meta:
        db_table = "company"


class UserCompanyMap(models.Model):
    # removed foreign key as there were issues while integrating
    employee = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    # removed foreign key as there were issues while integrating
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    # employee_id = models.IntegerField(null=True)
    # company_id = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    class Meta:
        db_table = "usercompanymap"

class UserMap(models.Model):
    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, related_name='employee')
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, related_name='amin')
    supervisor = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, related_name='supervisor')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    class Meta:
        db_table = "usermap"


class UseCase(models.Model):
    name = models.CharField(max_length=50)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    published_date = models.DateTimeField(
        blank=True, null=True)

    class Meta:
        db_table = "usecase"

class CompanyUseCaseMap(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, blank=False)
    usecase = models.IntegerField(blank=False)
    created_dt = models.DateTimeField(
        auto_now_add=True)
    published_date = models.DateTimeField(
        blank=True, null=True)

    class Meta:
        db_table = 'companyusecasemap'