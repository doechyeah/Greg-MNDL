import time, json, signal
import flask_server
import RPi.GPIO as GPIO



def quit_Greg(*args):
    print('Stopping Greg System')
    # Turn off LED here
    exit(0)

with open('/home/pi/Greg-MNDL/operationbox/system_info.json', 'r') as f:
    sys_info = json.loads(f.read())

wifiLED = sys_info['LowerTray']['wifiLED']
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

def restart_Wifi():
    import subprocess
    my_cmd = "sudo systemctl restart networking.service && sudo systemctl restart dhcpcd.service"
    subprocess.Popen(my_cmd, shell=True, stdout=subprocess.PIPE)

def apply_wifi_creds():
    import os
    results = False
    try:
        while not os.path.exists('/media/usb0/credentials.json'):
            blink1_wifi()
        with open('/media/usb0/credentials.json') as f:
            creds = json.loads(f.read())
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as wpa:
            wpa.write("network={\n"+
                    f"\tssid=\"{creds['SSID']}\"\n"+
                    f"\tpsk=\"{creds['psk']}\"\n"+
                    f"\tkey_mgmt={creds['key_mgmt']}\n"+
                    "}\n")
        splitIP = creds['gatewayIP'].split('.')
        splitIP[-1] = '200'
        staticIP = '.'.join(splitIP)
        sys_info['system_INFO']['gatewayIP'] = creds['gatewayIP']
        sys_info['system_INFO']['staticIP'] = staticIP
        with open('/home/pi/Greg-MNDL/operationbox/system_info.json', 'w') as f:
            json.dump(sys_info, f)
        with open('/etc/dhcpcd.conf', 'a') as dhcpcd:
            dhcpcd.write("interface wlan0\n"+
                        f"static ip_address={staticIP}/24\n"+
                        f"static routers={creds['gatewayIP']}\n"+
                        f"domain_name_servers={creds['DNS']}\n")
        restart_Wifi()
        results = True
    except Exception as e:
        print("error occurred while applying WiFI creds")
        print(e.message, e.args)
    return results

def check_wifi(timeout=30):
    import ifcfg
    limit = 0
    inet = ifcfg.interfaces()
    staticIP = sys_info['system_INFO']['staticIP']
    if 'wlan0' not in inet.keys():
        print('ERROR --- NO WIFI INTERFACE FOUND')
        while 1:
            GPIO.output(wifiLED, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(wifiLED, GPIO.LOW)
    if staticIP is None:
        return False
    while staticIP not in ifcfg.interfaces()['wlan0']['inet4']:
        # Blink BLUE LED HERE
        blink3_wifi()
        print('waiting for WLAN0 interface')
        if limit > timeout:
            return False
        limit = limit+2
    ### Don't check for now ####
    # if sys_info['staticIP'] not in ifcfg.interfaces()['wlan0']['inet4']:
    #     return False
    return True




if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit_Greg)
    GPIO.output(wifiLED, GPIO.LOW)
    configured = False
    # Look for WiFi
    try:
        while True:
            print("Checking for WiFi")
            if check_wifi():
                break
            print("Could not find WiFi network. Waiting for credentials to be loaded on USB")
            if not configured:
                configured = apply_wifi_creds()
                continue
            restart_Wifi()
            print("Failed to Connect to Network\n TRYING AGAIN")
        print("Connected to WiFi: Starting Greg Monitoring and Care System")
        GPIO.output(wifiLED, GPIO.HIGH)
        flask_server.main()
    except KeyboardInterrupt:
        quit_Greg()
