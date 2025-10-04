# Mount NFS Shares in LXC

Ok, this is really confusing. Basically, when you mount something on the Proxmox host, you have to convert the user and group IDs of the share filesystem. So, if it's mounted as `1000:22222` on the Proxmox host you will have to specify that you want to map it to the user `110:118` (in this example this is the Jellyfin user and group).


### Delete any existing users/groups with your target UID/GID

If a group or user exists with the same UID or GID of the owner of your share, any files owned by the user or group on the container will be set to `nobody:nogroup`. You must delete the user or group, mount the share, map the UID/GID, then re-create the user or group.

Any files you don't want to delete must be `chown`-ed to root and then changed back to your target user/group.

### Stop the container

```shell
pct stop [container]
```

### Mount path in the container

```shell
pct set [container] -mp0 [path to share on host],mp=[where to mount the share in the container]
```

### Find the UID/GID of the share

```shell
ls -n [path to share on host]
```

<br>

This will give you something like this:
```shell
root@duna:~# ls -n /mnt/lxc/nfs/archivebox/
total 4
drwxrws--- 13 1000 22222 4096 Feb  5 09:21 archive
```

### Set the UID/GID map

Use lxc-map-id.py to generate the mappings.

```shell
./lxc-map-id.py [host UID]:[HOST GID]=[container UID]:[container GID]
```

<br>

If I wanted to map `1000:22222` on the Proxmox host to `110:118` on the container, then I would do this:
```shell
$ ./lxc-map-id.py 110:118=1000:22222
user 1000 HOST → 110 CONTAINER
group 22222 HOST → 118 CONTAINER

====================================================

# Add to /etc/pve/lxc/<container_id>.conf:
lxc.idmap: u 0 100000 110
lxc.idmap: g 0 100000 118
lxc.idmap: u 110 1000 1
lxc.idmap: g 118 22222 1
lxc.idmap: u 111 100111 65425
lxc.idmap: g 119 100119 65417

# Add to /etc/subuid:
root:1000:1

# Add to /etc/subgid:
root:22222:1
```

<br>

Then, modify the container's LXC config, `/etc/subuid`, and `/etc/subgid`.

Now you can start the container.