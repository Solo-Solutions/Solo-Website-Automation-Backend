from django.urls import path

from .views import (
    get_routes,
    MyTokenObtainPairView, 
    refresh_access_token,
    get_user_session,
    logout_user,
    create_user,
    update_user_name,
    update_profile_picture,
    delete_profile_picture,  
    request_email_change,
    confirm_email_change,
    request_password_reset, 
    reset_password,
    get_users_empresa,
)

urlpatterns = [
    path('', get_routes, name='api_root'),
    
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', refresh_access_token, name='token_refresh'),
    path('token/get-user-session/', get_user_session, name='get_user_session'),
    path('token/logout/', logout_user, name='logout_user'),
    
    path('create-user/', create_user, name='create-user'),
    path('update-user-name/', update_user_name, name='update_user_name'),
    path('update-profile-picture/', update_profile_picture, name='update_profile_picture'),
    path('delete-profile-picture/', delete_profile_picture, name='delete_profile_picture'),

    path('request-email-change/', request_email_change, name='request-email-change'),
    path('confirm-email-change/', confirm_email_change, name='confirm-email-change'),

    path('request-password-reset/', request_password_reset, name='request-password-reset'),
    path('reset-password/', reset_password, name='reset-password'),

    path('get-users-empresa/', get_users_empresa, name='get-users-empresa')
]