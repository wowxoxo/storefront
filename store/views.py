from collections import Counter
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer

class ProductList(APIView):
  def get(self, request):
    query_set = Product.objects.select_related('collection').all()
    serializer = ProductSerializer(query_set, many=True, context={'request': request})
    return Response(serializer.data)

  def post(self, request):
    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# FIXME: remove, old way
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
  
class ProductDetail(APIView):
  def get(self, request, id):
    product = get_object_or_404(Product, pk=id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

  def put(self, request, id):
    product = get_object_or_404(Product, pk=id)
    serializer = ProductSerializer(product, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

  def delete(self, request, id):
    product = get_object_or_404(Product, pk=id)
    if product.orderitems.count() > 0:
      return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# FIXME: remove, old way
@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
  # try:
  #   product = Product.objects.get(pk=id)
  # except Product.DoesNotExist:
  #   return Response(status=status.HTTP_404_NOT_FOUND)
  # serializer = ProductSerializer(product)
  # return Response(serializer.data)

  product = get_object_or_404(Product, pk=id)
  if request.method == 'GET':
    serializer = ProductSerializer(product)
    return Response(serializer.data)

  elif request.method == 'PUT':
    serializer = ProductSerializer(product, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

  elif request.method == 'DELETE':
    if product.orderitems.count() > 0:
      return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def collection_list(request):
  if request.method == 'GET':
    query_set = Collection.objects.annotate(products_count=Count('products')).all()
    serializer = CollectionSerializer(query_set, many=True)
    return Response(serializer.data)

  elif request.method == 'POST':
    serializer = CollectionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
  collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
  if request.method == 'GET':
    serializer = CollectionSerializer(collection)
    return Response(serializer.data)

  elif request.method == 'PUT':
    serializer = CollectionSerializer(collection, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

  elif request.method == 'DELETE':
    if collection.products.count() > 0:
      return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    collection.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)