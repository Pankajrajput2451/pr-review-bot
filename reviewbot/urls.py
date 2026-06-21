from django.urls import path
from .views import (
    RepositoryListCreateView,
    PullRequestListCreateView,
    ReviewCommentListCreateView,
    github_login,
    github_callback,
    github_webhook,
)

urlpatterns = [
    path('repositories/', RepositoryListCreateView.as_view(), name='repository-list-create'),
    path('pull-requests/', PullRequestListCreateView.as_view(), name='pullrequest-list-create'),
    path('review-comments/', ReviewCommentListCreateView.as_view(), name='reviewcomment-list-create'),
    path('github/login/', github_login, name='github-login'),
    path('github/callback/', github_callback, name='github-callback'),
    path('github/webhook/', github_webhook, name='github-webhook'),
    
]