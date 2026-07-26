# azure storage emulator
docker run -d -p 10000:10000 -p 10001:10001 --name azurite mcr.microsoft.com/azure-storage/azurite

docker rm -f azurite

docker run -d --name azurite -p 10000:10000 -p 10001:10001 `
    -p 10002:10002 mcr.microsoft.com/azure-storage/azurite azurite `
        --blobHost 0.0.0.0 --queueHost 0.0.0.0 --tableHost 0.0.0.0 --skipApiVersionCheck
       
# start the azurite container if it is not running
docker start azurite

# dts emulator
docker rm -f dts-emulator

docker run -d --name dts-emulator -p 8080:8080 -p 8082:8082 mcr.microsoft.com/dts/dts-emulator:latest

docker start dts-emulator

# build the solution
dotnet build Ai-Agent-Travel-Plan-Orchestrator.sln

# build the function project
dotnet build TravelPlannerFunctions.csproj

# run the function project
dotnet run --project TravelPlannerFunctions.csproj

# clean the function project, which basically deletes the bin and obj folders, so that the next build is a clean build
dotnet clean TravelPlannerFunctions.csproj

# restore the function project, which restores the nuget packages
dotnet restore TravelPlannerFunctions.csproj

# build the function project
dotnet build TravelPlannerFunctions.csproj

# run the function project
dotnet run --project TravelPlannerFunctions.csproj

Invoke-RestMethod -Method Post -Uri "http://localhost:7252/api/travel-planner" -ContentType "application/json" -Body '{
    "userName": "John Doe",
    "preferences": "Cultural experiences and outdoor activities",
    "durationInDays": 7,
    "budget": "Moderate, around $3000 total",
    "travelDates": "May 15-22, 2026",
    "specialRequirements": "Free WiFi, mild shellfish allergy"
    }'


Get-CimInstance Win32_Process | `
    Where-Object { $_.Name -eq "dotnet.exe" -and $_.CommandLine -match "TravelPlannerFunctions|Functions.Worker|azure-functions" } | `
    Select-Object ProcessId, Name, CommandLine | Format-Table -AutoSize

Invoke-RestMethod -Method Get -Uri "http://localhost:7252/api/travel-planner/status/91bc08825b174d1a81701f3e3ea6749c"

Invoke-RestMethod -Method Post -Uri "http://localhost:7252/api/travel-planner/approve/91bc08825b174d1a81701f3e3ea6749c" -ContentType "application/json" -Body '{
"approved": true,
"comments": "Looks good, please proceed with booking."
}'

# starting the front end
npm run dev --prefix Frontend

# then, start the debug using the launch.json configuration in VS Code, 
# which will launch the Edge browser and navigate to http://localhost:3000