from django.contrib import admin
from .models import Order, OrderLineItem

# I’m making it easy to manage line items (the products/services inside each order) directly within the order admin.
class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)  # I don’t want admins to change this because it's auto-calculated.

# This is the main admin class to handle Orders
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)  # I’m linking the line items to appear inside each order like a section.

    # These fields can't be edited by admins — they're calculated or system-generated.
    readonly_fields = (
        'order_number',
        'date',
        'delivery_cost',
        'order_total',
        'grand_total',
    )

    # The layout I want in the admin form when someone views/edits an order.
    fields = (
        'order_number',
        'user_profile',  # once we add profiles, it’ll connect here
        'full_name',
        'email',
        'phone_number',
        'country',
        'postcode',
        'town_or_city',
        'street_address1',
        'street_address2',
        'county',
        'date',
        'delivery_cost',
        'order_total',
        'grand_total',
    )

    # This controls what columns are visible in the order list view in admin.
    list_display = (
        'order_number',
        'date',
        'full_name',
        'order_total',
        'delivery_cost',
        'grand_total',
    )

    ordering = ('-date',)  # Most recent orders first!

# Finally registering the Order model so it appears in admin with this custom layout
admin.site.register(Order, OrderAdmin)
