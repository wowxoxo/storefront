from decimal import Decimal
from rest_framework import serializers
from .models import Collection, Product, Cart, CartItem, Order, OrderItem

class CollectionSerializer0(serializers.Serializer):
  id = serializers.IntegerField()
  title = serializers.CharField(max_length=255)

class CollectionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Collection
    fields = ['id', 'title', 'products_count']

  products_count = serializers.IntegerField(read_only=True)

class ProductSerializer0(serializers.Serializer):
  id = serializers.IntegerField()
  title = serializers.CharField(max_length=255)
  price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
  price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
  # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
  # collection = serializers.StringRelatedField() # too many sql queries, to fix: add select_related in views.py
  # collection = CollectionSerializer() # get collection as a nested object
  collection = serializers.HyperlinkedRelatedField(
    queryset=Collection.objects.all(),
    view_name='collection-detail'
  )

  def calculate_tax(self, product: Product):
    return product.unit_price * Decimal(1.1)

class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']
  
  price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

  def calculate_tax(self, product: Product):
    return product.unit_price * Decimal(1.1)
  
  # def create(self, validated_data):
  #   product = Product(**validated_data)
  #   product.other = 1
  #   product.save()
  #   return product

  # def update(self, instance, validated_data):
  #   instance.title = validated_data.get('title', instance.title)
  #   instance.description = validated_data.get('description', instance.description)
  #   instance.save()
  #   return instance