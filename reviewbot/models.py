from django.db import models

from django.db import models

class Repository(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    github_repo_id = models.CharField(max_length=100, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner}/{self.name}"
    
    
class PullRequest(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='pull_requests')
    pr_number = models.IntegerField()
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PR #{self.pr_number} - {self.title}"
    
class ReviewComment(models.Model):
    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='comments')
    ai_feedback = models.TextField()
    quality_score = models.IntegerField(null=True, blank=True)
    posted_to_github = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for PR #{self.pull_request.pr_number}" 

class GitHubUser(models.Model):
    github_username = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    connected_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.github_username           
