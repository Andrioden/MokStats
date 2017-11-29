"Activating python environment"
& env\scripts\activate

"Django - Collectstatic"
& python manage.py collectstatic --noinput

"Deploying to google cloud"
& gcloud app deploy --quiet

Read-Host -Prompt "Finish deployment - press enter to exit"