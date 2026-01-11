from django.contrib import admin
from .models import Equipment, Rental
from django.contrib.auth.models import Group


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('is_available',)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipment', 'rental_date', 'return_date', 'status')
    list_filter = ('status', 'rental_date')
    search_fields = ('user__username', 'equipment__name')
    readonly_fields = ('created_at',)

# Wyrejestrowanie modelu Group, aby usunąć sekcję "Groups" z admin panelu
admin.site.unregister(Group)
