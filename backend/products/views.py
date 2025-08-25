from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Product
from api.mixins import StaffEditorPermissionMixin;
from .serializers import ProductSerializer


class ProductCreateAPIView(
    StaffEditorPermissionMixin,
    generics.CreateAPIView):
    queryset = Product.objects.all();
    serializer_class = ProductSerializer;
    
    def perform_create(self, serializer):
        print(serializer)
        title = serializer.validated_data.get('title');
        content = serializer.validated_data.get('content') or None;
        if content is None:
            content = title;
        serializer.save(content = content)


class ProductDetailsAPIViews(
    StaffEditorPermissionMixin,
    generics.RetrieveAPIView):
    queryset = Product.objects.all();
    serializer_class = ProductSerializer;
    # lookup_field = pk # this is the default lookup attribute django will use.
    
class ProductUpdateAPIViews(
    StaffEditorPermissionMixin,
    generics.UpdateAPIView):
    queryset = Product.objects.all();
    serializer_class = ProductSerializer;
    lookup_field = 'pk'; # this is the default lookup attribute django will use.
    def perform_update(self, serializer):
        instance = serializer.save();
        if not instance.content:
            instance.content = instance.title;


class ProductDestroyAPIViews(
    StaffEditorPermissionMixin,
    generics.DestroyAPIView):
    queryset = Product.objects.all();
    serializer_class = ProductSerializer;
    lookup_field = 'pk'; # this is the default lookup attribute django will use.
    def perform_destroy(self, instance):
        super().perform_destroy(instance);


class ProductListCreateAPIView(
    StaffEditorPermissionMixin,
    generics.ListCreateAPIView
    ):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    ##this authentication class has been taken care of in the settings.py
    # authentication_classes = [
    #     authentication.SessionAuthentication,
    #     TokenAuthentication
    # ]
    
    
    ##this permission class has been taken care of by the staffEditorPermissionMixin
    
    # permission_classes = [permissions.IsAdminUser, IsStaffEditorPermission]

product_list_create_view = ProductListCreateAPIView.as_view();
    
class ProductListAPIViews(
    StaffEditorPermissionMixin,
    generics.ListAPIView):
    queryset = Product.objects.all();
    serializer_class = ProductSerializer;

#class api view for post, get requests..
class ProductMixinView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView
):
    queryset = Product.objects.all();
    serializer_class = ProductSerializer;
    lookup_field = 'pk';
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk');
        if pk is not None:
            return self.retrieve(request, *args, **kwargs);
        return self.list(request, *args, **kwargs);
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    def perform_create(self, serializer):
        print(serializer)
        title = serializer.validated_data.get('title');
        content = serializer.validated_data.get('content') or None;
        if content is None:
            content = 'This is a cool post request from a Mixin class';
        serializer.save(content = content)

#method api view with get and post requests.
@api_view(['GET', 'POST'])
def product_alt_view(request, pk=None, *args, **kwargs):
    method = request.method
    
    if method == "GET":
        if pk is not None:
            obj = get_object_or_404(Product, pk=pk)
            data = ProductSerializer(obj, many=False).data;
            return Response(data);
        querySet = Product.objects.all()
        data = ProductSerializer(querySet, many = True).data;
        return Response(data);
    
    if method == "POST":
        serializer = ProductSerializer(data = request.data)
        if serializer.is_valid():
            title = serializer.validated_data.get('title');
            content = serializer.validated_data.get('content') or None;
            if content is None:
                content = title;
            serializer.save(content = content)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    