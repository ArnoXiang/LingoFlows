# AI-Powered Translation & Chat Platform

An integrated platform that combines AI chat capabilities, translation services, and project management functionalities.

## Core Features

### 1. AI Assistant
- Real-time chat interface
- Character-by-character response animation
- Context-aware conversations
- Live chat history

### 2. Translation Tool
- Professional translation services
- Multi-language support
- Integrated translation form interface

### 3. Project Management System
- Project listing and overview
- Project status tracking
- Detailed project information including:
  * Project Name
  * Project Status
  * Request Name
  * Project Manager
  * Creation Time
  * Translation Task Status
  * LQA Task Status
  * Translation Update Status
  * LQA Report Finalization Status

### 4. UI Features
- Responsive sidebar navigation
- User authentication (login/logout)
- Breadcrumb navigation
- Back-to-top functionality
- Dark theme support

## Technology Stack

### Frontend
- Vue 3
- Arco Design Vue (UI Framework)
- Axios (HTTP client)

### Backend
- Flask (Python web framework)
- PyMySQL (Database connector)
- Python

## Database
- MySQL

## Development Setup

### Prerequisites
- Node.js
- Python 3.8
- MySQL

### Installation

1. Clone the repository
```bash
git clone [repository-url]
cd [project-directory]
```

2. Install Frontend Dependencies
```bash
npm install
```

3. Install Backend Dependencies
```bash
pip install flask flask-cors pymysql
```

4. Database Setup
- Ensure MySQL service is running
- Create a database named 'l10n_management'
- Configure database connection in app.py

### Running the Application

1. Start Frontend Development Server
```bash
npm run dev
```

2. Start Backend Server
```bash
python app.py
```

## Configuration Notes
- Backend server runs on port 5000
- Ensure proper database table structure is created
- CORS settings must be properly configured
- Default database credentials:
  * Host: localhost
  * User: root
  * Password: root
  * Database: l10n_management

## Production Build
```bash
npm run build
```

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
This project is licensed under the MIT License.
