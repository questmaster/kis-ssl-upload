#!/usr/bin/env python3
from splinter import Browser
from time import sleep
import json
import os

from create_certificate import create_certificate

class Domain():
    url = ''
    ssl_href = ''
    local_path = ''
    cert_file = ''
    key_file = ''
    challenge_path = ''
    certificate_created = False
    ftp_server = ''
    ftp_user = ''
    ftp_pass = ''

    def __repr__(self):
        return self.url + ' / ' + self.ssl_href

def main():
    print("HostEurope SSL Updater")

    # parse config
    config, domains = read_config()
    if len(domains) == 0:
        print('Config file empty or not existing.')
        exit()

    print('Found ' + str(len(domains)) + ' domains in config file.')

    print(" ")
    print("Creating certificates")

    # create certificates
    for d in domains:
        print('Creating certificate for ' + str(d.url))
        if create_certificate(d.url, config['settings']['email'], d.ftp_server, d.ftp_user, d.ftp_pass, d.challenge_path, d.local_path):
            d.certificate_created = True

    # kis login
    print(" ")
    print("Uploading certificates")    
    print("- Logging into HE KIS.")
    browser = kis_login(config['settings']['kis_user'], config['settings']['kis_password'])
    if not browser:
        print('- Invalid user name or password.')
        exit()

    # pull ssl domains from kis
    hosteurope_domains = get_ssl_domains(browser, config['settings']['kis_webpack_id'])
    print("- Found " + str(len(hosteurope_domains)) + " domains in KIS.")

    # loop through HE domains and update SSL if in config & new certificate exists
    for h in hosteurope_domains:
        for d in domains:
            if d.certificate_created == True:
                if h.url == d.url:
                    print("- Now updating " + str(h.url))
                    h2 = get_domain(domains, h.url)
                    if upload_certificate(browser, h.ssl_href, h2.local_path, h2.cert_file, h2.key_file):
                        print("- Uploaded successfully")
                    else:
                        print("- Upload failed")

    # log out of KIS
    browser.visit('https://kis.hosteurope.de/?logout=1')

    print("Done!")

def read_config():
    # read domain settings from config.json
    domains = []
    try:
        config = json.load(open('config.json',encoding='utf-8'))
        for d in config['domains']:
            domain = Domain()
            domain.url = d['url']
            domain.local_path = d['local_path']
            domain.cert_file = d['cert_file']
            domain.key_file = d['key_file']
            domain.challenge_path = d['challenge_path']
            domain.ftp_server = d['ftp_server']
            domain.ftp_user = d['ftp_user']
            domain.ftp_pass = d['ftp_pass']
            domains.append(domain)
    except:
        config = json.loads('{}')

    return config, domains

def kis_login(username, password):
    browser = Browser('chrome')

    # log into KIS
    browser.visit('https://sso.hosteurope.de/?app=kis&path=')
    browser.fill('identifier', username)
    browser.fill('password', password)
    button = browser.find_by_tag('button')[1]
    button.click()

    # to do: change to while url still with SSO
    sleep(5)
    if 'https://sso.hosteurope.de/' in browser.url:
        return False
        
    return browser

def get_ssl_domains(browser, kis_webpack_id):
    # get list of domains available for SSL
    browser.visit('https://kis.hosteurope.de/administration/webhosting/admin.php?menu=6&mode=ssl_list&wp_id=' + str(kis_webpack_id))
    domain_table = browser.find_by_tag('table')[2]
    domain_table_rows = domain_table.find_by_tag('tr')

    # copy domain properties to collection
    domains = []
    for domain in domain_table_rows:
        if(domain.find_by_tag('td')[3].value == "Ja" or domain.find_by_tag('td')[3].value == "Yes"):
            d = Domain()

            if(domain.find_by_tag('td')[1].value != "- keine Domains zugeordnet -" and domain.find_by_tag('td')[1].value != '- no domain assigned -'):
                d.url = domain.find_by_tag('td')[1].value
            else:
                d.url = domain.find_by_tag('td')[2].value

            d.ssl_href = domain.find_by_tag('td')[4].find_by_tag('a').first['href']
            domains.append(d)

    return domains

def get_domain(domains, domain):
    for d in domains:
        if d.url == domain:
            return d
    
    return None

def upload_certificate(browser, ssl_href, local_path, cert_file, key_file):
    # open cert upload page for domain
    browser.visit(ssl_href)

    # select files to upload
    browser.attach_file('certfile', os.path.join(local_path, cert_file))
    browser.attach_file('keyfile', os.path.join(local_path, key_file))

    # find & press upload button
    for b in browser.find_by_tag('input'):
        if b['type'] == 'submit':
            b.click()
            break

    # check if successful
    if 'Die Dateien wurden erfolgreich hochgeladen.' in browser.html or 'the files have been successfully uploaded.' in browser.html:
        return True
    else:
        return False

if __name__ == "__main__":
    main()
