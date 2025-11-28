from django.urls import path
from . import views

urlpatterns = [
    # صفحات HTML
    path('', views.index, name='index'),
    path('smtp/', views.smtp_view, name='smtp'),
    path('pop3/', views.pop3_view, name='pop3'),
    path('imap/', views.imap_view, name='imap'),
    path('b64/', views.b64_view, name='b64'),

    # API endpoints
    path('api/send_smtp_email/', views.send_smtp_email, name='send_smtp_email'),
    path('api/pop3_login/', views.pop3_login, name='pop3_login'),
    path('api/imap_login/', views.imap_login, name='imap_login'),
    path('api/b64_action/', views.b64_action, name='b64_action'),
]
