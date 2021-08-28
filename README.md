# KIS SSL upload script
Script to upload domain SSL certificates to [HostEurope](https://www.hosteurope.de)'s customer portal ("[KIS](https://kis.hosteurope.de)").

<img src="https://github.com/nicolaus-hee/kis-ssl-upload/blob/main/images/KIS%20screenshot%20SSL%20cert%20replacement.png" width="600">

## What the script does
* Log into KIS (using Chrome)
* Replace existing SSL certificate / domain key with `domain.crt` & `domain-key.txt` from specified path
* Can be used in bulk: Add 1-n domains in the config file

## Usage
* Make sure packages in `requirements.txt` are available
* Edit `config.json.example` and remove `.example` suffix
* Make sure certificate & domain key are stored in path(s) as specified
* Run `python kis-ssl-upload.py`

## To do
- [ ] Allow for custom file names
- [ ] Simplify `Domain` class
- [ ] Add Let's Encrypt certificate renewal
- [ ] Add 'challenge' FTP upload
- [x] Confirm result after upload
- [ ] Support KIS GUI set to English
