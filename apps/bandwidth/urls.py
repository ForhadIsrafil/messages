# from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('callback', views.CallBackView.as_view(), name='callback'),
    path('last-10-history-list', views.Last10MessageHistoryView.as_view(), name='history_list'),
    path('single-history/<int:message_id>', views.SingleHistoryView.as_view(), name='single_history'),
    path('change-callback-url', views.ChangeCallBackUrlView.as_view(), name='callback_url'),
    path('get-notifications', views.GetNotification.as_view(), name='get_notifications'),

]
