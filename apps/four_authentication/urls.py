from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.OktaSignup.as_view({'post': 'create'}), name='signup'),
    path('signin', views.OktaSignin.as_view({'post': 'create'}), name='signin'),
    path('signout', views.OktaLogout.as_view({'delete': 'destroy'}), name='logout'),
    path('active-account/<str:userid>', views.ActivateUserAccount.as_view({'post': 'create'}), name='activate_account'),
]
