from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Vendor,Customer
from apps.product.models import Product, ProductImage
from django.contrib.auth.models import User

from .forms import ProductForm, ProductImageForm
# from apps.product.models import Product

# def frontpage(request):
#     newest_products = Product.objects.all()[0:8]

#     return render(request, 'core/frontpage.html', {'newest_products': newest_products})



def user_login(request):
    
    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username')
        password = request.POST.get('password')
        loginid = request.POST.get('loginid')

        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)

        # If we have a user
        if loginid == "vendor":
            if user:
                #Check it the account is active
                if user.is_active:
                    # Log the user in.
                    login(request,user)
                    # Send the user back to some page.
                    # In this case their homepage.
                    return redirect('vendor_admin')
                    #return HttpResponseRedirect(reverse('core/frontpage.html'))
                else:
                    # If account is not active:
                    return HttpResponse("Your account is not active.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username,password))
                return HttpResponse("Invalid login details supplied.")
        else:
            if user:
                #Check it the account is active
                if user.is_active:
                    # Log the user in.
                    login(request,user)
                    # Send the user back to some page.
                    # In this case their homepage.
                    return redirect('vendors')
                    #return HttpResponseRedirect(reverse('core/frontpage.html'))
                else:
                    # If account is not active:
                    return HttpResponse("Your account is not active.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username,password))
                return HttpResponse("Invalid login details supplied.")


    else:
        #Nothing has been provided for username or password.
        return render(request, 'vendor/login.html', {})

def become_vendor(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        loginid = request.POST.get('loginid')
        # password2 = request.POST.get('confirm_password')
        name = request.POST.get('username')
        if loginid == "vendor":
            # raw_password = password1
            user = User.objects.create_user(name, email, password)
            vendor = Vendor(name=name, email=email, password=password, created_by=user)
            vendor.save()
            login(request, user)
            return redirect('add_product')
        else:
            cus= User.objects.create_user(name, email, password)
            customer = Customer(name=name, email=email, password=password, created_by=cus)
            customer.save()
            login(request,cus)
            return redirect('vendors')

    return render(request, 'vendor/login.html', {})

@login_required
def vendor_admin(request):
    vendor = request.user.vendor
    products = vendor.products.all()
    orders = vendor.orders.all()

    for order in orders:
        order.vendor_amount = 0
        order.vendor_paid_amount = 0
        order.fully_paid = True

        for item in order.items.all():
            if item.vendor == request.user.vendor:
                if item.vendor_paid:
                    order.vendor_paid_amount += item.get_total_price()
                else:
                    order.vendor_amount += item.get_total_price()
                    order.fully_paid = False

    return render(request, 'vendor/vendor_admin.html', {'vendor': vendor, 'products': products, 'orders': orders})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.slug = slugify(product.title)
            product.save()

            return redirect('vendor_admin')
    else:
        form = ProductForm()
    
    return render(request, 'vendor/add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    vendor = request.user.vendor
    product = vendor.products.get(pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        image_form = ProductImageForm(request.POST, request.FILES)

        if image_form.is_valid():
            productimage = image_form.save(commit=False)
            productimage.product = product
            productimage.save()

            return redirect('vendor_admin')

        if form.is_valid():
            form.save()

            return redirect('vendor_admin')
    else:
        form = ProductForm(instance=product)
        image_form = ProductImageForm()
    
    return render(request, 'vendor/edit_product.html', {'form': form, 'image_form': image_form, 'product': product})

@login_required
def edit_vendor(request):
    vendor = request.user.vendor

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')

        if name:
            vendor.created_by.email = email
            vendor.created_by.save()

            vendor.name = name
            vendor.save()

            return redirect('vendor_admin')
    
    return render(request, 'vendor/edit_vendor.html', {'vendor': vendor})

def vendors(request):
    vendors = Vendor.objects.all()

    return render(request, 'vendor/vendors.html', {'vendors': vendors})

def vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)

    return render(request, 'vendor/vendor.html', {'vendor': vendor})