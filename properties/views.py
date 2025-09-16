from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Sum, Count, Min
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy

from bookings.models import Booking
from .models import Property, Room, Review, PropertyImage
from .forms import PropertyForm, RoomForm, ReviewForm
from django.urls import reverse_lazy
# views.py (add this to your existing views)
from django.views.generic import TemplateView
from django.db.models import Q


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get featured properties with their average ratings and review count
        # I've added an annotation for min_price, which we will use in the template.
        # I've also pre-fetched the primary image for each property.
        featured_properties = Property.objects.filter(
            is_active=True,
            is_featured=True
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews'),
            min_price=Min('room__price_per_night')
        ).prefetch_related('images').order_by('-avg_rating')[:6]

        # Now we need to process the queryset to get the primary image URL and amenities
        properties_with_data = []
        for prop in featured_properties:
            # Find the primary image or a fallback
            primary_image_url = ''
            primary_image = prop.images.filter(is_primary=True).first()
            if primary_image:
                primary_image_url = primary_image.image.url
            elif prop.images.first():
                primary_image_url = prop.images.first().image.url

            # Collect amenities
            amenities = []
            if prop.wifi:
                amenities.append('Free WiFi')
            if prop.parking:
                amenities.append('Free Parking')
            if prop.restaurant:
                amenities.append('Restaurant')
            # Add other amenities as needed

            properties_with_data.append({
                'id': prop.id,
                'title': prop.name,
                'location': f"{prop.city}, {prop.country}",
                'type': prop.property_type,
                'rating': prop.avg_rating or 0,
                'reviews': prop.review_count,
                'price': prop.min_price or 0,
                'image_url': primary_image_url,
                'amenities': amenities,
                'url': prop.get_absolute_url(),
            })
        
        context['featured_stays'] = properties_with_data
        return context

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True).annotate(
            avg_rating=Avg('reviews__rating')
        )
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(city__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by property type
        property_type = self.request.GET.get('type')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Filter by city
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
            
        return queryset

# views.py - Update PropertyDetailView
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = self.object.room_set.filter(is_available=True)
        context['reviews'] = self.object.reviews.all().order_by('-created_at')
        context['avg_rating'] = self.object.reviews.aggregate(Avg('rating'))['rating__avg']
        
        # Get unique room types
        room_types = self.object.room_set.filter(is_available=True).values(
            'room_type', 'name'
        ).distinct()
        context['room_types'] = room_types
        
        # Generate calendar data for next two months
        today = timezone.now().date()
        next_month = today + timedelta(days=60)
        context['calendar_start'] = today
        context['calendar_end'] = next_month
        
        return context
    

    

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
    



#@method_decorator(login_required, name='dispatch')
class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'vendor':
            messages.error(request, 'Only vendors can add properties.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('properties:vendor_property_detail', kwargs={'pk': self.object.pk})

#@method_decorator(login_required, name='dispatch')
class PropertyUpdateView(UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    
    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('properties:vendor_property_detail', kwargs={'pk': self.object.pk})

@login_required
def add_room(request, property_pk):
    property_obj = get_object_or_404(Property, pk=property_pk, owner=request.user)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.property = property_obj
            room.save()
            messages.success(request, 'Room added successfully!')
            return redirect('properties:vendor_property_detail', pk=property_pk)
    else:
        form = RoomForm()
    
    return render(request, 'properties/room_form.html', {
        'form': form,
        'property': property_obj
    })

#@method_decorator(login_required, name='dispatch')
class RoomUpdateView(UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'properties/room_form.html'
    
    def get_queryset(self):
        # Ensure users can only edit rooms in their properties
        return Room.objects.filter(property__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add property to context for both update and create
        context['property'] = self.object.property if self.object else None
        return context
    
    def get_success_url(self):
        return reverse_lazy('properties:vendor_property_detail', 
                          kwargs={'pk': self.object.property.pk})

@login_required
def add_review(request, property_pk):
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    # Check if user has already reviewed this property
    existing_review = Review.objects.filter(property=property_obj, user=request.user).first()
    if existing_review:
        messages.error(request, 'You have already reviewed this property.')
        return redirect('property_detail', pk=property_pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = property_obj
            review.user = request.user
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect('property_detail', pk=property_pk)
    else:
        form = ReviewForm()
    
    return render(request, 'properties/review_form.html', {
        'form': form, 
        'property': property_obj
    })

#@method_decorator(login_required, name='dispatch')
class VendorPropertyListView(ListView):
    model = Property
    template_name = 'properties/vendor/property_list.html'
    context_object_name = 'properties'
    paginate_by = 10
    
    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'vendor':
            messages.error(request, 'Access denied. Vendor account required.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)



@login_required
def vendor_property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    rooms = property.room_set.all()
    bookings = Booking.objects.filter(room__property=property).order_by('-created_at')
    
    # Calculate statistics
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    total_revenue = bookings.filter(status='confirmed').aggregate(Sum('total_amount'))
    avg_rating = property.reviews.aggregate(Avg('rating'))
    
    context = {
        'property': property,
        'rooms': rooms,
        'bookings': bookings[:5],  # Show only last 5 bookings
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue['total_amount__sum'],
        'avg_rating': avg_rating['rating__avg']
    }
    
    return render(request, 'properties/vendor/property_detail.html', context)
