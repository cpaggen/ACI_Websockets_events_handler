# simple Python code to subscribe to ACI event channel
# single threaded, no AAA refresh (will probably break after 60 minutes)
# quick PoC-level quality - use at your own risks
# cpaggen

import json
import websockets
import os
import sys
from sys import stdout
import requests
import ssl
import asyncio
import logging
    
proxies = {
 "http": "http://proxy.esl.cisco.com:80",
 "https": "http://proxy.esl.cisco.com:80",
 "no_proxy": "10.48.168.221"
}

def sendWebex(msg):
    # you can obtain the room ID from the Webex API after inviting your chatbot to that room
    print("%%DEBUG%% sendWebex received {} {}".format(type(msg),msg))
    tenant = msg['imdata'][0]['fvTenant']['attributes']['dn']
    attr = msg['imdata'][0]['fvTenant']['attributes']
    msg = "Tenant {} is reporting {}".format(tenant,attr)
    webexRoom = os.environ['WEBEX_ROOMID']
    webexAPI = "https://api.ciscospark.com/"
    auth_token = os.environ['WEBEX_TOKEN']
    headers = {
      "Authorization": "Bearer " + auth_token,
      "Content-Type": "application/json"
    }
    payload = {"roomId": webexRoom, "text": msg,}
    resp = requests.post(webexAPI + "messages", headers=headers, json=payload, proxies=proxies)
    logging.info("%%DEBUG%% sendWebex {}".format(resp.text))

def getCookie(url):
    aciUser = os.environ['APIC_USER']
    aciPwd = os.environ['APIC_PWD']
    body = {"aaaUser": {"attributes": {"name": aciUser, "pwd": aciPwd}}}
    logging.info("%%DEBUG%% getting cookie from url {} with user {} pass {}".format(url,aciUser,aciPwd))
    login_response = requests.post(url, json=body, verify=False)
    response_body = login_response.content
    response_body_dictionary = json.loads(response_body)
    logging.info("%%DEBUG%% {}".format(response_body_dictionary))
    token = response_body_dictionary["imdata"][0]["aaaLogin"]["attributes"]["token"]
    cookie = {"APIC-cookie": token}
    return cookie

async def getEvents(cookie):
    apic = os.environ['APIC_IP']
    tenant = os.environ['TENANT']
    tenant_url = 'https://' + apic + '/api/node/class/fvTenant.json?query-target-filter=and(eq(fvTenant.name,"' + tenant + '"))&query-target=subtree&subscription=yes&refresh-timeout=60m0s'
    websocket_url = "wss://{}/socket{}".format(apic,cookie['APIC-cookie'])
    logging.info("%%DEBUG%% tenant URL is {}".format(tenant_url))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE
    async with websockets.connect(websocket_url, ssl=context) as websocket:
        tenant_subscription = requests.get(tenant_url, verify=False, cookies=cookie)
        json_dict = json.loads(tenant_subscription.text)
        logging.info("%%DEBUG%% Tenant subscription {}".format(json_dict))
        while True:
            data = json.loads(await websocket.recv())
            sendWebex(data)
    

if __name__ == "__main__":
    apic = os.environ['APIC_IP']
    tenant = os.environ['TENANT']
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG) # set logger level
    consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
    logger.addHandler(consoleHandler)
    logging.info("%%DEBUG%% Launching with {} {}".format(apic,tenant))
    apicAaa = "https://" + apic + "/api/aaaLogin.json"
    cookie = getCookie(apicAaa)
    logging.info(cookie)
    asyncio.get_event_loop().run_until_complete(getEvents(cookie))
