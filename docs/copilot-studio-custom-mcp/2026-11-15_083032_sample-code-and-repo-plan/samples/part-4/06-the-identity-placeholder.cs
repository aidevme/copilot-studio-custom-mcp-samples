using ModelContextProtocol;

namespace AIDevMe.OrdersMcp.Tools;

/// <summary>
/// Resolves the customer ID for the current request. PLACEHOLDER until Part 5:
/// a validated sign-in token is the only trustworthy source of the customer ID.
/// </summary>
public class CallerContext(IHttpContextAccessor httpContextAccessor, IConfiguration config, ILogger<CallerContext> logger)
{
    public const string DemoHeader = "AIDevMe-Demo-Customer";

    public string GetCustomerId()
    {
        var http = httpContextAccessor.HttpContext
            ?? throw new McpException("No HTTP context; cannot identify the customer.");

        // Part 5: a validated Microsoft Entra External ID token. Its oid claim maps to the CU- customer ID.
        if (http.User.Identity?.IsAuthenticated == true)
        {
            throw new McpException("Customer sign-in isn't connected to this server yet.");
        }

        // Development only. Anyone can send a header, so it is never an identity on a deployed server.
        if (config.GetValue<bool>("Demo:AllowCustomerHeader")
            && http.Request.Headers.TryGetValue(DemoHeader, out var demo)
            && !string.IsNullOrWhiteSpace(demo))
        {
            logger.LogWarning("Using the unauthenticated {Header} header as the customer ID. Demo only.", DemoHeader);
            return demo.ToString().Trim();
        }

        throw new McpException("The customer isn't signed in. Ask the customer to sign in on the AIDevMe website first.");
    }
}
