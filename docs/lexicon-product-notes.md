# Lexicon Product Notes

These notes were preserved during the June 2026 Phase 1 hosting migration before removing the Emergent `memory/` folder from the repository.

---

# Lexicon - Word of the Day Vocabulary Builder

## Original Problem Statement
Build a Word of the Day Vocabulary Builder app with:
- Frontend: Daily new word with definition, quiz mode, track learned words
- Backend: Scheduled word rotation, quiz generation, progress tracking

## User Choices
- Word source: Dictionary.com style (pre-populated database)
- Quiz mode: Multiple choice
- Authentication: None needed
- Design: Swiss Editorial aesthetic with warm color scheme

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Database Collections**: words, progress

## User Personas
- Students preparing for SAT/GRE
- Professionals looking to expand vocabulary
- Language learners

## Core Requirements
- [x] Daily word rotation based on date
- [x] Word display with pronunciation, definition, example
- [x] Mark word as learned functionality
- [x] Multiple choice quiz with 5 questions
- [x] Progress tracking (streak, words learned, quiz scores)
- [x] Word archive with filters

## What's Been Implemented (Feb 10, 2026)
- Full backend API with 30 pre-seeded vocabulary words
- Word of the Day with date-based rotation
- Quiz generation with random questions and 4 options
- Progress tracking with streak system
- Beautiful "Lexicon" branded UI with dark/light mode
- Tab-based navigation (Today, Quiz, Stats, Archive)

## API Endpoints
- GET /api/word/today - Today's word
- GET /api/words - All words archive
- POST /api/progress/mark-learned - Mark word as learned
- GET /api/progress - Get user stats
- GET /api/quiz - Generate quiz questions
- POST /api/quiz/submit - Submit quiz answer

## Prioritized Backlog
### P0 (Critical)
- All complete

### P1 (High Priority)
- Audio pronunciation (Text-to-Speech)
- Spaced repetition algorithm for quiz
- Daily notification/reminder

### P2 (Nice to Have)
- User accounts for cross-device sync
- Word categories (SAT, GRE, etc.)
- Leaderboard system
- Export progress report
