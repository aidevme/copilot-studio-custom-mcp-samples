dotnet build                 # Build succeeded. 0 Warning(s) 0 Error(s)
dotnet run --launch-profile http
curl http://localhost:5201/health     # Healthy
