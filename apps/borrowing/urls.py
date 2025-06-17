from django.urls import path
from . import views

app_name = 'borrowing'

urlpatterns = [
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    path('borrow/<int:pk>/', views.borrow_book, name='borrow_book'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
] 