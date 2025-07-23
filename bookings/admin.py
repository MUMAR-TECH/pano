from django.contrib import admin
from .models import Booking, Payment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'room', 'check_in_date', 'check_out_date', 
                   'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'check_in_date']
    search_fields = ['guest_name', 'guest_email', 'room__property__name']
    readonly_fields = ['total_nights', 'total_amount']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'payment_method', 'amount', 'status', 'payment_date']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['booking__guest_name', 'transaction_id']