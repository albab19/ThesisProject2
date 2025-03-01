# DICOMHawk

DICOMHawk honeypot is a diception tool that allows attackers to interact with what appears to be a fully functional medical imaging system, receiving DICOM-compliant responses and real medical images.

# Key Features

- DICOMHawk provides attackers with ability to perform the main DICOM operations on the two standard DICOM information models (STUDYROOT and PATIENTROOT).

- DICOMHawk stores real DICOM files that are updated periodically through "The Cancer Imaging Archive (TCIA)" API and fabricated in a way that resembles real patient data of Danish citizens and in the Danish settings.

- DICOMHawk supports a dynamic data rotation mechanism that automatically replace the stored DICOM files with the ones downloaded from TCIA.

- An optional Blackhole service was integrated to the honeypot blocking traffic on kernel level for the known mass-scanner services

- DICOMHawk uses centralized monitoring to track attacker activities. The system employs a loosely coupled Elastic Stack where Logstash only needs the honeypot's IP address to retrieve staged data from the Redis server.

# DICOMHawk Monitoring System

- # Background

DICOMHawk implements a centralized security monitoring infrastructure designed to track and analyze attacker behaviors. This monitoring system utilizes several key components:

Logstash: Collects data from Redis and processes it
Elasticsearch: Indexes and stores security events
Kibana: Visualizes the collected data

Threat intelligence

It is important to ensure that the honeypot does not appear static over time, which could otherwise raise suspicion from potential adversaries.
\item Further addressing mimicking and decoying, it is important that potential adversaries perceive the system as legitimate and recognize it as an attractive target. A Web \api{} was implemented to mimic the Orthanc server, which is a commonly adopted in the medical imaging sector.
\item The Web \api{} should allow attackers to interact with it in a way that medical personnel would. It should provide the following possibilities: list the stored \dicom{} files, see the information corresponding to the respective files listed, search patients by their name or ID, as well as download and upload \dicom{} files into the system.
\item It is important to craft the \dicom{} images with honeyrecords and employ other types of honeytokens to detect unauthorized access and track adversary activity.
\item Therefore, a management stack should be employed to provide information on attackers interaction with the honeypot

The system is designed to include an integration to a web api server serves a simple user inferace enable potential attackers to query, search and retrieve DICOM files.

# Usage Guide

## Environment Separation

DICOMHawk supports separate development and production environments to facilitate testing and deployment.

## Production Deployment

For production environments, DICOMHawk can be easily deployed using Docker Compose with a single command:

```bash
docker-compose up -d
```

# Prerequisites / Requirements

# Configuration Options

# Usage Examples

# Deployment Architecture

# Troubleshooting

# Security Considerations

# Contributing Guidelines

# License Information

# Contact / Support
