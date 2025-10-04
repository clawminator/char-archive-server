# Install Python 3.11
```shell
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 python3.11-dev python3.11-venv
```

# Install MySQL Dev Libraries
```shell
sudo apt install pkg-config default-libmysqlclient-dev build-essential
```

# Download Spacy Model
```shell
python -m spacy download en_core_web_sm
```

## LOC

```shell
cloc . --exclude-dir=.venv --include-ext=py
```

# Elasticsearch Setup

```
PUT /proxy_stats
{
  "mappings": {
    "properties": {
      "timestamp": {
        "type": "date",
        "format": "epoch_second"
      }
    }
  }
}
```