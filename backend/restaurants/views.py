from rest_framework import viewsets, mixins, generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsRestaurantOwner
from .permissions import IsSuperUser, IsOwnerOrReadOnly
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .filters import DishFilter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Dish, Restaurant, FoodType, Category, Menu
from .serializers import DishSerializer, RestaurantSerializer, FoodTypeSerializer, CategorySerializer, MenuSerializer


class FoodTypeViewSet(viewsets.ModelViewSet):
    queryset = FoodType.objects.all().order_by("id")
    serializer_class = FoodTypeSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsSuperUser()]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related("restaurant").all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        """
        - Superuser can create global categories (restaurant=None) or scoped ones.
        - Owner can create only for their own restaurant (restaurant forced).
        """
        user = self.request.user
        if user.is_superuser:
            # superuser may send restaurant or omit (global)
            serializer.save()
        else:
            # force owner’s restaurant; global (None) not allowed for non-admins
            if not hasattr(user, "restaurant"):
                raise PermissionError("Only restaurant owners can create categories.")
            serializer.save(restaurant=user.restaurant)


class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer

    def get_queryset(self):
        qs = Menu.objects.select_related("restaurant")
        # If the user is authenticated AND owns a restaurant → show only their menus
        if self.request.user.is_authenticated and hasattr(self.request.user, "restaurant"):
            return qs.filter(restaurant=self.request.user.restaurant)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve", "public_menus", "by_restaurant"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]
    
    # --- Extra endpoint: view all menus (public listing) ---
    @action(detail=False, methods=["get"], url_path="public")
    def public_menus(self, request):
        """Return all menus (public endpoint for customers)."""
        qs = Menu.objects.select_related("restaurant").all()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    
    # --- Extra endpoint: view menus by restaurant ---
    @action(detail=False, methods=["get"], url_path="by-restaurant/(?P<restaurant_id>[^/.]+)")
    def by_restaurant(self, request, restaurant_id=None):
        """Return menus belonging to a specific restaurant."""
        qs = Menu.objects.filter(restaurant_id=restaurant_id).select_related("restaurant")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class DishViewSet(viewsets.ModelViewSet):
    """
    - Public: list & retrieve => only is_available=True
    - Owners: create/update/delete only on their restaurant's dishes
    - Added `mine/` action for owners to list ALL their dishes (including unavailable)
    """
    serializer_class = DishSerializer
    filterset_class = DishFilter
    ordering_fields = ["price", "created_at", "name"]

    def get_queryset(self):
        # Public listing / retrieve: available dishes
        if self.action in ["list", "retrieve"]:
            qs = Dish.objects.select_related("restaurant", "food_type").prefetch_related("categories", "menus").filter(is_available=True)
            # optional query param to let owners see their full set: ?mine=true
            mine = self.request.query_params.get("mine")
            if mine and mine.lower() in ("1", "true") and self.request.user.is_authenticated and hasattr(self.request.user, "restaurant"):
                return Dish.objects.select_related("restaurant", "food_type").prefetch_related("categories", "menus").filter(restaurant=self.request.user.restaurant)
            return qs

        # For unsafe methods (create/update/destroy) only allow owner's restaurant dishes
        if not self.request.user.is_authenticated or not hasattr(self.request.user, "restaurant"):
            return Dish.objects.none()
        return Dish.objects.select_related("restaurant", "food_type").prefetch_related("categories", "menus").filter(restaurant=self.request.user.restaurant)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "restaurant"):
            raise PermissionDenied("You do not own a restaurant.")

        categories_ids = self.request.data.get("categories", [])
        menus_ids = self.request.data.get("menus", [])

        # Check if menus belong to owner's restaurant
        if menus_ids:
            bad_menu = Menu.objects.filter(id__in=menus_ids).exclude(restaurant=user.restaurant).first()
            if bad_menu:
                raise PermissionDenied("One or more menus do not belong to your restaurant.")

        # Set restaurant automatically
        serializer.save(restaurant=user.restaurant)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """GET /dishes/mine/  — returns all dishes (including unavailable) for the requesting owner."""
        user = request.user
        if not hasattr(user, "restaurant"):
            return Response([], status=status.HTTP_200_OK)

        qs = Dish.objects.filter(restaurant=user.restaurant).select_related("food_type").prefetch_related("categories", "menus")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="add-to-menu", permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def add_to_menu(self, request, pk=None):
        """POST /dishes/<pk>/add-to-menu/  body: { "menu_id": 5 }"""
        dish = self.get_object()
        menu_id = request.data.get("menu_id")
        if not menu_id:
            return Response({"detail": "menu_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        menu = get_object_or_404(Menu, id=menu_id)
        # checking if the menu belongs to the same restaurant as the dish
        if menu.restaurant_id != dish.restaurant_id:
            return Response({"detail": "Menu not found or not in your restaurant"}, status=status.HTTP_404_NOT_FOUND)

        dish.menus.add(menu)
        return Response({"detail": "Dish added to menu"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="remove-from-menu", permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def remove_from_menu(self, request, pk=None):
        """POST /dishes/<pk>/remove-from-menu/  body: { "menu_id": 5 }"""
        dish = self.get_object()
        menu_id = request.data.get("menu_id")
        if not menu_id:
            return Response({"detail": "menu_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        menu = get_object_or_404(Menu, id=menu_id)
        if menu.restaurant_id != dish.restaurant_id:
            return Response({"detail": "Menu not found or not in your restaurant"}, status=status.HTTP_404_NOT_FOUND)

        dish.menus.remove(menu)
        return Response({"detail": "Dish removed from menu"}, status=status.HTTP_200_OK)


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
