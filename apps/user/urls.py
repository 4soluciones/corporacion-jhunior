from django.urls import path, include
from django.contrib.auth.decorators import login_required
from apps.user.views import users_list, UserList, user_create, user_update, user_save, authorization

urlpatterns = [
    # path('users/', login_required(users_list), name='users'),
    path('users/', login_required(UserList.as_view()), name='users'),
    path('user_create/', login_required(user_create), name='user_create'),
    path('user_update/<int:pk>/', login_required(user_update), name='user_update'),
    path('user_save/', login_required(user_save), name='user_save'),
    path('authorization/', login_required(authorization), name='authorization'),
]