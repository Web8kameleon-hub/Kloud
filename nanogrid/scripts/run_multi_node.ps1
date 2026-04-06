# Run Multi-Node Test for Nanogrid
# This script runs multiple instances of the node on different ports

# Node 1: 8080
Start-Process -NoNewWindow -FilePath "cargo" -ArgumentList "run" -Environment @{ "NODE_ID" = "1"; "LISTEN_PORT" = "8080"; "PEERS" = "2:8081,3:8082,4:8083,5:8084" }

# Node 2: 8081
Start-Process -NoNewWindow -FilePath "cargo" -ArgumentList "run" -Environment @{ "NODE_ID" = "2"; "LISTEN_PORT" = "8081"; "PEERS" = "1:8080,3:8082,4:8083,5:8084" }

# Node 3: 8082
Start-Process -NoNewWindow -FilePath "cargo" -ArgumentList "run" -Environment @{ "NODE_ID" = "3"; "LISTEN_PORT" = "8082"; "PEERS" = "1:8080,2:8081,4:8083,5:8084" }

# Node 4: 8083
Start-Process -NoNewWindow -FilePath "cargo" -ArgumentList "run" -Environment @{ "NODE_ID" = "4"; "LISTEN_PORT" = "8083"; "PEERS" = "1:8080,2:8081,3:8082,5:8084" }

# Node 5: 8084
Start-Process -NoNewWindow -FilePath "cargo" -ArgumentList "run" -Environment @{ "NODE_ID" = "5"; "LISTEN_PORT" = "8084"; "PEERS" = "1:8080,2:8081,3:8082,4:8083" }

Write-Host "Multi-node test started. Check logs for each node."