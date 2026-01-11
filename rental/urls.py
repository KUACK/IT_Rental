from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('new-rental/', views.new_rental, name='new_rental'),
    path('cancel-rental/<int:rental_id>/', views.cancel_rental, name='cancel_rental'),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('admin/toggle-availability/<int:equipment_id>/', views.admin_toggle_availability, name='toggle_availability'),
    path("api/equipment/<int:equipment_id>/reserved/", views.equipment_reserved_ranges, name="equipment_reserved_ranges"),
    path("api/equipment/<int:equipment_id>/reserved/", views.equipment_reserved, name="equipment_reserved"),
]
