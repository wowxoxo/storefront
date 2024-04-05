from django.db import connection
from django.forms import DecimalField
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Sum, Avg, Min, Max
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import atomic
from store.models import Collection, Product, OrderItem, Order, Customer
from tags.models import Tag, TaggedItem

def say_hello(request):
  return HttpResponse('Hello World!')

  # query_set = Product.objects.all()
  # for product in query_set:
  #   print(product.title)
  # list(query_set)
  # query_set[0:5]

  # try:
  #   product = Product.objects.get(pk=1)
  # except ObjectDoesNotExist:
  #   product = None

  # product = Product.objects.filter(pk=0).first()
  # exists = Product.objects.filter(pk=0).exists()

  # query_set = Product.objects.filter(unit_price__gt=20)
  # query_set = Product.objects.filter(unit_price__range=(20, 30))
  # query_set = Product.objects.filter(collection__id__range=(1, 2, 3)) # error

  # query_set = Product.objects.filter(title__icontains='coffee')
  # query_set = Product.objects.filter(last_update__year=2021)
  # query_set = Product.objects.filter(description__isnull=True)

  # Products: inventory < 10 and price < 20
  query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
  query_set = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)

  # Products: inventory < 10 OR price < 20
  query_set = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))
  query_set = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))

  # Products: inventory = price
  query_set = Product.objects.filter(inventory=F('unit_price'))

  query_set = Product.objects.order_by('unit_price', '-title').reverse()

  query_set = Product.objects.filter(collection__id=1).order_by('unit_price')

  product = Product.objects.order_by('unit_price').first()
  product = Product.objects.earliest('unit_price')

  query_set = Product.objects.all()[:5]

  # select fields
  query_set = Product.objects.values('id', 'title', 'collection__id', 'collection__title')

  query_set = OrderItem.objects.values('product_id').distinct()
  query_set = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

  # selecting related objects
  query_set = Product.objects.all() # bad, a lot of sql requests for each product to get collection title
  
  # select related (1)
  query_set = Product.objects.select_related('collection').all() # good, one sql request

  # select related (n)
  query_set = Product.objects.prefetch_related('promotions').all()

  # both
  query_set = Product.objects.prefetch_related('promotions').select_related('collection').all()

  # query_set = Order.objects.select_related('customer').order_by('-placed_at')[:5]
  query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]

  # Aggregations
  result = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))

  # annotations
  query_set = Customer.objects.annotate(is_new=Value(True))
  query_set = Customer.objects.annotate(new_id=F('id') + 1)

  # functions
  query_set = Customer.objects.annotate(full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT'))

  query_set = Customer.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))

  # grouping
  query_set = Customer.objects.annotate(orders_count=Count('order'))

  # expression wrapper
  # query_set = Product.objects.annotate(discounted_price=F('unit_price') * 0.8) # error, mixed types
  discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
  query_set = Product.objects.annotate(discounted_price=discounted_price)

  # querying generic relationships
  content_type = ContentType.objects.get_for_model(Product)

  # TaggedItem.objects.create(
  #   tag=Tag.objects.create(name='hello'),
  #   content_type=content_type,
  #   object_id=1
  # )

  query_set = TaggedItem.objects \
    .select_related('tag') \
    .filter(
      content_type=content_type,
      object_id=1
  )
  
  # custom manager
  query_set = TaggedItem.objects.get_tags_for(Product, 1)

  # create
  collection = Collection()
  collection.title = 'Video Games'
  collection.featured_product = Product.objects.first()
  # collection.featured_product_id = 1
  collection.save()

  # update
  collection = Collection.objects.get(pk=11)
  # collection.title = 'Games'
  collection.featured_product_id = None
  # collection.featured_product = Product.objects.filter(unit_price__lt=10).first()
  collection.save() # bad, reset title
  
  Collection.objects.filter(pk=11).update(featured_product_id=None)

  # delete
  collection.delete()
  Collection.objects.filter(id_gt=5).delete()

  # bulk create
  # Collection.objects.bulk_create([
  #   Collection(title='Collection 1'),
  #   Collection(title='Collection 2'),
  #   Collection(title='Collection 3'),
  # ])

  # # bulk update
  # Collection.objects.filter(title__startswith='Collection').update(title='Collection X')

  # # bulk delete
  # Collection.objects.filter(title__startswith='Collection').delete()

  # # get_or_create
  # collection, created = Collection.objects.get_or_create(title='Collection 4')

  # # get_or_create
  # collection, created = Collection.objects.get_or_create(title='Collection 4', defaults={'title': 'Collection 4'})

  # transaction
  with atomic():
    order = Order()
    order.customer_id = 1
    order.save()

    order_item = OrderItem()
    order_item.order = order
    order_item.product_id = 1
    order_item.quantity = 1
    order_item.unit_price = 10
    order_item.save()

    order_item = OrderItem()
    order_item.order = order
    order_item.product_id = 2
    order_item.quantity = 2
    order_item.unit_price = 20
    order_item.save()

  # return HttpResponse('ok')

  # RAW queries
  query_set = Product.objects.raw('SELECT * FROM store_product')

  product = Product.objects.first()
  product.unit_price = 10
  product.save()

  ## connection
  cursor = connection.cursor()
  cursor.execute('SELECT * FROM store_product')
  cursor.close()

  ## connection with
  with connection.cursor() as cursor:
    cursor.execute('SELECT * FROM store_product')
    cursor.callproc('get_product_by_id', [1])

  return render(request, 'hello.html', {'name': 'Mike', 'products': list(query_set), 'product': product})
