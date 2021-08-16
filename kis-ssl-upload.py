#!/usr/bin/env python3
from splinter import Browser
from time import sleep
import json
import os

class Domain():
    url = ''
    ssl_href = ''
    local_path = ''

    def __repr__(self):
        return self.url + ' / ' + self.ssl_href

def main():
    print("HostEurope SSL Updater")

    # parse config
    config, domains = read_config()
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
                upload_certificate(browser, h.ssl_href, get_domain(domains, h.url).local_path)

    print("Done!")

def read_config():
    # read domain settings from config.json
    config = json.load(open('config.json',encoding='utf-8'))
    domains = []
    for d in config['domains']:
        domain = Domain()
        domain.url = d['url']
        domain.local_path = d['local_path']
        domains.append(domain)

    return config, domains

def kis_login(username, password):
    browser = Browser('chrome')

    # log into KIS
    sign_in_url = "https://sso.hosteurope.de/?app=kis&path="
    browser.visit(sign_in_url)
    browser.fill('identifier', username)
    browser.fill('password', password)
    button = browser.find_by_tag('button')[1]
    button.click()

    sleep(3) # change to while url still with SSO
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
        if(domain.find_by_tag('td')[3].value == "Ja"):
            d = Domain()

            if(domain.find_by_tag('td')[1].value != "- keine Domains zugeordnet -"):
                d.url = domain.find_by_tag('td')[1].value
            else:
                d.url = domain.find_by_tag('td')[2].value

            d.ssl_href = domain.find_by_tag('td')[4].find_by_tag('a').first['href']
            domains.append(d)

    return domains

def upload_certificate(browser, ssl_href, local_path):
    # open cert upload page for domain
    browser.visit(ssl_href)

    # select files to upload
    browser.attach_file('certfile', os.path.join(local_path, 'domain.crt'))
    browser.attach_file('keyfile', os.path.join(local_path, 'domain-key.txt'))

    # press upload button
    for b in browser.find_by_tag('input'):
        if b['type'] == 'submit':
            b.click()
            break

    return True

def get_domain(domains, domain):
    for d in domains:
        if d.url == domain:
            return d
            break
    
    return False

if __name__ == "__main__":
    main()