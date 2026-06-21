PR Review Bot
Automated GitHub PR review bot using Django, GitHub Webhooks, and Google Gemini AI.
When a developer opens a Pull Request on GitHub, this bot automatically detects it, fetches the code changes, sends them to an AI model for review, and posts the AI-generated feedback directly as a comment on the PR — all without any manual intervention.
How It Works
```
1. Developer opens a Pull Request on GitHub
2. GitHub sends a webhook event to the bot
3. Bot saves the PR details to the database
4. Bot fetches the actual code diff via the GitHub REST API
5. The diff is sent to Google Gemini for review
6. Gemini returns feedback (bugs, improvements, best practices)
7. Feedback is saved to the database
8. Feedback is posted back to the GitHub PR as a comment
```
Features
GitHub OAuth 2.0 — securely connects to a user's GitHub account without ever handling their password
Webhook-driven — reacts to PR events in real time instead of polling GitHub
AI-powered code review — uses Google Gemini to analyze diffs and generate human-quality feedback
Automatic GitHub comments — posts review feedback directly on the Pull Request
REST API — built with Django REST Framework, exposing endpoints for repositories, pull requests, and review history
Tech Stack
Layer	Technology
Backend	Django, Django REST Framework
Database	SQLite
AI	Google Gemini API
GitHub Integration	GitHub REST API, GitHub Webhooks, OAuth 2.0
Local Tunneling (dev)	ngrok
Project Structure
```
pr_boat/
├── core/                  # Django project settings and URL routing
├── reviewbot/
│   ├── models.py           # Repository, PullRequest, ReviewComment, GitHubUser
│   ├── serializers.py      # DRF serializers for the API
│   ├── views.py            # OAuth, webhook handler, AI review, CRUD views
│   ├── urls.py              # App-level routes
│   └── admin.py              # Django admin registrations
├── manage.py
└── requirements.txt
```
Database Models
Repository — tracks connected GitHub repositories
PullRequest — stores PR metadata (title, author, status)
ReviewComment — stores AI-generated feedback and whether it was posted to GitHub
GitHubUser — stores connected users' GitHub usernames and OAuth access tokens
Setup & Installation
1. Clone the repository
```bash
git clone https://github.com/Pankajrajput2451/pr-review-bot.git
cd pr-review-bot
```
2. Create a virtual environment and install dependencies
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```
3. Set up environment variables
Create a `.env` file in the project root:
```
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GEMINI_API_KEY=your_gemini_api_key
```
4. Run migrations
```bash
python manage.py migrate
```
5. Start the server
```bash
python manage.py runserver
```
6. Set up GitHub OAuth App and Webhook
Register an OAuth App at `github.com/settings/developers` and set the callback URL to `<your-domain>/api/github/callback/`
Add a webhook on the target repository pointing to `<your-domain>/api/github/webhook/`, content type `application/json`, subscribed to Pull request events
API Endpoints
Endpoint	Method	Description
`/api/repositories/`	GET, POST	List or create repositories
`/api/pull-requests/`	GET, POST	List or create pull requests
`/api/review-comments/`	GET, POST	List or create review comments
`/api/github/login/`	GET	Redirects to GitHub OAuth consent screen
`/api/github/callback/`	GET	Handles the OAuth callback and stores the access token
`/api/github/webhook/`	POST	Receives GitHub PR webhook events
Author
Pankaj Rajput