# KIS SSL upload script
Script to upload domain SSL certificates to [HostEurope](https://www.hosteurope.de)'s customer portal ("[KIS](https://kis.hosteurope.de)").

## What the script does
* Log into KIS
* Replace existing SSL certificate as configures
* Can be used in bulk: Add 1-n domains in the config file

## Usage
* Edit `config.json.example` and remove `.example` suffix
* Make sure certificate & domain key are stored in path(s) as specified
* Run `python kis-ssl-upload.py`

## To do
- [ ] Allow for custom file names
- [ ] Simplify `Domain` class
- [ ] Add certificate renewal
- [ ] Add challenge FTP upload
