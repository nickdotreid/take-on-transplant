from django.contrib import admin
from django.urls import path

from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView

from patients.views import PatientStoryView
from patients.views import PatientStoryList

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', PasswordResetConfirmView.as_view(), name='password_reset_complete'),
    path('reset-password/sent/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/', PasswordResetView.as_view()),
    path('story/<patient_id>', PatientStoryView.as_view(), name='patient-story'),
    path('', PatientStoryList.as_view(), name='patient-story-list')
]
