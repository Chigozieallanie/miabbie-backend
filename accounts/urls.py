from django.urls import path
from .views import SignupView, VerifyView, LoginView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify/', VerifyView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
     
]
