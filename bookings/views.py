from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.db.models import Q
from properties.models import Room
from .models import Booking, Payment
from .forms import BookingForm
from datetime import datetime, timedelta

# views.py - Update create_booking view
@login_required
def create_booking(request):
    room_type = request.GET.get('room_type')
    check_in_date = request.GET.get('check_in')
    check_out_date = request.GET.get('check_out')
    guests = request.GET.get('guests')
    property_id = request.GET.get('property_id')
    
    if not all([room_type, check_in_date, check_out_date, guests, property_id]):
        messages.error(request, 'Missing booking information.')
        return redirect('properties:property_detail', pk=property_id)
    
    try:
        # Find the first available room of the selected type
        room = Room.objects.filter(
            property_id=property_id,
            room_type=room_type,
            is_available=True
        ).first()
        
        if not room:
            messages.error(request, 'No rooms available of the selected type.')
            return redirect('properties:property_detail', pk=property_id)
        
        # Check if room is actually available for the dates
        check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
        
        conflicting_bookings = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'pending'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        
        if conflicting_bookings.exists():
            messages.error(request, 'Room is no longer available for the selected dates.')
            return redirect('properties:property_detail', pk=property_id)
        
        if request.method == 'POST':
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.room = room
                booking.check_in_date = check_in
                booking.check_out_date = check_out
                booking.guests = int(guests)
                booking.save()
                
                messages.success(request, 'Booking created successfully!')
                return redirect('bookings:booking_detail', pk=booking.pk)
        else:
            # Pre-fill form with available data
            initial_data = {
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
                'guests': guests,
                'guest_name': request.user.get_full_name() or request.user.username,
                'guest_email': request.user.email,
            }
            form = BookingForm(initial=initial_data)
        
        return render(request, 'bookings/booking_form.html', {
            'form': form,
            'room': room,
            'check_in': check_in_date,
            'check_out': check_out_date,
            'guests': guests,
            'total_nights': (check_out - check_in).days,
            'total_amount': room.price_per_night * (check_out - check_in).days
        })
        
    except Exception as e:
        messages.error(request, f'Error creating booking: {str(e)}')
        return redirect('properties:property_detail', pk=property_id)
    
    
@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@method_decorator(login_required, name='dispatch')
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('check_in_date')

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if booking.status in ['confirmed', 'pending']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
    else:
        messages.error(request, 'Cannot cancel this booking.')
    
    return redirect('booking_list')

@login_required
def vendor_bookings(request):
    if request.user.userprofile.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('home')
    
    # Get all bookings for vendor's properties
    vendor_properties = request.user.property_set.all()
    bookings = Booking.objects.filter(
        room__property__in=vendor_properties
    ).select_related('user', 'room', 'room__property')
    
    return render(request, 'bookings/vendor_bookings.html', {
        'bookings': bookings
    })

@login_required
def confirm_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check if user is the property owner
    if booking.room.property.owner != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, 'Booking confirmed successfully!')
    
    return redirect('vendor_bookings')

def room_availability(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        
        conflicting_bookings = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'pending'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        )
        
        is_available = not conflicting_bookings.exists()
        
        return render(request, 'bookings/availability_check.html', {
            'room': room,
            'check_in': check_in_date,
            'check_out': check_out_date,
            'is_available': is_available
        })
    
    return render(request, 'bookings/availability_form.html', {'room': room})



# views.py - Add this view
from django.http import JsonResponse
import json
from datetime import datetime

def check_availability(request):
    room_type = request.GET.get('room_type')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    property_id = request.GET.get('property_id')
    
    if not all([room_type, check_in, check_out, property_id]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        
        # Find available rooms of the selected type
        available_rooms = Room.objects.filter(
            property_id=property_id,
            room_type=room_type,
            is_available=True
        )
        
        # Check for conflicting bookings
        for room in available_rooms:
            conflicting_bookings = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'pending'],
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            )
            
            if not conflicting_bookings.exists():
                # Room is available
                total_nights = (check_out_date - check_in_date).days
                return JsonResponse({
                    'available': True,
                    'room_id': room.id,
                    'price': float(room.price_per_night),
                    'total_nights': total_nights
                })
        
        return JsonResponse({'available': False})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)