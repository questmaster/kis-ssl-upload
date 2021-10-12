#!/usr/bin/env python3
from splinter import Browser
from time import sleep
import json
import os
from kis_ssl_upload import read_config, kis_login

def main():
    print("HostEurope DNS Updater")

    # parse config
    config, certificates = read_config()

    # kis login
    print(" ")
    print("- Logging into HE KIS.")
    browser = kis_login(config['settings']['kis_user'], config['settings']['kis_password'])
    if not browser:
        print('- Invalid user name or password.')
        exit()

    update_dns_entry(browser, "questmaster.de", "dyndns", "2a01:0488:0042:1000:50ed:85c9:ffff:ffff")
    print('- Update dyndns')

    # log out of KIS
    browser.visit('https://kis.hosteurope.de/?logout=1')

    print("Done!")

def update_dns_entry(browser, domain, entry, value):
    # get table of dns entries
    browser.visit('https://kis.hosteurope.de/administration/domainservices/index.php?menu=2&mode=autodns&submode=edit&domain=' + domain)
    dns_table = browser
    #.find_by_xpath('.//div[4]/table/tbody/tr/td[2]/div[2]/div/table[5]')
    
    # find table row of specified entry
    for dns in dns_table.find_by_tag('tr'):
        if dns.find_by_tag('td')[0].value.find(entry) != -1:
            #print("DBG: Selected - " + dns.find_by_tag('td')[0].value)
            dns_value = dns.find_by_tag('td')[2]
            #print("DBG: td line - " + dns_value.value)
            ip_input = dns_value.find_by_tag('input')[0]
            update_input = dns_value.find_by_tag('input')[1]
            ip_input.clear()
            ip_input.value = value
            update_input.click()
            sleep(2)
            break
        #else:
            #print("DBG: Not selected - "+ dns.find_by_tag('td')[0].value)

if __name__ == "__main__":
    main()
