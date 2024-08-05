from django.urls import path
from . import views

urlpatterns = [
    path('exam/', views.exam_create_api_view),
    path('subject/', views.subject_list_create_api_view),
    path('question/create/', views.question_create_api_view),
    path('exams/', views.get_exams_api_view),
    path('exams/<int:exam_id>/', views.question_get_based_on_exam_view),
    path('calendars/', views.list_create_calendar_view),
    path('questions/', views.get_all_questions_from_bank),
    path('questions/advice/', views.advice_question_list_view)
]
