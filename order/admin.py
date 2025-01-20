from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, Payment, Notification
from django.db.models import Sum

# Inline Admin for Payment model
class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0

# Custom Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'participant', 'get_order_details', 'total_price', 'status', 'order_date', 'payment_status')
    list_filter = ('status', 'payment_status', 'order_date')
    search_fields = ('participant__user__username', 'participant__user__email')
    ordering = ('-order_date',)
    inlines = [PaymentInline]

    def get_order_details(self, obj):
        if obj.post:
            return f"Food & Beverage: {obj.post.title}"
        if obj.conversation_hall_post:
            return f"Conversation Hall: {obj.conversation_hall_post.title}"
        if obj.activity_post:
            return f"Activity: {obj.activity_post.title}"
        return _("No Post")

    get_order_details.short_description = _('Order Details')

    def save_model(self, request, obj, form, change):
        # Optional: You can add extra logic to be executed before saving the object
        super().save_model(request, obj, form, change)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount_paid', 'payment_method', 'is_full_payment', 'created_at')
    list_filter = ('payment_method', 'is_full_payment', 'created_at')
    search_fields = ('order__participant__user__username',)
    ordering = ('-created_at',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    ordering = ('-created_at',)

# Registering models
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Notification, NotificationAdmin)
