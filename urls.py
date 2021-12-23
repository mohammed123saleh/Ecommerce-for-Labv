from django.urls import path
from .views import (home, about, Contact, ItemDetailView, OrderSummaryView,
                    add_to_cart,
                    remove_from_cart,
                    remove_single_item_from_cart,
                    PaymentView,
                    AddCouponView,
                    RequestRefundView,
                  
                

                    HomeView, CheckoutView, Contact,  index, Mission,ThankYou,
                    FAQ,
                    Towels,
                    Pillow,
                    BedSheet)
app_name = 'Main'

urlpatterns =[
    path('', home.as_view(), name='home'), 
    path('Products/', HomeView.as_view(), name='book'),
    path('about/', about, name='about'), 
    path('Contact/', Contact, name='Contact'), 
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView, name='order-summary'),
    path('product/<slug>/', ItemDetailView, name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('NewsLetter/', index, name='NewsLetter'),
    path('Mission/', Mission, name='Mission'),
    path('Terms&Conditions/', FAQ, name='Terms&Conditions'),
    path('ThankYou', ThankYou, name='ThankYou'),
    path('Towels', Towels, name='Towels'),
    path('Pillowcases', Pillow, name='Pillowcases'),
    path('BedSheets', BedSheet, name='BedSheets'),

    
]