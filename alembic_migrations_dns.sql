-- Alembic migration for DNS & Hosting Management schema
-- Run with: alembic upgrade head

-- Create DNS zones table
CREATE TABLE IF NOT EXISTS dns_zones (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'active',
    nameserver_1 VARCHAR(255) DEFAULT 'jonathan.ns.kloud.cloud',
    nameserver_2 VARCHAR(255) DEFAULT 'katja.ns.kloud.cloud',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create DNS records table
CREATE TABLE IF NOT EXISTS dns_records (
    id VARCHAR(36) PRIMARY KEY,
    zone_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(10) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    ttl INT DEFAULT 3600,
    proxy_status VARCHAR(50) DEFAULT 'DNS only',
    priority INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (zone_id) REFERENCES dns_zones(id) ON DELETE CASCADE,
    INDEX idx_zone_id (zone_id),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create hosting origins table
CREATE TABLE IF NOT EXISTS hosting_origins (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    health_status VARCHAR(50) DEFAULT 'Healthy',
    region VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    last_health_check TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_region (region),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample data for demo
INSERT INTO dns_zones (id, user_id, domain, status, nameserver_1, nameserver_2) VALUES
('zone-001', 'demo-user-001', 'kameleon.life', 'active', 'jonathan.ns.kloud.cloud', 'katja.ns.kloud.cloud'),
('zone-002', 'demo-user-001', 'aiagi.io', 'active', 'jonathan.ns.kloud.cloud', 'katja.ns.kloud.cloud'),
('zone-003', 'demo-user-001', 'aba-gmbh.eu', 'active', 'jonathan.ns.kloud.cloud', 'katja.ns.kloud.cloud'),
('zone-004', 'demo-user-001', 'clisonix.com', 'active', 'jonathan.ns.kloud.cloud', 'katja.ns.kloud.cloud');

INSERT INTO dns_records (id, zone_id, name, type, content, ttl, proxy_status) VALUES
('rec-001', 'zone-001', 'api', 'A', '217.160.0.175', 3600, 'Proxied'),
('rec-002', 'zone-001', '@', 'A', '217.160.0.175', 3600, 'Proxied'),
('rec-003', 'zone-001', 'api', 'AAAA', '2001:8d8:100f:f000::200', 3600, 'Proxied'),
('rec-004', 'zone-001', '@', 'AAAA', '2001:8d8:100f:f000::200', 3600, 'Proxied'),
('rec-005', 'zone-001', 'autoconfig', 'CNAME', 'autoconfigure.strato.de', 3600, 'Proxied'),
('rec-006', 'zone-001', 'www', 'CNAME', 'kameleon.life', 3600, 'Proxied'),
('rec-007', 'zone-001', '*', 'MX', 'smtpin.rzone.de', 3600, 'DNS only', 5),
('rec-008', 'zone-001', '@', 'MX', 'smtpin.rzone.de', 3600, 'DNS only', 5),
('rec-009', 'zone-001', '_domainkey', 'TXT', '"o=~; t=y; r=dkim@rzone.de"', 3600, 'DNS only');

INSERT INTO hosting_origins (id, user_id, name, endpoint, health_status, region, role) VALUES
('origin-001', 'demo-user-001', 'Web App Origin', 'web.kloud.aiagi.io', 'Healthy', 'EU Central', 'frontend'),
('origin-002', 'demo-user-001', 'API Gateway', 'api.kloud.aiagi.io', 'Healthy', 'EU West', 'api'),
('origin-003', 'demo-user-001', 'Ocean Core', 'ocean.kloud.aiagi.io', 'Healthy', 'Global', 'commerce'),
('origin-004', 'demo-user-001', 'Static Assets', 'assets.kloud.aiagi.io', 'Warning', 'Multi-region', 'cdn');
