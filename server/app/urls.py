from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.forms import CharField
from django.forms import EmailField
from django.urls import path

from patients.views import PatientStoryView
from patients.views import PatientStoryTableOfContentsView
from patients.views import PatientStoryList
from resources.views import ResourceListView
from resources.views import ResourceDetailView
from resources.views import AllResourcesView

class EmailAuthenticationForm(AuthenticationForm):
    
    email = CharField(
        label = 'Email',
        required = True
    )
    username = CharField(
        label = 'Username',
        required = False
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()
        if user and password:
            self.user_cache = authenticate(self.request, username=user.username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
            return self.cleaned_data
        else:
            raise self.get_invalid_login_error()

login_view = LoginView.as_view(
    authentication_form = EmailAuthenticationForm,
    template_name='login.html'
)
logout_view = LogoutView.as_view(
    next_page = '/login/'
)

urlpatterns = [
    # override admin login logout
    path('admin/login/', login_view),
    path('admin/logout/', logout_view),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset-password/sent/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/', PasswordResetView.as_view(), name='password_reset'),
    path('all-resources/', AllResourcesView.as_view(), name='resources-all'),
    path('resources/<resource_slug>', ResourceDetailView.as_view(), name='resource-detail'),
    path('resources/', ResourceListView.as_view(), name='resource-list'),
    path('story/<patient_id>/story/<story_id>/', PatientStoryTableOfContentsView.as_view(), name='patient-story'),
    path('story/<patient_id>/', PatientStoryView.as_view(), name='patient-story'),
    path('', PatientStoryList.as_view(), name='patient-story-list')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
