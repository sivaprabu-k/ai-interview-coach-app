# AI Interview Coach

An AI-powered interview preparation platform designed to help developers practice technical interview questions, improve their answers, and prepare for software engineering interviews.

## Project Goals

- Practice technical interview questions.
- Receive AI-assisted feedback on submitted answers.
- Upload technical documents and ask questions based on their content.
- Track interview preparation progress and identify improvement areas.
- Maintain a personalized career profile.
- Generate interview questions based on saved career details.
- Support resumable interview sessions and answer attempts.
- Build a full-stack application using modern backend, frontend, and AI technologies.

## Technology Stack

### Backend
- Python 3.13
- FastAPI
- Pydantic Settings
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT Authentication
- Pytest

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Axios
- Recharts
- Lucide React

### AI and Development Tools
- Google Gemini API
- LLM-based question generation and answer evaluation
- RAG (Retrieval-Augmented Generation)
- Text embeddings
- LangChain
- PostgreSQL with pgvector
- Git and GitHub
- Docker
- GitHub Actions for CI/CD

## Project Structure

```text
ai-interview-coach/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── uploads/
│   ├── alembic/
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
├── frontend/
├── .github/
├── .gitignore
└── README.md
```

## Current Progress

### Backend Development

- [x] Initialize the Git repository and configure GitHub.
- [x] Set up the Python backend environment.
- [x] Create the FastAPI application.
- [x] Implement root and health-check endpoints.
- [x] Add configuration management using Pydantic Settings.
- [x] Configure PostgreSQL database integration.
- [x] Integrate SQLAlchemy ORM.
- [x] Implement database migrations using Alembic.
- [x] Implement user registration and authentication.
- [x] Implement JWT-based authentication and authorization.
- [x] Implement access and refresh token management.
- [x] Implement logout and session revocation.
- [x] Implement interview session management.
- [x] Implement interview question generation.
- [x] Implement answer evaluation and session results functionality.
- [x] Implement user-specific access control for interview resources.
- [x] Implement interview history APIs.
- [x] Implement performance insights API.
- [x] Calculate evaluation metrics, average scores, and score trends.
- [x] Identify frequently mentioned strengths and improvement areas.
- [x] Implement the Career Profile model and database migration.
- [x] Implement Career Profile GET and PUT APIs.
- [x] Implement user-specific Career Profile management.
- [x] Integrate Career Profile defaults with AI question generation.
- [x] Support role, experience, skills, and difficulty fallback from the saved profile.
- [x] Support fractional years of experience.
- [x] Support configurable question generation from 1 to 20 questions.
- [x] Store resolved question-generation details in interview history.
- [x] Implement interview session detail retrieval.
- [x] Retrieve question-level progress and previous answer attempts.
- [x] Include expected answer points in session question details.
- [x] Support answer submission for individual session questions.
- [x] Implement answer evaluation retry functionality.
- [x] Automatically complete interview sessions when all questions have successful evaluations.
- [x] Implement session ownership and authorization checks.

### Career Profile Module

- [x] Create a user-specific Career Profile.
- [x] Store professional summary.
- [x] Store years of experience.
- [x] Store technical skills.
- [x] Store target job roles.
- [x] Store preferred interview difficulty.
- [x] Implement profile creation and update functionality.
- [x] Implement profile retrieval functionality.
- [x] Integrate profile details with AI question generation.

### AI Question Generation Module

- [x] Integrate Google Gemini for interview question generation.
- [x] Generate questions based on the selected job role.
- [x] Use saved Career Profile experience and technical skills.
- [x] Map profile difficulty levels to AI generation difficulty.
- [x] Allow users to override profile defaults during interview setup.
- [x] Support configurable question counts: 5, 10, 15, and 20.
- [x] Validate the requested number of generated questions.
- [x] Store generated questions in question-generation history.
- [x] Verify generated questions through the frontend interview workflow.

### Interview Session Management Module

- [x] Implement interview session creation.
- [x] Implement session detail retrieval.
- [x] Track individual question progress.
- [x] Display expected answer points for each question.
- [x] Store and retrieve multiple answer attempts.
- [x] Track answer evaluation status: pending, succeeded, and failed.
- [x] Track successful and total attempts for each question.
- [x] Support retrying failed answer evaluations.
- [x] Automatically mark sessions as completed after all questions are successfully evaluated.

### Document-Based RAG Module

- [x] Implement PDF and DOCX document upload.
- [x] Add file extension and file size validation.
- [x] Extract text from uploaded documents.
- [x] Implement document chunking with overlap.
- [x] Generate text embeddings using Gemini.
- [x] Configure PostgreSQL pgvector for vector storage.
- [x] Implement similarity-based document retrieval.
- [x] Add similarity threshold filtering.
- [x] Implement user-specific document retrieval.
- [x] Generate answers using retrieved document context.
- [x] Add fallback responses when relevant information is unavailable.
- [x] Implement document upload, listing, and question-answering APIs.
- [x] Add document module tests (12 tests passing).

### Frontend Development

- [x] Set up the React and TypeScript frontend.
- [x] Implement the authentication UI.
- [x] Build the dashboard based on the InterviewAI UI reference.
- [x] Develop interview session and question interfaces.
- [x] Integrate AI answer evaluation and session results.
- [x] Implement interview history interface.
- [x] Build the performance insights dashboard.
- [x] Display evaluation metrics and average scores.
- [x] Implement score trend visualization using Recharts.
- [x] Display top strengths and improvement areas.
- [x] Integrate frontend authentication with backend APIs.
- [x] Implement automatic access token refresh and retry.
- [x] Implement logout functionality.
- [x] Implement protected routes.
- [x] Verify frontend API integration and production build.
- [x] Create the My Career Profile page.
- [x] Integrate Career Profile GET and PUT APIs.
- [x] Implement profile loading, editing, and saving.
- [x] Load saved Career Profile defaults in interview setup.
- [x] Integrate AI question generation with the interview setup.
- [x] Add question-count selection (5, 10, 15, and 20).
- [x] Display dynamically generated questions in interview sessions.
- [x] Implement interview question progress tracking.
- [x] Display current question number and total question count.
- [x] Implement a dynamic progress percentage and progress bar.
- [x] Verify the interview generation workflow and frontend production build.
- [x] Implement the Interview Details modal.
- [x] Display interview questions, expected answer points, and previous attempts.
- [x] Display question-level completion and evaluation statuses.
- [x] Implement answer submission from the session details interface.
- [x] Implement retry evaluation from the session details interface.
- [x] Integrate session details retrieval with the frontend.
- [x] Automatically refresh dashboard data when the details modal closes.
- [x] Verify the frontend production build after session management changes.
- [ ] Build the document upload and listing interface.
- [ ] Integrate document-based question answering into the frontend.

### Backend Testing Status

- [x] Initial backend tests.
- [x] Authentication and interview module tests.
- [x] Document upload and validation tests.
- [x] Document listing and user isolation tests.
- [x] Vector retrieval and user isolation tests.
- [x] Document answer generation tests.
- [x] Document question-answering API tests.
- [x] Insights API tests.
- [x] Insights service tests.
- [x] Logout and refresh token tests.

**Latest previously recorded complete backend test result: 100 passed.**

The frontend production build also succeeded after the latest interview session management and dashboard refresh changes.

Note: The complete backend test suite should be run again after the latest changes to establish a new verified test result.

## Deployment and DevOps

- [x] Configure Git repository and GitHub remote.
- [ ] Configure Docker for backend and frontend.
- [ ] Create GitHub Actions workflow for backend CI.
- [ ] Create GitHub Actions workflow for frontend CI.
- [ ] Configure automated build and test validation.
- [ ] Configure continuous deployment.
- [ ] Perform end-to-end testing.
- [ ] Deploy the application.

## Project Status

The AI Interview Coach application has implemented its core interview preparation functionality, authentication, database integration, document-based RAG capabilities, performance insights, and personalized Career Profile management.

The Career Profile module allows users to maintain their professional summary, experience, technical skills, target roles, and preferred interview difficulty.

AI question generation integrates with the saved Career Profile. When generating questions, the application can automatically use the user's saved role, experience, technical skills, and preferred difficulty. Users can also override these defaults during interview setup.

The question-generation interface supports selecting 5, 10, 15, or 20 questions. Generated questions are displayed dynamically in the interview session, with a progress indicator showing the current question, total question count, and completion percentage.

The interview session management functionality supports retrieving session details, tracking question-level progress, storing multiple answer attempts, submitting answers, and retrying failed evaluations. Sessions are automatically marked as completed when all questions have successful evaluations.

The frontend includes an Interview Details modal that displays session questions, expected answer points, previous attempts, and evaluation statuses. Candidates can submit answers and retry failed evaluations directly from this interface.

The dashboard automatically refreshes its data when the Interview Details modal closes, allowing updated session completion status to appear without manually refreshing the browser.

The document Q&A module supports uploading PDF/DOCX files, extracting and embedding their content, retrieving relevant information using PostgreSQL pgvector, and generating context-based answers using Gemini.

The frontend currently includes authentication, dashboard, interview workflows, interview history, performance insights, Career Profile management, dynamic AI question generation, and resumable interview session functionality.

The current development focus is completing document management and document-based Q&A frontend integration, followed by Docker configuration, GitHub Actions CI/CD, end-to-end testing, and deployment.

This project is under active development, with a focus on clean architecture, testing, and practical AI engineering skills.

## Next Development Priorities

1. Commit and push the completed resumable interview session feature.
2. Complete document upload and listing UI.
3. Integrate document-based question answering into the frontend.
4. Run the complete backend test suite and frontend production build.
5. Configure Docker for the application.
6. Implement GitHub Actions CI workflows for backend and frontend.
7. Configure continuous deployment.
8. Perform end-to-end testing.
9. Deploy the application.

## V2 Roadmap

- [ ] Implement audio-based interviews with microphone recording.
- [ ] Integrate speech-to-text transcription.
- [ ] Evaluate answers generated from audio transcripts.
- [ ] Implement video-based interviews with camera and microphone recording.
- [ ] Integrate video upload and audio extraction.
- [ ] Explore optional speaking-performance analytics.
- [ ] Improve interview reporting and candidate feedback.

Audio and Video options are present in the interview setup UI, but recording, transcription, and processing functionality are planned for V2.
