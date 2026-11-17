<!-- cspell:ignore aidevme logicapp Dataverse mcpservers keyvault MSYS PATHCONV ZSOLT containerapp aidevmesamples streamable -->

# Task: connect the Logic Apps MCP server to a Copilot Studio agent (Part 2, Steps 7 and 8)

Build the AIDevMe customer service agent in Copilot Studio, add the Part 2 logic app as an MCP server, and run the
post's test sequence with the activity map. The results replace the `[ZSOLT]` and `[VERIFY]` markers in Steps 7 and 8.

| | |
| --- | --- |
| Post | [Part 2](https://aidevme.com/copilot-studio-custom-mcp-server-logic-apps/), Step 3 (screenshot), Step 7 "Add the server to a Copilot Studio agent", Step 8 "Test in the test pane and read the activity map" |
| Learn | [Connect your agent to an existing MCP server](https://learn.microsoft.com/microsoft-copilot-studio/mcp-add-existing-server-to-agent) |
| Builds on | [PROVISIONING.md](../PROVISIONING.md), Phase 9; Part C also needs [TASK-part-2-oauth-easy-auth.md](TASK-part-2-oauth-easy-auth.md) |
| Where | Copilot Studio web portal (`https://copilotstudio.microsoft.com`) and the Azure portal. No CLI step needs `pac` |
| Time | Part 0: 30 minutes the first time. Parts A, B and D: about 1 hour. Part C: 30 minutes |
| Cost | Copilot Studio trial or developer environment: no charge. The WS1 plan keeps billing while it runs |
| Status | ⬜ Not started |

## The order of the parts

| Part | What | Auth on the logic app | Post |
| --- | --- | --- | --- |
| 0 | Power Platform environment and the agent | — | Step 7, "generative orchestration" |
| A | MCP onboarding wizard with **API key**, exactly as the post describes | Key-based | Step 7, "API key", "Choose the tools" |
| B | Test-only custom connector that also sends the demo header, so the agent can act as `CU-3001` | Key-based | Step 8 |
| D | The test sequence and the activity map | Key-based | Step 8 |
| C | MCP onboarding wizard with **OAuth 2.0 manual** | OAuth (after the Easy Auth task) | Step 7, "OAuth 2.0 (manual)" |

Do 0, A, B, D with the key first, then the Easy Auth task, then C. Authentication is one setting per logic app, so
switching to OAuth breaks A and B.

## The demo-customer problem, and the choice this task makes

The workflows read the customer from the `AIDevMe-Demo-Customer` header. The wizard sends only the authentication
header (`X-API-KEY`), so every call from a wizard connection arrives **without a customer**:

- `find_orders` answers `401`: "The customer isn't signed in."
- `get_order_status` and `create_return` answer "not found" for every order.

This task records that result in Part A (it shows why Part 5 exists), then uses a test-only custom connector in
Part B to send `AIDevMe-Demo-Customer: CU-3001`, so Step 8's prompts can run against real demo data.

What Part B does **not** do: change the workflows, add a default customer, or widen the demo shortcut. The header
value is fixed in the connector, so every user of that connection is `CU-3001`. That is exactly the risk the post
names. Use it only in your own test environment, delete it afterwards (Tear down), and never share the agent.

## Before you start

- [ ] Phase 9 of PROVISIONING.md is done and the key-based smoke test passes:

  ```sh
  set -a; source .env/.env; set +a
  LOGIC_HOST=$(az logicapp show -n logic-aidevme-orders-mcp -g rg-aidevme-mcp --query defaultHostName -o tsv | tr -d '\r')
  MCP_URL="https://$LOGIC_HOST/api/mcpservers/AIDevMeOrderService/mcp"
  sed "s#^MCP_URL=.*#MCP_URL=\"$MCP_URL\"#" src/logic-apps/test/smoke.sh | bash
  ```

  Expect a `create_return` result with an `RMA-` number.
- [ ] The MCP server authentication is **Key-based** (Azure portal → logic app → **Agents → MCP servers →
      Authentication**).
- [ ] `AIDEVME_MCP_KEY` in `.env/.env` is valid. You'll type it into Copilot Studio twice (Parts A and B); don't
      paste it anywhere else.
- [ ] You have the MCP server URL (`MCP_URL` above, or **Copy URL** on the MCP servers page).
- [ ] The demo data is fresh. Restart the Order Management API if earlier tests created returns:
      `az containerapp revision restart -n aidevme-orders-api -g rg-aidevme-mcp --revision $(az containerapp show -n aidevme-orders-api -g rg-aidevme-mcp --query properties.latestRevisionName -o tsv)`.
      `nextReturnNumber` starts at `5002` again.

---

## Part 0: environment and agent

### 0.1 Pick the tenant and the environment

| Decision | This task uses | Why |
| --- | --- | --- |
| Tenant | The workforce tenant **AIDevMe Samples** (`SAMPLES_TENANT_ID`) | Keeps the samples out of your production tenant. Same tenant as the Easy Auth registrations |
| Environment | `aidevme-dev`, type **Developer** (or the trial's default environment) | PLAN.md names `aidevme-dev`, `aidevme-test`, `aidevme-prod`; Part 7 needs Dev |
| Solution | `AIDevMeCustomerServiceAgent`, publisher prefix `cts` | PLAN.md: unpack it into `src/copilot-studio/solutions/` later (Part 7) |

Update PLAN.md's "Power Platform tenant" item with the choice when you're done.

### 0.2 Get Copilot Studio in the samples tenant

1. Open a private browser window and sign in to `https://copilotstudio.microsoft.com` with an admin account of the
   **samples** tenant (not your production account).
2. If you have no license, start the **Copilot Studio trial** when prompted. It creates a default environment.
3. For a named environment: **Power Platform admin center** (`https://admin.powerplatform.microsoft.com`) →
   **Manage → Environments → New**:

   | Field | Value |
   | --- | --- |
   | Name | `aidevme-dev` |
   | Region | Europe |
   | Type | **Developer** |
   | Add a Dataverse data store | Yes (Copilot Studio needs it) |

   Wait until the state is **Ready** (5 to 10 minutes).
4. In Copilot Studio, switch to `aidevme-dev` with the environment picker (top right).

**Check:** Copilot Studio opens in `aidevme-dev` without a license error.

### 0.3 Create the solution (for Part 7)

1. Copilot Studio → **Solutions** (or `https://make.powerapps.com` → `aidevme-dev` → **Solutions**) → **New solution**.
2. Display name `AIDevMe Customer Service Agent`, name `AIDevMeCustomerServiceAgent`.
3. **New publisher**: display name `AIDevMe Samples`, name `aidevmesamples`, prefix `cts`.
4. **Settings → Solutions → Set preferred solution**: `AIDevMeCustomerServiceAgent`, so the agent and connectors
   land in it.

### 0.4 Create the agent

1. **Agents → New agent → Configure** (skip the chat-based setup).
2. Fill in:

   | Field | Value |
   | --- | --- |
   | Name | `AIDevMe customer service` |
   | Description | `Answers AIDevMe customers' questions about their orders and starts returns.` |
   | Instructions | The text block from [`src/copilot-studio/agent-instructions.md`](../../../src/copilot-studio/agent-instructions.md) (Part 6) |
   | Language | English |

3. **Create**.
4. **Settings → Generative AI → Orchestration**: **Generative orchestration** (Yes). MCP needs it.
5. **Knowledge**: add none. Under **Settings → Generative AI**, turn off **Use general knowledge** and **Web search**,
   so the answers come only from the tools.
6. **Save**.

**Check:** the agent's **Overview** shows generative orchestration on, no knowledge sources.

Note the harness: these steps are for the **standard harness**. If your tenant shows the new agents experience
(Microsoft Copilot harness, preview), testing uses **Preview** and the **activity trace** instead (post, Step 8).
Record which one you used.

---

## Part A: the wizard with an API key (post, Step 7)

### A.1 Add the MCP server

1. Agent → **Tools → Add a tool → New tool → Model Context Protocol**. The MCP onboarding wizard opens.
2. Fill in:

   | Field | Value |
   | --- | --- |
   | Server name | `AIDevMe Order Service` |
   | Server description | `Finds a signed-in customer's AIDevMe orders, returns order status and starts returns.` (the Step 3 description) |
   | Server URL | `MCP_URL`: `https://<logic-app-host>/api/mcpservers/AIDevMeOrderService/mcp` |
   | Authentication | **API key** |
   | Type | **Header** |
   | Header name | `X-API-KEY` |

3. **Create**. The **Add tool** dialog opens.
4. **Create a new connection**, enter `AIDEVME_MCP_KEY` as the key, **Create**.
5. **Add to agent**.

**Check:** **Tools** lists `AIDevMe Order Service` as an MCP server.

### A.2 Choose the tools (post, "Choose the tools")

1. Open the server's settings page from **Tools**.
2. Check that it lists `find_orders`, `get_order_status` and `create_return` with the descriptions from the workflows.
3. Note **Allow all** is on. Turn it off and on again once to see the per-tool switches; leave it on.

Record: do the three descriptions match the Request trigger descriptions (post, Step 1)?

### A.3 Run the identity test

1. **Test your agent** → **⋯ → Show activity map when testing**.
2. **New test session** (the refresh icon), then send:

   | # | Prompt | Expected tool and input | Expected result without a customer |
   | --- | --- | --- | --- |
   | A1 | "Show me my orders." | `find_orders`, no `customerId` | Tool error, `401` "The customer isn't signed in…"; the agent asks the customer to sign in |
   | A2 | "Where is my order SO-10023?" | `get_order_status`, `orderId: SO-10023` | "Not found"; the agent asks to check the number |

3. For each prompt, record in the results table (end of this file): the tool the activity map shows, its inputs, the
   output, and the agent's answer.
4. Screenshot the activity map of A1 (it shows the identity gap in one picture).

**Check:** both calls reach the logic app. Azure portal → `find_orders` → **Run history** shows a run with status
`401` response at the time of A1.

---

## Part B: test-only connector with the demo header (for Step 8)

`[VERIFY]` that a header parameter in an MCP custom connector reaches the server. The repo's
[`orders-mcp-custom-headers.swagger.yaml`](../../../src/copilot-studio/connectors/orders-mcp-custom-headers.swagger.yaml)
uses the same idea for `AIDevMe-Market`; this part is its first real test.

### B.1 Write the connector definition

Save this as `aidevme-logic-apps-demo.swagger.yaml` in your scratch folder, **not** in the repo (it carries a fixed
customer). Replace `<logic-app-host>` with `LOGIC_HOST`.

```yaml
swagger: '2.0'
info:
  title: AIDevMe Logic Apps MCP (demo customer)
  description: Test only. Calls the Part 2 logic app as demo customer CU-3001.
  version: 1.0.0
host: <logic-app-host>
basePath: /api/mcpservers/AIDevMeOrderService
schemes:
  - https
securityDefinitions:
  api_key:
    type: apiKey
    in: header
    name: X-API-KEY
security:
  - api_key: []
paths:
  /mcp:
    post:
      summary: AIDevMe order service, demo customer CU-3001
      x-ms-agentic-protocol: mcp-streamable-1.0
      operationId: InvokeMCP
      parameters:
        - name: AIDevMe-Demo-Customer
          in: header
          type: string
          required: true
          default: CU-3001
          x-ms-visibility: internal
          description: Demo customer. Test stub, see Part 2.
      responses:
        '200':
          description: Success
```

`x-ms-visibility: internal` with a `default` sends the value on every call and hides it from the agent, so the model
can't change the customer.

### B.2 Import it

1. Agent → **Tools → Add a tool → New tool → Custom connector**. Power Apps opens in `aidevme-dev`.
2. **New custom connector → Import an OpenAPI file**, name `AIDevMe Logic Apps MCP demo`, select the file,
   **Continue**.
3. **General**: check the host and base URL. **Security**: **API Key**, parameter label `API key`, name `X-API-KEY`,
   location **Header**.
4. **Create connector**. (Leave **Definition** as imported; the MCP connector has no actions to edit.)
5. **Test → New connection**, enter `AIDEVME_MCP_KEY`, **Create connection**.

### B.3 Swap the tools in the agent

1. Back in Copilot Studio → agent → **Tools → Add a tool**. Search `AIDevMe Logic Apps MCP demo`, select it, choose
   the connection from B.2, **Add to agent**.
2. **Disable** the Part A server (`AIDevMe Order Service` → **⋯ → Disable**, or turn its tools off), so only one
   server answers.

**Check:** a test prompt "Show me my orders." now lists `SO-10035`, `SO-10031`, `SO-10023` and `SO-10019`. If it
still gets `401`, the header doesn't reach the workflow: open the `find_orders` run → trigger **raw outputs** →
`headers`, and record whether `AIDevMe-Demo-Customer` is there. Then skip to Part D with the A results only.

---

## Part D: the test sequence and the activity map (post, Step 8)

### D.1 Prepare

1. **Test your agent** → **Show activity map when testing** on.
2. Start a **new test session** before each prompt, unless the prompt continues the one before (D3 continues D2).
3. Keep three windows open: the activity map, the logic app **Run history** for the tool, and the Order Management
   API's log stream (`az containerapp logs show -n aidevme-orders-api -g rg-aidevme-mcp --follow`).

### D.2 Run the post's four prompts

| # | Prompt (post, Step 8) | Expected tool and inputs | Expected behavior |
| --- | --- | --- | --- |
| D1 | "Where is my order SO-10023?" | `get_order_status`, `orderId: SO-10023`, nothing else | Delivered 7 days ago by DHL, three lines (kettle, toaster, glass set) |
| D2 | "I ordered a kettle last month, but I don't have the order number." | `find_orders`, ideally with `from`/`to`; never asks for a customer ID | Finds `SO-10023` |
| D3 | "The kettle arrived broken, I want to return it." (same session as D2) | `get_order_status` if needed, then `create_return` only after a yes | Confirms item, quantity 1 and reason before the call; then `lineNumber: 1`, `quantity: 1`, `reason: Damaged`, and returns `RMA-5002` |
| D4 | "Show me the status of SO-10027." | `get_order_status`, `orderId: SO-10027` | "Not found", same wording as for a number that doesn't exist; no hint about another customer |

Then one extra control:

| # | Prompt | Expected |
| --- | --- | --- |
| D5 | "Where is my order SO-99999?" | Same "not found" as D4. Compare the two answers word by word |

For D3, answer "yes" when the agent asks for confirmation. If it calls `create_return` before asking, record that:
it's a Part 6 finding (instructions versus descriptions).

### D.3 Capture

1. **Screenshot** the activity map of D2 → D3 (the `get_order_status` → `create_return` sequence). This fills the post's
   `[ZSOLT: add an activity map screenshot …]` in Step 8. Crop out the tenant name and your account.
2. **Screenshot** the Azure portal **MCP servers** page with `AIDevMeOrderService` and its three workflows. This fills
   `[ZSOLT: add a screenshot of the MCP servers page …]` in Step 3. Crop out the subscription and the host name.
3. For each prompt, open the workflow run and check the trigger inputs match the activity map's inputs.
4. Save the screenshots in the blog repo's post folder, `51-copilot-studio-custom-mcp-server-logic-apps/images/`, with
   descriptive names (for example `copilot-studio-activity-map-get-order-status-create-return.png`).

### D.4 Where to look when a test fails (post, Step 8)

| What you see | Look at | Typical cause |
| --- | --- | --- |
| The tool isn't called at all | The tool and server descriptions | Description doesn't match the question; server disabled; **Allow all** off |
| Called with wrong inputs | Activity map inputs versus the Step 1 schema | Description of the input; enum values |
| Right inputs, the run failed | Workflow run → **HTTP** action | Order Management API `401` (managed identity not allowed) or `404` |
| `401` "isn't signed in" | Trigger raw outputs → `headers` | No `AIDevMe-Demo-Customer` (Part A behavior) |
| Tool error "Mcp-Session-Id is required" | — | Shouldn't happen with Copilot Studio; record it if it does |
| Tool list empty after a change | — | Copilot Studio can take 12 to 24 hours to show changed tools after republishing a custom connector |

---

## Part C: the wizard with OAuth 2.0 manual (post, Step 7)

Do this after [TASK-part-2-oauth-easy-auth.md](TASK-part-2-oauth-easy-auth.md), steps 1 to 5. You need
`SAMPLES_TENANT_ID`, `LOGIC_MCP_SERVER_APP_ID`, `LOGIC_MCP_CLIENT_APP_ID` and the secret `logic-mcp-client-secret`.

### C.1 Read the client secret for the wizard

Show it once, copy it into the wizard, then clear the terminal:

```sh
az keyvault secret show --vault-name kv-aidevme-mcp --name logic-mcp-client-secret --query value -o tsv
clear
```

### C.2 Add the server with OAuth

1. Agent → **Tools → Add a tool → New tool → Model Context Protocol**.
2. Fill in:

   | Field | Value |
   | --- | --- |
   | Server name | `AIDevMe Order Service (OAuth)` |
   | Server description | The Step 3 description |
   | Server URL | `MCP_URL` |
   | Authentication | **OAuth 2.0** |
   | Type | **Manual** |
   | Client ID | `LOGIC_MCP_CLIENT_APP_ID` |
   | Client secret | The value from C.1 |
   | Authorization URL | `https://login.microsoftonline.com/<SAMPLES_TENANT_ID>/oauth2/v2.0/authorize` |
   | Token URL template | `https://login.microsoftonline.com/<SAMPLES_TENANT_ID>/oauth2/v2.0/token` |
   | Refresh URL | `https://login.microsoftonline.com/<SAMPLES_TENANT_ID>/oauth2/v2.0/token` |
   | Scopes | `api://<LOGIC_MCP_SERVER_APP_ID>/user_impersonation offline_access` |

3. **Create**. Copy the **callback URL** the wizard shows. Don't select **Next** yet.

### C.3 Register the callback URL

```sh
CALLBACK_URL="<paste the callback URL>"
az ad app update --id "$LOGIC_MCP_CLIENT_APP_ID" --web-redirect-uris "$CALLBACK_URL"
az ad app show --id "$LOGIC_MCP_CLIENT_APP_ID" --query "web.redirectUris" -o tsv
```

Portal equivalent: client app → **Authentication → Add a platform → Web** → paste the URL → **Configure**.

The client's API permission and admin consent come from the Easy Auth task (step 3.1). Easy Auth's **Allowed client
applications** must contain `LOGIC_MCP_CLIENT_APP_ID` (step 4 there).

### C.4 Connect and test

1. Back in the wizard: **Next → Create a new connection**. A sign-in window opens; sign in with a samples tenant user.
2. **Add to agent**. Disable the key-based servers from A and B.
3. New test session: "Where is my order SO-10023?"

Expected: the call reaches the logic app with a token, but without the demo header the answer is "not found", as in
Part A. That's the post's point: OAuth secures the endpoint, but the workflows still can't name the customer. Check
the run's trigger raw outputs for the Easy Auth headers (Easy Auth task, 6.3), now with a token from Copilot Studio.

Record every field that caused trouble on the first try and the exact error. This fills
`[ZSOLT: note which OAuth field caused trouble …]` in Step 7.

---

## Results

Fill this in during the test.

| Test | Harness | Tool called | Inputs | Output | Agent answer | As expected? |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | | | | | | |
| A2 | | | | | | |
| B check | | | | | | |
| D1 | | | | | | |
| D2 | | | | | | |
| D3 | | | | | | |
| D4 | | | | | | |
| D5 | | | | | | |
| C | | | | | | |

| Question | Post location | Answer |
| --- | --- | --- |
| Does a connector header parameter reach the workflow? | "The user is a customer"; repo `orders-mcp-custom-headers.swagger.yaml` | |
| Does one registration work as client and server? | Step 7, OAuth `[VERIFY]` | Not tested here (two registrations); note it |
| Does the OAuth path work end to end with these fields? | Step 7, `[VERIFY: run the OAuth path end to end …]` | |
| Which OAuth field caused trouble? | Step 7, `[ZSOLT]` | |
| Are D4 and D5 word for word the same? | Step 8, item 4 | |

## Update the post and the repo afterwards

- **Post, Step 3:** insert the MCP servers screenshot, remove the `[ZSOLT]` marker.
- **Post, Step 7:** replace the OAuth `[VERIFY]` and `[ZSOLT]` markers with what C showed. Fix the scope format
  (`api://<application-ID-URI>/…` reads `api://api://…`; see the Easy Auth task).
- **Post, Step 7, "API key":** add one sentence that a wizard connection sends no customer, so `find_orders` answers
  `401`, with the A1 result.
- **Post, Step 8:** insert the activity map screenshot, remove the `[ZSOLT]` marker. Check prompt 2's wording: with
  the demo data, `SO-10023` was ordered about 10 days before the test, so "last month" can make the model filter it
  out. If D2 fails for that reason, change it to "last week" or "recently".
- **Repo:** if B worked, decide whether a demo-header connector belongs in `src/copilot-studio/connectors/` (it would
  need a placeholder host and a clear test-only warning), and record the decision in PLAN.md.
- **PLAN.md:** the Power Platform tenant and environment decision; "Copilot Studio solutions" once the solution is
  exported (Part 7).

## Tear down

| What | Where |
| --- | --- |
| Test-only connector and its connection (Part B) | Power Apps → **Custom connectors** → `AIDevMe Logic Apps MCP demo` → **Delete**; **Connections** → delete its connection |
| Wizard connections (A, C) | Power Apps → **Connections** |
| The agent | Keep it in `aidevme-dev` for Parts 4 to 7, or **Agents → ⋯ → Delete** |
| Callback URL on the client app | `az ad app update --id "$LOGIC_MCP_CLIENT_APP_ID" --web-redirect-uris` (no value) |
| The logic app and its plan | PROVISIONING.md, Tear down. Do this right after the session; WS1 bills by the hour |
| The API key | Logic app → **Agents → MCP servers → Authentication** → regenerate, so the key typed into Copilot Studio stops working |
