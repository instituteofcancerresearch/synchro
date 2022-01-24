[![Python Version](https://img.shields.io/pypi/pyversions/synchro.svg)](https://pypi.org/project/synchro)
[![PyPI](https://img.shields.io/pypi/v/synchro.svg)](https://pypi.org/project/synchro)
[![Downloads](https://pepy.tech/badge/synchro)](https://pepy.tech/project/synchro)
[![Wheel](https://img.shields.io/pypi/wheel/synchro.svg)](https://pypi.org/project/synchro)
[![Development Status](https://img.shields.io/pypi/status/synchro.svg)](https://github.com/instituteofcancerresearch/synchro)
[![Tests](https://img.shields.io/github/workflow/status/instituteofcancerresearch/synchro/tests)](
    https://github.com/instituteofcancerresearch/synchro/actions)
[![Coverage Status](https://coveralls.io/repos/github/instituteofcancerresearch/synchro/badge.svg?branch=main)](https://coveralls.io/github/instituteofcancerresearch/synchro?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
# synchro
Customisable file transfers using rsync

---
## About
Synchro is a simple python-based tool for customisable file movements, e.g. copying data to a backup server.

Synchro currently supports/includes:
* Transfer via ssh
* Archiving using tar (and option extraction)
* Option to only transfer data when a specific file is present
* Logging to file

## To install
To install, you need a Unix-based system with Python (>=3.9) installed, and then:

```bash
pip install synchro
```

However, it is recommended to install conda (e.g. [miniconda](https://docs.conda.io/en/latest/miniconda.html)) first and create a new environment:

```bash
conda create --name synchro python=3.10
conda activate synchro
pip install synchro
```

If you don't have rsync installed, you will need to do so. E.g. on macOS 
it can be installed with homebrew:
```bash
brew install rsync
```

## To use
`synchro` has two modes of use on the command line, either with flags, or a config file.

### Command line flags
**Not yet implemented**


### Config file
The only input is the path to a source directory (the one being transferred).
```bash
synchro /path/to/config.conf
```

This source directory must contain a `synchro.conf` file which contains the 
information needed for the transfer. Including:
* `source` - Where the data comes from (contents of directory will be copied) e.g. `/path/to/source_directory`)
* `destination` - Where to move the data to e.g. `/path/to/destination_directory`)
* `tar` - Tar the data before copying? e.g. `y` 
* `untar` - Untar the data after copying? e.g. `y`
* `create_dest` - Create the destination directory if it doesn't exist? e.g. `y`
* `transfer_ready_file` - A file that must exist in the source directory
(or relative path) for the transfer to initative. This option is ignored if the line is
missing from `synchro.conf`.
* `permissions`  - Permissions for the destination file, in the
[chmod numerical format](Ohttps://chmodcommand.com/chmod-777/). e.g. `777`.
This option is ignored and defaults to `770` if the line is missing from `synchro.conf`.
* `owner`  - Username for ownership of the transferred files. 
This option is ignored and defaults to that of the source directory 
if the line is missing from `synchro.conf`.
* `group`  - Group for ownership of the transferred files. 
This option is ignored and defaults to that of the source directory 
if the line is missing from `synchro.conf`.

**Example:**
```text
source = /path/to/source_directory
destination = /path/to/destination_directory
tar = y
untar = y 
create_dest = y 
transfer_ready_file = ready.txt
permissions = 777
owner = user1
group = staff
```

N.B. the destination can also be on a remote host 
([an ssh key must be set up](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)), 
e.g.:
```text
destination = user@IP:/path/to/destination_directory
```

## To use with cron
*N.B. This assumes you've installed in a conda environment*

**Example - running file transfers hourly (tested on CentOS)**
* Create a text file in `/etc/cron.hourly` called `synchro`
```bash
cd /etc/cron.hourly
touch synchro
```
* Add `synchro` commands to the text file using the full path to the synchro executable
```text
/home/user/miniconda3/envs/synchro/bin/synchro /path/to/config_1.conf
/home/user/miniconda3/envs/synchro/bin/synchro /path/to/config_2.conf
```

This will then try to backup the directories specified in `config_1.conf` & `config_2.conf` every hour.