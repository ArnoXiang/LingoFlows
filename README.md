![LingoFlows](imgs/LIngoFlows_logo.jpg)

# LingoFlows - Collaborative Localization Management Platform



Yizhuo Xiang


**Overview**

LingoFlows is a streamlined and efficient localization project management platform designed to facilitate seamless collaboration between business stakeholders, project managers, and financial teams. It simplifies request submissions, project execution, and financial oversight, ensuring transparency, efficiency, and scalability in localization workflows.


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
=======
![Diagram

Description automatically generated](Aspose.Words.f62be7c3-b534-4baf-9e4f-44d57eba7483.001.png)

Workflow (basic)


` `**Key Features**

1\. Request Management: Allows business owners to submit, track, filter, and update localization requests.

<<<<<<< HEAD
### Backend
- Flask (Python web framework)
- PyMySQL (Database connector)
- JWT (User authentication)
- Python
=======
2\. Project Coordination: Enables project managers to oversee project basic information and progress, assign tasks, and distribute communications.
>>>>>>> dcdeeb93bcf01670b93ffa5a055d3932a7fa9beb

3\. Financial Oversight: Facilitates cost tracking and quote management from Language Service Providers (LSPs).

4\.** Role-Based Access Control: Granular permissions for different user roles to improve security and compliance.

<<<<<<< HEAD
### Prerequisites
- Node.js
- Python 3.8+
- MySQL
=======
5\. Data Insights: Provides real-time dashboards for project tracking and financial reporting.
>>>>>>> dcdeeb93bcf01670b93ffa5a055d3932a7fa9beb

6\. Timezone Converter: Facilitates time zone conversion to help PMs, business owners, and LSPs coordinate across different regions.

7\. AI Assistant: Assists users with various operational tasks, providing contextual help and handling calculations.

8\. External Multi-Language Machine Translation Services (Optional): Supports integration with external machine translation for enhanced flexibility.

<<<<<<< HEAD
3. Install Backend Dependencies
```bash
pip install flask flask-cors pymysql pyjwt
```
=======
` `**User Roles & Responsibilities**

` `1. Business Owner

(1) Submit localization requests via a structured form.

(2) Modify requests before project initiation.

(3) Monitor request status and receive final deliverables.

(4) Download Completed Files

` `2. Project Manager

(1) Review and process submitted requests.

(2) Create, assign, and track projects.

(3) Manage email communication with internal BOs and external LSPs.

(4) Ensure timely delivery and maintain project quality standards.

(5) Upload Completed Files

` `3. Financial Team

(1) Oversee budget allocation and expense tracking.

(2) Extract and consolidate quotes from LSPs’s emails. (Regular Expression & Pandas)

(3) Update financial records and approve cost estimates.

` `**Platform Workflow (overview)**

LingoFlows follows a structured workflow to streamline localization project management and ensure efficiency across all stakeholders:

- **Request Submission:** BOs submit localization requests by filling out key project details, including request name, language pairs, instructions, deadlines, and file uploads.

- **Project Creation & Task Assignment:** PMs review and approve requests, converting them into projects. They assign tasks to different LSPs or freelancers, set deadlines for each step, and send automated email notifications.

- **Translation & Quoting:** LSPs download source files from the platform, complete the translation, and upload the final files. They also send standardized quotes via email.

- **Quote Processing & Financial Tracking:** PMs upload received quotes, and the platform automatically extracts key details—such as project ID, pricing, and word count—storing them in the project database for financial tracking and reporting.

**Workflow (Detailed)**

` `Step 1: Request Submission (Business Owner)

1\. Log in to the platform.

2\. Click "Raise a Request."

3\. Complete the request form with necessary details:

`   `- Request Name: Provide a clear and distinguishable title.

`   `- Request Background: Briefly outline the project scope and objectives.

`   `- Source & Target Languages: Specify translation requirements.

`   `- Estimated Word Count: Helps determine the expected completion timeline.

`   `- Additional Requirements: Indicate if linguistic quality assurance (LQA) or image text translation is needed.

`   `- Expected Delivery Date: Set a realistic deadline based on system recommendations.

4\. Submit the request.

5\. Track the request status on the dashboard.

![Graphical user interface, text, application, email

Description automatically generated](Aspose.Words.f62be7c3-b534-4baf-9e4f-44d57eba7483.002.png) ![Graphical user interface, text, application, email

Description automatically generated](Aspose.Words.f62be7c3-b534-4baf-9e4f-44d57eba7483.003.png)

Request Raising Form (in developing)

![Graphical user interface, text, application, email

Description automatically generated](Aspose.Words.f62be7c3-b534-4baf-9e4f-44d57eba7483.004.png)

Requests / Projects Management Dashboard (in developing)


` `Step 2: Project Management (Project Manager)

1\. Review submitted requests and approve or request modifications.

2\. Assign tasks and define project timelines.

3\. Generate automated emails for project kickoff and updates.

4\. Monitor progress and address roadblocks.

5\. Upload completed deliverables and mark the project as “Completed.”

![Text

Description automatically generated with medium confidence](Aspose.Words.f62be7c3-b534-4baf-9e4f-44d57eba7483.005.png)

Project Mail Sending Form (in developing)


` `Step 3: Financial Processing

1\. Review LSP-provided quotes.

2\. Extract key financial details and update records.

3\. Approve and finalize project costs.

4\. Generate financial reports for stakeholders.



**Implemented Features (2025.03.04)**

The current version of LingoFlows already supports several essential functionalities, with both front-end and back-end implementations:

Project Management System (Early Development Stage)

- Project listing and detailed tracking, including:
  - Project Name
  - Project Status
  - Request Name
  - Project Manager
  - Creation Time
  - Translation Task Status
  - LQA Task Status
  - Translation Update Status
  - LQA Report Finalization Status
- Database Implementation: MySQL database structure established, storing project metadata and request details.
- Technology Stack: Back-end powered by Flask and MySQL, with Axios managing API requests between front-end and back-end.

AI Assistant

- Real-time chat interface with context-aware conversation capabilities.
- Character-by-character response animation for a dynamic user experience.
- Live chat history for seamless interactions and continuity.

Translation Tool

- Professional translation services with multi-language support.
- Integrated translation form interface for structured input and processing.

UI Features

- Responsive sidebar navigation for improved usability.
- User authentication (login/logout) with secure session handling.
- Breadcrumb navigation and back-to-top functionality for an intuitive experience.
- Dark theme support for enhanced visual comfort.
- ` `Vue 3, Arco Design Vue for UI components



` `Conclusion

LingoFlows is designed to enhance efficiency, transparency, and collaboration in localization project management. By standardizing workflows and automating key processes, it ensures smooth operations for all stakeholders. 








=============

## Developer
Yizhuo Xiang

