from django.urls import path
from .views import index,register,logout1,updatecart,cart,checkout,product_detail,stripe_config,create_checkout_session,SuccessView,CancelledView,stripe_webhook,myorders
urlpatterns = [
    path('',index,name="index"),
    path('register/',register,name="register"),
    path('logout/',logout1,name="logout1"),
    path('updatecart/',updatecart,name="updatecart"),
    path('cart/',cart,name="cart"),
    path('checkout/',checkout,name="checkout"),
    path('product/<int:pk>/',product_detail, name='product_detail'),
    path('config/',stripe_config),
    path('create-checkout-session/',create_checkout_session),
    path('success/',SuccessView),
    path('cancelled/',CancelledView),
    path('webhook/', stripe_webhook),
    path('myorders/', myorders, name="myorders"),
]