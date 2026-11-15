using System.Text.Json;
using System.Text.Json.Nodes;

namespace AIDevMe.OrderApi;

public record OrderLine(int LineNumber, string Product, int Quantity, decimal UnitPrice, int ReturnedQuantity);

public record Order(
    string OrderId, string CustomerId, string Status, DateOnly OrderDate, string Warehouse, string Carrier,
    string TrackingNumber, DateOnly? ExpectedDelivery, DateOnly? DeliveredOn, IReadOnlyList<OrderLine> Lines)
{
    public decimal Total => Lines.Sum(l => l.UnitPrice * l.Quantity);
}

public record ReturnRecord(
    string ReturnId, string OrderId, int LineNumber, string Product, int Quantity, string Reason, string Comment,
    string Status, DateTimeOffset CreatedAt);

/// <summary>Why a return was refused; the API answers 422 with the code and the message.</summary>
public record ReturnRefusal(string Code, string Message);

/// <summary>
/// In-memory demo data, loaded from data/seed.json. Dates in the seed are offsets from the day the API starts.
/// </summary>
public class OrderData
{
    public static readonly string[] Statuses = ["Open", "Shipped", "Delivered", "Cancelled"];
    public static readonly string[] Reasons = ["Damaged", "WrongItem", "NotAsDescribed", "NoLongerNeeded"];

    private readonly Lock _gate = new();
    private readonly TimeProvider _clock;
    private readonly List<Order> _orders = [];
    private readonly List<ReturnRecord> _returns = [];
    private readonly Dictionary<string, string> _identities = new(StringComparer.OrdinalIgnoreCase);
    private int _nextReturn;

    public OrderData(TimeProvider clock, IConfiguration config, IHostEnvironment env)
    {
        _clock = clock;
        var path = config["Data:SeedPath"] ?? Path.Combine(AppContext.BaseDirectory, "data", "seed.json");
        var seed = JsonNode.Parse(File.ReadAllText(path))!;
        var today = DateOnly.FromDateTime(clock.GetUtcNow().UtcDateTime);
        DateOnly? Day(JsonNode? offset) => offset is null ? null : today.AddDays(offset.GetValue<int>());

        Currency = seed["currency"]!.GetValue<string>();
        ReturnWindowDays = seed["returnWindowDays"]!.GetValue<int>();
        _nextReturn = seed["nextReturnNumber"]!.GetValue<int>();

        foreach (var o in seed["orders"]!.AsArray())
        {
            var lines = o!["lines"]!.AsArray().Select(l => new OrderLine(
                l!["lineNumber"]!.GetValue<int>(), l["product"]!.GetValue<string>(), l["quantity"]!.GetValue<int>(),
                l["unitPrice"]!.GetValue<decimal>(), l["returnedQuantity"]!.GetValue<int>())).ToList();
            _orders.Add(new Order(
                o["orderId"]!.GetValue<string>(), o["customerId"]!.GetValue<string>(), o["status"]!.GetValue<string>(),
                Day(o["orderedOffsetDays"])!.Value, o["warehouse"]!.GetValue<string>(), o["carrier"]!.GetValue<string>(),
                o["trackingNumber"]!.GetValue<string>(), Day(o["expectedDeliveryOffsetDays"]),
                Day(o["deliveredOffsetDays"]), lines));
        }

        foreach (var r in seed["returns"]!.AsArray())
        {
            var created = new DateTimeOffset(Day(r!["createdOffsetDays"])!.Value.ToDateTime(TimeOnly.MinValue), TimeSpan.Zero);
            _returns.Add(new ReturnRecord(
                r["returnId"]!.GetValue<string>(), r["orderId"]!.GetValue<string>(), r["lineNumber"]!.GetValue<int>(),
                r["product"]!.GetValue<string>(), r["quantity"]!.GetValue<int>(), r["reason"]!.GetValue<string>(),
                r["comment"]!.GetValue<string>(), r["status"]!.GetValue<string>(), created));
        }

        foreach (var (oid, customer) in seed["identities"]!.AsObject())
        {
            if (oid != "comment") _identities[oid] = customer!.GetValue<string>();
        }
        // App settings Customers__Identities__<oid>=CU-3001 add or override mappings for real External ID users.
        foreach (var entry in config.GetSection("Customers:Identities").GetChildren())
        {
            if (!string.IsNullOrWhiteSpace(entry.Value)) _identities[entry.Key] = entry.Value;
        }
    }

    public string Currency { get; }
    public int ReturnWindowDays { get; }
    public DateOnly Today => DateOnly.FromDateTime(_clock.GetUtcNow().UtcDateTime);

    public string? CustomerForIdentity(string oid) => _identities.GetValueOrDefault(oid.Trim());

    public IReadOnlyList<Order> FindOrders(string customerId, string? status, DateOnly? from, DateOnly? to)
    {
        lock (_gate)
        {
            return _orders
                .Where(o => o.CustomerId.Equals(customerId, StringComparison.OrdinalIgnoreCase))
                .Where(o => status is null || o.Status.Equals(status, StringComparison.OrdinalIgnoreCase))
                .Where(o => from is null || o.OrderDate >= from)
                .Where(o => to is null || o.OrderDate <= to)
                .OrderByDescending(o => o.OrderDate)
                .ToList();
        }
    }

    public Order? GetOrder(string orderId)
    {
        lock (_gate)
        {
            return _orders.FirstOrDefault(o => o.OrderId.Equals(orderId.Trim(), StringComparison.OrdinalIgnoreCase));
        }
    }

    /// <summary>
    /// Applies AIDevMe's fictional return policy: delivered orders only, within the return window after delivery,
    /// an existing line and a quantity between 1 and what's left to return.
    /// </summary>
    public (ReturnRecord? Created, ReturnRefusal? Refusal) CreateReturn(
        string orderId, int lineNumber, int quantity, string reason, string comment)
    {
        lock (_gate)
        {
            var order = _orders.First(o => o.OrderId.Equals(orderId.Trim(), StringComparison.OrdinalIgnoreCase));
            if (order.Status != "Delivered" || order.DeliveredOn is null)
            {
                return (null, new("not_delivered",
                    $"Order {order.OrderId} is {order.Status}. Only delivered orders can be returned."));
            }
            var lastDay = order.DeliveredOn.Value.AddDays(ReturnWindowDays);
            if (Today > lastDay)
            {
                return (null, new("return_window_closed",
                    $"Order {order.OrderId} was delivered on {order.DeliveredOn:yyyy-MM-dd}. The {ReturnWindowDays}-day " +
                    $"return window closed on {lastDay:yyyy-MM-dd}."));
            }
            var line = order.Lines.FirstOrDefault(l => l.LineNumber == lineNumber);
            if (line is null)
            {
                return (null, new("line_not_found",
                    $"Order {order.OrderId} has no line {lineNumber}. Valid lines: " +
                    string.Join(", ", order.Lines.Select(l => $"{l.LineNumber} ({l.Product})")) + "."));
            }
            var remaining = line.Quantity - line.ReturnedQuantity;
            if (quantity < 1 || quantity > remaining)
            {
                return (null, new("invalid_quantity", remaining == 0
                    ? $"Every item of line {lineNumber} ({line.Product}) has already been returned."
                    : $"Line {lineNumber} ({line.Product}) can be returned with a quantity from 1 to {remaining}."));
            }
            var knownReason = Reasons.FirstOrDefault(r => r.Equals(reason?.Trim(), StringComparison.OrdinalIgnoreCase));
            if (knownReason is null)
            {
                return (null, new("invalid_reason",
                    $"'{reason}' isn't a valid return reason. Use one of: {string.Join(", ", Reasons)}."));
            }
            if (comment.Length > 500)
            {
                return (null, new("comment_too_long", "The comment can have at most 500 characters."));
            }

            var lines = order.Lines
                .Select(l => l.LineNumber == lineNumber ? l with { ReturnedQuantity = l.ReturnedQuantity + quantity } : l)
                .ToList();
            _orders[_orders.IndexOf(order)] = order with { Lines = lines };

            var created = new ReturnRecord($"RMA-{_nextReturn++}", order.OrderId, lineNumber, line.Product, quantity,
                knownReason, comment, "Requested", _clock.GetUtcNow());
            _returns.Add(created);
            return (created, null);
        }
    }
}
