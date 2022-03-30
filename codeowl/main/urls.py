from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('', views.main_page, name='home'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', views.profile, name='profile'),
    path('registration/', views.registration, name='registration'),
    path('change_password/', views.change_password, name='change_password'),
    path('price/', views.price, name='price'),
    path('confirm/<str:token>/', views.confirm, name='confirm'),
    path('api/', views.api, name='api'),
    path('validate/', views.val, name='val'),
    path('download/', views.file_download, name="download")
]
