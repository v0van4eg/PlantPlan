# Plant Tracker Web Application

A web application for tracking plant growth phases, fertilization, notes, and calendar events, similar to "Grow with Jane" for Android.

## Features

- Track multiple plants with custom names and species
- Organize plants in user-defined locations
- Record growth phases, fertilization, watering, and notes
- View plant timelines with historical events
- Personalized user accounts with private data

## Database Schema

The application uses PostgreSQL with the following main tables:

- `users`: Stores user account information
- `locations`: User-defined locations for organizing plants
- `plants`: Individual plants with metadata
- `growth_phases`: Standard growth phase definitions
- `timeline_events`: Historical events for each plant
- `user_settings`: User-specific preferences

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database (update connection string in `app.py` as needed)
4. Initialize the database:
   ```bash
   python init_db.py
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Access the application through your browser at `http://localhost:5000`
2. Navigate to the Plants section to view and manage your plants
3. Add new plants and record events in their timelines
4. Organize plants by assigning them to different locations

## Project Structure

```
plant_tracker/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── dashboard.html     # Dashboard page
│   ├── plants.html        # Plants listing
│   ├── plant_detail.html  # Plant detail page
│   ├── locations.html     # Locations page
│   └── add_plant.html     # Add plant form
└── static/                # Static assets (CSS, JS, images)
```

## Development

To extend the application:

1. Add new routes in `app.py`
2. Create new templates in the `templates/` directory
3. Extend models in `models.py` as needed
4. Update the database schema in `plant_tracker_db_schema.sql` and apply migrations

## API Endpoints

- `GET /api/timeline/<plant_id>`: Get timeline data for a specific plant in JSON format

## Security Considerations

For production deployment:
- Use environment variables for sensitive configuration
- Implement proper authentication and authorization
- Add CSRF protection
- Sanitize user inputs
- Use HTTPS