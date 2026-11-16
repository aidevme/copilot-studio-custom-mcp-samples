using Azure.Monitor.OpenTelemetry.AspNetCore;
using AIDevMe.OrdersMcp.Data;
using AIDevMe.OrdersMcp.Resources;
using AIDevMe.OrdersMcp.Tools;
using ModelContextProtocol.AspNetCore;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);

// Structured JSON logs: Container Apps sends stdout to Log Analytics.
builder.Logging.ClearProviders();
builder.Logging.AddJsonConsole(o => o.IncludeScopes = true);

// Optional: traces, metrics and logs to Application Insights when a connection string is set.
if (!string.IsNullOrEmpty(builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"]))
{
    builder.Services.AddOpenTelemetry().UseAzureMonitor();
    builder.Services.ConfigureOpenTelemetryTracerProvider(t => t.AddSource("Experimental.ModelContextProtocol"));
    builder.Services.ConfigureOpenTelemetryMeterProvider(m => m.AddMeter("Experimental.ModelContextProtocol"));
}

builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<OrderStore>();
builder.Services.AddScoped<CallerContext>();
builder.Services.AddHttpContextAccessor();
builder.Services.AddHealthChecks();

builder.Services
    .AddMcpServer(o =>
    {
        o.ServerInfo = new() { Name = "aidevme-orders", Version = "1.0.0" };
        o.ServerInstructions =
            "AIDevMe customer service tools for order status and returns. " +
            "Only the signed-in customer's orders are visible. Confirm every return with the customer first.";
    })
    .WithHttpTransport(o =>
    {
        // No server-side sessions: any replica can answer any request.
        o.SessionMode = HttpServerSessionMode.Stateless;
    })
    .WithTools<OrderTools>()
    .WithResources<PolicyResources>();

var app = builder.Build();

app.MapHealthChecks("/health");
app.MapMcp("/mcp");

app.Run();
