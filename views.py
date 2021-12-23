import datetime
import stripe
from lazysignup.decorators import allow_lazy_user
import re
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Q
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, ContactForm, EmailSignupForm,ContactHome, Burba
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Signupmodel, ContactHomeModel, Variation
from django.views.generic.edit import FormView
import random
from django.core.mail import EmailMultiAlternatives
import string
import requests 
import json
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
stripe.api_key = settings.STRIPE_SECRET_KEY
#from lazysignup.decorators import allow_lazy






from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from django.utils.html import strip_tags
from post_office import mail


MAILCHIMP_API_KEY = settings.MAILCHIMP_API_KEY
MAILCHIMP_DATA_CENTER = settings.MAILCHIMP_DATA_CENTER
MAILCHIMP_EMAIL_LIST_ID = settings.MAILCHIMP_EMAIL_LIST_ID

api_url = 'https://{dc}.api.mailchimp.com/3.0'.format(dc=MAILCHIMP_DATA_CENTER)
members_endpoint = '{api_url}/lists/{list_id}/members'.format(
    api_url=api_url,
    list_id=MAILCHIMP_EMAIL_LIST_ID
)

def subscribe(email):
    data = {
        "email_address": email,
        "status": "subscribed"
    }
    r = requests.post(
        members_endpoint,
        auth=("", MAILCHIMP_API_KEY),
        data=json.dumps(data)
    )
    return r.status_code, r.json()


def index(request):
    formy = EmailSignupForm(request.POST or None)
    if request.method == "POST":
        if formy.is_valid():
            email_signup_qs = Signupmodel.objects.filter(email=formy.instance.email)
            if email_signup_qs.exists():
                messages.info(request, "You are already subscribed")
            else:
                subscribe(formy.instance.email)
                formy.save()
            formy = EmailSignupForm()

    context = {
        'formy':formy
    }            
    return render(request, 'Main/join.html', context)








def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
  
    context = {
        'items': Item.objects.all(),
    
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid








def randGen():
    return ''.join(random.choices(string.ascii_lowercase + string.digits , k=6)) 


order_num= randGen()





class CheckoutView(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            return render(self.request, "Main/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("Main:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name  = form.cleaned_data.get('last_name')
                Email      = form.cleaned_data.get('Email')
                Mobile     = form.cleaned_data.get('Mobile')
                shipping_address = form.cleaned_data.get('shipping_address')
                shipping_address2 = form.cleaned_data.get('shipping_address2')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                govs         = form.cleaned_data.get('govs')


                shipping_address = Address(
                    user=self.request.user,
                    first_name=first_name,
                    last_name=last_name,
                    Email=Email,
                    Mobile=Mobile,
                    street_address=shipping_address,
                    apartment_address=shipping_address2,
                    country=shipping_country,
                    zip=shipping_zip,
                    govs=govs)


              
                   
    
        
                print(shipping_address.Email)

                order.shipping_address = shipping_address
                order.ref_code = get_random_string().upper()
                order_number = order.ref_code
                shipping_address.save()
                if shipping_address.first_name:
                    order.ordered =True
               
                order.save()

                if shipping_address.Email:
                    template_email = render_to_string('Main/email_template.html', {'name':first_name +' '+ last_name, 'order_num':order_number, 'customer_tel':Mobile, 'customer_address':shipping_address2, 'customer_gov':govs, 'customer_country':shipping_country} )
                    me = EmailMessage(
                        'Egypt Fabrics | Order Confirmation',template_email , settings.EMAIL_HOST_USER, ['mohamedsaleh902@yahoo.com'], 
                    )
                    me.content_subtype = "html"
                    me.fail_silently = False
                    me.send()
         

            messages.info(self.request, "")
            return redirect("Main:ThankYou")

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("Main:order-summary")


def ThankYou(request):
    return render(request, 'Main/thankyou.html')













class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "Main/payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("Main:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):

    model = Item
    paginate_by = 10
    template_name = "Main/Book.html"

    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)                     
        stuff = Item.objects.all().first()
        context["stuff"] = stuff
        Mat = Variation.objects.all()
        context["Mat"] = Mat
        return context



    def get_queryset(self):
       
        query = self.request.GET.get('q')
        if query:
            object_list = Item.objects.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(price__icontains=query)|
            Q(Company__icontains=query)|
            Q(discount_price__icontains=query)

        )
            return object_list                
        else:
            object_list = Item.objects.all()
        
        return object_list

@allow_lazy_user
def OrderSummaryView(request):
 

    try:
        order = Order.objects.get(user=request.user, ordered=False)
       
        context = {
            'object': order,
       
            
        }
        return render(request, 'Main/order_summary.html', context)
    except ObjectDoesNotExist:
        messages.warning(request, "You do not have an active order")
        return redirect("/")







def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("Main:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("Main:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("Main:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "Main/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("Main:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("Main:request-refund")


class home(ListView):
#    my_form = ContactHome(request.POST or None)
#    if my_form.is_valid():
#        Name    = my_form.cleaned_data.get('Your_name')
#        Email   = my_form.cleaned_data.get('Your_Email')
#        Phone   = my_form.cleaned_data.get('Your_Phone')
#        Message = my_form.cleaned_data.get('Your_Message')
#        my_form = ContactHome()

#        Customer = ContactHomeModel(
#            Name=Name,
#            Email=Email,
#            Phone= Phone,
#            Message=Message


#)
       
#        Customer.save()
#        my_form = ContactHome()
    model = Item
    paginate_by = 300
    

    def get_context_data(self, **kwargs):
        try:

            context = super(home, self).get_context_data(**kwargs)
            context['Towel'] = Item.objects.order_by('title')[0]
            context['Towel2'] = Item.objects.order_by('title')[1]
            context['Towel3'] = Item.objects.order_by('title')[2]
            context['Towel4'] = Item.objects.order_by('title')[3]
            context['Towel5'] = Item.objects.order_by('title')[4]
            context['Towel6'] = Item.objects.order_by('title')[5]
            context['Towel7'] = Item.objects.order_by('title')[6:]
        except:
            pass    
        return context
    
    success_url='/'
    template_name = 'Main/Home.html'
    

#    def get_context_data (self, ** kwargs):
#        context = super (). get_context_data (** kwargs)
#        try:
#            
#            context ['order'] = Order.objects.get(ordered=False)
#        except ObjectDoesNotExist:
#            messages.info(self.request,"")
#        
#        return context and messages.info(self.request, "Dear customer we are using High-Resolution pictures to provide you with wonderful experience which you deserve. If you are using mobile phone to browse our website, you might need from time to time to Rotate your screen to see more details. Thanks please have a wonderful time!")
      
    


    

       

    def get_queryset(self):
       
        query = self.request.GET.get('q')
        if query:
            object_list = Item.objects.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(price__icontains=query)|
            Q(Company__icontains=query)|
            Q(discount_price__icontains=query)

        )
            return object_list                 
        else:
            object_list = Item.objects.all()
        
        return object_list



    

from django.utils import timezone
def about(request):
    me = datetime.datetime.today()
    
    context = {
        'me':me
    }
    return render(request, 'Main/about.html', context)

def Contact(request):
    form = ContactHome(request.POST or None)
    if form.is_valid():
        Name      = form.cleaned_data.get('Your_Name')
        Email     = form.cleaned_data.get('Your_Email')
        Phone     = form.cleaned_data.get('Your_Phone')
        Message   = form.cleaned_data.get('Your_Message') 

        Contact = ContactHomeModel(
        Name=Name,
        Email=Email,
        Phone=Phone,
        Message=Message,

        )
        Contact.save()
        form =  ContactHome()  
    

    return render(request, 'Main/Contact.html', context={'form':form})


 

'''
class ItemDetailView(DetailView):

    model = Item
    template_name = "Main/product.html"




    def get_context_data(self, **kwargs):
            context = super(ItemDetailView, self).get_context_data(**kwargs)
            context['first'] = Item.variation_set.all().first()
            return context
    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)
'''



def ItemDetailView(request, slug):


    object = Item.objects.get(slug=slug)
    st = str(object.product_category)
    print(st)

    relevant_items = Item.objects.all().filter(product_category__icontains=st).exclude(slug=object.slug)[:6]
   
    if object:
        print('Yes  you are right  Mohammmed')
   
    context = {
        'object':object,
        'relevant_items':relevant_items,
   
    }
    return render(request, "Main/product.html", context)

def Mission(request):
    return render(request, 'Main/Mission.html')    
def FAQ(request):
    return render(request, 'Main/FAQ.html')    


'''


@allow_lazy_user
def add_to_cart(request, slug):

    item_var = []
    item = get_object_or_404(Item, slug=slug)
    
    order_item_qs = OrderItem.objects.filter(
        item=item,
        user=request.user,
        ordered=False
    )

    

    if request.method == "POST":
        try:


            key_item = list(request.POST.keys())[1]
            value_item = list(request.POST.values())[1]
            initial_price = value_item[:5] 
            the_title     = value_item[6:]
            titly = the_title.strip()
            the_price = float(initial_price)
            #pricey = the_price.strip()
            print(key_item)
            print("The Title is: ",the_title)
            print("The price is: ", the_price)
            print("The price is: ", len(initial_price))
        except:
            pass    

        try:        
            v = Variation.objects.get(itemy=item, Title__icontains=titly, category=key_item, pricy=the_price)           
            print(v)
            item_var.append(v)
            print(item_var)
        except:
            pass   


        if len(item_var) > 0:
            for items in item_var:
                order_item_qs = order_item_qs.filter(
                    variation__exact=items,
                )


    if order_item_qs.exists():
        order_item = order_item_qs.first()
        print(order_item_qs.first(),'j2')
        order_item.quantity += 1
        order_item.save()
    else:
        order_item = OrderItem.objects.create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_item.variation.add(*item_var)
        order_item.save()

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if not order.items.filter(item__id=order_item.id).exists():
            order.items.add(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("Main:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to cart.")
        return redirect("Main:order-summary")




@allow_lazy_user
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            
            messages.info(request, "This item was removed from your cart.")
            return redirect("Main:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("Main:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("Main:product", slug=slug)


@allow_lazy_user
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("Main:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("Main:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("Main:product", slug=slug)




@allow_lazy_user
def remove_single_customer_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.guest > 1:
                order_item.guest -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("Main:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("Main:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("Main:product", slug=slug)



@allow_lazy_user
def add_guest_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.guest += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("Main:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("Main:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("Main:order-summary")
'''








@allow_lazy_user
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("Main:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("Main:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("Main:order-summary")


@allow_lazy_user
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("Main:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("Main:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("Main:product", slug=slug)


@allow_lazy_user
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("Main:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("Main:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("Main:product", slug=slug)


















def Towels(request):
    Tows = Item.objects.all().filter(Q(title__icontains='towels')|
                                    Q(title__icontains='towel')|
                                    Q(title__icontains='cottontowels')|
                                    Q(title__icontains='cottontowel'))
    context = {
        'Tows':Tows
    }
    return render(request, "Main/Towels.html", context)



def Pillow(request):
    Pils = Item.objects.all().filter(Q(title__icontains='pillow')|
                                    Q(title__icontains='pillowcase')|
                                    Q(title__icontains='pillows')|
                                    Q(title__icontains='pillowcases'))
    context = {
        'Pils':Pils
    }
    return render(request, "Main/Pillows.html", context)





def BedSheet(request):
    Beds = Item.objects.all().filter(Q(title__icontains='sheet')|Q(title__icontains='Bedsheet')|Q(title__icontains="Percale"))

    context = {
        'Beds':Beds
    }
    return render(request, "Main/BedSheet.html", context)




