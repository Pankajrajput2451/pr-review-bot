from django.contrib import admin
from .models import Repository, PullRequest, ReviewComment, GitHubUser


admin.site.register(Repository)
admin.site.register(PullRequest)
admin.site.register(ReviewComment)
admin.site.register(GitHubUser)
