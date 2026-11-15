using System.Security.Claims;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using ModelContextProtocol.AspNetCore.Authentication;
using ModelContextProtocol.Authentication;

var builder = WebApplication.CreateBuilder(args);

// Microsoft Entra External ID (external tenant) settings, from configuration.
var tenantId = builder.Configuration["ExternalId:TenantId"]!;        // external tenant ID (GUID)
var tenantSubdomain = builder.Configuration["ExternalId:Subdomain"]!; // e.g. aidevmecustomers
var apiClientId = builder.Configuration["ExternalId:ApiClientId"]!;   // client ID of the Orders MCP API app
var serverUrl = builder.Configuration["Mcp:ServerUrl"]!;              // e.g. https://orders-mcp.aidevme.com/mcp
var authority = $"https://{tenantSubdomain}.ciamlogin.com/{tenantId}/v2.0";

builder.Services
    .AddAuthentication(options =>
    {
        options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
        options.DefaultChallengeScheme = McpAuthenticationDefaults.AuthenticationScheme; // 401 + resource_metadata
    })
    .AddJwtBearer(options =>
    {
        // Keys and the expected issuer come from the external tenant's metadata document.
        // Its issuer has the form https://<tenant-id>.ciamlogin.com/<tenant-id>/v2.0.
        options.MetadataAddress = $"{authority}/.well-known/openid-configuration";
        options.MapInboundClaims = false;  // keep "scp" and "oid" as issued
        options.TokenValidationParameters.ValidAudience = apiClientId; // v2 access tokens: aud = API client ID
    })
    .AddMcp(options =>
    {
        options.ResourceMetadata = new ProtectedResourceMetadata
        {
            Resource = serverUrl,
            AuthorizationServers = { authority },
            ScopesSupported = ["Orders.Read"],   // minimal set; Returns.Create is requested for returns
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy(OrderPolicies.Read, policy => policy
        .RequireAuthenticatedUser()
        .RequireAssertion(ctx => ctx.User.HasScope("Orders.Read")));

    options.AddPolicy(OrderPolicies.CreateReturn, policy => policy
        .RequireAuthenticatedUser()
        .RequireAssertion(ctx => ctx.User.HasScope("Returns.Create")));
});

builder.Services.AddHttpContextAccessor();
builder.Services.AddSingleton<ICustomerDirectory, DemoCustomerDirectory>();
builder.Services.AddSingleton<IOrderStore, DemoOrderStore>();

builder.Services
    .AddMcpServer()
    .WithHttpTransport()
    .AddAuthorizationFilters()   // honors [Authorize] on individual tools
    .WithTools<OrderTools>();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

app.MapMcp("/mcp").RequireAuthorization(OrderPolicies.Read);

app.Run();

public static class OrderPolicies
{
    public const string Read = "Orders.Read";
    public const string CreateReturn = "Returns.Create";
}

public static class ClaimsPrincipalExtensions
{
    // Delegated v2 access tokens carry scopes as one space-separated "scp" claim.
    public static bool HasScope(this ClaimsPrincipal user, string scope) =>
        (user.FindFirst("scp")?.Value ?? string.Empty)
            .Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Contains(scope, StringComparer.Ordinal);

    // oid: the stable object ID of the customer in the external tenant.
    public static string GetObjectId(this ClaimsPrincipal user) =>
        user.FindFirst("oid")?.Value
        ?? throw new UnauthorizedAccessException("The access token has no oid claim.");
}
