"Activating python environment"
& env\scripts\activate

"Django - Collectstatic"
& python manage.py collectstatic --noinput

"Deploying to google cloud"
& gcloud app deploy --quiet

"Clearing site cache"
Invoke-WebRequest -Uri "https://mokstats.appspot.com/ajax/clear_cache/"

Read-Host -Prompt "Finished deployment - press enter to exit"