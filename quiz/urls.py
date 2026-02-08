from django.urls import path
from . import views

urlpatterns = [
    path('modules/', views.module_list, name='module_list'),
    path('start/<int:module_id>/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/<int:question_index>/', views.take_quiz, name='take_quiz'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
]
