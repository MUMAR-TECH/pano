from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserProfileForm, VendorProfileForm, UserSignUpForm, VendorSignUpForm
from .models import UserProfile, VendorProfile

class UserSignUpView(CreateView):
    form_class = UserSignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('account_login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please log in.')
        return response

class VendorSignUpView(CreateView):
    form_class = VendorSignUpForm
    template_name = 'accounts/vendor_signup.html'
    success_url = reverse_lazy('account_login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Vendor account created successfully! Please verify your email.')
        return response

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    try:
        vendor_profile = request.user.vendorprofile
    except VendorProfile.DoesNotExist:
        vendor_profile = None

    context = {
        'user_profile': request.user.userprofile,
        'vendor_profile': vendor_profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_profile.user_type == 'vendor':
            try:
                vendor_profile = request.user.vendorprofile
                vendor_form = VendorProfileForm(request.POST, instance=vendor_profile)
            except VendorProfile.DoesNotExist:
                vendor_form = None
        else:
            vendor_form = None

        if user_form.is_valid() and (vendor_form is None or vendor_form.is_valid()):
            user_form.save()
            if vendor_form:
                vendor_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=user_profile)
        if user_profile.user_type == 'vendor':
            try:
                vendor_profile = request.user.vendorprofile
                vendor_form = VendorProfileForm(instance=vendor_profile)
            except VendorProfile.DoesNotExist:
                vendor_form = None
        else:
            vendor_form = None

    context = {
        'user_form': user_form,
        'vendor_form': vendor_form,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def vendor_dashboard(request):
    if request.user.userprofile.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('home')

    try:
        vendor_profile = request.user.vendorprofile
        properties = vendor_profile.user.property_set.all()
    except VendorProfile.DoesNotExist:
        vendor_profile = None
        properties = []

    context = {
        'vendor_profile': vendor_profile,
        'properties': properties,
    }
    return render(request, 'accounts/vendor_dashboard.html', context)