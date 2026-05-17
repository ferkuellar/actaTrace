# ActaTrace Agent Instructions

## Project Role

ActaTrace is a professional web system for electoral document traceability, auditability, and public verification. Treat all work in this repository as production-oriented software for a real civic and institutional context.

Build with senior engineering judgment: secure, maintainable, modular, scalable, testable, documented, and easy for another developer to operate.

These instructions are the canonical development memory for this project. They take priority over `.agent.md` when there is a conflict. Keep `.agent.md` as a secondary draft unless the user explicitly asks to update or remove it.

## Current Project State

The repository currently contains prototype and planning artifacts, not a complete application scaffold:

- `actatrace-prototipo.jsx` — React prototype.
- `actatrace-arquitectura.html` — architecture presentation/document.
- `actatrace-pitch-slides.html` — pitch slides.
- `actatrace-pitch-doc.md` and `actatrace-pitch-script.md` — pitch material.
- `actatrace-normativo.md` — legal, ethical, privacy, and electoral framework.

Do not create a full `docs/`, `planning/`, `src/`, `tests/`, or Axon scaffold unless the user explicitly requests scaffolding.

## Operating Method: Architect / Builder

ActaTrace follows the Axon Architect / Builder methodology.

### Architect Responsibilities

The Architect defines:

- Problem, users, goals, and business context.
- Scope, non-goals, risks, assumptions, and open questions.
- Architecture, data model, permissions, validation rules, and acceptance criteria.
- Sprint or phase handoff documents before implementation.

The Architect must not silently invent business rules. Unknowns should be recorded as assumptions or questions.

### Builder Responsibilities

The Builder implements approved scope in the workspace:

- Read existing files before changing code.
- Preserve project conventions and existing artifacts.
- Keep changes focused and reviewable.
- Do not redefine scope, legal claims, electoral rules, roles, or security policy without explicit approval.
- Do not overwrite, delete, or reorganize project files unless the task requires it and the user approves.

The handoff between Architect and Builder must be files in the repository, not only conversation context.

## Axon Reference Materials

Use these local Axon materials as methodological references when planning or scaffolding ActaTrace work. Do not copy them wholesale into this repository unless the user asks for that.

- `D:\AxonArchitect\120x-Operators-Kit\Axon-AI-Desing-Patterns.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\Axon-AI-architect-builder-philosophy.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\Axon-AI-project-scaffold-instructions.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\Axon-AI-quickstart.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\README.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\prompts\01-architect-pack.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\prompts\02-architect-tighten.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\prompts\03-builder-scaffold.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\prompts\04-builder-populate.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\prompts\05-sprint-start.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\prompts\06-sprint-completion.md`
- `D:\AxonArchitect\120x-Operators-Kit\120x-Operators-Kit\prompts\07-architect-kickoff.md`

## Preferred Technical Stack

Prioritize these technologies unless the existing project or user request clearly indicates another stack:

- Frontend: React, Next.js, Vite, TypeScript, TailwindCSS, HTML5, CSS3, shadcn/ui when appropriate, Framer Motion only when useful.
- Backend: Node.js, Express, FastAPI, Flask, REST APIs, webhooks, background jobs when needed.
- Database: PostgreSQL, Supabase, MySQL, SQLite only for prototypes, Redis for caching or queues when useful.
- DevOps: Docker, Docker Compose, GitHub Actions, Vercel, Netlify, AWS, Azure, Nginx, environment variables, CI/CD pipelines.

Do not introduce unnecessary dependencies. Use the smallest robust architecture that can support the real product requirements.

## Engineering Standards

All code and documentation should be:

- Clean, readable, modular, and maintainable.
- Secure by default.
- Testable and documented where needed.
- Easy to deploy and operate.
- Compatible with future audits and handoffs.

Before implementation, reason through:

- What problem is being solved?
- What data models and API contracts are needed?
- What roles and permissions exist?
- What can fail, and how should the system respond?
- What privacy, security, and legal risks apply?
- How will the change be tested, deployed, and maintained?

## Frontend Standards

Frontend work must include:

- Responsive, mobile-first layout.
- Accessible markup and clear interaction states.
- Loading, empty, error, and success states where relevant.
- Clean component boundaries and reusable UI patterns.
- Practical form validation.
- SEO metadata when building public pages.

Avoid overdesigned UI, unclear component names, repeated code, random animations, and client-only authorization assumptions.

For ActaTrace specifically, public verification experiences should prioritize clarity, trust, auditability, and evidence visibility over marketing decoration.

## Backend and API Standards

Backend work must include:

- Clear route structure and consistent response formats.
- Input validation and safe error handling.
- Authentication and authorization checks where required.
- Proper HTTP status codes.
- Logging where useful.
- Environment variables for secrets and configuration.

Use this success response shape unless the project establishes a stronger convention:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed"
}
```

Use this error response shape:

```json
{
  "success": false,
  "error": "Clear error message"
}
```

Never expose stack traces, credentials, private infrastructure URLs, or sensitive election data in public responses.

## Database Standards

When designing or changing persistence:

- Use clear table names and normalized schemas unless denormalization is justified.
- Add `created_at` and `updated_at` timestamps.
- Use foreign keys where appropriate.
- Add indexes for common queries.
- Avoid storing sensitive personal data unless required.
- Use migrations when database changes are part of the implementation.
- Consider audit logs and reporting needs early.

For ActaTrace, distinguish carefully between public verification data, internal operational data, personal data, document metadata, hashes, chain-of-custody events, and immutable audit events.

## Authentication, Authorization, and Roles

When auth is required:

- Use secure password hashing or a trusted managed auth provider.
- Use JWT or session-based auth according to architecture.
- Protect private routes on the backend, not only in the frontend.
- Validate permissions server-side for every sensitive action.
- Never trust client-side state for authorization.

Common roles may include `ADMIN`, `MANAGER`, `USER`, `CLIENT`, `EDITOR`, `VIEWER`, and project-specific electoral roles such as observer or auditor if defined in approved planning documents.

## Security and Privacy Standards

Always consider:

- XSS, CSRF, SQL injection, and broken access control.
- Exposed secrets and unsafe environment handling.
- Insecure CORS and missing secure headers.
- File upload risks, especially for electoral documents.
- Rate limiting for sensitive endpoints.
- Dependency vulnerabilities.
- Privacy and personal-data minimization.
- Public transparency without exposing restricted personal or operational information.

Never hardcode credentials, tokens, API keys, passwords, private URLs, or secrets. If a secret is needed, request it from the user or document it in `.env.example` without real values.

## Testing and Validation

Add tests when practical, especially for:

- API validation.
- Authentication and authorization.
- Hashing, document integrity, and traceability logic.
- Form validation.
- Role-based access.
- Public verification flows.

At minimum, provide a manual test checklist for meaningful feature work. For bug fixes, explain the root cause, the smallest safe fix, and how to verify it.

## Documentation Standards

For meaningful work, document:

- What was built or changed.
- Files changed.
- How to run.
- Required environment variables.
- How to test.
- Known limitations.
- Recommended next improvements.

For larger phases, maintain Markdown documentation for architecture, data model, APIs, permissions, validation, operations, decisions, risks, questions, and sprint handoffs.

## Development Workflow

For complex tasks, organize work by phase:

```text
Phase:
Goal:
Files affected:
Implementation:
Validation:
Risks:
Next step:
```

Keep changes incremental. Avoid broad rewrites unless the user explicitly requests a refactor or the current architecture makes the task unsafe.

## Quality Audit Before Completion

Before finishing any task, verify:

- The implementation solves the actual request.
- File paths are clear.
- Dependencies and environment variables are documented.
- Security and privacy risks are addressed.
- The result is maintainable and testable.
- Deployment impact is considered when relevant.
- Unrelated files were not changed.

