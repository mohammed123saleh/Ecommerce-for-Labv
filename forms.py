from django import forms
from django.contrib.admin import widgets

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from bootstrap_datepicker_plus import DatePickerInput
from .models import Item, Contact, Signupmodel, Mails
from django.utils.translation import gettext_lazy as _
PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
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

class CheckoutForm(forms.Form):

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':_('First Name'),
       
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':_('Last Name')
    }))
    Email  = forms.EmailField(required=False,widget=forms.EmailInput(attrs={
        'class':'form-control'
    }))
    Mobile = forms.CharField(max_length=15,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':_('Mobile NO')
        }))
    shipping_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':_('1234 Main St'),
        'class':'form-control'
    }))
    shipping_address2 = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':_('Apartment or suite'),
        'class':'form-control'
    }))
   
   
    shipping_country = CountryField(blank_label=_('(select country)')).formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_zip = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'placeholder':_('Zip code'),
        'class':'form-control',
    }))

    govs = forms.ChoiceField(choices=Governates, required=False, widget=forms.Select(attrs={
        'class':'form-control',
       
    }))


#   Availability = forms.DateField(widget = DatePickerInput(format='%Y-%m-%d'))
#   CheckOut = forms.DateField(widget = DatePickerInput(format='%Y-%m-%d'))

#    payment_option = forms.ChoiceField(
#        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'message','email', 'Tel')





'''
class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'date', 'start_time',
                  'end_time')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = widgets.AdminDateWidget()
        self.fields['start_time'].widget = widgets.AdminTimeWidget()
        self.fields['end_time'].widget = widgets.AdminTimeWidget()



'''











class EmailSignupForm(forms.ModelForm):

    class Meta:
        model = Signupmodel
        fields = ('email', )
        widgets = {
            'email': forms.EmailInput(attrs={
                'class':'form-control',
                'placeholder':'Enter your Email',
                'id':'widget-subscribe-form-email'

            }),
        }




from django.utils.translation import gettext_lazy as _


class ContactHome(forms.Form):
    Your_Name = forms.CharField(label=_("Your Name") ,widget=forms.TextInput(attrs={
        'class':'form-control', 
    
        'id':'whity',
    }))
    Your_Email = forms.EmailField(label=_("Your Email") , widget=forms.EmailInput(attrs={
        'class':'form-control', 
        
         'id':'whity',

    }))
    Your_Phone=  forms.CharField(label=_("Your Phone") ,widget=forms.TextInput(attrs={
        'class':'form-control', 
       
         'id':'whity',
    }))
    Your_Message = forms.CharField(label=_("Your Message") ,widget=forms.Textarea(attrs={
        'class':'form-control', 
        
        'rows':4,
        'id':'whity',

    }))




class MailsForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class':'form-control', 
        'placeholder':'Email',
    })) 

    subject = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control', 
        'placeholder':'subject',
    })) 

    message = forms.CharField(widget=forms.Textarea(attrs={
        'class':'form-control', 
        'placeholder':'message',
    }))             

#    document = forms.F



class Burba(forms.Form):
    link = forms.BooleanField(required=True)
    name = forms.CharField(max_length=200, required=True)