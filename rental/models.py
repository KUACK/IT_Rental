from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('laptop', 'Laptop'),
        ('monitor', 'Monitor'),
        ('keyboard', 'Klawiatura'),
        ('mouse', 'Mysz'),
        ('headphones', 'Słuchawki'),
        ('projector', 'Projektor'),
        ('camera', 'Kamera'),
        ('other', 'Inne'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Kategoria")
    description = models.TextField(verbose_name="Opis")
    is_available = models.BooleanField(default=True, verbose_name="Dostępny")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sprzęt"
        verbose_name_plural = "Sprzęt"
    
    def __str__(self):
        return self.name


class Rental(models.Model):
    STATUS_CHOICES = [
        ('active', 'Aktywne'),
        ('completed', 'Ukończone'),
        ('cancelled', 'Anulowane'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals', verbose_name="Użytkownik")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='rentals', verbose_name="Sprzęt")
    rental_date = models.DateField(verbose_name="Data wynajmu")
    return_date = models.DateField(verbose_name="Data zwrotu")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Wypożyczenie"
        verbose_name_plural = "Wypożyczenia"
    
    def __str__(self):
        return f"{self.user.username} - {self.equipment.name} ({self.rental_date} do {self.return_date})"
    
    def clean(self):
        """Walidacja - blokowanie podwójnych wynajmów"""
        if self.rental_date >= self.return_date:
            raise ValidationError("Data zwrotu musi być po dacie wynajmu!")
        
        overlapping = Rental.objects.filter(
            equipment=self.equipment,
            status='active',
            rental_date__lt=self.return_date,
            return_date__gt=self.rental_date
        )
        
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError(f"Sprzęt '{self.equipment.name}' jest już wynajęty w tym okresie!")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
