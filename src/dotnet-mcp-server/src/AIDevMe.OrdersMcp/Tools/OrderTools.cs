using System.ComponentModel;
using System.Globalization;
using System.Text.Json;
using AIDevMe.OrdersMcp.Data;
using AIDevMe.OrdersMcp.Resources;
using ModelContextProtocol;
using ModelContextProtocol.Protocol;
using ModelContextProtocol.Server;

namespace AIDevMe.OrdersMcp.Tools;

[McpServerToolType]
public class OrderTools(OrderStore store, CallerContext caller, ILogger<OrderTools> logger)
{
    private static readonly TimeSpan ReturnWindow = TimeSpan.FromDays(30);
    private static readonly string[] Statuses = ["Any", "Open", "Shipped", "Delivered", "Cancelled"];
    private static readonly string[] Reasons = ["Damaged", "WrongItem", "NotAsDescribed", "NoLongerNeeded"];
    private static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web);

    // Optional inputs are plain strings with defaults, never string?: Copilot Studio truncates
    // input schemas whose "type" is an array such as ["string","null"].

    [McpServerTool(Name = "find_orders", Title = "Find orders",
        ReadOnly = true, Idempotent = true, OpenWorld = false)]
    [Description("Lists the signed-in customer's AIDevMe orders, newest first. Use it when the customer doesn't know the order number.")]
    public object FindOrders(
        [Description("Order status filter: Any, Open, Shipped, Delivered or Cancelled.")] string status = "Any",
        [Description("Optional. Only orders placed on or after this date, ISO 8601, for example 2026-10-01.")] string from = "",
        [Description("Optional. Only orders placed on or before this date, ISO 8601.")] string to = "")
    {
        var customerId = caller.GetCustomerId();
        var statusFilter = OneOf(status, Statuses, "status");
        var orders = store.FindOrders(customerId,
            statusFilter == "Any" ? null : statusFilter, ParseDate(from, "from"), ParseDate(to, "to"));

        logger.LogInformation("find_orders status={Status} results={Count}", statusFilter, orders.Count);
        return orders.Select(o => new
        {
            o.OrderId,
            o.Status,
            OrderedAt = o.OrderedAt.ToString("yyyy-MM-dd"),
            Items = o.Lines.Select(l => l.Product).ToArray(),
        }).ToList();
    }

    [McpServerTool(Name = "get_order_status", Title = "Get order status",
        ReadOnly = true, Idempotent = true, OpenWorld = false)]
    [Description("Returns the status of one AIDevMe order by its number (for example SO-10023): order lines, carrier, tracking number and expected delivery date.")]
    public object GetOrderStatus(
        [Description("Order number, for example SO-10023.")] string orderId)
    {
        var order = store.GetOrder(caller.GetCustomerId(), orderId) ?? throw NotFound(orderId);

        logger.LogInformation("get_order_status orderId={OrderId} status={Status}", order.OrderId, order.Status);
        return new
        {
            order.OrderId,
            order.Status,
            OrderedAt = order.OrderedAt.ToString("yyyy-MM-dd"),
            order.Warehouse,
            order.Carrier,
            order.TrackingNumber,
            ExpectedDelivery = order.ExpectedDelivery?.ToString("yyyy-MM-dd") ?? "",
            DeliveredAt = order.DeliveredAt?.ToString("yyyy-MM-dd") ?? "",
            Lines = order.Lines,
        };
    }

    [McpServerTool(Name = "create_return", Title = "Create return",
        ReadOnly = false, Destructive = false, Idempotent = false, OpenWorld = false)]
    [Description("Starts a return for one line of a delivered AIDevMe order and returns the return number (RMA). Confirm the item, quantity and reason with the customer before calling it.")]
    public IEnumerable<ContentBlock> CreateReturn(
        [Description("Order number, for example SO-10023.")] string orderId,
        [Description("Line number of the item on the order (1, 2, 3...), from get_order_status.")] int lineNumber,
        [Description("How many units to return, at least 1.")] int quantity,
        [Description("Return reason: Damaged, WrongItem, NotAsDescribed or NoLongerNeeded.")] string reason,
        [Description("Optional. The customer's own words about the problem.")] string comment = "")
    {
        var order = store.GetOrder(caller.GetCustomerId(), orderId) ?? throw NotFound(orderId);
        var returnReason = OneOf(reason, Reasons, "reason");

        // AIDevMe's fictional policy: delivered orders only, within 30 days after delivery.
        if (order.Status != "Delivered" || order.DeliveredAt is null)
        {
            throw new McpException(
                $"Order {order.OrderId} is {order.Status}, not delivered. Returns can start only after delivery; " +
                "use get_order_status to tell the customer the expected delivery date.");
        }

        var windowEnds = order.DeliveredAt.Value + ReturnWindow;
        if (store.Now > windowEnds)
        {
            throw new McpException(
                $"Order {order.OrderId} was delivered on {order.DeliveredAt:yyyy-MM-dd}. The 30-day return window " +
                $"ended on {windowEnds:yyyy-MM-dd}, so this agent can't start a return. Tell the customer.");
        }

        var line = order.Lines.FirstOrDefault(l => l.LineNumber == lineNumber)
            ?? throw new McpException(
                $"Order {order.OrderId} has no line {lineNumber}. Valid lines: " +
                string.Join(", ", order.Lines.Select(l => $"{l.LineNumber} ({l.Product})")) + ".");

        var remaining = line.Quantity - line.ReturnedQuantity;
        if (quantity < 1 || quantity > remaining)
        {
            throw new McpException(remaining == 0
                ? $"Line {line.LineNumber} ({line.Product}) has already been returned in full."
                : $"Line {line.LineNumber} ({line.Product}): {line.Quantity} ordered, {line.ReturnedQuantity} already " +
                  $"returned, so the customer can return at most {remaining}. Ask the customer how many to return.");
        }

        var rma = store.TryAddReturn(order.OrderId, line.LineNumber, quantity, returnReason, comment.Trim())
            ?? throw new McpException("The remaining quantity changed. Call get_order_status and try again.");

        logger.LogInformation("create_return returnId={ReturnId} orderId={OrderId} line={Line} quantity={Quantity}",
            rma.ReturnId, rma.OrderId, rma.LineNumber, rma.Quantity);

        // Copilot Studio reaches resources only through tool results, so link the return policy here.
        return
        [
            new TextContentBlock { Text = JsonSerializer.Serialize(rma, Json) },
            new ResourceLinkBlock
            {
                Uri = PolicyResources.ReturnPolicyUri,
                Name = "return_policy",
                Description = "What happens next: return label, refund and the 30-day rule.",
                MimeType = "text/markdown",
            },
        ];
    }

    // Same message for "doesn't exist" and "belongs to someone else", so order numbers can't be probed.
    private static McpException NotFound(string orderId) =>
        new($"No order {orderId.Trim()} was found for this customer. Check the number, or use find_orders.");

    private static string OneOf(string value, string[] allowed, string name) =>
        allowed.FirstOrDefault(a => a.Equals(value.Trim(), StringComparison.OrdinalIgnoreCase))
        ?? throw new McpException($"'{value}' isn't a valid {name}. Use one of: {string.Join(", ", allowed)}.");

    private static DateTimeOffset? ParseDate(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return null;
        }
        return DateTimeOffset.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var date)
            ? date
            : throw new McpException($"'{value}' isn't an ISO 8601 date for '{name}'. Example: 2026-10-01.");
    }
}
