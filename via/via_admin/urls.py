from django.conf.urls import url, include
from . import views
from django.urls import path, re_path
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', views.vw_admin_index, name='admin_main'),
    url(r'^user/create/$', views.vw_create_user),
    url(r'^user_edit/', views.vw_user_edit, name='user_edit'),
    url(r'^user_update/', views.vw_user_update, name='user_update'),
    url(r'^user_delete/', views.vw_user_delete, name='operator'),
    url(r'^toggle_button/', views.vw_toggle_button, name='toggle_button'),
    # url(r'^label_create/', views.Labelcreate.as_view(), name='add_label'),
    # url(r'^label_create/', views.vw_label_create, name='label_create'),
    # url(r'^toggle_label/', views.vw_toggle_label, name='toggle_label'),
]