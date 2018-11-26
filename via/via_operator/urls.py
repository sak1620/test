from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from via_image import views as i_view

urlpatterns = [
    path('', views.vw_index, name="index"),
    path('vatic/', views.vw_vatic, name="vatic"),
    # path('vatic-side/', views.vw_vatic_sidebar, name="vatic_sidebar"),
    path('annotate/', views.vw_annotate, name="annotate"),
    path('upload/', views.vw_upload_file, name="upload"),
    path('annotateCom/', views.vw_annotate_common, name="annotateCom"),    
    path('save_xml/', views.vw_saveXml, name='save_xml'),  
    path('xml_upload/', views.XmlUploadView.as_view(), name='xml_upload'),   
    path('saveXmlFile/', views.vw_saveXmlFile, name='saveXmlFile'),   
    path('some/', views.vw_some, name="some"),
    path('logout/', views.vw_log, name="logout"),
    # path('login/', auth_views.LoginView.as_view(), name = "login"),
    path('batch_completed/', views.vw_batch_completed, name="batch_completed"),
    path('chart_data_op/', views.vw_chart_data, name="chart_data")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
