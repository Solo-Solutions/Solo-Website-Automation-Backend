from django.urls import path

from . import views
from .views import MyTokenObtainPairView


urlpatterns = [
    path('', views.api_overview, name='api_root'),
    
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('token/refresh/', views.refresh_access_token, name='token_refresh'),
    path('token/logout/', views.logout_user, name='logout_user'),
    
    path('create-user/', views.create_user, name='create_user'),
    path('update-user/', views.update_user, name='update_user'),

    path('request-email-change/', views.request_email_change, name='request_email_change'),
    path('confirm-email-change/', views.confirm_email_change, name='confirm-email-change'),

    path('request-password-reset/', views.request_password_reset, name='request-password-reset'),
    path('reset-password/', views.reset_password, name='reset-password'),

    path('get-user/<uuid:id>/', views.get_user, name='get_user'),
    path('get-user-session/', views.get_user_session, name='get_user_session'),
    path('get-users-empresa/', views.get_users_empresa, name='get-users-empresa')
]