from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

app_name = 'useraccounts'
urlpatterns = [
    # ex /stabbitystyle/
    #path('<str:username>/', views.login, name='login'),
    # ex /useraccounts/signup/
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(template_name='useraccounts/login.html'), name="login"),
    path('logout/', views.logoutView, name='logout')
]