import time
from django.shortcuts import render, redirect,HttpResponse
from .models import FullShop,ContactMessage
from django.shortcuts import get_object_or_404
from .forms import ContactForm
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def Home(request):
    item = FullShop.objects.all()
    return render(request,'index.html',{'item' : item})

# New Table
def shop(request):
    query = request.GET.get('item_name')
    if query:
        item = FullShop.objects.filter(name__icontains=query)
    else:
        item = FullShop.objects.all()
    return render(request, 'shop.html', {'item': item})
  # Shop Page

def item_detail(request, slug):
    item = get_object_or_404(FullShop, slug=slug)
    return render(request, 'item_detail.html', {'item': item})

def about_us(request):
    return render(request,'about_us.html')  # About Page


def contact_view(request):  
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            record = ContactMessage.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                message=form.cleaned_data["message"]
            )

            # Send email from pm4190157@gmail.com to pavantester123@gmail.com
            send_mail(
                subject="New Contact Form Submission",
                message=f"Name: {record.name}\nEmail: {record.email}\nMessage: {record.message}",
                from_email="pm4190157@gmail.com",  # Sender email
                recipient_list=["pm4190157@gmail.com"],  # Recipient email
                fail_silently=False,
            )

            return redirect("home")  # Redirect after submission

    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

# Function to send email dynamically
def send_email_notification(name, email, message):
    subject = "New Form Submission"
    body = f"New form submitted:\n\nName: {name}\nEmail: {email}\nMessage: {message}"
    sender = "ambikatraders@gmail.com"
    recipients = ["pm4190157@gmail.com"]

    send_mail(subject, body, sender, recipients, fail_silently=False)

# Form Submission View
def form_submission_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        send_email_notification(name, email, message)  # Trigger email on submission

        return HttpResponse("Form submitted successfully!")
    

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])  # Hash password
            user.save()
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid credentials!"})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def add_to_cart(request, product_id):
    # Logic to add the item to the cart
    return redirect("login.html")




def cart_view(request):
    return render(request, "cart.html")  # Make sure you have a 'cart.html' template!
