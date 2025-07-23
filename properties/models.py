from django.db import models
from accounts.models import User
from django.urls import reverse

class PropertyType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Property(models.Model):
    PROPERTY_TYPES = (
        ('hotel', 'Hotel'),
        ('lodge', 'Lodge'),
        ('motel', 'Motel'),
        ('guesthouse', 'Guest House'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    description = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Amenities
    wifi = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    restaurant = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    spa = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('property_detail', kwargs={'pk': self.pk})
    
    @property
    def min_price(self):
        rooms = self.room_set.all()
        if rooms:
            return min(room.price_per_night for room in rooms)
        return 0

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.property.name} - Image"

class Room(models.Model):
    ROOM_TYPES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('twin', 'Twin'),
        ('suite', 'Suite'),
        ('family', 'Family'),
        ('deluxe', 'Deluxe'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    total_rooms = models.PositiveIntegerField(default=1)
    
    # Room amenities
    air_conditioning = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    tv = models.BooleanField(default=False)
    mini_bar = models.BooleanField(default=False)
    room_service = models.BooleanField(default=False)
    
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.property.name} - {self.name}"

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')
    caption = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.room.name} - Image"

class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('property', 'user')
    
    def __str__(self):
        return f"{self.property.name} - {self.rating} stars"