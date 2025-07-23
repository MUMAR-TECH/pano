from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from bookings.models import Booking
from .models import Property, Room, Review
from .forms import PropertyForm, RoomForm, ReviewForm

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

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = self.object.room_set.filter(is_available=True)
        context['reviews'] = self.object.reviews.all().order_by('-created_at')
        context['avg_rating'] = self.object.reviews.aggregate(Avg('rating'))['rating__avg']
        return context

@method_decorator(login_required, name='dispatch')
class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.userprofile.user_type != 'vendor':
            messages.error(request, 'Only vendors can add properties.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class PropertyUpdateView(UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    
    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

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
            return redirect('property_detail', pk=property_pk)
    else:
        form = RoomForm()
    
    return render(request, 'properties/room_form.html', {
        'form': form, 
        'property': property_obj
    })

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

@method_decorator(login_required, name='dispatch')
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