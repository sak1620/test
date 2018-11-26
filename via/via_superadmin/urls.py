from django.urls import path
from . import views

urlpatterns = [
    path('', views.vw_get, name='superadmin_main'),
    path('admin/create/', views.vw_create_admin, name='createadmin'),
    path('admin_edit/', views.vw_admin_edit, name='admin_edit'),
    path('admin_update/', views.vw_admin_update, name='admin_update'),
    path('admin_delete/', views.vw_admin_delete, name='user_delete'),
    path('toggle_button/', views.vw_toggle_button, name='toggle_button'),
    path('upload_logo/', views.vw_upload_logo, name='upload_logo'),
    
     ]