# Botnet Proof of Concept

## Features
- Command & Control Server
  - Tracks active bots
  - Distributes propagation modules
  - Distributes execution modules
- Bots
  - Sends heartbeat to C2
  - Downloads new modules
  - Executes modules

## Roadmap

### Stage 1: Boilerplate
- [ ] Basic C2 server with heartbeat endpoint
- [ ] Basic bot sending heartbeat

### State 2: Monitoring
- [ ] C2 stores all clients in a DB, along with last beat time
- [ ] C2 can provide basic stats about clients (lifetime, currently connected, etc)

### State 3: Execution Modules
- [ ] C2 broadcasts new execution modules
- [ ] Bots fetch new modules and save them locally
- [ ] Bots execute modules

### State 4: Propagation Modules