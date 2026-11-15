# AIDevMe Order Management API. Build context: src/order-api (the project and data/seed.json).
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /repo
COPY src/AIDevMe.OrderApi/AIDevMe.OrderApi.csproj src/AIDevMe.OrderApi/
RUN dotnet restore src/AIDevMe.OrderApi/AIDevMe.OrderApi.csproj
COPY data/ data/
COPY src/ src/
RUN dotnet publish src/AIDevMe.OrderApi/AIDevMe.OrderApi.csproj -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_HTTP_PORTS=8080
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "AIDevMe.OrderApi.dll"]
