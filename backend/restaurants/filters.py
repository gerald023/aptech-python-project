import django_filters
from .models import Dish

class DishFilter(django_filters.FilterSet):
    restaurant = django_filters.NumberFilter(field_name="restaurant_id")
    food_type = django_filters.CharFilter(field_name="food_type__name", lookup_expr="iexact")
    category = django_filters.NumberFilter(field_name="categories__id")
    menu = django_filters.NumberFilter(field_name="menus__id")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    is_available = django_filters.BooleanFilter(field_name="is_available")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Dish
        fields = ["restaurant", "food_type", "category", "menu", "is_available"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)