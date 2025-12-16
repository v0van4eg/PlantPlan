-- Plant Tracker Application Database Schema

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations table (each user can have their own locations)
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plants table
CREATE TABLE plants (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(100),
    planted_date DATE,
    notes TEXT,
    photo_data BYTEA, -- Binary data for photo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Growth phases table
CREATE TABLE growth_phases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    phase_order INTEGER NOT NULL DEFAULT 0
);

-- Insert standard growth phases
INSERT INTO growth_phases (name, description, phase_order) VALUES
('Прорастание', 'Seed germinating', 1),
('Вегетация', 'Growth period with leaves and stems', 2),
('Цветение', 'Flowers beginning to form', 3),
('Плодоношение', 'Fruits developing', 4),
('Сбор урожая', 'Ready for harvest', 5);

-- Plant timeline events table
CREATE TABLE timeline_events (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'growth_phase', 'fertilization', 'note', 'watering', etc.
    event_date DATE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    phase_id INTEGER REFERENCES growth_phases(id), -- for growth phase events
    fertilization_type VARCHAR(100), -- for fertilization events
    fertilization_amount VARCHAR(50), -- quantity of fertilizer
    photo_data BYTEA, -- Binary data for photo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_locations_user_id ON locations(user_id);
CREATE INDEX idx_plants_user_id ON plants(user_id);
CREATE INDEX idx_plants_location_id ON plants(location_id);
CREATE INDEX idx_timeline_events_plant_id ON timeline_events(plant_id);
CREATE INDEX idx_timeline_events_event_date ON timeline_events(event_date);
CREATE INDEX idx_timeline_events_event_type ON timeline_events(event_type);

-- Optional: Table for user preferences/settings
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    preferred_units VARCHAR(20) DEFAULT 'metric', -- metric/imperial
    notifications_enabled BOOLEAN DEFAULT TRUE,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);