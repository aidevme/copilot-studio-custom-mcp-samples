# responses

Real responses of the Part 4 C# server to the requests in `../protocol-examples.http`, as quoted in Part 1.

| File | Request | Customer |
| --- | --- | --- |
| `tools-list.json` | `tools/list` | `CU-3001` |
| `tools-call-get-order-status.json` | `get_order_status` for `SO-10023` | `CU-3001` |
| `tools-call-not-found.json` | `get_order_status` for `SO-10027`, which belongs to `CU-3002` | `CU-3001` |
| `tools-call-create-return.json` | `create_return` for line 1 of `SO-10023`, reason `Damaged` | `CU-3001` |

The demo data counts dates back from the day the server starts, so dates and the `createdAt` time differ on every
run. A second `create_return` on the same running server gets the next RMA number.
