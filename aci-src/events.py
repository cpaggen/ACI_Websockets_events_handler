#!/usr/local/bin/python3
import ssl
import websocket
import threading
import requests
import json
import time
import sys
import os 

requests.packages.urllib3.disable_warnings()

loginToken = ""
aciUser = os.environ['APIC_USER']
aciPwd = os.environ['APIC_PWD']
apic = os.environ['APIC_IP']
tenant = os.environ['TENANT']
webexRoom = os.environ['WEBEX_ROOMID']
webexAPI = "https://api.ciscospark.com/"
webexToken = os.environ['WEBEX_TOKEN']
subId = ''
proxies = {
 "http": "http://proxy.esl.cisco.com:80",
 "https": "http://proxy.esl.cisco.com:80",
 "no_proxy": "10.48.168.221"
}

mdTemplate = '''
**Event {}**
- user: *{}*
- what: *{}*
- description: *{}*
- affected   : *{}*
- changeSet  : *{}*
- timestamp  : *{}*
\n
'''

def apicLogin():
    body = {"aaaUser": {"attributes": {"name": aciUser, "pwd": aciPwd}}}
    resp = requests.post(
            'https://' + apic + '/api/aaaLogin.json',
            headers = {'Content-Type': 'application/json'},
            json = body,    
        verify = False
    )

    respJson = json.loads(resp.text)
    try:
        token = respJson['imdata'][0]['aaaLogin']['attributes']['token']
    except KeyError:
        token = 0
    return token

def subscribe(loginToken):
    global subId
    sub = '/api/node/class/fvTenant.json?query-target-filter=and(eq(fvTenant.name,"' + tenant + '"))'
    resp = requests.get(
        "https://" + apic + sub + "&query-target=subtree&rsp-subtree-include=audit-logs,no-scoped&rsp-prop-include=all&subscription=yes&refresh-timeout=600",
        headers = {'Cookie': "APIC-cookie=" + loginToken},
        verify = False
        )
    subId=json.loads(resp.text)['subscriptionId']
    print("Subscription id is {}".format(subId))

def refresh():
    global subId
    while True:
        time.sleep(60)
        loginToken = apicLogin()
        print("Refreshing sub {}".format(subId))
        resp = requests.get(
                "https://" + apic + "/api/subscriptionRefresh.json?id=" + subId,
                headers = {'Cookie': "APIC-cookie=" + loginToken},
                verify = False
                )
        respJson = json.loads(resp.text)['totalCount']
        if respJson == '0':
            print("Sub refreshed successfully")

def on_message(ws, msg):
    msg = json.loads(msg)['imdata'][0]
    msgTstamp = msg["aaaModLR"]["attributes"]["created"]
    msgId  = msg["aaaModLR"]["attributes"]["id"]
    msgUser = msg["aaaModLR"]["attributes"]["user"]
    msgInd = msg["aaaModLR"]["attributes"]["ind"]
    msgDescr = msg["aaaModLR"]["attributes"]["descr"]
    msgAffected = msg["aaaModLR"]["attributes"]["affected"]
    msgChangeSet = msg["aaaModLR"]["attributes"]["changeSet"]
    mdMsg = mdTemplate.format(msgId,msgUser,msgInd,msgDescr,msgAffected,msgChangeSet,msgTstamp)
    print("%%DEBUG%% on_message received type {} => {}".format(type(msg),msg))
    headers = {
      "Authorization": "Bearer " + webexToken,
      "Content-Type": "application/json"
    }
    payload = {"roomId": webexRoom, "markdown": mdMsg,}
    resp = requests.post(webexAPI + "messages", headers=headers, json=payload, proxies=proxies)
    print("%%DEBUG%% webex response {}".format(resp.text))

def on_error(ws, error):
    print("we have a websocket error :/")

def on_close(ws):
    print("Closing socket now.")

def on_open(ws):
    subscribe(loginToken)

if __name__ == "__main__":
    loginToken = apicLogin()
    if not loginToken:
        sys.exit("APIC login failure")
    refreshThread = threading.Thread(target=refresh)
    refreshThread.start()
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://" + apic + "/socket" + loginToken,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
