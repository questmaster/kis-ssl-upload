# KIS SSL certificate creation & upload script
Script to create & upload domain SSL certificates to [HostEurope](https://www.hosteurope.de)'s customer portal ("[KIS](https://kis.hosteurope.de)").

<img src="https://github.com/nicolaus-hee/kis-ssl-upload/blob/main/images/kis-ssl-upload.png">

## What the script does
* Create new SSL certificate for domain (incl. HTTP-01 challenge file upload to FTP server)
* Log into KIS (using Chrome)
* Upload SSL certificate / domain key files to KIS
* Can be used in bulk: Add 1-n certificates / domains aliases in the config file

## Usage
* Make sure packages in `requirements.txt` are available
* Edit `config.json.example` and remove `.example` suffix
* Choose between 'staging' and 'production' environment in `create_certificate.py` (line 18/19)
* Run `python kis_ssl_upload.py`

## Configuration

`config.json.example` contains a sample configuration.
### General settings

```
"settings": {
    "email": "aa@bb.com",
    "kis_user": "user",
    "kis_password": "pass",
    "kis_webpack_id": "123456"
}
```
* `email` - Your email address. Needed for registration at certification authority.
* `kis_user` and `kis_password` - Your login credentials for [KIS](https://kis.hosteurope.de).
* `kis_webpack_id` - ID number of your webpack contract (found in leftmost column [here](https://kis.hosteurope.de/administration/webhosting/?mode=1))

### Certificate requests

```
"certificates": [
    {
        "name": "Test name",
        "urls": [
            {
                "url": "url1.de",
                "challenge_path": "/www/url1/.well-known/acme-challenge",
                "kis_domain": "url1.de"
            },
            {
                "url": "www.url1.de",
                "challenge_path": "/www/url1/.well-known/acme-challenge"
            },                
            {
                "url": "url2.de",
                "challenge_path": "/www/url2/.well-known/acme-challenge",
                "kis_domain": "url2.de"
            }
        ],
        "local_path": "C:\\Users\\Test\\Desktop",
        "cert_file": "domain.crt",
        "key_file": "domain-key.txt",
        "csr_file": "domain-csr.txt",
        "account_file": "account-key.txt",
        "ftp_server": "ftp.url1.de",
        "ftp_user": "user",
        "ftp_pass": "pass"
    }
]
```

* `name` - Friendly name of your certificate
* `urls` - Contains all urls / domain aliases you want in the certificate
  * `url` - (Sub)domain name; if you want to include www. and non-www, add a url for both
  * `challenge_path` - Path to  ACME challenge directory of that domain
  * `kis_domain` - Domain name in KIS to upload the certificate to (leave blank if you have one url for www. and one for non-www)
* `local_path` - Local path to store the created files in
* `cert_file` - File name of certification file
* `key_file`- File name of domain key
* `csr_file` - File name of certificate signing request
* `account_file` - File name of account key
* `ftp_server`, `ftp_user` and `ftp_pass` - Login credentials for your FTP server

Note: The script does support multiple certificate requests.

## To do
- [x] Allow for custom file names
- [x] Simplify `Domain` class
- [x] Add Let's Encrypt certificate renewal
- [x] Add 'challenge' FTP upload
- [x] Confirm result after upload
- [x] Support KIS GUI set to English
- [x] Multi-domain certificates
- [ ] Better error handling
- [ ] Enable individual FTP logins for URLs
- [ ] Switch to [woob](https://github.com/rbignon/woob) (or similar)
