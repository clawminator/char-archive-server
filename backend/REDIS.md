To disable RDB snapshotting, you can modify the Redis configuration file (`redis.conf`) and set the `save` directive to an empty value. Here's how you can do it:

1. Open the `redis.conf` file in a text editor.

2. Find the `save` directive in the configuration file. It may look something like this:
   ```
   save 900 1
   save 300 10
   save 60 10000
   ```

3. Comment out or remove all the `save` lines to disable RDB snapshotting. For example:
   ```
   # save 900 1
   # save 300 10
   # save 60 10000
   ```

4. Save the changes to the `redis.conf` file.

5. Restart your Redis server for the changes to take effect.

By disabling RDB snapshotting, Redis will no longer attempt to save snapshots to disk, and you won't encounter the error related to RDB persistence.

To disable the DB:

```
# dbfilename dump.rdb
```