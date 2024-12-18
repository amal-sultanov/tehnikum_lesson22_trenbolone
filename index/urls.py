from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_page),
    path('product/<int:pk>', views.product_page),
    path('category/<int:pk>', views.category_page),
    path('register', views.Register.as_view()),
    path('search', views.search),
    path('logout', views.logout_view),
    path('add-to-cart/<int:pk>', views.add_to_cart),
    path('delete-from-cart/<int:pk>', views.delete_from_cart),
    path('cart', views.cart_page),
]
