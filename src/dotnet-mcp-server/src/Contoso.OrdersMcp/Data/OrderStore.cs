namespace Contoso.OrdersMcp.Data;

public record OrderLine(int LineNumber, string Product, int Quantity, int ReturnedQuantity);

public record Order(
    string OrderId, string CustomerId, string Status, DateTimeOffset OrderedAt, string Warehouse,
    string Carrier, string TrackingNumber, DateTimeOffset? ExpectedDelivery, DateTimeOffset? DeliveredAt,
    IReadOnlyList<OrderLine> Lines);

public record ReturnRequest(
    string ReturnId, string OrderId, int LineNumber, string Product, int Quantity,
    string Reason, string Comment, string Status, DateTimeOffset CreatedAt);

/// <summary>In-memory demo data, standing in for the Order Management API.</summary>
public class OrderStore
{
    private readonly Lock _gate = new();
    private readonly TimeProvider _clock;
    private readonly List<Order> _orders;
    private readonly List<ReturnRequest> _returns;
    private int _nextReturn = 5002;

    public OrderStore(TimeProvider clock)
    {
        _clock = clock;
        // Dates are relative to server start, so the 30-day window behaves the same on any day.
        var today = new DateTimeOffset(clock.GetUtcNow().Date, TimeSpan.Zero);
        _orders =
        [
            new("SO-10023", "CU-3001", "Delivered", today.AddDays(-10), "Hamburg", "DHL", "DEMO-DHL-0010023",
                today.AddDays(-7), today.AddDays(-7),
                [new(1, "Contoso Kettle 1.7 l", 1, 0), new(2, "Contoso Toaster 2-slice", 1, 0),
                 new(3, "Contoso Glass Set, 6 pcs", 2, 1)]),
            new("SO-10019", "CU-3001", "Delivered", today.AddDays(-48), "Hamburg", "DHL", "DEMO-DHL-0010019",
                today.AddDays(-45), today.AddDays(-45),
                [new(1, "Contoso Blender 1.5 l", 1, 0)]),
            new("SO-10031", "CU-3001", "Shipped", today.AddDays(-2), "Utrecht", "PostNL", "DEMO-PNL-0010031",
                today.AddDays(2), null,
                [new(1, "Contoso Espresso Machine", 1, 0)]),
            new("SO-10035", "CU-3001", "Open", today.AddDays(-1), "Hamburg", "", "", today.AddDays(5), null,
                [new(1, "Contoso Stand Mixer", 1, 0)]),
            new("SO-10027", "CU-3002", "Delivered", today.AddDays(-6), "Utrecht", "PostNL", "DEMO-PNL-0010027",
                today.AddDays(-3), today.AddDays(-3),
                [new(1, "Contoso Dishwasher 60 cm", 1, 0)]),
        ];
        _returns =
        [
            new("RMA-5001", "SO-10023", 3, "Contoso Glass Set, 6 pcs", 1, "Damaged", "One glass broken",
                "Approved", today.AddDays(-5)),
        ];
    }

    public DateTimeOffset Now => _clock.GetUtcNow();

    public IReadOnlyList<Order> FindOrders(string customerId, string? status, DateTimeOffset? from, DateTimeOffset? to)
    {
        lock (_gate)
        {
            return _orders
                .Where(o => o.CustomerId == customerId)
                .Where(o => status is null || o.Status.Equals(status, StringComparison.OrdinalIgnoreCase))
                .Where(o => from is null || o.OrderedAt >= from)
                .Where(o => to is null || o.OrderedAt <= to)
                .OrderByDescending(o => o.OrderedAt)
                .ToList();
        }
    }

    /// <summary>Returns the order only when it belongs to the customer; otherwise null, like a missing order.</summary>
    public Order? GetOrder(string customerId, string orderId)
    {
        lock (_gate)
        {
            return _orders.FirstOrDefault(o =>
                o.OrderId.Equals(orderId.Trim(), StringComparison.OrdinalIgnoreCase) && o.CustomerId == customerId);
        }
    }

    /// <summary>Re-checks the remaining quantity under the lock, then records the return.</summary>
    public ReturnRequest? TryAddReturn(string orderId, int lineNumber, int quantity, string reason, string comment)
    {
        lock (_gate)
        {
            var order = _orders.First(o => o.OrderId == orderId);
            var line = order.Lines.First(l => l.LineNumber == lineNumber);
            if (quantity > line.Quantity - line.ReturnedQuantity)
            {
                return null;
            }

            var lines = order.Lines
                .Select(l => l.LineNumber == lineNumber ? l with { ReturnedQuantity = l.ReturnedQuantity + quantity } : l)
                .ToList();
            _orders[_orders.IndexOf(order)] = order with { Lines = lines };

            var rma = new ReturnRequest($"RMA-{_nextReturn++}", orderId, lineNumber, line.Product,
                quantity, reason, comment, "Requested", Now);
            _returns.Add(rma);
            return rma;
        }
    }
}
