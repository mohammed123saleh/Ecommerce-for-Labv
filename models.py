from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django_countries import Countries
from django.core.mail import send_mail

import datetime

from datetime import date, timedelta
from django.template.defaultfilters import slugify
from math import ceil
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import random 
import string

slugRand = random.choices(string.ascii_lowercase + string.digits, k=20)
me = random.randrange(0, 100000, 2)
mar = str(me * 5) 
CATEGORY_CHOICES = (
    ('Si', _('Single 120 x 200')),
    ('Q', _('Queen 160 x 200')),
    ('K', _('King 180 x 200')),
    ('SK', _('Super King 200 x 200')),
    ('S', _('Set')),
    ('PS',_('Standard  51 x 56')),
    ('PQ',_('Queen size  51 x 76')),
    ('PK',_('King size  51 x 92')),
    ('PB',_('Body size  51 x 137 ')),



)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)








Governates = (
            ('', _('For Egypt Only')),
            ('6th of October',  '6th of October'),
            ('Al Sharqia',  'Al Sharqia'),
            ('alexandria',  'alexandria'),
            ( 'Aswan',  'Aswan'),
            ('Asyut',  'Asyut'),
            ('Beheira',  'Beheira'),
            ('Beni Suef',  'Beni Suef'),
            ('Cairo',  'Cairo'),
            ( 'Dakahlia',  'Dakahlia'),
            ('Damietta ',  'Damietta '),
            ( 'Faiyum',  'Faiyum'),
            ('Gharbia',  'Gharbia'),
            ( 'Giza',  'Giza'),
            ( 'Ismailia',  'Ismailia'),
            ('Kafr El Sheikh',  'Kafr El Sheikh'),
            ('Luxor',  'Luxor'),
            ( 'Matruh',  'Matruh'),
            ( 'Minya',  'Minya'),
            ('Monufia', 'Monufia'),
            ('New Valley', 'New Valley'),
            ('North Sinai', 'North Sinai'),
            ('Port Said', 'Port Said'),
            ('Qalyubia ', 'Qalyubia '),
            ('Qena', 'Qena'),
            ('Red Sea', 'Red Sea'),
            ('Sharqia ', 'Sharqia '),
            ('Sohag', 'Sohag'),
            ('South Sinai', 'South Sinai'),
            ('Suez', 'Suez'),
)
 

# remove it in Travencia 



class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



types = (
    ('T', 'Towels'),
    ('BS','Bedsheets'),
    ('V', 'Variety'),  
    ('PC', 'Pillowcases')
)

class Item(models.Model):
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2, default="S", help_text='sizes and quantity' ,verbose_name='1-category')
    product_category = models.CharField(max_length=2, choices=types, default='V', help_text='Products Dropdown in Egypt Fabrics Navbar', verbose_name='2-Product Category')
    title = models.CharField(max_length=250, unique=False, verbose_name="3-Product Name")
    Company = models.CharField(max_length=260, unique=False, null=True, blank=True,editable=False)
    price = models.FloatField(unique=False, verbose_name="4- Price")
  
    discount_price = models.FloatField(blank=True, null=True, editable=False)
    description = models.TextField(verbose_name="5- description ")   
    slug = models.SlugField(max_length=300, unique=False,help_text="Random input, it is better to add the category of the product here for example : Towels ")
    start_date = models.DateField(null=True, blank=True, editable=False)
    end_date = models.DateField(null=True, blank=True, editable=False)
    image = models.ImageField(upload_to='Egypt_fabrics', blank=False, null=False, verbose_name="1- image")
    image2 = models.ImageField(upload_to='Egypt_fabrics', blank=True, null=True,help_text="this field is optional",  verbose_name="2- image" )
    image3 = models.ImageField(upload_to='Egypt_fabrics', blank=True, null=True,help_text="this field is optional",  verbose_name="3- image" )
 



    def __str__(self):
        return self.title
    def save(self, *args, **kwargs, ):

        self.slug = slugify(self.title + self.slug + str(self.price) + '/' )+ mar
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("Main:product", kwargs={
        'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("Main:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("Main:remove-from-cart", kwargs={
            'slug': self.slug
        })
'''
    def add_guest_to_cart_url(self):
        return reverse("Main:add-guest-to-cart", kwargs={
        'slug': self.slug
    })

    def remove_single_customer_from_cart_url(self):
        return reverse("Main:remove-single-customer-from-cart", kwargs={
        'slug': self.slug
        })
'''

var_category = (
    ('size','size'),
   
)

class ObjectVariation(models.Manager):
    def sizes(self):
        return self.all().filter(category='size')
  
        
class Variation(models.Model):
    itemy = models.ForeignKey(Item, on_delete=models.CASCADE)
    Title = models.CharField(max_length=200)
    category = models.CharField(max_length=200, choices=var_category, default='size')
    pricy = models.FloatField()

    def __str__(self):
        return self.Title
    
   

class Temp(models.Model):
    Title = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    pricy = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation)
    quantity = models.IntegerField(default=1)
   
   
    
    

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    vari = models.ManyToManyField(Variation, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    address = models.ForeignKey(
       'Address', on_delete=models.SET_NULL, blank=True, null=True)
   
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

 
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    first_name = models.CharField(max_length=260)
    last_name =  models.CharField(max_length=260)
    Email = models.EmailField(null=True, blank=True)  
    Mobile = models.CharField(max_length=15)                   
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(null=True, blank=True, max_length=5)
    govs = models.CharField(max_length=30, choices=Governates, null=True, blank=True)
    


    def __str__(self):
        return f'Customer: {self.first_name} {self.last_name}. Mobile: {self.Mobile}'

    class Meta:
        verbose_name = 'Customer Info'
        verbose_name_plural = 'Customer Info'


class Payment(models.Model):
    payment_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)



class Contact(models.Model):
    name = models.CharField(max_length=250, null=False, blank=False)
    message = models.TextField(null=False, blank=False)
    email = models.EmailField()
    time  = models.DateTimeField(auto_now=True)
    Tel   = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'
    class Meta:
        verbose_name = 'Message' 
        verbose_name_plural =   'Messages'


class Signupmodel(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'News Letter' 
        verbose_name_plural =   'News Letters'






class ContactHomeModel(models.Model):
    Name = models.CharField(max_length=250)
    Email = models.EmailField()
    Phone = models.CharField(max_length=15)   
    Message = models.TextField()     
    def __str__(self):
        return f'Customer Name: {self.Name} | Customer Phone: {self.Phone} '

    class Meta:
        verbose_name = 'Customer Message'
        verbose_name_plural = 'Customer Message'



email_user = (
    ('me', settings.EMAIL_HOST_USER),
)












class Mails(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=260)
    message = models.TextField()
    document = models.FileField(upload_to='Documents/')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Mail'
        verbose_name_plural = 'Mails'





class Publication(models.Model):
    Title = models.CharField(max_length=30)

    def __str__(self):
        return self.Title


class Article(models.Model):
    HeadLine = models.CharField(max_length=100)
    publications = models.ManyToManyField(Publication)

    def __str__(self):
        return self.HeadLine
           
    

