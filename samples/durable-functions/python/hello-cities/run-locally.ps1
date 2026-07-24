docker run -d -p 8080:8080 -p 8082:8082 mcr.microsoft.com/dts/dts-emulator:latest

curl -X POST http://localhost:7071/api/StartChaining

curl -X POST http://localhost:7071/api/StartFanOutFanIn