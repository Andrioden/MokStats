$cloud_sql_path = "C:\bin\cloud_sql_proxy.exe"

"Starting proxy using $cloud_sql_path"
& $cloud_sql_path -instances="mokstats:europe-west1:mokstatsmysql"=tcp:3307

Read-Host -Prompt "Proxy stopped - press enter to exit"