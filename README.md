# Botnet Proof of Concept

For educational and research purposes only.

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

- [x] Basic C2 server with heartbeat endpoint
- [x] Basic bot sending heartbeat

### Stage 2: Monitoring

- [x] C2 stores all clients in a DB, along with last beat time
- [x] C2 can provide basic stats about clients (lifetime, currently connected, etc)

### Stage 3: Execution Modules

- [x] C2 broadcasts new execution modules
- [x] Bots fetch new modules and save them locally
- [x] Bots execute new modules

### Stage 4: Improved Monitoring

- [ ] C2 can monitor which modules are regularly timing out
- [ ] C2 can monitor which modules bots have
