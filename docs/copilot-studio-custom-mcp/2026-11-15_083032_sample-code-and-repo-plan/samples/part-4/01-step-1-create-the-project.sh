dotnet --version            # 10.0.300 in the local test
dotnet new web -n AIDevMe.OrdersMcp --framework net10.0
cd AIDevMe.OrdersMcp
dotnet add package ModelContextProtocol.AspNetCore --version 2.4.0
