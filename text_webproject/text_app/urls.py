from django.urls import path
from text_app import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'text_app'

urlpatterns = [
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Built-in function
    path('token/refresh', views.RefreshTokenView.as_view()),  # Custom function
    path('login', views.LoginApi.as_view()),
    path('snippet/create', views.SnippetListCreateView.as_view()),
    path('snippet/list', views.SnippetListCreateView.as_view()),
    path('snippet/detail/<int:snippet_id>', views.SnippetDetailView.as_view(), name='snippet-detail'),
    path('snippet/update/<int:snippet_id>', views.SnippetUpdateView.as_view(), name='snippet-update'),
    path('snippet/delete', views.SnippetDeleteView.as_view(), name='snippet-delete'),
    path('tag/list', views.TagListView.as_view(), name='tag-list'),
    path('snippet/list_by_tag/<int:tag_id>', views.SnippetListByTag.as_view(), name='snippet-by-tag'),
]
