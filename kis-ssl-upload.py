#!/usr/bin/env python3
from splinter import Browser
from time import sleep
import json
import os

class Domain():
    url = ''
    ssl_href = ''
    local_path = ''
    cert_file = ''
    key_file = ''

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

    # kis login
    print("Logging into HE KIS.")
    browser = kis_login(config['settings']['kis_user'], config['settings']['kis_password'])

    # pull ssl domains from kis
    hosteurope_domains = get_ssl_domains(browser, config['settings']['kis_webpack_id'])
    print("Found " + str(len(hosteurope_domains)) + " domains in KIS.")

    # loop through HE domains and update SSL if in config
    for h in hosteurope_domains:
        for d in domains:
            if h.url == d.url:
                print("Now updating " + str(h.url))
                if upload_certificate(browser, h.ssl_href, get_domain(domains, h.url).local_path, get_domain(domains, h.url).cert_file, get_domain(domains, h.url).key_file):
                    print("Uploaded successfully")
                else:
                    print("Upload failed")

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

    sleep(3)
    # to do: change to while url still with SSO
    # to do: catch ok / not ok
        
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

    # check if successul
    if 'Die Dateien wurden erfolgreich hochgeladen.' in browser.html or 'the files have been successfully uploaded.' in browser.html:
        return True
    else:
        return False

def get_domain(domains, domain):
    for d in domains:
        if d.url == domain:
            return d
    
    return None

if __name__ == "__main__":
    main()