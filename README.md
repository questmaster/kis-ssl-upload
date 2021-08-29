# KIS SSL certificate creation & upload script
Script to create & upload domain SSL certificates to [HostEurope](https://www.hosteurope.de)'s customer portal ("[KIS](https://kis.hosteurope.de)").

<img src="https://github.com/nicolaus-hee/kis-ssl-upload/blob/main/images/KIS%20screenshot%20SSL%20cert%20replacement.png" width="600">

## What the script does
* Create new SSL certificate for domain (incl. HTTP-01 challenge file upload to FTP server)
* Log into KIS (using Chrome)
* Upload SSL certificate / domain key files
* Can be used in bulk: Add 1-n domains in the config file

## Usage
* Make sure packages in `requirements.txt` are available
* Edit `config.json.example` and remove `.example` suffix
* Run `python kis_ssl_upload.py`

## To do
- [x] Allow for custom file names
- [ ] Simplify `Domain` class
- [x] Add Let's Encrypt certificate renewal
- [x] Add 'challenge' FTP upload
- [x] Confirm result after upload
- [x] Support KIS GUI set to English
- [ ] Multi-domain certificates
