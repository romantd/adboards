from django.urls import path
from .views import other_page
from .views import index
from .views import BBLoginView
from .views import BBLogoutView
from .views import profile
from .views import ChangeUserInfoView
from .views import BBPasswordChangeView
from .views import RegisterUserView, RegisterDoneView   
from .views import user_activate
from .views import DeleteUserView
from .views import by_category
from .views import detail
from .views import profile_ad_detail
from .views import profile_ad_add
from .views import profile_ad_change, profile_ad_delete
from .views import start_conversation, ConversationListView, ConversationDetailView, send_message
app_name = 'main'
urlpatterns = [
    path('start_conversation/<int:ad_id>/', start_conversation, name='start_conversation'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:pk>/send_message/', send_message, name='send_message'),
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register', RegisterUserView.as_view(), name='register'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/change/<int:pk>/', profile_ad_change, name='profile_ad_change'),
    path('accounts/profile/delete/<int:pk>/', profile_ad_delete, name='profile_ad_delete'),
    path('accounts/profile/add/', profile_ad_add, name='profile_ad_add'),
    path('accounts/profile/<int:pk>/', profile_ad_detail, name='profile_ad_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('account/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('<int:category_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_category, name='by_category'),
    path('page/<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]
