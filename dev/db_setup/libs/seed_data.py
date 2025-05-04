# seed_data.py - Centralized data definitions

# Company data
COMPANIES = [
    ("Nimbus Financial", "Large financial services company with hybrid cloud environment, primarily AWS and on-prem."),
    ("Velocity Healthcare Systems", "Healthcare provider with growing Azure footprint and strict compliance requirements."),
    ("GlobalTech Retail", "Multi-national retailer operating across GCP, AWS, and Azure with containerized microservices."),
    ("Quantum Innovations", "Fast-growing SaaS provider with cloud-native architecture using Kubernetes across multiple clouds."),
    ("Meridian Energy", "Energy company with critical infrastructure transitioning from on-prem to AWS cloud services."),
    ("Axion Logistics", "Supply chain company with legacy systems and new cloud initiatives creating security visibility gaps."),
    ("Horizon Media Group", "Media company with extensive data analytics workloads running in multi-cloud environment."),
]

# Capability categories and their capabilities
CAPABILITY_MAP = {
    "Cloud Security": ["CSPM", "CWPP", "Container Security", "Cloud IAM Security", "Cloud Data Security"],
    "DevSecOps": ["Pipeline Security", "IaC Scanning", "Container Registry Scanning", "SBOM Management"],
    "Compliance": ["HIPAA", "PCI-DSS", "SOC2", "GDPR", "ISO27001"],
    "Identity": ["Privileged Access Management", "SSO Integration", "Zero Trust Implementation"],
    "Network Security": ["ZTNA", "Cloud Network Segmentation", "API Security"],
}

# Company-capability relationships
COMPANY_CAPABILITY_MAP = {
    "Nimbus Financial": ["CSPM", "Cloud IAM Security", "Privileged Access Management", "PCI-DSS"],
    "Velocity Healthcare Systems": ["HIPAA", "CSPM", "Cloud Data Security", "ZTNA"],
    "GlobalTech Retail": ["Container Security", "Pipeline Security", "Cloud Network Segmentation"],
    "Quantum Innovations": ["Container Security", "IaC Scanning", "SBOM Management", "API Security"],
    "Meridian Energy": ["CSPM", "CWPP", "SOC2", "SSO Integration"],
    "Axion Logistics": ["CSPM", "Zero Trust Implementation", "Cloud Network Segmentation"],
    "Horizon Media Group": ["Cloud Data Security", "GDPR", "API Security", "Container Registry Scanning"],
}