from django.contrib import admin
from django.urls import path

from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', PasswordResetConfirmView.as_view(), name='password_reset_complete'),
    path('reset-password/sent/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/', PasswordResetView.as_view())
]
