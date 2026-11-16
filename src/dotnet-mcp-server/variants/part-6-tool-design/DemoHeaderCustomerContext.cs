using AIDevMe.OrdersMcp;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpContextAccessor();
builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<OrderStore>();
builder.Services.AddScoped<ICustomerContext, DemoHeaderCustomerContext>();

builder.Services
    .AddMcpServer()
    .WithHttpTransport(options => options.Stateless = true)
    .WithTools<OrderTools>();

var app = builder.Build();
app.MapMcp("/mcp");
app.Run();

// Local demo only: Part 5 replaces this with the customer from a validated token.
public sealed class DemoHeaderCustomerContext(IHttpContextAccessor accessor) : ICustomerContext
{
    public string? CustomerId =>
        accessor.HttpContext?.Request.Headers["AIDevMe-Demo-Customer"].FirstOrDefault();
}
