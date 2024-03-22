from django.urls import path,include
from . import views


urlpatterns = [
    path('Login',views.login_view,name='login_view'),
    path('Register',views.register_user,name='register_user'),
    path('Logout',views.logout_view,name='logout_view'),
    path('index',views.index,name='index'),
    path('upload_files', views.upload_files, name='upload_files'),
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('update_book/<int:book_id>/', views.update_book, name='update_book'),
    path('delete_video/<int:video_id>/', views.delete_video, name='delete_video'),
    path('ask_questions', views.ask_questions, name='ask_questions'),
    path('learn_help_html', views.learn_help_html, name='learn_help_html'),
    path('learn_help', views.LearnHelp, name= 'learn_help'),
    path('load_book', views.LoadBook, name='load_book'),
    path('quiz_generator', views.quiz_generator, name='quiz_generator'),
    path('test_eval', views.TestEval, name= 'test_eval'),
    path('mindspace_html',views.mindspace_html,name='mindspace_html'),
    path('mindspace',views.Mindspace,name='mindspace'),
    path('vision',views.Vision,name='vision'),
    path('vision_stream',views.Vision_Stream,name='vision'),
    path('vision_html',views.vision_html,name='vision_html'),
    path('solver',views.Solve_Question,name='solver'),
    path('youtube_ai_html', views.youtube_ai_html, name= 'youtube_ai_html'),
    path('upload_video', views.upload_video, name='upload_video'),
    path('load_video', views.LoadVideo, name= 'load_video'),
    path('youtube_ai', views.YoutubeAi, name='youtube_ai')
]