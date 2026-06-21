from rest_framework import generics
from .models import Repository, PullRequest, ReviewComment,GitHubUser
from .serializers import RepositorySerializer, PullRequestSerializer, ReviewCommentSerializer
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from .models import GitHubUser
from google import genai

class RepositoryListCreateView(generics.ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer


class PullRequestListCreateView(generics.ListCreateAPIView):
    queryset = PullRequest.objects.all()
    serializer_class = PullRequestSerializer


class ReviewCommentListCreateView(generics.ListCreateAPIView):
    queryset = ReviewComment.objects.all()
    serializer_class = ReviewCommentSerializer

def github_login(request):
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&scope=repo"
    )
    return redirect(github_auth_url)

def github_callback(request):
    code = request.GET.get('code')

    token_url = "https://github.com/login/oauth/access_token"
    response = requests.post(
        token_url,
        data={
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
        },
        headers={'Accept': 'application/json'}
    )

    token_data = response.json()
    access_token = token_data.get('access_token')

    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_data = user_response.json()
    github_username = user_data.get('login')

    GitHubUser.objects.update_or_create(
        github_username=github_username,
        defaults={'access_token': access_token}
    )

    return HttpResponse(f"Connected as: {github_username}")
def get_ai_review(diff_text):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""
You are an experienced code reviewer. Review the following code diff and give short, helpful feedback.
Point out bugs, bad practices, or improvements if any. Keep it concise.

Diff:
{diff_text}
"""

    response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)

    return response.text

def post_comment_to_github(repo_data, pr_number, comment_text, token):
    comment_url = f"https://api.github.com/repos/{repo_data['owner']['login']}/{repo_data['name']}/issues/{pr_number}/comments"

    response = requests.post(
        comment_url,
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        },
        json={'body': comment_text}
    )

    return response.status_code


@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        payload = json.loads(request.body)

        if 'pull_request' in payload:
            repo_data = payload['repository']
            pr_data = payload['pull_request']

            repository, created = Repository.objects.update_or_create(
                github_repo_id=repo_data['id'],
                defaults={
                    'name': repo_data['name'],
                    'owner': repo_data['owner']['login'],
                }
            )

            PullRequest.objects.update_or_create(
                repository=repository,
                pr_number=pr_data['number'],
                defaults={
                    'title': pr_data['title'],
                    'author': pr_data['user']['login'],
                    'status': payload['action'],
                }
            )

            print(f"PR Saved: #{pr_data['number']} - {pr_data['title']}")

            # ---- NAYA CODE YAHAN SE SHURU ----

            # Step 1: Repository owner ka token database se nikalo
            try:
                github_user = GitHubUser.objects.get(github_username=repo_data['owner']['login'])
                token = github_user.access_token
            except GitHubUser.DoesNotExist:
                print("Is repo owner ka token nahi mila, diff fetch nahi kar sakte")
                return HttpResponse("Webhook received but no token found", status=200)

            # Step 2: GitHub se PR ka diff maango
            diff_url = f"https://api.github.com/repos/{repo_data['owner']['login']}/{repo_data['name']}/pulls/{pr_data['number']}"
            
            diff_response = requests.get(
                diff_url,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/vnd.github.v3.diff'
                }
            )

            diff_text = diff_response.text
            print("PR Ka Diff Mila:")
            print(diff_text)
            # ---- NAYA CODE: AI Review Lena ----
            ai_feedback = get_ai_review(diff_text)
            print("AI Ka Feedback:")
            print(ai_feedback)
            # ---- NAYA CODE KHATAM ----
            pull_request_obj = PullRequest.objects.get(
                repository=repository,
                pr_number=pr_data['number']
            )

            ReviewComment.objects.create(
                pull_request=pull_request_obj,
                ai_feedback=ai_feedback,
                quality_score=0,
                posted_to_github=False
            )

        print("Feedback database mein save ho gaya!")

# ---- NAYA CODE: GitHub Pe Comment Post Karna ----
        status_code = post_comment_to_github(
            repo_data=repo_data,
            pr_number=pr_data['number'],
            comment_text=ai_feedback,
            token=token
            )

        if status_code == 201:
            print("Comment GitHub pe successfully post ho gaya!")
                
# Database mein bhi update kar do ki post ho gaya
            ReviewComment.objects.filter(
                pull_request=pull_request_obj,
                ai_feedback=ai_feedback
                ).update(posted_to_github=True)
        else:
                print(f"Comment post nahi ho paya. Status code: {status_code}")
# ---- NAYA CODE KHATAM ----

            # ---- NAYA CODE YAHAN KHATAM ----

        return HttpResponse("Webhook received successfully", status=200)

    return HttpResponse("Only POST allowed", status=405)

