from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError

from .models import Equipment, Rental


# ===== STRONY =====

def index(request):
    """Strona główna - lista sprzętu (z dostępnością na dziś)"""
    today = timezone.localdate()

    Rental.objects.filter(
        status='active',
        return_date__lt=today
    ).update(status='completed')

    equipment_list = list(Equipment.objects.all().order_by('name'))

    for eq in equipment_list:
        eq.rented_today = Rental.objects.filter(
            equipment=eq,
            status='active',
            rental_date__lte=today,
            return_date__gte=today,
        ).exists()

    return render(request, 'rental/index.html', {'equipment': equipment_list})


def register(request):
    """Rejestracja użytkownika"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, 'rental/register.html', {'error': 'Hasła się nie zgadzają!'})

        if User.objects.filter(username=username).exists():
            return render(request, 'rental/register.html', {'error': 'Użytkownik już istnieje!'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        login(request, user)
        return redirect('index')

    return render(request, 'rental/register.html')


def login_view(request):
    """Login użytkownika"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'rental/login.html', {'error': 'Błędne dane logowania!'})

    return render(request, 'rental/login.html')


def logout_view(request):
    """Logout"""
    logout(request)
    return redirect('index')


def equipment_reserved_ranges(request, equipment_id):
    today = timezone.localdate()

    rentals = Rental.objects.filter(
        equipment_id=equipment_id,
        status='active',
        return_date__gte=today
    ).values('rental_date', 'return_date')

    ranges = [
        {"from": r["rental_date"].isoformat(), "to": r["return_date"].isoformat()}
        for r in rentals
    ]
    return JsonResponse({"ranges": ranges})

@require_GET
def equipment_reserved(request, equipment_id):
    today = timezone.now().date()
    qs = (Rental.objects
          .filter(equipment_id=equipment_id, status='active', return_date__gte=today)
          .order_by('rental_date'))

    ranges = [
        {"from": r.rental_date.strftime("%Y-%m-%d"),
         "to": r.return_date.strftime("%Y-%m-%d")}
        for r in qs
    ]
    return JsonResponse({"ranges": ranges})


@login_required(login_url='login')
def my_rentals(request):
    """Moje wynajęcia"""
    today = timezone.localdate()


    #  Auto-zamykanie starych wynajęć
    Rental.objects.filter(
        user=request.user,
        status='active',
        return_date__lt=today
    ).update(status='completed')


    # Zaplanowane 
    planned_rentals = Rental.objects.filter(
        user=request.user,
        status='active',
        rental_date__gt=today
    ).order_by('rental_date')


    #  Aktywne 
    active_rentals = Rental.objects.filter(
        user=request.user,
        status='active',
        rental_date__lte=today,
        return_date__gte=today
    ).order_by('-rental_date')


    #  Ukończone i anulowane
    completed_rentals = Rental.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-return_date')


    cancelled_rentals = Rental.objects.filter(
        user=request.user,
        status='cancelled'
    ).order_by('-created_at')


    return render(request, 'rental/my_rentals.html', {
        'planned_rentals': planned_rentals,
        'active_rentals': active_rentals,
        'completed_rentals': completed_rentals,
        'cancelled_rentals': cancelled_rentals,
    })


@login_required(login_url='login')
def new_rental(request):
    """Dodawanie nowego wynajęcia"""
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        rental_date_str = request.POST.get('rental_date')
        return_date_str = request.POST.get('return_date')


        try:
            equipment = Equipment.objects.get(id=equipment_id)
            rental_date = datetime.strptime(rental_date_str, '%Y-%m-%d').date()
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()


            rental = Rental(
                user=request.user,
                equipment=equipment,
                rental_date=rental_date,
                return_date=return_date
            )
            rental.full_clean()
            rental.save()


            return redirect('my_rentals')


        except ValidationError as e:
            available_equipment = Equipment.objects.all()


            error_messages = []
            if hasattr(e, "message_dict"):
                for _field, msgs in e.message_dict.items():
                    error_messages.extend(msgs)
            else:
                error_messages = e.messages


            return render(request, 'rental/new_rental.html', {
                'equipment': available_equipment,
                'today': timezone.localdate(),
                'error_messages': error_messages,
            })


        except Exception as e:
            available_equipment = Equipment.objects.all()
            return render(request, 'rental/new_rental.html', {
                'equipment': available_equipment,
                'today': timezone.localdate(),
                'error_messages': [str(e)],
            })


    available_equipment = Equipment.objects.all()
    today = timezone.localdate()
    return render(request, 'rental/new_rental.html', {
        'equipment': available_equipment,
        'today': today
    })



@login_required(login_url='login')
def cancel_rental(request, rental_id):
    """Anulowanie wynajęcia"""
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    today = timezone.localdate()

    # Anulować można tylko przyszłe
    if rental.status == 'active' and rental.rental_date > today:
        rental.status = 'cancelled'
        rental.save()

    return redirect('my_rentals')


# ===== ADMIN PANEL =====

@login_required(login_url='login')
def admin_panel(request):
    """Panel administratora"""
    if not request.user.is_staff:
        return redirect('index')

    equipment_list = Equipment.objects.all()
    rentals = Rental.objects.all().order_by('-created_at')

    return render(request, 'rental/admin_panel.html', {
        'equipment': equipment_list,
        'rentals': rentals,
    })


@login_required(login_url='login')
def admin_toggle_availability(request, equipment_id):
    """Toggle dostępności sprzętu"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)

    equipment = get_object_or_404(Equipment, id=equipment_id)
    equipment.is_available = not equipment.is_available
    equipment.save()

    return JsonResponse({'success': True, 'is_available': equipment.is_available})
