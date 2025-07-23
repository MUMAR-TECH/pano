from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Profile, User, VendorProfile

from .forms import HostRegistrationForm, ResetPasswordForm, ForgotPasswordForm, UserLoginForm, UserCreationForm, UserProfileForm, UserRegistrationForm, OTPVerificationForm, VendorProfileForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login, logout, authenticate

import random
from datetime import timedelta

#---------- home views ----------------------#
"""def home(request):
    from events.models import Event, Category
    from store.models import Product
    from django.utils import timezone
    #import datetime
    # Get current time with proper timezone handling
    now = timezone.now()

    # Get upcoming events
    categories = Category.objects.all().order_by('id')
    featured_events = Event.objects.all().order_by('-date')[:12]
    # Get featured products with stock > 0
    featured_products = Product.objects.filter(stock__gt=0).select_related('event__organizer').order_by('-created_at')[:4]
    
    # Get featured membership tiers
    featured_tiers = MembershipTier.objects.filter(is_active=True).select_related('bundle', 'host', 'host__profile').order_by('price')[:3]
    # Get featured products
    featured_products = Product.objects.all().order_by('-created_at')[:3]
    
    return render(request, 'home.html', {
        'categories':categories,
        'featured_events': featured_events,
        'featured_products': featured_products,
        'featured_tiers': featured_tiers
    })
"""

def home(request):
    return render(request, 'home.html')
#---------- Authentication Views ----------#

def register_host(request):
    if request.method == "POST":
        form = HostRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.role = 'vendor'
            user.is_active = False  # Prevent login until email verification
            user.otp_code = str(random.randint(100000, 999999))  # Generate OTP
            user.save()

            # Send OTP Email
            send_mail(
                'OTP Verification for Host Registration',
                f'Your OTP Code is {user.otp_code}. Use this to verify your email.',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )

            request.session['email'] = user.email  # Store email for OTP verification
            return redirect('accounts:verify_host_otp')  # Redirect to OTP verification page

    else:
        form = HostRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})
    

def verify_host_otp(request):
    email = request.session.get('email')
    if not email:
        return redirect('accounts:register_host')

    user = get_object_or_404(User, email=email)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if user.otp_code == otp:
                user.is_active = True
                user.otp_code = None  # Clear OTP after verification
                user.save()
                login(request, user)  # Automatically log in the user
                messages.success(request, 'Account verified and logged in successfully!')
                
                try:
                    profile = user.profile
                    if not profile.is_profile_complete:
                        return redirect('accounts:complete_vendor_profile')
                except Profile.DoesNotExist:
                    # If profile doesn't exist, create one and redirect to complete it
                    Profile.objects.create(user=user)
                    return redirect('accounts:complete_vendor_profile')

                # Redirect based on user role
                if user.role == 'vendor':
                    return redirect('accounts:vendor_dashboard')
                elif user.role == 'customer':
                    return redirect('accounts:customer_dashboard')
                else:
                    return redirect('accounts:home')
            else:
                messages.error(request, 'Invalid OTP. Try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'accounts/verify_host_otp.html', {'form': form})


def verify_otp(request):
    email = request.session.get('email')
    if not email:
        return redirect('accounts:register')

    user = User.objects.get(email=email)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if user.otp_code == otp:
                user.is_active = True
                user.otp_code = None  # Clear OTP after verification
                user.save()
                login(request, user)  # Automatically log in the user
                messages.success(request, 'Account verified and logged in successfully!')
                
                try:
                    profile = user.profile
                    if not profile.is_profile_complete:
                        return redirect('accounts:complete_profile')
                except Profile.DoesNotExist:
                    # If profile doesn't exist, create one and redirect to complete it
                    Profile.objects.create(user=user)
                    return redirect('accounts:complete_profile')

                # Redirect based on user role
                if user.role == 'vendor':
                    return redirect('accounts:host_dashboard')
                elif user.role == 'customer':
                    return redirect('accounts:user_dashboard')
                else:
                    return redirect('accounts:home')

            else:
                messages.error(request, 'Invalid OTP. Try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'accounts/verify_otp.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Prevent login until OTP verification
            user.otp_code = str(random.randint(100000, 999999))  # Generate OTP
            user.save()

            # Send OTP Email
            send_mail(
                'OTP Verification',
                f'Your OTP Code is {user.otp_code}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            request.session['email'] = user.email  # Store email in session for OTP verification
            return redirect('accounts:verify_otp')  # Add namespace here

    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})




def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user:
                login(request, user)
                messages.success(request, 'Login successful!')

                # Check if profile exists and is complete
                if user.role == "Customer":
                    try:
                        profile = user.profile
                        if not Profile.is_profile_complete:
                            return redirect('accounts:complete_profile')
                    except Profile.DoesNotExist:
                        # If profile doesn't exist, create one and redirect to complete it
                        Profile.objects.create(user=user)
                        return redirect('accounts:complete_profile')
                    
                elif user.role == "Vendor" :
                    try:
                        profile = user.profile
                        if not VendorProfile.is_profile_complete:
                            return redirect('accounts:complete_vendor_profile')
                    except VendorProfile.DoesNotExist:
                        # If profile doesn't exist, create one and redirect to complete it
                        VendorProfile.objects.create(user=user)
                        return redirect('accounts:complete_vendor_profile')
                else:
                    return redirect('accounts:home')

                # Redirect based on user role
                if user.role == 'vendor':
                    return redirect('accounts:host_dashboard')
                elif user.role == 'customer':
                    return redirect('accounts:user_dashboard')
                else:
                    return redirect('accounts:home')

            else:
                messages.error(request, 'Invalid email or password.')

    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})



def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('accounts:login')

class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    success_message = "Password reset instructions have been sent to your email."

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

##################

class ForgotPasswordView(PasswordResetView):
    template_name = 'accounts/forgot_password.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    form_class = ForgotPasswordForm

class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm


@login_required
def complete_profile(request):
    user = request.user
    now = timezone.now()
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            profile.is_profile_complete = True
            profile.save()
            messages.success(request, "Profile updated successfully!")
            if user.role == 'vendor':
                return redirect('accounts:host_dashboard')
            elif user.role == 'customer':
                return redirect('accounts:user_dashboard')
            else:
                return redirect('accounts:home')
            
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/complete_profile.html', {'form': form})

@login_required
def complete_vendor_profile(request):
    try:
        vendor_profile = VendorProfile.objects.get(user=request.user)
    except VendorProfile.DoesNotExist:
        vendor_profile = VendorProfile.objects.create(user=request.user)

    if request.method == "POST":
        form = VendorProfileForm(request.POST, instance=vendor_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_profile_complete = True
            profile.save()
            messages.success(request, "Vendor profile completed successfully!")
            return redirect('accounts:vendor_dashboard')
    else:
        form = VendorProfileForm(instance=vendor_profile)
        
    return render(request, 'accounts/complete_vendor_profile.html', {'form': form})

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})




#---------------------------------------------------------------
#                Dashboard Views
#---------------------------------------------------------------
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from properties.models import Property, Room
from bookings.models import Booking
from datetime import timedelta

@login_required
def vendor_dashboard(request):
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('home')
    
    # Get vendor's properties
    properties = Property.objects.filter(owner=request.user)
    
    # Get recent bookings
    recent_bookings = Booking.objects.filter(
        room__property__owner=request.user
    ).select_related('user', 'room', 'room__property').order_by('-created_at')[:5]
    
    # Calculate statistics
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    monthly_stats = Booking.objects.filter(
        room__property__owner=request.user,
        created_at__gte=thirty_days_ago,
        status='confirmed'
    ).aggregate(
        total_bookings=Count('id'),
        total_revenue=Sum('total_amount'),
        avg_rating=Avg('room__property__reviews__rating')
    )
    
    context = {
        'properties': properties,
        'recent_bookings': recent_bookings,
        'monthly_stats': monthly_stats,
        'total_properties': properties.count(),
        'total_rooms': Room.objects.filter(property__owner=request.user).count(),
    }
    
    return render(request, 'accounts/vendor/dashboard.html', context)