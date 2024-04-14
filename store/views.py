from collections import Counter
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer

@api_view(['GET', 'POST'])
def product_list(request):
  # return HttpResponse("Hello, world. You're at the store index.")
  # return Response("Hello, world. You're at the store index.")

  if request.method == 'GET':
    query_set = Product.objects.select_related('collection').all()
    serializer = ProductSerializer(query_set, many=True, context={'request': request})
    return Response(serializer.data)

  elif request.method == 'POST':
    serializer = ProductSerializer(data=request.data)
    # if serializer.is_valid():
    #   serializer.save()
    #   return Response(serializer.data, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # no if
    serializer.is_valid(raise_exception=True)
    # print(serializer.validated_data)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view()
def product_detail(request, id):
  # try:
  #   product = Product.objects.get(pk=id)
  # except Product.DoesNotExist:
  #   return Response(status=status.HTTP_404_NOT_FOUND)
  # serializer = ProductSerializer(product)
  # return Response(serializer.data)

  product = get_object_or_404(Product, pk=id)
  serializer = ProductSerializer(product)
  return Response(serializer.data)

@api_view()
def collection_list(request):
  query_set = Collection.objects.annotate(products_count=Counter('product')).all()
  serializer = CollectionSerializer(query_set, many=True)
  return Response(serializer.data)

@api_view()
def collection_detail(request, pk):
  collection = get_object_or_404(Collection, pk=pk)
  serializer = CollectionSerializer(collection)
  return Response(serializer.data)