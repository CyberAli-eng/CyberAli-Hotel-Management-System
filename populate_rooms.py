import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_management.settings')
django.setup()

from hotel.models import Room

# Clear existing rooms (optional reset)
Room.objects.all().delete()

# Define room types with price
room_types = {
    'Single': {'count': 8, 'price': 1000},
    'Double': {'count': 6, 'price': 1800},
    'Suite': {'count': 6, 'price': 2500},
}

room_number = 1

for room_type, details in room_types.items():
    for _ in range(details['count']):
        Room.objects.create(
            room_number=room_number,
            room_type=room_type,
            price=details['price'],
            is_available=True
        )
        room_number += 1

print("✅ Rooms created successfully.")
