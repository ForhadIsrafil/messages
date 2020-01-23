from django.urls import path
from . import views

urlpatterns = [
    path('sms', views.SmsView.as_view({'post': 'create'}), name='sms'),
    path('number', views.NumberView.as_view(), name='number'),
    path('forward-message/<int:message_id>', views.ForwardSmsView.as_view({'post': 'create'}), name='forward_message'),
    path('number-list', views.NumberListView.as_view({'get': 'list'}), name='number_list'),
    path('delete-number/<int:number_id>', views.DeleteNumberView.as_view({'delete': 'destroy'}), name='delete_number'),

    path('single-chat-history', views.SingleChatHistory.as_view(), name='single_chat_history'),
    path('accountnumbers/<str:e164>/conversations/<str:number>', views.P2PChatHistory.as_view({'get': 'list'}), name='p2p_chat_history'),
    path('contact-list', views.ContactList.as_view(), name='contact_list'),
    path('accountnumbers/<str:e164>/contacts', views.SingleNumberContactList.as_view(), name='single_number_contact_list'),
    path('external-number', views.ExternalNumberView.as_view({'post': 'create', 'get': 'list'}),
         name='external_number'),
    path('single-external-number/<str:number>', views.SingleExternalView.as_view({'delete': 'destroy', 'get': 'list'}),
         name='single_external_number'),

    path('upload', views.UploadView.as_view()),


]
