from django.urls import path
from Product_image import views
from .views import contact_view
from .views import form_submission_view
from .views import register_view, login_view, logout_view



urlpatterns = [
    path("", views.Home,name="home"),
    path('item/<slug>/', views.item_detail, name='item_detail'),
    path("shop/",views.shop,name="shop"),
    path("about_us/",views.about_us,name="about_us"),
    path('contact/', contact_view, name="contact"),
    path("", views.Home, name="home"),  # Redirects to home page
    path('submit-form/', form_submission_view, name='submit_form'),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),


]
