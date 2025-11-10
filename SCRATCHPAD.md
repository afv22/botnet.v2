## Module Execution

Modules will have different runtime behaviors. Some may be one-off - an initial environment scan, for instance. Some will have a regular cadence, like the heartbeat module. And others, like a crypto miner, will be continuous. To account for all of these at once, we'll need some form of parallelism.

Multithreading makes more sense than threading, because threading shares a common memory space - multithreading keeps each process isolated.

We'll want to make sure for those with a regular cadence, they do not overrun the candence and cause multiple instance to spin up. We'd want to enforce a timeout, and log the overrun. C2 should somehow access this data to show which modules are having regular issues.

We want to make sure we don't allow heavier modules to churn through memory. This would both impact performance, and potentially lead to discovery.

The APScheduler library seems like is would manage this very well. It allows for one time execution, scheduled cron jobs, and interval-based. Processes are isolated, and can even leverage persistent storage to survive restarts.

## Module Download

The C2 should manage a version ticker, along with which module was updated in this version.

Each bot should remember which version it has most recently successfully fetched. When it sends a heartbeat, it should request the current version number from the C2. If the bot's local version number is outdated, it should request all changes since.

Let's say a bot is very out of date, and some modules have been updated multiple times. The bot should only fetch the most recent version rather than downloading each one. C2 should maintain a state table with the hashes of the current modules, and a changelog. When a bot requests new files, C2 should go through the changelog, note which have been touched since the bot's latest version, and send back the IDs and hashes of needed files. The bot then requests the most recent versions. 

Thanks to the dynamic scheduler registrations, we don't need to explicitly register the new modules, only write them to the executables directory. Once successfully written, the local version number should be updated.

If the heartbeat jobs runs over the configured interval while downloading the new module, APScheduler won't run the new job instance since interval jobs are configured to only have one concurrent instance. This will look to the C2 like the bot is temporarily offline, but if the heartbeat was allowed to continue, it wouldn't realize the download was already occuring, and request it again. If the download fails though, the next heartbeat will naturally attempt the download again since the version number will still be outdated.

We'll probably want to set up some form of monitoring, backoff, or something else if downloads repeatedly fail.

The module hashes should be sent to verify accuracy.

Need to figure out how to start the new modules.

1. Bot send Heartbeat. C2 returns latest version number.
2. If bot's latest version is outdated, bot requests files that have since been modified. C2 returns file names and hashes.
3. Bot requests each file. C2 returns file signed with private key.
4. Bot verifies private key.
5. Bot saves new file to executables folder.