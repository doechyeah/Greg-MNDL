#!/usr/bin/env python3
import os, time, re, json, ifcfg, signal
import flask_server
import RPi.GPIO as GPIO



def quit_Greg(*args):
    print('Stopping Greg System')
    # Turn off LED here
    exit(0)

with open('system_info.json') as f:
    sys_info = json.loads(f.read())['system_INFO']

wifiLED = sys_info["LowerTray"]["wifiLED"]
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(wifiLED, GPIO.OUT)

def blink3_wifi():
    for _ in range(3):
        GPIO.output(wifiLED, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(wifiLED, GPIO.LOW)
    time.sleep(1)

def blink1_wifi():
    GPIO.output(wifiLED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(wifiLED, GPIO.LOW)
    time.sleep(1)

def apply_wifi_creds():
    results = False
    try:
        while not os.path.exists('/media/usb0/credentials.json'):
            blink1_wifi()
        with open('/media/usb0/credentials.json') as f:
            creds = json.loads(f.read())
        with open('/etc/wpa_supplicant/wpa_supplicant.conf') as wpa:
            wpa.write("network={\n"+
                    f"\tssid=\"{creds['SSID']}\"\n"+
                    f"\tpsk=\"{creds['psk']}\"\n"+
                    f"\tkey_mgmt={creds['key_mgmt']}\n"+
                    "}")
        splitIP = creds['gatewayIP'].split('.')
        splitIP[-1] = '200'
        staticIP = '.'.join(splitIP)
        with open('/etc/dhcpcd.conf') as dhcpcd:
            dhcpcd.write("interface wlan0\n"+
                        f"static ip_address={staticIP}/24\n"+
                        f"static routers={creds['gatewayIP']}\n"+
                        f"domain_name_servers={creds['DNS']}")
        results = True
    except Exception as e:
        print("error occurred while applying WiFI creds")
        print(e.message, e.args)
    return results

def check_wifi(timeout=30):
    limit = 0
    while 'wlan0' not in ifcfg.interfaces().keys():
        # Blink BLUE LED HERE
        blink3_wifi()
        print('waiting for WLAN0 interface')
        if limit == timeout:
            return False
        limit = limit+1
    ### Don't check for now ####
    # if sys_info['staticIP'] not in ifcfg.interfaces()['wlan0']['inet4']:
    #     return False
    return True




if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit_Greg)
    GPIO.output(wifiLED, GPIO.LOW)
    # Look for WiFi
    try:
        for x in range(3):
            print("Checking for WiFi")
            if check_wifi():
                break
            print("Could not find WiFi network. Waiting for credentials to be loaded on USB")
            if apply_wifi_creds():
                break
            print("Failed to apply wifi credentials\n TRYING AGAIN")
        print("Connected to WiFi: Starting Greg Monitoring and Care System")
        GPIO.output(wifiLED, GPIO.HIGH)
        flask_server()
    except KeyboardInterrupt:
        quit_Greg()
