
from django.contrib import admin
from django.urls import path, include
import expenses.views as ev

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/signup/', ev.signup, name='signup'),
    path( 'accounts/activate/<uidb64>/<token>/', ev.activate, name='activate' ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('expenses.urls')),
]