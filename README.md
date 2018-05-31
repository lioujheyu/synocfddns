The reason choosing python3 is becuase there is an issue in installing pip in synology's python2. 
See [here](https://github.com/pypa/pip/issues/3588) for more detail about the issue

# Installation
1. Install python3 from synology package in NAS
2. ssh into NAS
3. Install pip for python3, then get python-cloudflare
```
    sudo python3 -m ensurepip
    sudo python3 -m pip install --upgrade pip
    sudo python3 -m pip install python-cloudflare
```
