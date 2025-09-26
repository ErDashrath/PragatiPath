# Overview

PragatiPath is an AI-powered adaptive learning platform built for educational assessment and progress tracking. The application uses a full-stack TypeScript architecture with a React frontend and Express.js backend, designed to provide personalized learning experiences through intelligent assessment and progress monitoring. The system supports both student and administrator user types, with comprehensive tracking of learning fundamentals (listening, grasping, retention, application) across multiple educational modules (quantitative, logical, verbal reasoning).

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: React 18 with TypeScript using Vite for development and build tooling
- **UI Library**: Radix UI components with shadcn/ui design system for consistent, accessible interface components
- **Styling**: Tailwind CSS with custom CSS variables for theming and responsive design
- **State Management**: TanStack Query (React Query) for server state management and caching
- **Routing**: Wouter for client-side routing with protected route implementation
- **Forms**: React Hook Form with Zod validation for type-safe form handling

## Backend Architecture
- **Framework**: Express.js with TypeScript for RESTful API services
- **Authentication**: Passport.js with local strategy, session-based authentication using express-session
- **Password Security**: Node.js crypto module with scrypt for secure password hashing and comparison
- **Data Validation**: Zod schemas for runtime type checking and API request validation
- **Storage Interface**: Abstracted storage layer with in-memory implementation (IStorage interface allows for easy database integration)

## Data Storage Design
- **ORM**: Drizzle ORM configured for PostgreSQL with type-safe database operations
- **Schema Design**: Comprehensive schema including users, student profiles, modules, assessment questions, and assessment sessions
- **Database**: PostgreSQL configured via Neon Database serverless connection
- **Session Storage**: Configurable session store (currently in-memory, ready for PostgreSQL integration)

## Authentication & Authorization
- **Session Management**: Express-session with configurable store backend
- **User Types**: Role-based access control supporting 'student' and 'admin' user types
- **Password Security**: Industry-standard scrypt hashing with salt for password storage
- **Route Protection**: Client-side route guards with server-side session validation

## Assessment System Architecture
- **Adaptive Learning**: Four fundamental learning dimensions (listening, grasping, retention, application) with scoring
- **Module Structure**: Hierarchical content organization with modules containing chapters and assessment questions
- **Session Tracking**: Comprehensive assessment session management with progress persistence
- **Difficulty Adaptation**: Dynamic difficulty adjustment based on performance metrics

# External Dependencies

## Database Services
- **Neon Database**: Serverless PostgreSQL hosting for production data storage
- **Drizzle Kit**: Database migration and schema management tooling

## UI and Design
- **Radix UI**: Unstyled, accessible UI component primitives
- **Tailwind CSS**: Utility-first CSS framework for responsive design
- **Lucide React**: Icon library for consistent iconography
- **Google Fonts**: Web font loading for typography (Inter, Architects Daughter, DM Sans, Fira Code, Geist Mono)

## Development Tools
- **Vite**: Fast development server and build tool with React plugin
- **TypeScript**: Static type checking across frontend and backend
- **ESBuild**: Fast JavaScript bundler for production builds
- **Replit Integration**: Development environment plugins for cartographer and dev banner

## Authentication Libraries
- **Passport.js**: Authentication middleware with local strategy support
- **connect-pg-simple**: PostgreSQL session store adapter for production sessions

## Utility Libraries
- **date-fns**: Date manipulation and formatting utilities
- **nanoid**: URL-safe unique ID generation for session and entity identifiers
- **class-variance-authority**: Type-safe CSS class variant management
- **clsx/tailwind-merge**: Conditional CSS class composition utilities