from django.urls import path
from . import views

urlpatterns = [

    # ------------------------------
    # Home + Authentication
    # ------------------------------
    path('', views.index, name='index'),
    path('register/', views.index, name='register'),  # Optional landing

    # Login/Logout
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # ------------------------------
    # User Registration (Role-based)
    # ------------------------------
    path('register/seller/', views.seller_register, name='seller_register'),
    path('register/buyer/', views.buyer_register, name='buyer_register'),
    path('register/branch/', views.branchuser_register, name='branchuser_register'),

    # ------------------------------
    # Dashboards
    # ------------------------------
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('branch/<int:branch_id>/dashboard/', views.branch_dashboard, name='branch_dashboard'),

    # ------------------------------
    # Store Management
    # ------------------------------
    path('stores/', views.store_list, name='store_list'),
    path('store/create/', views.store_create, name='store_create'),
    path('store/<int:store_id>/edit/', views.store_edit, name='store_edit'),
    path('store/<int:store_id>/delete/', views.store_delete, name='store_delete'),
    path('store/<int:store_id>/branches/', views.view_branches, name='view_branches'),
    path('store/<int:store_id>/create-branch-and-user/', views.create_branch_and_user, name='create_branch_and_user'),


    # ------------------------------
    # Branch Management
    # ------------------------------
    path('branch/<int:branch_id>/edit/', views.branch_edit, name='branch_edit'),
    path('branch/<int:branch_id>/delete/', views.branch_delete, name='branch_delete'),
    path('branch/<int:branch_id>/products/', views.branch_products, name='branch_products'),
    path('branch/<int:branch_id>/add-product/', views.add_product_direct_branch, name='add_product_direct_branch'),

    # ------------------------------
    # Product CRUD & Display
    # ------------------------------
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('branch/<int:branch_id>/product/add/', views.add_product, name='add_product'),
    path('store/<int:store_id>/add-product/', views.add_product_store, name='add_product_store'),

    # Product modals
    path('store/<int:store_id>/add-product-store-modal/', views.add_product_store_modal, name='add_product_store_modal'),
    path('store/<int:store_id>/add-product-branch-modal/', views.add_product_branch_modal, name='add_product_branch_modal'),
    path('store/<int:store_id>/move-products-modal/', views.move_products_modal, name='move_products_modal'),

    # ------------------------------
    # Product Display to Buyers & Public
    # ------------------------------
    path('store/<int:company_id>/', views.product, name='product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('store/<int:store_id>/products/', views.buyer_store_products, name='buyer_store_products'),

    # Seller website product view
    path('sellers/<int:store_id>/products/', views.seller_website, name='seller_website'),

    # ------------------------------
    # Static Content Pages
    # ------------------------------
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),



    # ------------------------------
    # For Buyers to see Products
    # ------------------------------
    path('store/<int:store_id>/products/', views.buyer_store_products, name='buyer_store_products'),
    path("products/all/", views.all_products, name="all_products"),


    # ------------------------------
    # Cart
    # ------------------------------
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),


    # ------------------------------
    # CheckOut urls
    # ------------------------------
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/history/', views.order_history, name='order_history'),

]
