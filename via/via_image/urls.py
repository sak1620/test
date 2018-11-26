from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    path('',views.vw_index, name="index"),
    path('logout/', views.vw_log, name="logout"),
    # path('login/', auth_views.LoginView.as_view(), name = "login"),
    # path('login/', views.vw_login_user, name="login")
    re_path(r'^$', views.index, name='index'),
    re_path(r'^segment/(?P<image_id>\d+)/$', views.segment, name='segment'),
    re_path(r'^review/(?P<image_id>\d+)/$', views.review, name='review'),
    re_path(r'^question/(?P<image_id>\d+)/$',views.question, name="question"),
    re_path(r'^question_review/(?P<image_id>\d+)/$',views.question_review, name="question_review"),
    re_path(r'^review/(?P<image_id>\d+)/$', views.review, name='review'),
    re_path(r'^addlabel/', views.addlabel, name='addlabel')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)