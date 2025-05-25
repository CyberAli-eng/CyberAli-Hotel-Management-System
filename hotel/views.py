from django.shortcuts import render, redirect,  get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
from .models import Room, Customer, Bill,FoodOrder, FoodItem
from reportlab.pdfgen import canvas
from decimal import Decimal, InvalidOperation
import csv  

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'hotel/login.html', {'error': 'Invalid credentials'})
    return render(request, 'hotel/login.html')

@login_required
def dashboard(request):
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    current_bookings = Customer.objects.filter(check_out_date__isnull=True).count()
    total_revenue = Bill.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    recent_customers = Customer.objects.order_by('-check_in_date')[:5]
    return render(request, 'hotel/dashboard.html', {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'current_bookings': current_bookings,
        'total_revenue': total_revenue,
        'recent_customers': recent_customers,
    })


@login_required
def book_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        room_type = request.POST.get('room_type')
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_in_date')


        # Get the first available room
        room = Room.objects.filter(room_type=room_type, is_available=True).first()

        if room:
            Customer.objects.create(
                name=name,
                email=email,
                phone=phone,
                room=room,
                check_in_date=check_in_date
            )
            room.is_available = False
            room.save()
            messages.success(request, 'Room booked successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'No available rooms of selected type.')

    return render(request, 'hotel/book_room.html', {
        'room_types': Room.ROOM_TYPES
    })

@login_required
def customers_list(request):
    customers = Customer.objects.all()
    return render(request, 'hotel/customer_list.html', {'customers': customers})

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    # Release room only if customer has not checked out
    if customer.room and not customer.check_out_date:
        customer.room.is_available = True
        customer.room.save()

    customer.delete()
    messages.success(request, "Customer deleted and room released if applicable.")
    return redirect('customer_list')

@login_required
def checkout_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if customer.check_out_date:
        messages.warning(request, "Customer has already checked out.")
        return redirect('dashboard')

    # Set current date as checkout date
    customer.check_out_date = timezone.now().date()

    # Release room
    if customer.room:
        customer.room.is_available = True
        customer.room.save()

    customer.save()

    # Calculate stay duration (minimum 1 day)
    stay_duration = (customer.check_out_date - customer.check_in_date).days
    stay_duration = stay_duration if stay_duration > 0 else 1

    # Calculate food charges
    food_orders = customer.foodorder_set.all()
    food_total = sum(order.total_price() for order in food_orders)

    # Final bill
    room_total = stay_duration * customer.room.price
    total_amount = Decimal(room_total) + Decimal(food_total)

    # Create Bill if not already exists
    Bill.objects.update_or_create(
        customer=customer,
        defaults={
            'room': customer.room,
            'room_charge': room_total,
            'food_charge': food_total,
            'total_amount': total_amount
        }
    )

    messages.success(
        request,
        f"{customer.name} checked out. Room ₹{room_total} + Food ₹{food_total} = ₹{total_amount}"
    )
    return redirect('dashboard')


@login_required
def food_order(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    menu = FoodItem.objects.all()

    if request.method == "POST":
        item_id = request.POST.get("food_item")
        quantity = int(request.POST.get("quantity"))
        food_item = get_object_or_404(FoodItem, id=item_id)

        # ✅ Add price while creating the order
        FoodOrder.objects.create(
            customer=customer,
            food_item=food_item,
            quantity=quantity,
            price=food_item.price
        )
        return redirect('food_order', customer_id=customer.id)

    orders = FoodOrder.objects.filter(customer=customer)
    return render(request, 'hotel/food_order.html', {
        'customer': customer,
        'orders': orders,
        'menu': menu,
    })

@login_required
def generate_bill(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if not customer.check_out_date:
        messages.warning(request, "Customer has not checked out yet.")
        return redirect('customer_list')

    # Safely calculate stay duration
    stay_duration = (customer.check_out_date - customer.check_in_date).days
    stay_duration = max(stay_duration, 1)

    try:
        room_price = Decimal(customer.room.price or 0)
    except (InvalidOperation, TypeError, ValueError):
        room_price = Decimal(0)

    try:
        room_cost = stay_duration * room_price
    except (InvalidOperation, TypeError, ValueError):
        room_cost = Decimal(0)

    # Safe food order total
    food_orders = FoodOrder.objects.filter(customer=customer)
    try:
        food_total = sum(Decimal(order.total_price() or 0) for order in food_orders)
    except (InvalidOperation, TypeError, ValueError):
        food_total = Decimal(0)

    try:
        total_amount = room_cost + food_total
    except (InvalidOperation, TypeError, ValueError):
        total_amount = Decimal(0)

    # Create or update the Bill
    bill, _ = Bill.objects.update_or_create(
        customer=customer,
        defaults={
            'room': customer.room,
            'room_charge': room_cost,
            'food_charge': food_total,
            'total_amount': total_amount
        }
    )

    return render(request, 'hotel/final_bill_summary.html', {
        'customer': customer,
        'room_cost': room_cost,
        'food_total': food_total,
        'total_amount': total_amount,
        'food_orders': food_orders,
        'bill': bill,
    })


@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Mark the room as available
    if customer.room:
        customer.room.is_available = True
        customer.room.save()
    
    customer.delete()
    messages.success(request, "Customer deleted and room made available.")
    return redirect('customer_list')


def export_bill_csv(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    bill = Bill.objects.get(customer=customer)

    food_orders = FoodOrder.objects.filter(customer=customer)
    food_total = sum(order.total_price() for order in food_orders)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{customer.name}_bill.csv"'

    writer = csv.writer(response)
    writer.writerow(['Customer Name', 'Room Number', 'Food Charges', 'Total Amount', 'Date Issued'])
    writer.writerow([customer.name, bill.room.room_number, food_total, bill.total_amount, bill.created_at])

    return response




@login_required
def export_bill_pdf(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    try:
        bill = Bill.objects.get(customer=customer)
    except Bill.DoesNotExist:
        messages.error(request, "Bill not found. Please checkout the customer or generate the bill first.")
        return redirect('dashboard')

    food_orders = FoodOrder.objects.filter(customer=customer)

    # PRINT EVERYTHING
    print("=== DEBUG START ===")
    print("bill.room_charge:", bill.room_charge, type(bill.room_charge))
    print("bill.food_charge:", bill.food_charge, type(bill.food_charge))
    print("bill.total_amount:", bill.total_amount, type(bill.total_amount))
    print("bill.room.room_number:", bill.room.room_number, type(bill.room.room_number))
    print("bill.room.price:", bill.room.price, type(bill.room.price))
    print("=== DEBUG END ===")

    try:
        food_total = Decimal(str(bill.food_charge or '0'))
        total_amount = Decimal(str(bill.total_amount or '0'))
    except (InvalidOperation, ValueError, TypeError) as e:
        return HttpResponse(f"<h2>Error: {e}</h2><p>One of the fields has invalid decimal value. Fix it in DB.</p>")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{customer.name}_bill.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Customer Name: {customer.name}")
    p.drawString(100, 780, f"Room Number: {bill.room.room_number}")
    p.drawString(100, 760, f"Food Charges: ₹{food_total:.2f}")
    p.drawString(100, 740, f"Total Amount: ₹{total_amount:.2f}")
    p.drawString(100, 720, f"Date Issued: {bill.created_at.strftime('%Y-%m-%d')}")
    p.showPage()
    p.save()

    return response
def custom_logout(request):
    logout(request)
    return redirect('login')



