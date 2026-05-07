# Lexicon - Word of the Day Vocabulary Builder

<div align="center">

![Lexicon](https://img.shields.io/badge/Lexicon-Vocabulary%20Builder-F97316?style=for-the-badge)
![React](https://img.shields.io/badge/React-19.0-61DAFB?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-4.5-47A248?style=flat-square&logo=mongodb)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Build your vocabulary, one word at a time.**

[Live Demo](https://daily-vocab-27.emergent.host) • [Report Bug](https://github.com/Golboni/lexicon/issues) • [Request Feature](https://github.com/Golboni/lexicon/issues)

</div>

---

## ✨ Features

### 📖 Word of the Day
- Daily rotating vocabulary words with pronunciation
- **Audio pronunciation** - Click to hear the word spoken
- Clear definitions with example sentences
- **Synonyms** - Similar words to expand your vocabulary
- **Antonyms** - Opposite words for deeper understanding
- **Etymology popup** - Learn the origin and history of each word

### 🧠 Quiz Mode
- Multiple choice quizzes to test your knowledge
- Instant feedback on answers
- Track your score and progress
- Randomized questions from 30+ vocabulary words

### 📊 Progress Tracking
- Daily learning streaks
- Words learned counter
- Quiz statistics (total taken, correct answers)
- View all your learned words

### 📚 Word Archive
- Browse all 30 vocabulary words
- Filter by: All / Learned / Unlearned
- Quick access to definitions and details

### 🎨 Beautiful Design
- Swiss Editorial aesthetic with Playfair Display typography
- Light and dark mode support
- Responsive design for all devices
- Smooth animations and transitions

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19, Tailwind CSS, Shadcn/UI |
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB |
| **Styling** | Tailwind CSS with custom design system |
| **Icons** | Lucide React |
| **Deployment** | Emergent |

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- MongoDB

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Golboni/lexicon.git
   cd lexicon
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create `/backend/.env`:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=lexicon_db
   CORS_ORIGINS=*
   ```

   Create `/frontend/.env`:
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

4. **Set up the frontend**
   ```bash
   cd frontend
   yarn install
   ```

5. **Start the services**
   
   Backend:
   ```bash
   cd backend
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```
   
   Frontend:
   ```bash
   cd frontend
   yarn start
   ```

6. **Open your browser**
   
   Navigate to `http://localhost:3000`

---

## 📁 Project Structure

```
lexicon/
├── backend/
│   ├── server.py          # FastAPI application & API routes
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React application
│   │   ├── App.css       # Component styles
│   │   ├── index.css     # Global styles & Tailwind config
│   │   └── components/
│   │       └── ui/       # Shadcn/UI components
│   ├── package.json      # Node dependencies
│   └── .env             # Frontend environment variables
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/word/today` | Get today's word of the day |
| `GET` | `/api/words` | Get all vocabulary words |
| `GET` | `/api/progress` | Get user progress & statistics |
| `POST` | `/api/progress/mark-learned` | Mark a word as learned |
| `GET` | `/api/quiz?count=5` | Generate quiz questions |
| `POST` | `/api/quiz/submit` | Submit a quiz answer |
| `POST` | `/api/progress/reset` | Reset all progress |
| `POST` | `/api/admin/reseed-words` | Reseed vocabulary database |

---

## 📝 Vocabulary Words

Lexicon includes 30 carefully curated vocabulary words, each with:
- Pronunciation guide
- Part of speech
- Definition
- Example sentence
- 2 synonyms
- 2 antonyms
- Etymology/origin

**Sample words:** eudemonic, perspicacious, ephemeral, mellifluous, serendipity, quintessential, and more!

---

## 🎯 Roadmap

- [ ] Audio pronunciation using Text-to-Speech API
- [ ] Spaced repetition algorithm for smarter quizzes
- [ ] User accounts for cross-device sync
- [ ] Daily notifications/reminders
- [ ] Word categories (SAT, GRE, etc.)
- [ ] Social sharing for streaks
- [ ] Leaderboard system

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Word definitions inspired by [Dictionary.com](https://www.dictionary.com)
- UI components from [Shadcn/UI](https://ui.shadcn.com)
- Icons from [Lucide](https://lucide.dev)
- Built with [Emergent](https://emergent.sh)

---

<div align="center">

**[⬆ Back to Top](#lexicon---word-of-the-day-vocabulary-builder)**

Made with ❤️ by [Golboni](https://github.com/Golboni)

</div>

