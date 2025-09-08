from django.urls import path
from . import views;

#/api/products/
urlpatterns = [
    path("", views.product_list_create_view),
    path("create_product/", views.ProductCreateAPIView.as_view()),
    path('<uuid:pk>/', views.ProductDetailsAPIViews.as_view()),
    path('list_products/', views.ProductListAPIViews.as_view()),
    path('alt_view/', views.product_alt_view),
    path('<uuid:pk>/method_details/', views.product_alt_view),
    path('<uuid:pk>/update/', views.ProductUpdateAPIViews.as_view()),
    path('<uuid:pk>/delete/', views.ProductDestroyAPIViews.as_view()),
    path('mixin_view/', views.ProductMixinView.as_view()),
    path('<uuid:pk>/mixin_details/', views.ProductMixinView.as_view()),
]
