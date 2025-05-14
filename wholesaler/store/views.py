from django.shortcuts import render, redirect, get_object_or_404 ,HttpResponse
from .models import Store, Buyer, Seller, Product, ProductImage, User,Branch,BranchUser,Category, Cart, CartItem , Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import ProductForm, ProductImageFormSet, BranchUserCreationForm, StoreForm, BuyerRegistrationForm, SellerRegistrationForm, BranchForm
from django.forms import modelformset_factory
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import random,string
from django.contrib.auth.forms import AuthenticationForm
from django import forms


# Create your views here.

def index(request):
    return render (request,"index.html")

def store_list(request):
    stores = Store.objects.all().order_by('-created_at')
    is_seller = False
    if request.user.is_authenticated:
        is_seller = Seller.objects.filter(user=request.user).exists()
    return render(request, 'store_list.html', {'stores': stores, 'is_seller': is_seller})

@login_required
def store_create(request):
    if not Seller.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("<b style = 'background-color:black; color:white; font-size:30px; display:flex; justify-content:center; padding:30px; border-radius:20px; margin:20px;'>Only sellers can create a store.</b>")

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            return redirect('store_list')
    else:
        form = StoreForm()
    return render(request, 'store_form.html', {'form': form})

@login_required
def store_edit(request,store_id):
    store = get_object_or_404(Store , pk=store_id , user= request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES,instance=store)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            return redirect('store_list')
    else:
        form = StoreForm(instance=store)
    return render (request , 'store_form.html',{'form' : form})


@login_required
def store_delete(request, store_id):
    store = get_object_or_404(Store, pk = store_id, user = request.user)
    if request.method == 'POST':
        store.delete()
        return redirect ('store_list')
    return render (request , 'store_confirm_delete.html',{'store' : store})


@login_required
def product(request, company_id):
    store = get_object_or_404(Store, pk=company_id)
    branches = Branch.objects.filter(store=store)
    categories = Category.objects.all()

    # Category filter
    category_id = request.GET.get('category')

    # Main Store Products (branch=None)
    if category_id and category_id != 'all':
        main_store_products = Product.objects.filter(store=store, branch__isnull=True, category_id=category_id)
    else:
        main_store_products = Product.objects.filter(store=store, branch__isnull=True)

    paginator = Paginator(main_store_products, 5)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Branch Products with Pagination
    branch_products = []
    for branch in branches:
        if category_id and category_id != 'all':
            branch_product_list = Product.objects.filter(branch=branch, category_id=category_id)
        else:
            branch_product_list = Product.objects.filter(branch=branch)

        branch_paginator = Paginator(branch_product_list, 5)
        branch_page_number = request.GET.get(f'branch_page_{branch.id}')
        branch_page_obj = branch_paginator.get_page(branch_page_number)

        branch_products.append((branch, branch_page_obj))

    return render(request, "products.html", {
        'store': store,
        'branches': branches,
        'categories': categories,
        'selected_category': category_id,
        'page_obj': page_obj,
        'branch_products': branch_products,
        'product_form': ProductForm(),
        'branches': Branch.objects.filter(store=store),
        'categories': Category.objects.all(),

    })



@login_required
def add_product(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    store = branch.store  # Get store from branch

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none())

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save(commit=False)
            product.store = store
            product.branch = branch
            product.save()

            for form in formset.cleaned_data:
                if form:
                    ProductImage.objects.create(product=product, image=form['image'])

            return redirect('branch_dashboard', branch_id=branch.id)
    else:
        product_form = ProductForm()
        formset = ProductImageFormSet(queryset=ProductImage.objects.none())

    return render(request, 'product_form.html', {
        'product_form': product_form,
        'formset': formset,
        'branch': branch,
    })



@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, store__user=request.user)
    ProductImageFormSet = modelformset_factory(ProductImage, fields=('image',), extra=1, can_delete=True)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.filter(product=product))

        if product_form.is_valid() and formset.is_valid():
            updated_product = product_form.save(commit=False)

            # ✅ Fix: Keep branch if exists
            updated_product.branch = product.branch

            # ✅ Auto-update stock status based on stock quantity
            updated_product.stock_status = True if updated_product.stock_quantity > 0 else False

            updated_product.save()

            # ✅ Handle product images (save new, delete old)
            for form in formset:
                if form.cleaned_data:
                    if form.cleaned_data.get('DELETE'):
                        if form.instance.pk:
                            form.instance.delete()
                    elif form.cleaned_data.get('image'):
                        img = form.save(commit=False)
                        img.product = updated_product
                        img.save()
            return redirect('product', company_id=product.store.id)

    else:
        product_form = ProductForm(instance=product)
        formset = ProductImageFormSet(queryset=ProductImage.objects.filter(product=product))

    return render(request, 'product_form.html', {
        'product_form': product_form,
        'formset': formset,
        'product': product,
        'action': 'Edit',
        'categories': product.store.categories.all() if hasattr(product.store, 'categories') else [],
    })



@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, store__user=request.user)
    company_id = product.store.id  # ✅ correct
    if request.method == 'POST':
        product.delete()
        return redirect('product', company_id=company_id)
    return render(request, 'product_confirm_delete.html', {'product': product})


@login_required
def add_product_store(request, store_id):
    store = get_object_or_404(Store, pk=store_id)

    if request.method == 'POST':
        name = request.POST.get("name")
        price = request.POST.get("price")
        description = request.POST.get("description", "")
        stock_quantity = request.POST.get("stock_quantity")
        category_id = request.POST.get("category_id")
        branch_id = request.POST.get("branch_id", "")
        images = request.FILES.getlist("images")

        # Validate required fields
        if not all([name, price, stock_quantity, category_id]):
            messages.error(request, "❌ Please fill all required fields.")
            return redirect("product", company_id=store.id)

        # Get related models
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            messages.error(request, "❌ Invalid category.")
            return redirect("product", company_id=store.id)

        branch = Branch.objects.filter(pk=branch_id).first() if branch_id else None

        # Create product manually
        product = Product.objects.create(
            store=store,
            branch=branch,
            name=name,
            price=price,
            description=description,
            stock_quantity=stock_quantity,
            stock_status=int(stock_quantity) > 0,
            category=category
            # product_id auto-generated
        )

        # Handle image uploads
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        messages.success(request, "✅ Product added successfully.")
        return redirect("product", company_id=store.id)

    return redirect("product", company_id=store.id)


class SellerAwareLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        try:
            seller = Seller.objects.get(user=user)
            store = Store.objects.filter(user=user).first()
            if store:
                return reverse('product', kwargs={'company_id': store.id})
            else:
                return reverse('store_list')  # fallback if no store yet
        except Seller.DoesNotExist:
            return reverse('buyer_dashboard')


def seller_website(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    products = Product.objects.filter(store=store)
    return render(request, 'seller_website.html', {'store': store, 'products': products})


def view_branches(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    branches = store.branches.all()
    return render(request, 'view_branches.html', {'store': store, 'branches': branches})


@login_required
def branch_edit(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    # ✅ Allow only the store owner OR the assigned branch user
    is_store_owner = request.user == branch.store.user
    is_branch_user = hasattr(request.user, "branchuser") and request.user.branchuser.branch == branch

    if not (is_store_owner or is_branch_user):
        messages.error(request, "❌ You are not authorized to edit this branch.")
        return redirect("seller_dashboard")

    if request.method == "POST":
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Branch updated successfully.")
            return redirect("seller_dashboard")
    else:
        form = BranchForm(instance=branch)

    return render(request, "edit_branch.html", {"form": form, "branch": branch})



def branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    # 🛡️ Security Check: only the assigned BranchUser can delete
    if not request.user.is_authenticated or not hasattr(request.user, 'branchuser') or request.user.branchuser.branch.id != branch_id:
        return HttpResponseForbidden("You are not allowed to delete this branch.")

    store_id = branch.store.id
    branch.delete()
    return redirect('view_branches', store_id=store_id)

def branch_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user is a branch user
            try:
                branch_user = BranchUser.objects.get(user=user)
                login(request, user)
                return redirect('branch_dashboard', branch_id=branch_user.branch.id)
            except BranchUser.DoesNotExist:
                # Not a branch user
                return render(request, 'branch_login.html', {'error': 'Invalid branch user.'})
        else:
            return render(request, 'branch_login.html', {'error': 'Invalid credentials.'})

    return render(request, 'branch_login.html')


def generate_product_id():
    """Auto-generate product ID like PRD-XXXXXX"""
    random_number = ''.join(random.choices(string.digits, k=6))
    return f"PRD-{random_number}"

# 1️⃣ Add Product to Main Store
@login_required
def add_product_store_modal(request, store_id):
    if request.method == 'POST':
        store = get_object_or_404(Store, id=store_id)

        name = request.POST.get('name')
        price = request.POST.get('price')
        stock_quantity = int(request.POST.get('stock_quantity'))
        stock_status = True if stock_quantity > 0 else False
        category_id = request.POST.get('category_id')

        category = get_object_or_404(Category, id=category_id)

        product = Product.objects.create(
            store=store,
            branch=None,  # ✅ Main Store: No branch
            name=name,
            price=price,
            stock_status=stock_status,
            stock_quantity=stock_quantity,
            product_id=generate_product_id(),
            category=category,
        )

        # Handle images
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        return redirect('product', company_id=store_id)

    return redirect('product', company_id=store_id)


# 2️⃣ Add Product to Branch
@login_required
def add_product_branch_modal(request, store_id):
    if request.method == 'POST':
        store = get_object_or_404(Store, id=store_id)
        branch_id = request.POST.get('branch_id')
        branch = get_object_or_404(Branch, id=branch_id, store=store)

        name = request.POST.get('name')
        price = request.POST.get('price')
        stock_quantity = int(request.POST.get('stock_quantity'))
        stock_status = True if stock_quantity > 0 else False
        category_id = request.POST.get('category_id')

        category = get_object_or_404(Category, id=category_id)

        product = Product.objects.create(
            store=store,
            branch=branch,  # ✅ IMPORTANT: Correctly set branch here!
            name=name,
            price=price,
            stock_status=stock_status,
            stock_quantity=stock_quantity,
            product_id=generate_product_id(),
            category=category,
        )

        # Handle images
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return redirect('product', company_id=store_id)

    return redirect('product', company_id=store_id)


# 3️⃣ Move All Products from Main Store to a Branch
@login_required
def move_products_modal(request, store_id):
    if request.method == 'POST':
        store = get_object_or_404(Store, id=store_id)
        branch_id = request.POST.get('branch_id')
        branch = get_object_or_404(Branch, id=branch_id, store=store)

        # Move all products from Main Store (branch=None) to selected branch
        products = Product.objects.filter(store=store, branch__isnull=True)
        products.update(branch=branch)

        return redirect('product', company_id=store_id)

    return redirect('product', company_id=store_id)


def buyer_store_products(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # Fetch categories linked to this store's products
    category_ids = Product.objects.filter(store=store, branch=None).values_list('category', flat=True).distinct()
    categories = Category.objects.filter(id__in=category_ids)

    selected_category = request.GET.get('category', 'all')

    if selected_category != 'all':
        products = Product.objects.filter(store=store, category_id=selected_category)
    else:
        products = Product.objects.filter(store=store)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'buyer_store_products.html', {
        'store': store,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    images = product.images.all()

    # Fetch Related Products (same category, in stock, excluding current)
    related_products = Product.objects.filter(
        category=product.category,
        stock_status=True
    ).exclude(id=product.id)[:5]

    return render(request, 'product_detail.html', {
        'product': product,
        'images': images,
        'related_products': related_products,
    })


@login_required
def branch_products(request, branch_id):
    branch_user = get_object_or_404(BranchUser, user=request.user)

    if branch_user.branch.id != branch_id:
        return HttpResponseForbidden("You are not allowed to view this branch.")

    branch = branch_user.branch
    products = Product.objects.filter(branch=branch)
    categories = Category.objects.all().order_by('name')   # ✅ ADD THIS LINE

    return render(request, 'branch_products.html', {
        'branch': branch,
        'products': products,
        'branch_user': branch_user,
        'categories': categories,    # ✅ SEND IT HERE
    })

def branch_logout(request):
    logout(request)
    return redirect('store_list')

def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    return render(request, 'contact_us.html')

@login_required
def add_product_direct_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_quantity = int(request.POST.get('stock_quantity'))
        category_id = request.POST.get('category_id')

        category = get_object_or_404(Category, id=category_id)

        # Auto-update stock status based on stock quantity
        stock_status = True if stock_quantity > 0 else False

        # Create Product
        product = Product.objects.create(
            store=branch.store,    # Important: Link to store also
            branch=branch,
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            stock_status=stock_status,
            product_id=generate_product_id(),  # Auto-generated product ID
            category=category,
        )

        # Handle multiple images
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        messages.success(request, "✅ Product added successfully to this branch!")
        return redirect('branch_dashboard', branch_id=branch.id)

    else:
        return redirect('branch_dashboard', branch_id=branch.id)
    

# ----------------------------
# Universal Login View (role-based)
# ----------------------------

def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')

            if hasattr(user, 'seller') and user.seller.role == 0:
                return redirect(next_url or 'seller_dashboard')
            elif hasattr(user, 'branchuser') and user.branchuser.role == 1:
                return redirect(next_url or 'branch_dashboard', branch_id=user.branchuser.branch.id)
            elif hasattr(user, 'buyer') and user.buyer.role == 2:
                return redirect(next_url or 'buyer_dashboard')
            else:
                messages.error(request, "No valid role assigned.")
                return redirect('user_login')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html", {'form': form})

# ----------------------------
# Registration Views
# ----------------------------

def seller_register(request):
    if request.method == "POST":
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Seller registered successfully.")
            return redirect(f"{reverse('user_login')}?next={request.path}")
    else:
        form = SellerRegistrationForm()
    return render(request, 'registration/register.html', {'form': form, 'user_type': 'Seller'})

def buyer_register(request):
    if request.method == "POST":
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Buyer registered successfully.")
            return redirect(f"{reverse('user_login')}?next={request.path}")
    else:
        form = BuyerRegistrationForm()
    return render(request, 'registration/register.html', {'form': form, 'user_type': 'Buyer'})


def branchuser_register(request):
    if request.method == "POST":
        form = BranchUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Branch User registered successfully.")
            return redirect(f"{reverse('user_login')}?next={request.path}")
    else:
        form = BranchUserCreationForm()
    return render(request, 'registration/register.html', {'form': form, 'user_type': 'Branch User'})


# ----------------------------
# Dashboards
# ----------------------------

@login_required
def seller_dashboard(request):
    if hasattr(request.user, 'seller') and request.user.seller.role == 0:
        stores = Store.objects.filter(user=request.user)
        branch_form = BranchForm()
        branch_user_form = BranchUserCreationForm()

        return render(request, 'seller_dashboard.html', {
            'stores': stores,
            'branch_form': branch_form,
            'branch_user_form': branch_user_form
        })

    return redirect(f"{reverse('user_login')}?next={request.path}")

@login_required
def buyer_dashboard(request):
    if hasattr(request.user, 'buyer') and request.user.buyer.role == 2:
        stores = Store.objects.all()
        return render(request, 'buyer_dashboard.html', {'stores': stores})
    return redirect(f"{reverse('user_login')}?next={request.path}")

@login_required
def branch_dashboard(request, branch_id):
    if hasattr(request.user, 'branchuser') and request.user.branchuser.role == 1:
        branch_user = request.user.branchuser
        if branch_user.branch.id == branch_id:
            products = Product.objects.filter(branch=branch_user.branch)
            return render(request, 'branch_dashboard.html', {
                'branch': branch_user.branch,
                'products': products
            })
    return redirect(f"{reverse('user_login')}?next={request.path}")


# ----------------------------
# Optional: Create Branch User directly (for sellers)
# ----------------------------

@login_required
def create_branch_and_user(request, store_id):
    store = get_object_or_404(Store, pk=store_id)

    if request.method == "POST":
        branch_form = BranchForm(request.POST)
        branch_user_form = BranchUserCreationForm(request.POST)

        if branch_form.is_valid() and branch_user_form.is_valid():
            # Create the branch
            branch = branch_form.save(commit=False)
            branch.store = store
            branch.save()

            # Create the user
            username = branch_user_form.cleaned_data['username']
            password = branch_user_form.cleaned_data['password']
            email = branch_user_form.cleaned_data['email']
            phone = branch_user_form.cleaned_data['phone_number']

            user = User.objects.create_user(username=username, password=password)

            # Assign the user to the branch
            BranchUser.objects.create(
                user=user,
                branch=branch,
                email=email,
                phone_number=phone,
                role=1
            )

            # Link the branch back to the user
            branch.user = user
            branch.save()

            messages.success(request, "✅ Branch and user assigned successfully.")
            return redirect("seller_dashboard")

    else:
        branch_form = BranchForm()
        branch_user_form = BranchUserCreationForm()

    return render(request, "create_branch_and_user.html", {
        "branch_form": branch_form,
        "branch_user_form": branch_user_form,
        "store": store
    })
    

# ----------------------------
# Logout View
# ----------------------------

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect(f"{reverse('user_login')}?next={request.path}")


# ----------------------------
# Buyer Products View
# ----------------------------
def buyer_store_products(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    branches = Branch.objects.filter(store=store)
    categories = Category.objects.all()
    selected_category = request.GET.get("category")

    # Fetch main store products
    if selected_category and selected_category != "all":
        main_store_products = Product.objects.filter(store=store, branch__isnull=True, category_id=selected_category)
    else:
        main_store_products = Product.objects.filter(store=store, branch__isnull=True)

    paginator = Paginator(main_store_products, 6)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    # Fetch branch products per branch (optional)
    branch_products = []
    for branch in branches:
        if selected_category and selected_category != "all":
            branch_items = Product.objects.filter(branch=branch, category_id=selected_category)
        else:
            branch_items = Product.objects.filter(branch=branch)

        branch_products.append((branch, branch_items))

    return render(request, "buyer_store_products.html", {
        "store": store,
        "branches": branches,
        "categories": categories,
        "selected_category": selected_category,
        "page_obj": page_obj,
        "branch_products": branch_products
    })


#---------------------#
# All Prodcuts Navbar #
#---------------------#
def all_products(request):
    categories = Category.objects.all()
    selected_category = request.GET.get("category")

    if selected_category and selected_category != "all":
        products = Product.objects.filter(category_id=selected_category)
    else:
        products = Product.objects.all()

    paginator = Paginator(products, 9)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "all_products.html", {
        "products": page_obj,
        "categories": categories,
        "selected_category": selected_category
    })

#------------#
# Cart Views #
#------------#

@login_required
def add_to_cart(request, product_id):
    if not hasattr(request.user, 'buyer'):
        return redirect(f"{reverse('user_login')}?next={request.path}")

    product = get_object_or_404(Product, id=product_id)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity = 1
    else:
        cart_item.quantity += 1

    cart_item.save()  # ✅ Always save

    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart_detail.html', {'cart': cart})


@login_required
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')

def update_cart_quantity(request, product_id):
    try:
        cart = Cart.objects.get(user=request.user)
        item = CartItem.objects.get(cart=cart, product_id=product_id)
        action = request.POST.get('action')

        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            item.quantity -= 1
            if item.quantity <= 0:
                item.delete()
            else:
                item.save()

    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            cart_items = cart.items.all()

            # 🔍 Stock Validation
            for item in cart_items:
                if item.quantity > item.product.stock_quantity:
                    messages.error(
                        request,
                        f"❌ Not enough stock for {item.product.name}. Only {item.product.stock_quantity} left."
                    )
                    return redirect('checkout')

            # ✅ Proceed with Order Placement
            order = form.save(commit=False)
            order.user = request.user
            order.total = sum(item.product.price * item.quantity for item in cart_items)
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

                # 🔻 Reduce Stock
                item.product.stock_quantity -= item.quantity
                item.product.stock_status = item.product.stock_quantity > 0
                item.product.save()

            cart.items.all().delete()
            messages.success(request, f"✅ Order #{order.id} placed successfully!")
            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm()  # ✅ make sure form is defined for GET requests

    return render(request, 'checkout.html', {'cart': cart, 'form': form})



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'phone', 'payment_method']
        widgets = {
            'payment_method': forms.Select(choices=[('COD', 'Cash on Delivery')]),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})