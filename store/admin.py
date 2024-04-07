from urllib.parse import urlencode
from django.contrib import admin, messages

from .models import Collection, Customer, Order, Product, OrderItem
from django.db.models.aggregates import Count
from django.utils.html import format_html
from django.urls import reverse

class InventoryFilter(admin.SimpleListFilter):
  title = 'inventory'
  parameter_name = 'inventory'

  def lookups(self, request, model_admin):
    return [
      ('<10', 'Low')
    ]

  def queryset(self, request, queryset):
    if self.value() == '<10':
      return queryset.filter(inventory__lt=10)
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  # exclude = ['promotions']
  autocomplete_fields = ['collection']
  prepopulated_fields = {
    'slug': ['title']
  }
  actions = ['clean_inventory']
  list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
  list_editable = ['unit_price']
  list_filter = ['collection', 'last_update', InventoryFilter]
  list_per_page = 10
  list_select_related = ['collection']
  search_fields = ['title']

  def collection_title(self, product):
    return product.collection.title

  @admin.display(ordering='inventory')
  def inventory_status(self, product):
    if product.inventory < 10:
      return 'Low'
    return 'Enough'
  
  @admin.action(description='Clean inventory')
  def clean_inventory(self, request, queryset):
    updated_count = queryset.update(inventory=0)
    self.message_user(request, f'{updated_count} products were successfully updated!', messages.ERROR)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
  list_display = ['first_name', 'last_name', 'membership']
  list_editable = ['membership']
  ordering = ['first_name', 'last_name']
  list_per_page = 10
  search_fields = ['first_name__istartswith', 'last_name__istartswith']

# admin.site.register(Product, ProductAdmin)
# admin.site.register(Collection)
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
  list_display = ['title', 'products_count']
  search_fields = ['title']

  def get_queryset(self, request):
    return super().get_queryset(request).annotate(
      products_count=Count('product')
    )

  @admin.display(ordering='products_count')
  def products_count(self, collection):
    url = (
      reverse('admin:store_product_changelist')
      + '?collection__id='
      + str(collection.id)
      # + urlencode({'collection__id': str(collection.id)}) // doesn't work
    )
    # return collection.products_count
    return format_html('<a href="{}">{}</a>', url, collection.products_count)

class OrderItemInline(admin.TabularInline):
  autocomplete_fields = ['product']
  model = OrderItem
  extra = 0
  min_num = 1
  max_num = 10

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  autocomplete_fields = ['customer']
  inlines = [
    OrderItemInline
  ]
  list_display = ['id', 'customer', 'placed_at', 'payment_status']
  list_editable = ['payment_status']
  list_per_page = 10
  list_select_related = ['customer']