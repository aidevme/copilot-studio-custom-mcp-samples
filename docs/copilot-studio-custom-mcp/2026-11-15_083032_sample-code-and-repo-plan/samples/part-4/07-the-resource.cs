using System.ComponentModel;
using ModelContextProtocol.Server;

namespace AIDevMe.OrdersMcp.Resources;

[McpServerResourceType]
public class PolicyResources
{
    public const string ReturnPolicyUri = "aidevme://policies/returns";

    private const string ReturnPolicy = """
        # AIDevMe return policy (fictional demo)

        - Delivered orders can be returned within 30 days after the delivery date.
        - Each return covers one order line, up to the ordered quantity minus earlier returns.
        - Reasons: Damaged, WrongItem, NotAsDescribed, NoLongerNeeded.
        - The customer receives a return label by email within one business day.
        - Refunds go to the original payment method after the warehouse receives the item.
        """;

    [McpServerResource(UriTemplate = ReturnPolicyUri, Name = "return_policy",
        Title = "AIDevMe return policy", MimeType = "text/markdown")]
    [Description("AIDevMe's return rules: 30-day window after delivery, quantities, reasons, labels and refunds.")]
    public static string GetReturnPolicy() => ReturnPolicy;
}
