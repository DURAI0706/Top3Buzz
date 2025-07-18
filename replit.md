# Top3Buzz - Buzzer Competition System

## Overview

Top3Buzz is a web-based buzzer system designed for competitive gaming events or quiz competitions. It allows multiple teams to join a game session and compete by buzzing in when they want to answer questions. The system features a real-time buzzer mechanism with admin controls for managing the competition flow.

**Recent Major Update (2025-07-18):** Modified system to record ALL teams that buzz in (not just top 3), display complete rankings, and simplified team registration by removing manual team ID entry.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **Styling**: Custom CSS with retro gaming theme featuring neon effects and gradients
- **User Interface**: Responsive design with separate interfaces for teams and admin
- **Real-time Updates**: JavaScript-based polling for live buzzer state updates

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Session Management**: Flask sessions for team identification
- **State Management**: In-memory global variables for buzzer state
- **API Structure**: RESTful endpoints for team actions and admin controls

## Key Components

### Team Management System
- **Team Registration**: Simplified registration requiring only team name (auto-generated IDs)
- **Team Removal**: Admin ability to remove teams from active competition
- **Session Tracking**: Per-team session management for persistent identification

### Buzzer System
- **Buzzer State**: Global state management for active/inactive buzzer
- **Timer System**: Countdown timer functionality for timed responses
- **Buzz Queue**: Ordered list of teams that have buzzed in with timestamps
- **Team Filtering**: Ability to exclude removed teams from competition

### Admin Panel
- **Competition Control**: Start/stop buzzer, reset system, manage timer
- **Team Management**: View active teams, remove teams, monitor buzz queue
- **Real-time Monitoring**: Live updates of buzzer state and team activity

## Data Flow

1. **Team Join Flow**: Teams select ID and name → Session creation → Redirect to team buzzer page
2. **Buzzer Flow**: Team clicks buzzer → Check if buzzer active → Add to buzz queue → Update global state
3. **Admin Flow**: Admin controls → Update global state → Broadcast changes to all connected clients
4. **State Synchronization**: JavaScript polling keeps all clients synchronized with server state

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and templating
- **Python Standard Library**: datetime, os, logging modules
- **Browser APIs**: JavaScript for client-side interactivity

### Session Management
- **Flask Sessions**: Server-side session storage using secret key
- **Environment Variables**: SESSION_SECRET for production security

### Styling Framework
- **Custom CSS**: Retro gaming theme with neon effects
- **Responsive Design**: Mobile-friendly interface design
- **Font**: Courier New monospace for retro aesthetic

## Deployment Strategy

### Environment Configuration
- **Session Secret**: Configurable via environment variable with fallback
- **Debug Mode**: Logging configured for development debugging
- **Static Assets**: CSS served via Flask static file handling

### Application Structure
- **Single Module**: Monolithic Flask application in app.py
- **Template Directory**: HTML templates in templates/ folder
- **Static Directory**: CSS and other assets in static/ folder
- **Entry Point**: main.py imports and runs the Flask app

### State Management Considerations
- **In-Memory Storage**: Current implementation uses global variables
- **Scalability Limitation**: Single-instance deployment due to in-memory state
- **Session Persistence**: Team sessions maintained across page refreshes
- **Data Volatility**: All buzzer state lost on application restart

### Security Considerations
- **Session Security**: Secret key required for session management
- **Production Ready**: Environment-based configuration for deployment
- **Input Validation**: Form data validation for team registration