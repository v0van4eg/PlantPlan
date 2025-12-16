# Plant Tracker - Docker Setup

This is a web application for tracking plant growth phases, fertilization, notes, and calendar events, similar to "Grow with Jane" for Android. Plants can be organized in different user-defined locations, and each plant has a timeline tracking events and growth phases.

## Features

- Plant management with names, species, and notes
- User-defined locations for organizing plants
- Timeline functionality to record events (growth phases, fertilization, watering, notes)
- Growth phase tracking with predefined stages
- Responsive UI with Bootstrap

## Docker Setup

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Build and start the services:
```bash
docker-compose up --build
```

2. The application will be available at `http://localhost:5000`

3. To stop the services, press `Ctrl+C` or run:
```bash
docker-compose down
```

### Services

- Web application: Runs on port 5000
- PostgreSQL database: Runs on port 5432 (internal only)

### Data Persistence

Database data is persisted using Docker volumes. Data will remain even after stopping the containers.

## Architecture

- Flask web application
- PostgreSQL database
- SQLAlchemy ORM
- Bootstrap frontend framework

## Development

For development purposes, the application volume is mounted to enable live updates without rebuilding the container.