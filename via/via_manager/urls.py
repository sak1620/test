from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.vw_ManagerIndex, name="via_manager_index"),
    path('some/', views.vw_some, name="some"),
    # path('dashboard/', views.vw_dashboardManager, name="dashboard-manager"),
    path('basic-upload/', views.BasicUploadView.as_view(), name='basic_upload'),
    path('image-upload/', views.ImageUploadView.as_view(), name='image_upload'),
    # path('dashboard-upload/', views.vw_model_form_upload, name="dashboard-manager"),
    path('batch_show/', views.vw_batch_files, name="batch_files"),
    path('batch_show_images/', views.vw_batch_images, name="batch_images"),
    path('batch_upload/', views.vw_save_batch, name="save_batch"),
    path('batch_image_upload/', views.vw_save_image_batch, name="vw_save_image_batch"),
    path('create_batch/', views.vw_create_batch, name="create_batch"),
    path('create_image_batch/', views.vw_create_image_batch, name="create_image_batch"),
    path('select_op/', views.vw_select_operator, name="select_op"),
    path('batch/', views.vw_batch_upload, name="batch"),
    path('update_batch/', views.vw_update_batch, name="batch_update"),
    path('update_batch_name/', views.vw_update_batch_name, name="update_batch_name"),
    path('batch_edit/', views.vw_batch_edit, name="batch_edit"),
    path('batch_update/', views.vw_batch_update, name="batch_update"),
    path('batch_delete/', views.vw_batch_delete, name="batch_delete"),
    path('completed_batch/', views.vw_completed_batch, name="completed_batch"),
    # path('completed_batch/', views.vw_completed_batch, name="completed_batch"),
    #Saving XML file
    path('save_xml/', views.vw_saveXml, name='save_xml'),   
    path('chart_data/', views.vw_chart_data, name="chart_data"),
    path('download/', views.vw_download, name='download'),   


 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
