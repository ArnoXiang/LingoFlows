# LingoFlows - Collaborative Localization Management Platform

An integrated platform that combines AI chat capabilities, translation services, and project management functionalities, specifically designed for localization workflows.

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
- Translation history tracking

### 3. Request Management
- Localization request submission
- Detailed request form with:
  * Request name
  * Request background
  * Source and target languages
  * Word count estimation
  * Additional requirements
  * Expected delivery date
  * File upload
- Automatic creation of associated projects

### 4. Project Management System
- Project listing and overview
- Project status tracking
- Role-based permission control:
  * Localization Managers (LM) have full access
  * Business Owners (BO) can only view and edit their own projects
- Detailed project information including:
  * Project Name
  * Project Status
  * Request Name
  * Project Manager
  * Creation Time
  * Source and target languages
  * Word count
  * Expected delivery date
  * Additional requirements

### 5. Task Management
- Four task types tracking:
  * Translation
  * Linguistic Quality Assessment (LQA)
  * Translation Update
  * LQA Report Finalization
- Task status management:
  * Not Started
  * In Progress
  * Completed
- Task details:
  * Assignee allocation
  * Deadline setting
  * Task notes

### 6. Financial Management
- Project quote management
- Financial reporting
- Accessible only to Localization Managers

### 7. UI Features
- Responsive sidebar navigation
- User authentication (login/logout)
- Breadcrumb navigation
- Back-to-top functionality
- Bilingual interface (Chinese/English)
- Role-based menu display

## User Roles

### Localization Manager (LM)
- Can access all features and projects
- Can edit details of any project
- Can manage task assignments and deadlines
- Can access financial management

### Business Owner (BO)
- Can only view and edit their own projects
- Can submit localization requests
- Can view project status
- Cannot access financial management

### Non-logged Users
- Can only access AI Assistant and Translator tools

## Technology Stack

### Frontend
- Vue 3
- Arco Design Vue (UI Framework)
- Axios (HTTP client)

### Backend
- Flask (Python web framework)
- PyMySQL (Database connector)
- JWT (User authentication)
- Python

## Database
- MySQL

## Development Setup

### Prerequisites
- Node.js
- Python 3.8+
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
pip install flask flask-cors pymysql pyjwt
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

## Developer
Yizhuo Xiang
