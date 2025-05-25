# --- admin.py ---
from django.contrib import admin
from .models import Room, Customer, Bill

admin.site.register(Room)
admin.site.register(Customer)
admin.site.register(Bill)
