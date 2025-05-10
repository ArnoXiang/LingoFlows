**LingoFlows - Collaborative Localization Management System (CLMS)**

Yizhuo Xiang

**Overview**

LingoFlows is a streamlined localization project management platform designed to facilitate seamless collaboration between Business Owners (BO), Project Managers (PM), Language Managers (LM), and Financial teams. It simplifies request submissions, project execution, and financial oversight, ensuring transparency, efficiency, and scalability in localization workflows.

![Diagram


Workflow (basic)

` `**Key Features**

1\. Request Management: Allows BOs to submit, track, filter, and update localization requests.

2\. Project Coordination: Enables PMs to oversee project basic information and progress, assign tasks, and distribute communications.

3\. Financial Oversight: Facilitates cost tracking and quote management from Language Service Providers (LSPs).

4\.** Role-Based Access Control: Granular permissions for different user roles to improve security and compliance.

5\. Data Insights: Provides real-time dashboards for project tracking and financial reporting.

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

2\. Click “Raise a Request.”

3\. Complete the request form with necessary details:

`   `- Request Name: Provide a clear and distinguishable title.

`   `- Request Background: Briefly outline the project scope and objectives.

`   `- Source & Target Languages: Specify translation requirements.

`   `- Estimated Word Count: Helps determine the expected completion timeline.

`   `- Additional Requirements: Indicate if LQA or image localization is needed.

`   `- Expected Delivery Date: Set a realistic deadline based on system recommendations.

4\. Submit the request.

5\. Track the request status on the dashboard.


Request Raising Form I  (in developing)


Request Raising Form II  (in developing)


Requests / Projects Management Dashboard (in developing)


Requests / Projects Management  (in developing)

` `Step 2: Project Management (Project Manager)

1\. Review submitted requests and approve or request modifications.

2\. Assign tasks and define project timelines.

3\. Generate automated emails for project kickoff and updates.

4\. Monitor progress and address roadblocks.

5\. Upload completed deliverables and mark the project as “Completed.”


Project Mail Sending Form (in developing)


` `Step 3: Financial Processing (In developing)

1\. Review LSP-provided quotes.

2\. Extract key financial details and update records.

3\. Approve and finalize project costs.

4\. Generate financial reports for stakeholders.




Financial Management (in developing)


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


UI Features

- Responsive sidebar navigation for improved usability.
- User authentication (login/logout) with secure session handling.
- Breadcrumb navigation and back-to-top functionality for an intuitive experience.
- Dark theme support for enhanced visual comfort.
- ` `Vue 3, Arco Design Vue for UI components



` `Conclusion

LingoFlows is designed to enhance efficiency, transparency, and collaboration in localization project management. By standardizing workflows and automating key processes, it ensures smooth operations for all stakeholders. 
