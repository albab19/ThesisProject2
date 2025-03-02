# DICOMHawk

DICOMHawk honeypot is a diception tool that allows attackers to interact with what appears to be a fully functional medical imaging system, receiving DICOM-compliant responses and real medical images.

# Key Features

- \*\*DICOMHawk enables potential attackers to perform DICOM operations on the two standard DICOM information models (STUDYROOT and PATIENTROOT) through its DICOM port.

- \*\*DICOMHawk provides an API service enabling attackers to interact with the DICOM server content. Using the API endpoints, an attacker can serach and download studies, series, patient and images data. Moreover, they can upload files to the web api server.

- \*\*DICOMHawk stores real DICOM files that are updated periodically through "The Cancer Imaging Archive (TCIA)" API and formed in a way that resembles real patient data of Danish citizens and in the Danish settings.

- \*\*DICOMHawk supports a dynamic data rotation mechanism that automatically replaces the stored DICOM files with the ones downloaded from TCIA.

- \*\*DICOMHawk employs different types of honeytoken in both the DICOM server and the web API including encapsulated PDF canary tokens, honeyURLs (Fake URLs that is seeded into the DICOM data-sets), CredentialsHoneytokens, hidden endpoints and hidden credentials in the source code.

- DICOMHawk provides automatic threat intelligence chack on each unique IP address interacts with honeypot. here we have to talk about IPQualityscore, VTOTAL.....

- \*\*An optional Blackhole service is integrated to DICOMHawk blocking traffic on kernel level for the known mass-scanner services

- \*\*DICOMHawk uses centralized monitoring to track attackers activities. IT employs a loosely coupled Elastic Stack where Logstash only needs the honeypot's IP address to retrieve staged data from the Redis server.

-

# DICOMHawk Monitoring System

- # Background
  ![DICOMHawk Web Interface](cover_images/kibana.png)

DICOMHawk implements a centralized security monitoring infrastructure designed to track and analyze attacker behaviors. This monitoring system utilizes several key components:

Logstash: Collects data from Redis database integrated with the honeypot.
Elasticsearch: Indexes and stores security events.
Kibana: Visualizes the collected data.

shows the logs-data representation for
both the DICOM server and the Web API. It includes summary metrics and detailed anal-
ysis for the received DICOM sessions and API requests. The dashboard includes multiple
visualization types (numbers, tables, pie charts, timelines). It also include Malicious and
abuse scoring as immedate response on each API request or DICOM session. Moreover,
a timeline at the bottom of the figure shows activity patterns across time period comparing
the DICOM server and the Web APIE describe

# Usage Guide

## Environment Separation

DICOMHawk supports separate development and production environments to facilitate developing and deployment.

## Production Deployment

### Deploying DICOMHawk

Before deploying DICOMHawk in a production environment, be sure that the required ports (104, 3000, 5000, and 6379) are not in use on your system.

**For Linux users**

```bash
netstat -tuln | grep -E '104|3000|5000|6379'
```

**For Windows users**

```bash
netstat -tuln | grep -E '104|3000|5000|6379'
```

If any of these ports are in use, you will need to free them or configure DICOMHawk to use different ports.

Deploying DICOMHawk in a production environment is managed using Docker Compose. Using the following command you can clone the repository, navigates to the project directory, and launches the required services. Note that cloning the repository may take a significant amount of time due to the large size of the real DICOM files from various modalities stored in it

```bash
git clone https://github.com/albab19/ThesisProject2.git && cd ./ThesisProject2 && docker-compose up -d
```

### Deploying the monitoring stack

Before deploying monitoring stack in a production environment, be sure that the required ports (5601, 9200, 9300) are not in use on your system. Follow the same steps to check DICOMHawk ports and free them in case they are in used or configure the monitoring stack to use different ports.

## Development Deployment

# Configuration Options

# Usage Examples

# Deployment Architecture

# Troubleshooting

# Security Considerations

# Contributing Guidelines

# License Information

# Contact / Support
