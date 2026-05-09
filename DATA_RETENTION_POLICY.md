# 🔒 Data Retention & Privacy Policy

## Kloud Cloud - GDPR Compliance Document

---

## 1. Data Retention Policy

### Personal Data Retention Periods

| Data Type | Retention Period | Justification | Deletion Method |
| :--- | :--- | :--- | :--- |
| User Account Info | Duration of Account | Active Use | PURGE from DB |
| Payment Records | 7 Years | Tax/Legal | Encrypted Archive |
| EEG Data (Raw) | 30 Days | Processing Only | Secure Delete |
| Audio Data (Raw) | 14 Days | Processing Only | Secure Delete |
| Aggregated Analytics | 2 Years | Performance | Archive |
| Logs & Audit Trail | 1 Year | Security | Backup Archive |
| Cookies | 12 Months | Functionality | Client Delete |
| IP Addresses | 90 Days | Security | Anonymized |

### Deletion Process

``` sql
-- 1. Mark for deletion (soft delete)
UPDATE users SET deleted_at = NOW() WHERE user_id = $1;

-- 2. Wait for retention period
-- (Automated job runs daily)

-- 3. Hard delete after retention
DELETE FROM users WHERE deleted_at < NOW() - INTERVAL '30 days';
DELETE FROM user_data WHERE user_id NOT IN (SELECT id FROM users);
```

### Automated Retention Jobs

``` python
# retention_service.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)
def delete_expired_logs():
    """Daily deletion of logs older than 1 year"""
    db.execute("""
        DELETE FROM audit_logs 
        WHERE created_at < NOW() - INTERVAL '1 year'
    """)

@scheduler.scheduled_job('cron', hour=3, minute=0)
def delete_temp_eeg_data():
    """Daily deletion of temporary EEG data"""
    db.execute("""
        DELETE FROM raw_eeg 
        WHERE created_at < NOW() - INTERVAL '30 days'
        AND processing_completed = true
    """)
```

---

## 2. User Rights

### Right to Access (Article 15)

- **Method:** POST `/api/v1/user/data-export`
- **Format:** JSON, CSV, XML
- **Timeline:** 30 days
- **Cost:** Free

### Right to Erasure (Article 17)

- **Method:** DELETE `/api/v1/user/account`
- **Confirmation:** Email verification required
- **Timeline:** 30 days for all copies
- **Exceptions:** Legal obligation, payment records

### Right to Portability (Article 20)

- **Method:** POST `/api/v1/user/data-export`
- **Format:** Machine-readable (JSON/CSV)
- **Timeline:** 30 days
- **Cost:** Free

### Right to Rectification (Article 16)

- **Method:** PATCH `/api/v1/user/profile`
- **Audit:** All changes logged
- **Timeline:** Immediate

---

## 3. Data Categories

### 1️⃣ Directly Provided

- Email address
- Password (hashed + salted)
- Full name
- Phone number (optional)
- Payment info (via Stripe - PCI-DSS)

### 2️⃣ Automatically Collected

- IP addresses
- Device information
- Browser fingerprint
- Cookies (consent-based)
- Login timestamps

### 3️⃣ Derived/Generated

- EEG analysis results
- Audio processing output
- ML model predictions
- Behavioral patterns (anonymized)
- Usage analytics

### 4️⃣ Third-party Sourced

- Stripe payment data
- OAuth provider info (Clerk)
- Geographical location
- Device logs

---

## 4. Consent Management

### Consent Types

```javascript
// Managed via Clerk Authentication + Custom Consent Widget

const CONSENT_CATEGORIES = {
  ESSENTIAL: {
    description: "Authentication, security, fraud prevention",
    required: true,
    retention: "session"
  },
  FUNCTIONAL: {
    description: "User preferences, language, UI settings",
    required: false,
    retention: "12 months"
  },
  ANALYTICS: {
    description: "Usage patterns, performance monitoring",
    required: false,
    retention: "24 months"
  },
  MARKETING: {
    description: "Promotional emails, personalized content",
    required: false,
    retention: "24 months"
  }
};
```

### Consent Record

```sql
CREATE TABLE user_consents (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  category VARCHAR NOT NULL,
  granted BOOLEAN NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  ip_address INET,
  user_agent TEXT,
  version VARCHAR -- Consent version
);
```

---

## 5. Third-party Data Sharing

### Processors & Sub-processors

| Service | Purpose | Type | DPA | Adequacy |
| :--- | :--- | :--- | :--- | :--- |
| Stripe | Payments | Processor | ✅ | ✅ US/EU |
| AWS S3 | File Storage | Processor | ✅ | ✅ US/EU |
| Ollama | AI Processing | Internal | N/A | N/A |
| Clerk | Authentication | Processor | ✅ | ✅ US/EU |
| Grafana Cloud | Monitoring | Processor | ✅ | ✅ US/EU |

### Data Transfer Agreements

- **Legal Basis:** SCCs (Standard Contractual Clauses)
- **Adequacy:** EU-US Data Privacy Framework
- **Mechanism:** Automated + Annual Review

---

## 6. Data Protection Impact Assessment (DPIA)

### Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Unauthorized Access | Medium | High | Encryption + 2FA |
| Data Breach | Low | Critical | Incident Response Plan |
| Unauthorized Sharing | Low | High | Access Control + Audit |
| Service Interruption | Low | Medium | Backups + Redundancy |
| Regulatory Breach | Low | Critical | Compliance Monitoring |

### Safeguards Implemented

**Technical:**

- End-to-end encryption (TLS 1.3)
- AES-256 encryption at rest
- Secure password hashing (bcrypt)
- Regular penetration testing

**Organizational:**

- GDPR compliance training
- Incident response plan
- Data protection officer
- Privacy by design

**Contractual:**

- DPA with all processors
- SCCs with non-EU partners
- Confidentiality agreements

---

## 7. Incident Response

### Notification Timeline

``` text
⏱️ Detection
    ↓ (1-24 hours)
📢 Internal Alert
    ↓ (24 hours)
⚖️ Authority Notification (if required)
    ↓ (72 hours max)
👥 User Notification
```

### Incident Log Template

``` json
{
  "incident_id": "INC-2026-001",
  "date": "2026-02-03",
  "type": "Unauthorized Access",
  "severity": "MEDIUM",
  "affected_users": 150,
  "data_categories": ["EEG Data", "Metadata"],
  "root_cause": "Misconfigured S3 bucket",
  "detection_time": "2 hours",
  "containment_time": "30 minutes",
  "remediation": "Policy updated + re-encryption",
  "authority_notified": true,
  "users_notified": true,
  "lessons_learned": "Implement automated compliance checks"
}
```

---

## 8. Compliance Status

**Last Audit:** 2026-02-03  
**Next Audit:** 2026-05-03 (Quarterly)  
**Compliance Level:** 75% (In Progress)

### Remaining Actions

- [ ] Implement Data Retention Schedule (Week 1)
- [ ] Deploy Consent Management Widget (Week 2)
- [ ] Create DPIA Documentation (Week 3)
- [ ] Setup Incident Response (Week 4)
- [ ] Train Team on GDPR (Ongoing)

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-03  
**Next Review:** 2026-03-03  
**Approved By:** Compliance Team

