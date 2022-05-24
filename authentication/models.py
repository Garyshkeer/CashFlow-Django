from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse

# cash app models
from django.utils import timezone


class Currency(models.Model):
    name = models.CharField(max_length=10)
    shortcut = models.CharField(max_length=4)
    sign = models.CharField(max_length=2)
    rate = models.FloatField()

    def __str__(self):
        return f"{self.shortcut}"


class Bank(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"


class Wallet(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    bank = models.ForeignKey(Bank, models.DO_NOTHING)
    currency = models.ForeignKey(Currency, models.DO_NOTHING)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user}"


class Transaction(models.Model):
    sender = models.ForeignKey(Wallet, models.DO_NOTHING, related_name="sent_transactions")
    receiver = models.ForeignKey(Wallet, models.DO_NOTHING, related_name="received_transactions")
    amount = models.FloatField()
    net_amount = models.FloatField()
    # TO be handled in the application user
    exchange_rate = models.FloatField(null=True, blank=True)
    commission_percent = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=250)


# user models

class UserInformation(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING)
    mobile_number = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user.get_full_name()} {self.user}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, **kwargs):
        super(Profile, self).save(**kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Contacts(models.Model):
    full_name = models.CharField('Full name', max_length=50)
    email_address = models.EmailField('Email address', max_length=254)
    company = models.CharField('Company', max_length=80)
    phone_number = models.BigIntegerField('hone numberP')
    message = models.TextField('Message')

    def __str__(self):
        return self.full_name


class Category(models.Model):
    code = models.IntegerField(default=0, null=False)
    name = models.CharField(max_length=255)
    description = models.CharField(default=0, max_length=255)
    registered_at = models.DateField(null=True)
    registered_by = models.CharField(default=0, null=False, max_length=55)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bankcard')


class BankCard(models.Model):
    cardName = models.CharField(max_length=255, default='coding')
    cardBalance = models.IntegerField()
    date = models.DateTimeField(auto_now_add=False, null=True)

    def str(self):
        return self.cardName

    def get_absolute_url(self):
        return reverse('account')


class Inflow(models.Model):
    name = models.CharField(null=False, max_length=255)
    value = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    registered_at = models.DateTimeField()
    registered_by = models.CharField(null=False, max_length=55)

    def __str__(self):
        return self.name

    def was_registered_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.registered_at <= now


class Outflow(models.Model):
    name = models.CharField(null=False, max_length=255)
    value = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    registered_at = models.DateTimeField()
    registered_by = models.CharField(null=False, max_length=55)

    def __str__(self):
        return self.name

    def was_registered_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.registered_at <= now
