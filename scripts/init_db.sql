-- Helix Database Initialization
-- Creates tables for caching, metrics, and ML training data

-- Enable pgvector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Table for caching successful strategies
CREATE TABLE IF NOT EXISTS strategy_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    platform VARCHAR(100) NOT NULL,
    page_type VARCHAR(100) NOT NULL,
    intent TEXT NOT NULL,
    selector TEXT NOT NULL,
    strategy_type VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    metadata JSONB,
    success_count INTEGER DEFAULT 1,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days')
);

-- Index for fast cache lookups
CREATE INDEX IF NOT EXISTS idx_strategy_cache_key ON strategy_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_strategy_cache_platform ON strategy_cache(platform, page_type);

-- Table for element identification attempts (for metrics and ML training)
CREATE TABLE IF NOT EXISTS identification_attempts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(100) NOT NULL,
    page_type VARCHAR(100) NOT NULL,
    intent TEXT NOT NULL,
    strategies_attempted JSONB NOT NULL,
    successful_strategy JSONB,
    success BOOLEAN NOT NULL,
    time_taken_ms FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table for user feedback
CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    feedback_id VARCHAR(255) UNIQUE NOT NULL,
    platform VARCHAR(100) NOT NULL,
    intent TEXT NOT NULL,
    selector_attempted TEXT,
    was_successful BOOLEAN NOT NULL,
    correct_selector TEXT,
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table for strategy weights (ML Layer 7)
CREATE TABLE IF NOT EXISTS strategy_weights (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(100) NOT NULL,
    weight FLOAT NOT NULL DEFAULT 1.0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(platform, strategy_type)
);

-- Initialize default strategy weights
INSERT INTO strategy_weights (platform, strategy_type, weight) VALUES
    ('salesforce_lightning', 'semantic_intent', 1.0),
    ('salesforce_lightning', 'visual_fingerprint', 1.0),
    ('salesforce_classic', 'semantic_intent', 1.0),
    ('salesforce_classic', 'visual_fingerprint', 1.0),
    ('sap_fiori', 'semantic_intent', 1.0),
    ('sap_fiori', 'visual_fingerprint', 1.0),
    ('sap_gui', 'semantic_intent', 1.0),
    ('sap_gui', 'visual_fingerprint', 1.0),
    ('workday', 'semantic_intent', 1.0),
    ('workday', 'visual_fingerprint', 1.0),
    ('oracle_cloud', 'semantic_intent', 1.0),
    ('oracle_cloud', 'visual_fingerprint', 1.0)
ON CONFLICT (platform, strategy_type) DO NOTHING;

-- Table for visual fingerprints (for computer vision caching)
CREATE TABLE IF NOT EXISTS visual_fingerprints (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(100) NOT NULL,
    page_type VARCHAR(100) NOT NULL,
    element_type VARCHAR(100) NOT NULL,
    perceptual_hash VARCHAR(255) NOT NULL,
    bbox_coordinates JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_matched TIMESTAMP DEFAULT NOW()
);

-- Performance monitoring views
CREATE OR REPLACE VIEW platform_performance AS
SELECT 
    platform,
    COUNT(*) as total_attempts,
    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
    AVG(time_taken_ms) as avg_time_ms,
    COUNT(CASE WHEN successful_strategy->>'strategy_type' = 'semantic_intent' THEN 1 END) as semantic_successes,
    COUNT(CASE WHEN successful_strategy->>'strategy_type' = 'visual_fingerprint' THEN 1 END) as visual_successes
FROM identification_attempts
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY platform;

-- Grant permissions to helix user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO helix;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO helix;