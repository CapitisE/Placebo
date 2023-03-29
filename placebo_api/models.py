from django.db import models
from django.db.models import Model
from djmoney.models.fields import MoneyField
import uuid
import datetime


# Create your models here.
class BaseModel(Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Contact(BaseModel):
    """Model for Phone number"""
    countrycode = models.IntegerField()
    phone = models.IntegerField()


class Medical_info(BaseModel):
    """Model for medical info"""
    medical_history = models.TextField()
    attachments = models.FileField(upload_to='medical_history/')
    allergies = models.TextField()
    current_diagnosis = models.TextField()


class Users(BaseModel):
    """Model for Users"""
    avatar = models.ImageField(upload_to='userpic/%d/%m/%Y/', null=True)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    phonenumber = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name='phonenumber'
    )
    email = models.EmailField(null=True)
    reward_points = models.IntegerField(null=True)
    medical_info = models.ForeignKey(
        Medical_info, null=True, on_delete=models.CASCADE,
        related_name='medical_info')
    other_health_info = models.TextField(null=True)
    dob = models.DateField()

    def age(self):
        """Creating a method to find user age"""
        dob = self.dob
        return datetime.datetime.now().date().year - dob.year


class Fda_drug_categories(BaseModel):
    """Model for Drug Categories"""
    name = models.CharField(max_length=80)
    drug_info = models.TextField(max_length=300)


class Ban(BaseModel):
    """Model for banned drugs"""
    upi = models.CharField(max_length=14)
    brand_name = models.CharField(max_length=60)
    product_desc = models.TextField()
    reason_for_ban = models.TextField()


class Blacklist(BaseModel):
    """Model for blacklisted drugstores"""
    prn = models.CharField(max_length=7)
    pharm_name = models.CharField(max_length=30)
    reason_for_ban = models.TextField()


class Drugstores(BaseModel):
    """Model for Drugstores"""
    prn = models.CharField(max_length=7)
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='drugstorepic/')
    location = models.CharField(max_length=300)
    phonenumber = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name='phonenum')
    email = models.EmailField()
    website = models.URLField()
    other_contact = models.TextField()
    door_delivery = models.BooleanField(default=True)
    phar_license = models.FileField(
        upload_to='pharmlicensecert/', max_length=300)
    phar_license_status = models.CharField(max_length=7, choices=(
        ('choice1', 'PRESENT'), ('choice2', 'ABSENT'), ('choice3', 'INVALID')))
    license_expdate = models.DateField()
    owner = models.CharField(max_length=50)
    lead_pharmacist = models.CharField(max_length=50)
    # Introduce rating as a method field, just like age in model Users


class Drugs(BaseModel):
    """Model for Drugs"""
    prn = models.ForeignKey(Drugstores, related_name='pharmacy',
                            on_delete=models.CASCADE)
    upi = models.CharField(max_length=14)
    image = models.ImageField(upload_to='drugpic/')
    category = models.ManyToManyField(
        Fda_drug_categories, related_name='category')
    brand_name = models.CharField(max_length=60)
    product_desc = models.TextField()
    purpose = models.CharField(max_length=200)
    contraindications = models.TextField()
    side_effects = models.TextField()
    nafdac_number = models.CharField(max_length=7)
    origin = models.CharField(max_length=8, choices=(
        ('choice1', 'LOCAL'), ('choice2', 'IMPORTED')))
    son_approved = models.BooleanField(default=False)
    min_unitofpurchase = models.SmallIntegerField()
    active_ingredients = models.TextField()
    inactive_ingredients = models.TextField()
    uses = models.TextField()
    otc = models.BooleanField(default=False, null=False)
    pricing = MoneyField(
        decimal_places=2, max_digits=12, default_currency='NGN')
    child_friendly = models.BooleanField(default=False, null=False)
    batch_num = models.CharField(max_length=6)
    man_date = models.DateField()
    exp_date = models.DateField()
    total_units = models.IntegerField()
    units_sold = models.IntegerField(default=0)


class Support(BaseModel):
    """# Model for Help/Support"""
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    phonenumber = models.ForeignKey(Contact, on_delete=models.CASCADE)
    email = models.EmailField(null=True)
    message = models.TextField()


class Reviews(BaseModel):
    """Model for Review"""
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    phonenumber = models.ForeignKey(Contact, on_delete=models.CASCADE)
    email = models.EmailField(null=True)
    message = models.TextField()
