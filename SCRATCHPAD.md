## Module Execution

Modules will have different runtime behaviors. Some may be one-off - an initial environment scan, for instance. Some will have a regular cadence, like the heartbeat module. And others, like a crypto miner, will be continuous. To account for all of these at once, we'll need some form of parallelism.

Multithreading makes more sense than threading, because threading shares a common memory space - multithreading keeps each process isolated.

We'll want to make sure for those with a regular cadence, they do not overrun the candence and cause multiple instance to spin up. We'd want to enforce a timeout, and log the overrun. C2 should somehow access this data to show which modules are having regular issues.

We want to make sure we don't allow heavier modules to churn through memory. This would both impact performance, and potentially lead to discovery.

The APScheduler library seems like is would manage this very well. It allows for one time execution, scheduled cron jobs, and interval-based. Processes are isolated, and can even leverage persistent storage to survive restarts.
