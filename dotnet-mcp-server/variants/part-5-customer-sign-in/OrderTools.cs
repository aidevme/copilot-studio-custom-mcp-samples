using System.ComponentModel;
using Microsoft.AspNetCore.Authorization;
using ModelContextProtocol.Server;

[McpServerToolType]
public sealed class OrderTools(
    IHttpContextAccessor http, ICustomerDirectory customers, IOrderStore orders, ILogger<OrderTools> logger)
{
    // The customer ID never comes from a tool input: oid from the validated token -> Contoso customer ID.
    private string CurrentCustomerId()
    {
        var user = http.HttpContext?.User ?? throw new UnauthorizedAccessException("No authenticated user.");
        return customers.FindCustomerId(user.GetObjectId())
            ?? throw new UnauthorizedAccessException("No Contoso customer account is linked to this sign-in.");
    }

    [McpServerTool(Name = "find_orders", ReadOnly = true)]
    [Description("Lists the signed-in customer's Contoso orders, newest first. Use it when the customer doesn't know the order number.")]
    [Authorize(Policy = OrderPolicies.Read)]
    public IReadOnlyList<OrderSummary> FindOrders(
        [Description("Open, Shipped, Delivered, Cancelled or Any.")] string status = "Any",
        [Description("Earliest order date, ISO 8601. Empty for no limit.")] string from = "",
        [Description("Latest order date, ISO 8601. Empty for no limit.")] string to = "")
        => orders.FindForCustomer(CurrentCustomerId(), status, from, to);

    [McpServerTool(Name = "get_order_status", ReadOnly = true)]
    [Description("Returns the status of one Contoso order by its number (for example SO-10023): order lines, carrier, tracking number and expected delivery date.")]
    [Authorize(Policy = OrderPolicies.Read)]
    public OrderStatus GetOrderStatus(
        [Description("Order number, for example SO-10023.")] string orderId)
    {
        var order = orders.Get(orderId);
        // Ownership check: someone else's order looks exactly like a missing one.
        if (order is null || order.CustomerId != CurrentCustomerId())
            throw new KeyNotFoundException($"Order {orderId} was not found.");
        return order.ToStatus(); // no address, phone or payment data in the tool result
    }

    [McpServerTool(Name = "create_return", ReadOnly = false, Destructive = false)]
    [Description("Starts a return for one line of a delivered Contoso order and returns the return number (RMA). Confirm the item, quantity and reason with the customer before calling it.")]
    [Authorize(Policy = OrderPolicies.CreateReturn)]
    public ReturnResult CreateReturn(
        [Description("Order number, for example SO-10023.")] string orderId,
        [Description("Order line number: 1, 2, 3 ...")] int lineNumber,
        [Description("How many items of that line to return.")] int quantity,
        [Description("Damaged, WrongItem, NotAsDescribed or NoLongerNeeded.")] string reason,
        [Description("Optional comment from the customer.")] string comment = "")
    {
        var customerId = CurrentCustomerId();
        var order = orders.Get(orderId);
        if (order is null || order.CustomerId != customerId)
            throw new KeyNotFoundException($"Order {orderId} was not found.");

        // Server-side policy: the description asks the agent to confirm, but the server decides.
        if (order.Status != "Delivered" || order.DeliveredOn is null
            || order.DeliveredOn.Value.AddDays(30) < DateOnly.FromDateTime(DateTime.UtcNow))
            throw new InvalidOperationException("Only delivered orders can be returned, within 30 days of delivery.");
        if (!ReturnReasons.All.Contains(reason))
            throw new ArgumentException("Unknown return reason.", nameof(reason));
        var line = order.Lines.FirstOrDefault(l => l.LineNumber == lineNumber)
            ?? throw new KeyNotFoundException($"Order {orderId} has no line {lineNumber}.");
        if (quantity < 1 || quantity > line.Quantity - line.ReturnedQuantity)
            throw new ArgumentOutOfRangeException(nameof(quantity), "More items than can still be returned.");

        var rma = orders.CreateReturn(orderId, lineNumber, quantity, reason, comment);

        // Audit: IDs only, no free text, no token.
        logger.LogInformation("create_return {Rma} customer {CustomerId} order {OrderId} line {Line} qty {Qty} reason {Reason}",
            rma, customerId, orderId, lineNumber, quantity, reason);

        return new ReturnResult(rma, orderId, lineNumber, quantity, reason);
    }
}
