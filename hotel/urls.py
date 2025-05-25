
from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.custom_logout, name='logout'),

    path('book-room/', views.book_room, name='book_room'),
    path('food-order/<int:customer_id>/', views.food_order, name='food_order'),

    path('checkout/<int:customer_id>/',views.checkout_customer, name='checkout_customer'),
    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),

    path('customer-list/', views.customers_list, name='customer_list'),
    path('export/pdf/<int:customer_id>/', views.export_bill_pdf, name='export_bill_pdf'),
    path('export/csv/<int:customer_id>/', views.export_bill_csv, name='export_bill_csv'),

    path('generate-bill/<int:customer_id>/', views.generate_bill, name='generate_bill'),    


] 









