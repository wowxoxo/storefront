from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product

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
  query_set = Product.objects.filter(title__icontains='coffee')
  query_set = Product.objects.filter(last_update__year=2021)
  query_set = Product.objects.filter(description__isnull=True)

  return render(request, 'hello.html', {'name': 'Mike', 'products': list(query_set)})
