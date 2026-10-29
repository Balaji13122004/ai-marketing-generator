-- ==============================================================================
-- FS-7: AI-Powered Image Generator Database Schema (MySQL 8.x)
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS zap_imagegen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zap_imagegen;

-- 1. Brand Profiles Table
CREATE TABLE IF NOT EXISTS brand_profiles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    app_name        VARCHAR(100) NOT NULL UNIQUE,
    style_prompt    VARCHAR(1000) NOT NULL,
    accent_color    VARCHAR(20) DEFAULT '#6c2bd9',    -- hex color, used by the template engine
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Generation Threads Table
CREATE TABLE IF NOT EXISTS generation_threads (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    app_name            VARCHAR(100) NOT NULL,
    image_type          VARCHAR(50) NOT NULL,          -- 'tile', 'banner', 'timeline_card', 'custom'
    width_px            INT NOT NULL,
    height_px           INT NOT NULL,
    original_prompt     VARCHAR(500) NOT NULL,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Generated Images Table (Supports Multi-Round Refinement Trees)
CREATE TABLE IF NOT EXISTS generated_images (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    thread_id           INT NOT NULL,
    round_number        INT NOT NULL DEFAULT 1,          -- 1 = initial generation, 2+ = refinement round
    refinement_text     VARCHAR(500) DEFAULT NULL,        -- instruction that guided this round
    template_used       VARCHAR(50) DEFAULT NULL,         -- parametric template name applied
    prompt_text         VARCHAR(500) NOT NULL,            -- effective prompt sent to AI
    image_url           VARCHAR(500) NOT NULL,            -- e.g. /media/generated/banner_1024x500_201.png
    parent_image_id     INT DEFAULT NULL,                 -- chosen parent from prior round
    is_selected         BOOLEAN NOT NULL DEFAULT FALSE,    -- true if user finalized/chose this image
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_gen_thread FOREIGN KEY (thread_id) REFERENCES generation_threads(id) ON DELETE CASCADE,
    CONSTRAINT fk_parent_image FOREIGN KEY (parent_image_id) REFERENCES generated_images(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed Default Brand Profiles
INSERT INTO brand_profiles (app_name, style_prompt, accent_color) VALUES
('Campus Life', 'Vibrant campus photography, energetic university students, modern collegiate atmosphere, warm natural sunlight, optimistic and social vibe', '#3377FF'),
('Carelon.engage', 'Professional healthcare and wellness, modern clinical consultation, calming blues and greens, empathetic human connection, clean minimal aesthetic', '#06C270'),
('LifeCykul', 'Dynamic athletic adventure, outdoor cycling and fitness, vibrant high-contrast action photography, cinematic golden hour lighting, energetic and healthy lifestyle', '#FF5722'),
('Zap Creative', 'Bold tech-forward design, cybernetic geometric elements, vivid purple neon accents, futuristic workspace aesthetic, innovative commercial look', '#6C2BD9')
ON DUPLICATE KEY UPDATE app_name=app_name;
