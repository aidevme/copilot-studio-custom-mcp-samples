# Start the sample server
dotnet run --urls http://localhost:5080

# List the tools as a client sees them
npx -y @modelcontextprotocol/inspector@2.15.0 --cli http://localhost:5080/mcp --transport http --method tools/list

# Call a tool as demo customer CU-3001
npx -y @modelcontextprotocol/inspector@2.15.0 --cli http://localhost:5080/mcp --transport http \
  --header "Contoso-Demo-Customer: CU-3001" \
  --method tools/call --tool-name get_order_status --tool-arg orderId=SO-10023

# Negative test: another customer's order must look like a missing one
npx -y @modelcontextprotocol/inspector@2.15.0 --cli http://localhost:5080/mcp --transport http \
  --header "Contoso-Demo-Customer: CU-3001" \
  --method tools/call --tool-name get_order_status --tool-arg orderId=SO-10040
