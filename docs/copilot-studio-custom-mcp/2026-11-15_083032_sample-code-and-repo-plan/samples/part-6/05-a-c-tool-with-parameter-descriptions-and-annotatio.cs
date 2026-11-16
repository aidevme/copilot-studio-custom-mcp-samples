using System.ComponentModel;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;
using ModelContextProtocol;
using ModelContextProtocol.Server;

namespace AIDevMe.OrdersMcp;

[JsonConverter(typeof(JsonStringEnumConverter<OrderStatus>))]
public enum OrderStatus { Open, Shipped, Delivered, Cancelled }

// Input-only filter: a non-nullable enum with an "Any" default keeps the schema type a single "string".
// A nullable enum (OrderStatus?) produces "type": ["string","null"], which Copilot Studio truncates.
[JsonConverter(typeof(JsonStringEnumConverter<OrderStatusFilter>))]
public enum OrderStatusFilter { Any, Open, Shipped, Delivered, Cancelled }

[JsonConverter(typeof(JsonStringEnumConverter<ReturnReason>))]
public enum ReturnReason { Damaged, WrongItem, NotAsDescribed, NoLongerNeeded }

public record OrderSummary(string OrderId, DateOnly OrderDate, OrderStatus Status, int LineCount, string FirstItem);
public record FindOrdersResult(IReadOnlyList<OrderSummary> Orders, int Count, string Message);
public record OrderLine(int LineNumber, string Product, int Quantity);
public record OrderStatusResult(string OrderId, OrderStatus Status, IReadOnlyList<OrderLine> Lines,
    string Carrier, string TrackingNumber, string ExpectedDelivery, string DeliveredOn);
public record ReturnResult(string ReturnId, string OrderId, int LineNumber, int Quantity, ReturnReason Reason, string Message);

[McpServerToolType]
public sealed partial class OrderTools(OrderStore store, ICustomerContext customer, TimeProvider clock)
{
    // The customer ID never comes from a tool input; it comes from the caller's identity (Part 5).
    private string CustomerId => customer.CustomerId
        ?? throw new McpException("The customer isn't signed in. Ask them to sign in on the AIDevMe website.");

    [McpServerTool(Name = "find_orders", Title = "Find my orders",
        ReadOnly = true, Idempotent = true, OpenWorld = false, UseStructuredContent = true)]
    [Description("Lists the signed-in customer's AIDevMe orders, newest first. " +
                 "Use it when the customer doesn't know the order number.")]
    public FindOrdersResult FindOrders(
        [Description("Order status: Any, Open, Shipped, Delivered or Cancelled. Use Any unless the customer names a status.")]
        OrderStatusFilter status = OrderStatusFilter.Any,
        [Description("Earliest order date, ISO 8601 date such as 2026-10-01. Leave empty for no lower limit.")]
        string from = "",
        [Description("Latest order date, ISO 8601 date such as 2026-11-13. Leave empty for no upper limit.")]
        string to = "")
    {
        var orders = store.FindOrders(CustomerId, status, ParseDate(from, nameof(from)), ParseDate(to, nameof(to)))
            .Take(10).ToList();
        var message = orders.Count == 0
            ? "No orders match. Ask the customer for the order number or a different time range."
            : "Newest first, at most 10. Use an orderId from this list in get_order_status.";
        return new FindOrdersResult(orders, orders.Count, message);
    }

    [McpServerTool(Name = "get_order_status", Title = "Get order status",
        ReadOnly = true, Idempotent = true, OpenWorld = false, UseStructuredContent = true)]
    [Description("Returns the status of one AIDevMe order by its number (for example SO-10023): " +
                 "order lines, carrier, tracking number and expected delivery date.")]
    public OrderStatusResult GetOrderStatus(
        [Description("Order number in the format SO-<digits>, for example SO-10023. Take it from the customer or from find_orders.")]
        string orderId)
    {
        ValidateOrderId(orderId);
        return store.GetOrder(CustomerId, orderId) ?? throw NotFound(orderId);
    }

    [McpServerTool(Name = "create_return", Title = "Start a return",
        ReadOnly = false, Destructive = false, Idempotent = false, OpenWorld = false, UseStructuredContent = true)]
    [Description("Starts a return for one line of a delivered AIDevMe order and returns the return number (RMA). " +
                 "Confirm the item, quantity and reason with the customer before calling it.")]
    public ReturnResult CreateReturn(
        [Description("Order number in the format SO-<digits>, for example SO-10023.")]
        string orderId,
        [Description("Line number of the item, taken from get_order_status (1, 2, 3 ...). Never guess it from how the customer counts items.")]
        int lineNumber,
        [Description("How many units to return: at least 1 and at most the quantity on that order line.")]
        int quantity,
        [Description("Return reason: Damaged, WrongItem, NotAsDescribed or NoLongerNeeded.")]
        ReturnReason reason,
        [Description("Optional note in the customer's words, for example 'Lid cracked on arrival'. Max 500 characters.")]
        string comment = "")
    {
        ValidateOrderId(orderId);
        var order = store.GetOrder(CustomerId, orderId) ?? throw NotFound(orderId);

        if (order.Status != OrderStatus.Delivered)
            throw new McpException($"Order {orderId} is {order.Status}, not Delivered. Only delivered orders can be returned.");

        var today = DateOnly.FromDateTime(clock.GetUtcNow().UtcDateTime);
        var lastDay = DateOnly.Parse(order.DeliveredOn).AddDays(30);
        if (today > lastDay)
            throw new McpException($"The 30-day return window for {orderId} ended on {lastDay:yyyy-MM-dd}. " +
                                   "Tell the customer the order can't be returned; don't retry.");

        var line = order.Lines.FirstOrDefault(l => l.LineNumber == lineNumber)
            ?? throw new McpException($"Order {orderId} has no line {lineNumber}. Its lines are " +
                string.Join(", ", order.Lines.Select(l => $"{l.LineNumber} ({l.Product})")) + ".");

        if (quantity < 1 || quantity > line.Quantity)
            throw new McpException($"Line {lineNumber} ({line.Product}) has quantity {line.Quantity}. " +
                                   $"Ask the customer for a quantity from 1 to {line.Quantity}.");
        if (comment.Length > 500)
            throw new McpException("'comment' must be 500 characters or fewer.");

        var rma = store.CreateReturn(CustomerId, orderId, lineNumber, quantity, reason, comment);
        return new ReturnResult(rma, orderId, lineNumber, quantity, reason,
            $"Return {rma} started for {quantity} x {line.Product}. The customer gets the return label by email.");
    }

    private static void ValidateOrderId(string orderId)
    {
        if (!OrderIdPattern().IsMatch(orderId))
            throw new McpException($"'{orderId}' isn't an AIDevMe order number. Order numbers look like SO-10023.");
    }

    // Same answer for "doesn't exist" and "belongs to another customer", so order numbers can't be probed.
    private static McpException NotFound(string orderId) =>
        new($"No order {orderId} was found for this customer. Check the number with the customer, or use find_orders.");

    private static DateOnly? ParseDate(string value, string name) =>
        string.IsNullOrWhiteSpace(value) ? null
        : DateOnly.TryParse(value, out var date) ? date
        : throw new McpException($"'{name}' must be an ISO 8601 date such as 2026-10-01, or empty.");

    [GeneratedRegex("^SO-[0-9]{5}$")]
    private static partial Regex OrderIdPattern();
}
