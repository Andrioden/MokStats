"Activating python environment"
& env\scripts\activate

"Starting..."
python manage.py runserver

Read-Host -Prompt "Web server stopped - press enter to exit"