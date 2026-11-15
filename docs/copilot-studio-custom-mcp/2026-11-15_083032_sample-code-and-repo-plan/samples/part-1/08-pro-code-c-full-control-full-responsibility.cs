[McpServerTool(Name = "get_order_status", ReadOnly = true)]
[Description("Returns the status of one Contoso order by its number (for example SO-10023): order lines, carrier, tracking number and expected delivery date.")]
public static string GetOrderStatus(IHttpContextAccessor http,
    [Description("Order number, for example SO-10023.")] string orderId)
    => OwnOrder(http, orderId) is { } o
        ? JsonSerializer.Serialize(new { o.OrderId, o.Status, o.Carrier, o.TrackingNumber, o.ExpectedDelivery, o.Lines })
        : throw new McpException($"Order {orderId} was not found.");
