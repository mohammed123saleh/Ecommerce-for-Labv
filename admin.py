from django.db import models
from django.contrib import admin
from tinymce.widgets import TinyMCE

from .models import (Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile, Contact, Signupmodel, ContactHomeModel, Mails,ContactHomeModel, Variation, Publication, Article )

admin.site.site_header = "Egypt Fabrics Admin"
admin.site.site_title = "Egypt Fabrics Admin Portal"
admin.site.index_title = "Welcome to Egypt Fabrics"

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
            #        'shipping_address',
            #        'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
         'user',
      #  'shipping_address',
       # 'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
      #  'street_address',
      #  'apartment_address',
        'country',
        'zip',
    #    'address_type',

    ]
    list_filter = [ 'country']
    search_fields = [ 'street_address', 'apartment_address', 'zip']

class ItemAdmin(admin.ModelAdmin):
  
    list_display = ['title',
            
                    'price',
                    'category',
                  
                   
                  
                    ]
    list_display_links = [
                        'title',  
                        'price',
                        'category',
                        
                        ]

    search_fields = [
                    'title',
                    'category',
                    'price',
              
                    ]


    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
        }



class orderitemadmin(admin.ModelAdmin):
    list_display = [
                    'item',
               
                   
                  
                    ]
    list_display_links = [
                           
                            'item',
                        
                        ]
    list_filter = [ 
                    'item',
                       ]

'''                       
    search_fields = [
                  
                    'item',

                    ]  
'''                          
from .models import Temp
admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem, orderitemadmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
#admin.site.register(Contact)
#admin.site.register(Signupmodel)
admin.site.register(ContactHomeModel)


admin.site.register(Mails)









