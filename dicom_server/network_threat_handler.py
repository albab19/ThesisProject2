import subprocess, requests


def get_known_scanners(scanners_file):
    knownScanners = []
    try:
        with open(scanners_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    ip_address = line.split('#')[0].strip()
                    knownScanners.append(ip_address)
    except Exception as e:
        print(f"Error reading file: {e}")
    return knownScanners


def create_ipset(ipset_name):
    try:
        subprocess.run(f" ipset create {ipset_name} hash:ip", shell=True, check=True)
        print(f"IP set '{ipset_name}' created.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create IP set: {e}")

def add_ip_to_ipset(ipset_name, ip_address):
    try:
        subprocess.run(f" ipset add {ipset_name} {ip_address}", shell=True, check=True)
        print(f"IP address {ip_address} added to IP set '{ipset_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add IP {ip_address} to IP set: {e}")

def setup_iptables_rule(ipset_name):
    try:
        subprocess.run(f" iptables -I INPUT -m set --match-set {ipset_name} src -j DROP", shell=True, check=True)
        print(f"iptables rule added for IP set '{ipset_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add iptables rule: {e}")



def block_known_scanners(source_list, set_name):
    create_ipset(set_name)
    for ip in get_known_scanners(source_list):
        add_ip_to_ipset(set_name,ip)

    setup_iptables_rule(set_name)

def allow_scanners(set_name):
    subprocess.run(f" iptables -D INPUT -m set --match-set {set_name} src -j DROP",shell=True, check=True)

    subprocess.run(" ipset destroy {set_name}",shell=True, check=True)




def getIPSecurityScore(ip):
    
    api_key= "95c2c4b357f46e9fb9ce626d06295c1002454709007a43ed5ea49de785a7e3bb0db670e44bb10875"
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Accept": "application/json",
        "Key": api_key
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90  
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()["data"]
            print(data)
           
            country= data.get('countryCode', 'N/A')
            isp= data.get('isp', 'N/A')
            abuseIPConfidenceScore= data['abuseConfidenceScore']
            return [isp,abuseIPConfidenceScore,country]
        else:
            print(f"Error: {response.status_code} - {response.json().get('errors', [{'detail': 'Unknown error'}])[0]['detail']}")
    except Exception as e:
        print(f"An error occurred: {e}")

def getIpqualityScore(ip):
    api_key= "JyGDPZk1kg5Y6Cqqiagx4y1YBkDmJ7tP"
    url = f"https://ipqualityscore.com/api/json/ip/{api_key}/{ip}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print (data)
        return [
            data.get("fraud_score",'N/A'),
            data.get("proxy",'N/A'),
            data.get("city",'N/A'),
            data.get("bot_status",'N/A'),
            data.get("vpn", 'N/A'),
            data.get("latitude","N/A"),
            data.get("longitude","N/A")
        
        ]
    return {"service": "IPQualityScore", "error": response.text}

def getVirusTotalScore(ip):

    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": "715bccfb503dc801d1fdc5f095bb3c0c2a4412a7b81cca1a2f5c15e14361f1fa"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]
        #print(data)
        result_counts = {}

        for analysis in data['attributes']['last_analysis_results'].values():
            result = analysis['result']
            result_counts[result] = result_counts.get(result, 0) + 1
        print(result_counts)
        return result_counts

def is_known_scanner(ip):
    with open("./blackhole_list.txt", "r") as file:
        for line in file:
            if ip in line:
                return "True"

    return "False"    