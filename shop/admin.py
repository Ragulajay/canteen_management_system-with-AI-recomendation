from django.contrib import admin
from .models import Product, Contact, Orders, OrderUpdate
import json
from operator import itemgetter

class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'update_desc', 'timestamp')
    list_filter = ['timestamp']

    def has_delete_permission(self, request, obj=None):
        return False


class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'userId', 'name', 'email', 'timestamp')
    list_filter = ['timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'ordered_count_display')
    list_filter = ['category']
    search_fields = ['product_name']

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset
            product_counts = []

            for product in qs:
                count = self.calculate_ordered_count(product)
                product_counts.append((product, count))

            sorted_products = sorted(product_counts, key=itemgetter(1), reverse=True)
            sorted_queryset = [p[0] for p in sorted_products]

            response.context_data['cl'].result_list = sorted_queryset
        except Exception as e:
            print("Error sorting by ordered_count:", e)

        return response

    def calculate_ordered_count(self, obj):
        total = 0
        for order in Orders.objects.all():
            try:
                items = json.loads(order.items_json)
                for key, value in items.items():
                    if str(value[2]) == str(obj.id):  # value[2] = product_id
                        total += int(value[0])        # value[0] = quantity
            except Exception as e:
                continue
        return total

    def ordered_count_display(self, obj):
        return self.calculate_ordered_count(obj)

    ordered_count_display.short_description = "Sales Analytics"


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'email', 'timestamp')
    list_filter = ['timestamp']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Register the models with their custom admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderUpdate, OrderUpdateAdmin)

# Admin site branding
admin.site.site_header = "Canteen Management"
admin.site.index_title = "Canteen Management Administration"
admin.site.site_title = "Canteen Management Admin"
