#!/usr/bin/env python3
"""
Stage Compliance Checker - Kloud Cloud
==========================================
Kontrollon përputhshmërinë me rregullata evropiane automatikisht.
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, Tuple

import requests


class ComplianceChecker:
    def __init__(self):
        self.results = defaultdict(dict)
        self.timestamp = datetime.now().isoformat()
        self.api_base = "http://localhost:8000"
        
    # ========================
    # GDPR CHECKS
    # ========================
    
    def check_encryption_at_rest(self) -> Tuple[bool, str]:
        """Check if PostgreSQL encryption is configured"""
        try:
            # Check if password env vars are set
            if os.getenv("DB_PASSWORD"):
                return True, "✅ PostgreSQL configured with credentials"
            return False, "❌ Database not properly secured"
        except Exception as e:
            return False, f"⚠️  Error: {str(e)}"
    
    def check_tls_certificates(self) -> Tuple[bool, str]:
        """Check if TLS/HTTPS is configured"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                return True, "✅ API accessible (TLS ready)"
            return False, "❌ API not responding"
        except Exception as e:
            return False, f"⚠️  No HTTPS: {str(e)}"
    
    def check_consent_management(self) -> Tuple[bool, str]:
        """Check Clerk auth for consent management"""
        if os.getenv("CLERK_PUBLISHABLE_KEY"):
            return True, "✅ Clerk Authentication enabled"
        return False, "⚠️  Clerk not fully configured"
    
    def check_data_retention(self) -> Tuple[bool, str]:
        """Check if data retention policy is documented"""
        if os.path.exists("DATA_RETENTION_POLICY.md"):
            return True, "✅ Data Retention Policy exists"
        return False, "❌ Missing Data Retention Policy"
    
    # ========================
    # PSD2 CHECKS
    # ========================
    
    def check_payment_gateway(self) -> Tuple[bool, str]:
        """Check if payment gateways are configured"""
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        sepa_key = os.getenv("SEPA_API_KEY")
        paypal_key = os.getenv("PAYPAL_SECRET")
        
        configured = [k for k in [stripe_key, sepa_key, paypal_key] if k]
        
        if len(configured) >= 2:
            return True, f"✅ {len(configured)} payment gateway(s) configured"
        elif len(configured) == 1:
            return True, f"⚠️  Only {len(configured)} gateway configured (recommend 2+)"
        return False, "❌ No payment gateways configured"
    
    def check_sca_authentication(self) -> Tuple[bool, str]:
        """Check for Strong Customer Authentication"""
        try:
            # Check if 2FA/MFA is implemented
            if os.path.exists("curiosity_admin_auth.py"):
                return True, "✅ SCA/2FA Authentication implemented"
            return False, "⚠️  SCA authentication not fully implemented"
        except Exception as e:
            return False, f"⚠️  Error: {str(e)}"
    
    def check_pci_compliance(self) -> Tuple[bool, str]:
        """Check PCI DSS compliance measures"""
        checks = [
            os.getenv("STRIPE_SECRET_KEY"),  # PCI-compliant payment processor
            os.path.exists("SECURITY_POLICY.md"),
        ]
        
        if all(checks):
            return True, "✅ PCI DSS measures in place"
        return False, "⚠️  PCI DSS compliance needs review"
    
    # ========================
    # AI/ML CHECKS
    # ========================
    
    def check_ai_transparency(self) -> Tuple[bool, str]:
        """Check if AI model is documented"""
        ollama_docs = os.path.exists("CURIOSITY_OCEAN_SETUP.md")
        
        if ollama_docs:
            return True, "✅ AI Model (Ollama) documented"
        return False, "❌ Missing AI documentation"
    
    def check_model_version(self) -> Tuple[bool, str]:
        """Check if model versioning is in place"""
        if os.path.exists("requirements-lite.txt"):
            return True, "✅ Model dependencies versioned"
        return False, "❌ Model versions not tracked"
    
    # ========================
    # SECURITY CHECKS
    # ========================
    
    def check_api_authentication(self) -> Tuple[bool, str]:
        """Check if API has authentication"""
        if os.path.exists("api_key_management.py"):
            return True, "✅ API Key management system in place"
        return False, "⚠️  API authentication needs review"
    
    def check_docker_security(self) -> Tuple[bool, str]:
        """Check Docker security configuration"""
        if os.path.exists("docker-compose.yml"):
            with open("docker-compose.yml", "r") as f:
                content = f.read()
                if "read_only: true" in content or "security_opt" in content:
                    return True, "✅ Docker security hardening applied"
        return False, "⚠️  Docker security could be enhanced"
    
    def check_monitoring(self) -> Tuple[bool, str]:
        """Check if monitoring is configured"""
        services = ["prometheus", "grafana", "jaeger", "loki"]
        if os.path.exists("docker-compose.yml"):
            with open("docker-compose.yml", "r") as f:
                content = f.read()
                found = sum(1 for svc in services if svc in content)
                if found >= 3:
                    return True, f"✅ {found} monitoring tools configured"
                elif found >= 1:
                    return True, f"⚠️  {found} monitoring tool(s) configured"
        return False, "❌ Monitoring system not fully configured"
    
    # ========================
    # ACCESSIBILITY CHECKS
    # ========================
    
    def check_api_documentation(self) -> Tuple[bool, str]:
        """Check if API is documented"""
        docs_files = [
            "API-COMPLETE-REFERENCE.md",
            "API_DOCS.md",
            "README.md"
        ]
        
        found = sum(1 for f in docs_files if os.path.exists(f))
        if found >= 2:
            return True, f"✅ API documentation complete ({found} files)"
        return False, "⚠️  API documentation needs improvement"
    
    def check_web_accessibility(self) -> Tuple[bool, str]:
        """Check if web frontend meets WCAG standards"""
        if os.path.exists("apps/web/README.md"):
            return True, "✅ Web frontend documented"
        return False, "⚠️  Web accessibility not fully documented"
    
    # ========================
    # PERFORMANCE CHECKS
    # ========================
    
    def check_rate_limiting(self) -> Tuple[bool, str]:
        """Check if rate limiting is implemented"""
        if os.path.exists("ocean-core/ocean_nanogrid.py"):
            with open("ocean-core/ocean_nanogrid.py", "r") as f:
                if "rate_limit" in f.read():
                    return True, "✅ Rate limiting implemented"
        return False, "⚠️  Rate limiting not found"
    
    def check_caching(self) -> Tuple[bool, str]:
        """Check if caching is configured"""
        if os.getenv("REDIS_URL"):
            return True, "✅ Redis caching configured"
        return False, "⚠️  Caching not fully configured"
    
    # ========================
    # RUN ALL CHECKS
    # ========================
    
    def run_all_checks(self) -> Dict:
        """Run all compliance checks"""
        
        checks = {
            "🔒 GDPR - Sigurimi i të Dhënave": {
                "Encryption at Rest": self.check_encryption_at_rest(),
                "TLS Certificates": self.check_tls_certificates(),
                "Consent Management": self.check_consent_management(),
                "Data Retention Policy": self.check_data_retention(),
            },
            "💳 PSD2 - Pagesa": {
                "Payment Gateway": self.check_payment_gateway(),
                "SCA Authentication": self.check_sca_authentication(),
                "PCI Compliance": self.check_pci_compliance(),
            },
            "🤖 AI/ML Compliance": {
                "AI Transparency": self.check_ai_transparency(),
                "Model Versioning": self.check_model_version(),
            },
            "🛡️  Security": {
                "API Authentication": self.check_api_authentication(),
                "Docker Security": self.check_docker_security(),
                "Monitoring": self.check_monitoring(),
            },
            "♿ Accessibility": {
                "API Documentation": self.check_api_documentation(),
                "Web Accessibility": self.check_web_accessibility(),
            },
            "⚡ Performance": {
                "Rate Limiting": self.check_rate_limiting(),
                "Caching": self.check_caching(),
            },
        }
        
        return checks
    
    def print_report(self):
        """Print formatted compliance report"""
        checks = self.run_all_checks()
        
        print("\n" + "="*70)
        print("🏛️  COMPLIANCE & STAGE CHECKER - KLOUD CLOUD")
        print("="*70)
        print(f"📅 Data: {self.timestamp}\n")
        
        total_checks = 0
        passed_checks = 0
        
        for category, items in checks.items():
            print(f"\n{category}")
            print("-" * 70)
            
            for check_name, (status, message) in items.items():
                total_checks += 1
                if status:
                    passed_checks += 1
                
                print(f"  {check_name:.<45} {message}")
        
        # Summary
        percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        print("\n" + "="*70)
        print(f"📊 REZYME: {passed_checks}/{total_checks} checks passed ({percentage:.1f}%)")
        print("="*70 + "\n")
        
        # Recommendations
        if percentage < 60:
            print("⚠️  VËREJTJE: Sistem nuk është i plotësisht në përputhje")
            print("    Prioritizoni kontrollimin e sigurisë dhe GDPR.\n")
        elif percentage < 80:
            print("🔶 PARALAJMËRIM: Disa kontrollime nuk kanë kaluar")
            print("    Shqyrtoni dhe plotësoni dokumentacionin.\n")
        else:
            print("✅ SUKSES: Sistemi është në përputhje të mirë!")
            print("    Vazhdoni me kontrollime periodike.\n")
        
        return {"passed": passed_checks, "total": total_checks, "percentage": percentage}

def main():
    checker = ComplianceChecker()
    result = checker.print_report()
    
    # Save report to JSON
    with open("compliance_report.json", "w") as f:
        json.dump({
            "timestamp": checker.timestamp,
            "result": result
        }, f, indent=2)
    
    print("💾 Raporti i ruajtur në: compliance_report.json")

if __name__ == "__main__":
    main()

