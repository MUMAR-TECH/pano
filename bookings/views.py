from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Q
from properties.models import Room
from .models import Booking, Payment
from .forms import BookingForm
from datetime import datetime, timedelta

@login_required
def create_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_available=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            
            # Check room availability
            check_in = form.cleaned_data['check_in_date']
            check_out = form.cleaned_data['check_out_date']
            
            conflicting_bookings = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'pending'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            )
            
            if conflicting_bookings.exists():
                messages.error(request, 'Room is not available for the selected dates.')
                return render(request, 'bookings/booking_form.html', {
                    'form': form, 
                    'room': room
                })
            
            try:
                booking.save()
                messages.success(request, 'Booking created successfully!')
                return redirect('booking_detail', pk=booking.pk)
            except Exception as e:
                messages.error(request, f'Error creating booking: {str(e)}')
    else:
        form = BookingForm()
    
    return render(request, 'bookings/booking_form.html', {
        'form': form, 
        'room': room
    })

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@method_decorator(login_required, name='dispatch')
class BookingListView(ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

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