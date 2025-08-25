from django.http import JsonResponse;
import json;
from products.models import Product;
from django.forms.models import model_to_dict;
from rest_framework.decorators import api_view
from rest_framework.response import Response;
from products.serializers import ProductSerializer;

@api_view(["GET"])
def api_home(request, *args, **kwargs):
    """
    DRF view. this is an official look of a django rest framework.
    """
    instance = Product.objects.all().order_by('?').first()
    data = {};
    
        
    # data = model_to_dict(instance, fields=['id', 'title', 'price'])
    data = ProductSerializer(instance).data;
        
    
    return Response(data)

@api_view(['POST'])
def add_products(request, *args, **kwargs):
    serializer = ProductSerializer(data = request.data)
    if serializer.is_valid():
        instance = serializer.save();
        print(instance)
        return Response(serializer.data)
    return Response(serializer.errors, status=400)