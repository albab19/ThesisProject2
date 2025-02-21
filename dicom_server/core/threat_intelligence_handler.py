import requests
from datetime import datetime
from services.threat_intelligence_service import IThreatIntelligence


class ThreatIntelligence(IThreatIntelligence):
    def __init__(
        self,
        exceptions_logger,
        abuse_ip_api_key,
        ip_quality_score_api_key,
        virus_total_api_key,
    ):
        self.abuse_ip_api_key = abuse_ip_api_key
        self.ip_quality_score_api_key = ip_quality_score_api_key
        self.virus_total_api_key = virus_total_api_key
        self.exceptions_logger = exceptions_logger

    # Get IP security score from ABUSEIPDB

    def getIPSecurityScore(self, ip):

        api_key = self.abuse_ip_api_key
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Accept": "application/json", "Key": api_key}
        params = {"ipAddress": ip, "maxAgeInDays": 90}

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()["data"]
                print(data)

                country = data.get("countryCode", "N/A")
                isp = data.get("isp", "N/A")
                abuseIPConfidenceScore = data["abuseConfidenceScore"]
                return [isp, abuseIPConfidenceScore, country]
            else:
                print(
                    f"Error: {response.status_code} - {response.json().get('errors', [{'detail': 'Unknown error'}])[0]['detail']}"
                )
        except Exception:
            self.exceptions_logger.exception(
                f'Exception while getting IP security score from "abuseipdb.com"'
            )

    # Get IP security score from IPQUALITYSCORE

    def getIpqualityScore(self, ip):
        try:
            api_key = self.ip_quality_score_api_key
            url = f"https://ipqualityscore.com/api/json/ip/{api_key}/{ip}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(data)
                return [
                    data.get("fraud_score", "N/A"),
                    data.get("proxy", "N/A"),
                    data.get("city", "N/A"),
                    data.get("bot_status", "N/A"),
                    data.get("vpn", "N/A"),
                    data.get("latitude", "N/A"),
                    data.get("longitude", "N/A"),
                ]
            return {"service": "IPQualityScore", "error": response.text}
        except Exception:
            self.exceptions_logger.exception(
                f'Exception while getting IP quality score from "ipqualityscore.com"'
            )

    # Get IP security score from VIRUSTOTAL

    def getVirusTotalScore(self, ip):
        try:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
            headers = {"x-apikey:", self.virus_total_api_key}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()["data"]
                # print(data)
                result_counts = {}

                for analysis in data["attributes"]["last_analysis_results"].values():
                    result = analysis["result"]
                    result_counts[result] = result_counts.get(result, 0) + 1
                print(result_counts)
                return result_counts
        except Exception:
            self.exceptions_logger.exception(
                f'Exception while getting IP information from "virustotal.com"'
            )

    # Build reputation object

    def get_reputation_data(self, rep_dat, ip, ip_scanned):

        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        abusedb_report = self.getIPSecurityScore(ip) if not ip_scanned else ["", "", ""]
        ip_quality_score = (
            self.getIpqualityScore(ip)
            if not ip_scanned
            else ["", "", "", "", "", "", ""]
        )
        virus_total = self.getVirusTotalScore(ip) if not ip_scanned else {}
        try:
            rep_dat["timestamp"] = str(current_time)
            rep_dat["virus_total_results"] = virus_total
            rep_dat["ip"] = ip
            rep_dat["ip_quality_score"] = ip_quality_score[0]
            rep_dat["proxy"] = ip_quality_score[1]
            rep_dat["region"] = ip_quality_score[2]
            rep_dat["vpn"] = ip_quality_score[4]
            rep_dat["country"] = abusedb_report[2]
            rep_dat["ISP"] = abusedb_report[0]
            rep_dat["AbuseDBScore"] = abusedb_report[1]
            return rep_dat
        except Exception:
            self.exceptions_logger.exception(
                "Exception while building IP reputation object"
            )
            pass
