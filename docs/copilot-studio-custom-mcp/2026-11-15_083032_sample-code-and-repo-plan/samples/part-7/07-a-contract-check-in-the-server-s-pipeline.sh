$ node check-tool-contract.mjs tools-approved.json tools-candidate.json
BREAKING  get_order_status   input 'postalCode' is now required
APPROVAL  issue_refund       new tool: needs the approval checklist before production
REVIEW    create_return      description changed (the orchestrator routes on it)
ADDITIVE  find_orders        new optional input 'pageSize'
$ echo $?
1
