from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value
from django.db.models.aggregates import Count, Sum, Avg, Min, Max
from store.models import Product, OrderItem, Order, Customer

def say_hello(request):
  # return HttpResponse('Hello World!')

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

  return render(request, 'hello.html', {'name': 'Mike', 'products': list(query_set), 'product': product})
