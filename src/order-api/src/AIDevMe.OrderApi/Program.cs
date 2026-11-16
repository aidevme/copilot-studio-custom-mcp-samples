// AIDevMe Order Management API: the backend REST API that the Logic Apps workflows (Part 2) and API Management
// (Part 3) call. In-memory demo data from data/seed.json. Described in openapi/orders-api.yaml.
using System.Globalization;
using AIDevMe.OrderApi;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<OrderData>();

// Callers authenticate with a Microsoft Entra token for this API, requested by the logic app's or API Management's
// managed identity. Off for local runs (appsettings.Development.json); on in Azure.
var auth = builder.Configuration.GetSection("Auth");
var authEnabled = auth.GetValue<bool>("Enabled");
if (authEnabled)
{
    var tenantId = auth["TenantId"] ?? throw new InvalidOperationException("Auth:TenantId is required when Auth:Enabled is true.");
    var allowedCallers = auth.GetSection("AllowedCallerObjectIds").Get<string[]>() ?? [];
    builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddJwtBearer(o =>
    {
        o.Authority = $"https://login.microsoftonline.com/{tenantId}/v2.0";
        o.MapInboundClaims = false;
        o.TokenValidationParameters.ValidAudiences = new[] { auth["Audience"], auth["ClientId"] }
            .Where(a => !string.IsNullOrWhiteSpace(a)).ToArray();
        // Managed identity tokens are v1 tokens unless the app registration accepts v2.
        o.TokenValidationParameters.ValidIssuers =
            [$"https://login.microsoftonline.com/{tenantId}/v2.0", $"https://sts.windows.net/{tenantId}/"];
    });
    builder.Services.AddAuthorization(o => o.FallbackPolicy = new Microsoft.AspNetCore.Authorization.AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        // Any app in the tenant can request a token for this API, so allow only the listed managed identities.
        .RequireAssertion(ctx => allowedCallers.Length == 0
            || allowedCallers.Contains(ctx.User.FindFirst("oid")?.Value, StringComparer.OrdinalIgnoreCase))
        .Build());
}

var app = builder.Build();
if (authEnabled)
{
    app.UseAuthentication();
    app.UseAuthorization();
}
else
{
    app.Logger.LogWarning("Auth:Enabled is false: the API accepts unauthenticated calls. Local testing only.");
}

const string CustomerIdHeader = "AIDevMe-Customer-Id";   // set by API Management from the caller's identity (Part 3)
const string CustomerOidHeader = "AIDevMe-Customer-Oid"; // the caller's External ID oid, mapped here (Part 5)

// The caller's customer, when a gateway passed one. Logic Apps doesn't, and checks ownership itself (Part 2).
string? CallerCustomer(HttpRequest request, OrderData data)
{
    if (request.Headers.TryGetValue(CustomerIdHeader, out var id) && !string.IsNullOrWhiteSpace(id))
        return id.ToString().Trim();
    if (request.Headers.TryGetValue(CustomerOidHeader, out var oid) && !string.IsNullOrWhiteSpace(oid))
        return data.CustomerForIdentity(oid.ToString()) ?? "";
    return null;
}

IResult Error(int status, string code, string message) => Results.Json(new { code, message }, statusCode: status);

IResult OrderNotFound(string orderId) => Error(404, "order_not_found",
    $"No order {orderId} was found for this customer. Check the number, or use find_orders.");

object OrderBody(Order o, OrderData data) => new
{
    o.OrderId,
    o.CustomerId,
    OrderDate = o.OrderDate.ToString("yyyy-MM-dd"),
    o.Status,
    o.Warehouse,
    o.Carrier,
    o.TrackingNumber,
    ExpectedDelivery = o.ExpectedDelivery?.ToString("yyyy-MM-dd") ?? "",
    DeliveredOn = o.DeliveredOn?.ToString("yyyy-MM-dd") ?? "",
    Total = $"{o.Total.ToString("0.00", CultureInfo.InvariantCulture)} {data.Currency}",
    Lines = o.Lines.Select(l => new { l.LineNumber, l.Product, l.Quantity, l.ReturnedQuantity }),
};

app.MapGet("/health", () => Results.Ok(new { status = "ok" })).AllowAnonymous();

// find_orders
app.MapGet("/customers/{customerId}/orders",
    (string customerId, string? status, string? from, string? to, HttpRequest request, OrderData data) =>
{
    var caller = CallerCustomer(request, data);
    if (caller is not null && !caller.Equals(customerId, StringComparison.OrdinalIgnoreCase))
        return Error(404, "customer_not_found", "No orders were found for this customer.");

    string? statusFilter = null;
    if (!string.IsNullOrWhiteSpace(status) && !status.Equals("Any", StringComparison.OrdinalIgnoreCase))
    {
        statusFilter = OrderData.Statuses.FirstOrDefault(s => s.Equals(status.Trim(), StringComparison.OrdinalIgnoreCase));
        if (statusFilter is null)
            return Error(400, "invalid_filter", $"'{status}' isn't a valid status. Use one of: Any, {string.Join(", ", OrderData.Statuses)}.");
    }
    DateOnly? fromDate = null, toDate = null;
    if (!string.IsNullOrWhiteSpace(from))
    {
        if (!DateOnly.TryParseExact(from.Trim(), "yyyy-MM-dd", out var d))
            return Error(400, "invalid_filter", $"'{from}' isn't an ISO 8601 date for 'from'. Example: 2026-10-01.");
        fromDate = d;
    }
    if (!string.IsNullOrWhiteSpace(to))
    {
        if (!DateOnly.TryParseExact(to.Trim(), "yyyy-MM-dd", out var d))
            return Error(400, "invalid_filter", $"'{to}' isn't an ISO 8601 date for 'to'. Example: 2026-11-13.");
        toDate = d;
    }

    var items = data.FindOrders(customerId, statusFilter, fromDate, toDate).Select(o => new
    {
        o.OrderId,
        OrderDate = o.OrderDate.ToString("yyyy-MM-dd"),
        o.Status,
        Total = $"{o.Total.ToString("0.00", CultureInfo.InvariantCulture)} {data.Currency}",
        Items = o.Lines.Select(l => l.Product),
    });
    return Results.Ok(new { items });
});

// get_order_status. Returns customerId, so a caller without a customer header (Logic Apps) can check ownership.
app.MapGet("/orders/{orderId}", (string orderId, HttpRequest request, OrderData data) =>
{
    var order = data.GetOrder(orderId);
    var caller = CallerCustomer(request, data);
    if (order is null || (caller is not null && !caller.Equals(order.CustomerId, StringComparison.OrdinalIgnoreCase)))
        return OrderNotFound(orderId);
    return Results.Ok(OrderBody(order, data));
});

// create_return
app.MapPost("/orders/{orderId}/returns",
    (string orderId, [FromBody] CreateReturnRequest? body, HttpRequest request, OrderData data) =>
{
    if (body is null)
        return Error(400, "invalid_request", "Send lineNumber, quantity and reason in the request body.");
    var order = data.GetOrder(orderId);
    var caller = CallerCustomer(request, data);
    if (order is null || (caller is not null && !caller.Equals(order.CustomerId, StringComparison.OrdinalIgnoreCase)))
        return OrderNotFound(orderId);

    var (created, refusal) = data.CreateReturn(order.OrderId, body.LineNumber, body.Quantity, body.Reason ?? "",
        (body.Comment ?? "").Trim());
    if (refusal is not null)
        return Error(422, refusal.Code, refusal.Message);

    app.Logger.LogInformation("Return {ReturnId} created for {OrderId} line {Line}", created!.ReturnId, created.OrderId, created.LineNumber);
    return Results.Json(new
    {
        created.ReturnId,
        created.OrderId,
        created.LineNumber,
        created.Product,
        created.Quantity,
        created.Reason,
        created.Comment,
        created.Status,
        created.CreatedAt,
    }, statusCode: 201);
});

// Internal: maps an External ID oid to the customer ID. Called by API Management's OAuth policy (Part 3).
app.MapGet("/customers/by-identity/{oid}", (string oid, OrderData data) =>
    data.CustomerForIdentity(oid) is { } customerId
        ? Results.Ok(new { customerId })
        : Error(404, "identity_not_mapped", "This sign-in isn't linked to an AIDevMe customer."));

app.Run();

public record CreateReturnRequest(int LineNumber, int Quantity, string? Reason, string? Comment);
