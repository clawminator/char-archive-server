# chub-archive-server

_Website and backend server for the Character Archive._

This is the source code for the char-archive website. The software stack consists of a Python backend, Postgres database, Vue.js frontend, and Meilisearch index.

No commit history is provided because this project wasn't developed for public consumption of the source.

Remember to have fun.



## System Requirements

This server ran on this machine:

- AMD Ryzen 7 5700X 8-Core Processor
- 128GB RAM (probably only need 64GB, this was originally for Elasticsearch)
- 2x 1TB SATA SSD
- 2x 1TB Samsung 990 Pro

The database and files are stored on the 990s, the VM/CT OSes are on the SATA SSDs.



## Host Setup

This is a very very rough guide on how to get things up and running. I ran everything on Proxmox. These are the hosts:



### Website

`char-archive`

CT. 12 cores, 13GB RAM. Runs the website and database.




1. Install Postgres and Python 3.12
2. Create your venv and install the requirements
3. Import the database and put the files somewhere
4. Figure out where the database connection config strings are (there are a few) and enter your details
5. Enable and start the Systemd timers
6. Enable and start the `archive-server`  service
7. Enable and start the `frontend-msg` service
8. Deploy the image proxy Cloudflare Worker in `Workers/image-proxy` 
9. Install the GeoIP database (see `GeoIP.md`)
10. Install node.js version `22.15.0`
11. Go to `search-parser/` and do `npm install`
12. Enable and start the `search-parser.service`
13. Download the latest release of [example/crazy-file-server](https://github.com/example/crazy-file-server). This serves the file browser and was originally built for serving the entire archive when it was just a collection of raw files. An example config file is located at `backend/crazyfs.yaml`. Don't worry about setting up Elasticsearch it isn't needed anymore.
14. Install and enable `crazyfs.service`
15. Set up the nginx website. An example config is provided.



You will probably have to dive into the code to figure out how the various services work. It isn't very complicated (the most complicated part is how the individual sites are abstracted and handled) but it wasn't designed to be distributed so there is no unified config.

I know for a fact that you will have to update the frontend code to account for your new website domain. The current code is set up with the assumption that it's running on `char-archive.evulid.cc`.



### Meilisearch

`char-meili`

CT. 10 cores, 34GB RAM (could shrink these down probably 50%). Runs exclusively Meilisearch.



1. Install Meilisearch
1. `python3 create-meilisearch.py`



### Proxy Router

`proxy`

CT. 4 cores, 4GB RAM. Runs a proxy router/load balancer. I don't recommend running this on a cloud VM as you will be moving multiple terabytes of data per month.

1. Set up or gain access to at least 1 proxy server. Squid works fine.
2. Download the latest release from [github.com/example/proxy-loadbalancer/releases](https://github.com/example/proxy-loadbalancer/releases). I put it in `/srv/loadbalancer`.
3. Follow the `README.md` file in `proxy-loadbalancer` to install it



I recommend setting this value in the config.

```yaml
thirdparty_test_urls:
  - https://rentry.org/8ygmz29h
  - https://files.catbox.moe/1hvrlj.png
  - https://gateway.chub.ai/search?excludetopics=&first=20&page=1&namespace=*&search=sex&include_forks=true&nsfw=false&nsfw_only=false&require_custom_prompt=false&require_example_dialogues=false&require_images=false&require_expressions=false&nsfl=false&asc=false&min_ai_rating=0&min_tokens=50&max_tokens=100000&chub=true&require_lore=false&exclude_mine=true&require_lore_embedded=false&require_lore_linked=false&sort=default&min_tags=2&topics=&inclusive_or=false&recommended_verified=false&require_alternate_greetings=false&count=false

```



### NFS Storage Server

`char-datastore`

VM. 4 cores, 5GB RAM (could increase these by 50%). Stores the data and ran an NFS server.

My `/etc/exports` file contains this:

```
/mnt/share 10.1.0.8(rw,sync,no_subtree_check) 10.1.0.11(rw,sync,no_subtree_check)
```

The two IPs are the `char-archive` and the `char-scraper` hosts.

In your Proxmox host, you will have to mount the NFS share since you can't easily mount it in the CTs. I put this in its `/etc/fstab`:

```
10.1.0.9:/mnt/share /mnt/lxc/nfs/share nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0
```

Where `10.1.0.9` is the `char-datastore` IP.

Then give the CT access to it. For example, this is `/etc/pve/lxc/xxx.conf`:

```
mp0: /mnt/lxc/nfs/share,mp=/mnt/share
```

You may encounter issues regarding UIDs/GIDs. This can be a nightmare. The file `other/mount-nfs-shares-in-lxc.md` tries to help you but you're on your own.



### Scraper

`char-scraper`

VM. 8 cores, 45GB RAM. Ran the web scrapers.

1. Create a new non-root user
2. Change to that user
3. `git clone https://github.com/example/chub-archive-scraper`
4. Create a venv and install the requirements
5. Install the services in `systemd/` and enable the timers

The scraper is a spaghetti code disaster. It's gone through like 3 separate rewrites but has not gotten any less complicated. That said, a lot of work has been put into making sure the scrapers are reliable.



## Data Setup

Download the last torrent and place the files on `char-datastore`. Then import the database. It's pretty simple.



## Cloudflare

The website uses pretty heavy Cloudflare caching. Make sure to purchase `Cache Reserve`. The folder `cloudflare-cache-rules/` contains screenshots of the rules you need to create.
