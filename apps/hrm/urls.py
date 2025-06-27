from django.urls import path, include
from apps.hrm.views import SubsidiaryList, subsidiary_create, subsidiary_update, subsidiary_save, PersonList, \
    person_create, person_update, person_save, get_person, update_person, insert_person
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('subsidiaries/', login_required(SubsidiaryList.as_view()), name='subsidiaries'),
    path('subsidiary_create/', login_required(subsidiary_create), name='subsidiary_create'),
    path('subsidiary_update/<int:pk>/', login_required(subsidiary_update), name='subsidiary_update'),
    path('subsidiary_save/', login_required(subsidiary_save), name='subsidiary_save'),

    path('persons/', login_required(PersonList.as_view()), name='persons'),
    path('person_create/', login_required(person_create), name='person_create'),
    path('person_update/<int:pk>/', login_required(person_update), name='person_update'),
    path('person_save/', login_required(person_save), name='person_save'),
    path('get_person/', login_required(get_person), name='get_person'),
    path('insert_person/', login_required(insert_person), name='insert_person'),
    path('update_person/', login_required(update_person), name='update_person'),

]
