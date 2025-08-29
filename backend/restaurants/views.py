from rest_framework import viewsets, mixins, generics, permissions
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsRestaurantOwner
from rest_framework.pagination import PageNumberPagination
from .models import Dish, Restaurant, FoodType
from .serializers import DishSerializer, RestaurantSerializer, FoodTypeSerializer

# Create your views here.
class DishViewSet(viewsets.ModelViewSet):
    """
    CRUD for dishes.
    - Owners can list/manage only their restaurant's dishes.
    - Everyone can list/retrieve public dishes (optional; tweak perms as needed).
    """
    serializer_class = DishSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsRestaurantOwner()]

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            # public browsing of dishes across restaurants
            return Dish.objects.select_related("restaurant", "food_type").filter(is_available=True)
        # owner-only: restrict to their own restaurant dishes
        if not hasattr(self.request.user, "restaurant"):
            # Owner doesn't have a restaurant yet
            return Dish.objects.none()
        return Dish.objects.select_related("restaurant", "food_type").filter(restaurant=self.request.user.restaurant)

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "restaurant"):
            raise PermissionDenied("You do not have a restaurant.")
        serializer.save(restaurant=user.restaurant)
        

class RestaurantPagination(PageNumberPagination):
    page_size = 5  # number of restaurants per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class RestaurantMixin(mixins.ListModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Restaurant.objects.all().order_by("id")
    serializer_class = RestaurantSerializer;
    lookup_field = 'pk';
    pagination_class = RestaurantPagination
    
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk');
        if pk is not None:
            return self.retrieve(request, *args, **kwargs);
        return self.list(request, *args, **kwargs);
    # authentication_classes = []
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())

        #pagination here
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class FoodTypeView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = FoodType.objects.all();
    serializer_class = FoodTypeSerializer;
    lookup_field = 'pk';
    
    permission_classes = [IsRestaurantOwner]
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk');
        if pk is not None:
            return self.retrieve(request, *args, **kwargs);
        return self.list(request, *args, **kwargs);
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
