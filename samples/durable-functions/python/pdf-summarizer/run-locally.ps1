docker run -d -p 8080:8080 -p 8082:8082 mcr.microsoft.com/dts/dts-emulator:latest

docker stop $(docker ps -q --filter ancestor=mcr.microsoft.com/dts/dts-emulator:latest)

az storage container create --connection-string "UseDevelopmentStorage=true" --name input

az storage container create --connection-string "UseDevelopmentStorage=true" --name output

az storage blob upload --connection-string "UseDevelopmentStorage=true" --container-name input --name agents.pdf --file "C:\temp\the-open-group-guide-bpg-ai-agents-agentic-ai-v0.1-draft.pdf"

az storage blob upload --connection-string "UseDevelopmentStorage=true" --container-name input --name fassis-linkedin-profile.pdf --file "C:\temp\fassis-linkedin-profile.pdf" --overwrite true

az storage blob delete --connection-string "UseDevelopmentStorage=true" --container-name input --name fassis-linkedin-profile.pdf

azurite --skipApiVersionCheck