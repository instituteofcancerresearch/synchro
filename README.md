# synchro
Customisable file transfers using rsync

---

## To install
To install, you need a Unix-based system with conda (miniconda or anaconda) installed.

```bash
conda create --name synchro python=3.9
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
synchro /path/to/source_directory
```

This source directory must contain a `synchro.conf` file which contains the 
information needed for the transfer. Including:
* `destination` - Where to move the data to e.g. `/path/to/destination_directory`)
* `untar` - Untar the data after copying? e.g. `y`
* `create_dest` - Create the destination directory if it doesn't exist? e.g. `y`
* `transfer_ready_file` - A file that must exist in the source directory
(or relative path) for the transfer to initative. This option is ignored if the line is
missing from `synchro.conf`

**Example:**
```text
destination = /path/to/destination_directory
untar = y 
create_dest = y 
transfer_ready_file = ready.txt
```

N.B. the destination can also be on a remote host 
([an ssh key must be set up](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)), 
e.g.:
```text
destination = user@IP:/path/to/destination_directory
```