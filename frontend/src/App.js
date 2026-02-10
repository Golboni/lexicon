import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { Book, Brain, Trophy, Archive, Sun, Moon, Flame, Check, X, ChevronRight, RotateCcw, Volume2, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Theme toggle hook
const useTheme = () => {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark' || 
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
    return false;
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  return [isDark, setIsDark];
};

// Text-to-Speech hook
const useSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);

  const speak = (text) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8; // Slower for clarity
      utterance.pitch = 1;
      utterance.volume = 1;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      window.speechSynthesis.speak(utterance);
    } else {
      toast.error("Speech synthesis not supported in this browser");
    }
  };

  return { speak, isSpeaking };
};

// Word of the Day Component
const WordOfTheDay = ({ word, onMarkLearned, loading }) => {
  const { speak, isSpeaking } = useSpeech();
  if (loading) {
    return (
      <Card className="card-hover animate-fade-in-up">
        <CardContent className="p-8 md:p-12">
          <div className="animate-pulse space-y-6">
            <div className="h-12 bg-muted rounded w-48"></div>
            <div className="h-6 bg-muted rounded w-32"></div>
            <div className="h-20 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!word) {
    return (
      <Card className="card-hover">
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">No word available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="card-hover animate-fade-in-up overflow-hidden" data-testid="word-of-day-card">
      <div className="absolute top-0 left-0 w-full h-1 bg-accent"></div>
      <CardContent className="p-8 md:p-12 space-y-8">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
              Word of the Day
            </p>
            <div className="flex items-center gap-3">
              <h1 className="text-4xl md:text-6xl font-serif font-bold tracking-tight" data-testid="word-title">
                {word.word}
              </h1>
              <button
                onClick={() => speak(word.word)}
                className={`p-2 rounded-sm border border-border hover:bg-secondary hover:border-accent transition-all ${isSpeaking ? 'bg-accent/10 border-accent' : ''}`}
                title="Hear pronunciation"
                data-testid="speak-word-btn"
              >
                <Volume2 className={`w-6 h-6 ${isSpeaking ? 'text-accent animate-pulse-soft' : 'text-muted-foreground'}`} />
              </button>
            </div>
          </div>
          {word.is_learned && (
            <Badge variant="outline" className="learned-badge" data-testid="learned-badge">
              <Check className="w-3 h-3" /> Learned
            </Badge>
          )}
        </div>

        {/* Pronunciation & Part of Speech */}
        <div className="flex flex-wrap items-center gap-4">
          <span className="font-mono text-sm text-muted-foreground" data-testid="pronunciation">
            [{word.pronunciation}]
          </span>
          <Badge variant="secondary" className="rounded-sm text-xs uppercase tracking-wider">
            {word.part_of_speech}
          </Badge>
        </div>

        {/* Definition */}
        <div className="space-y-2">
          <h3 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
            Definition
          </h3>
          <p className="text-lg md:text-xl leading-relaxed" data-testid="definition">
            {word.definition}
          </p>
        </div>

        {/* Example */}
        <div className="space-y-2">
          <h3 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
            Example
          </h3>
          <blockquote className="border-l-2 border-accent pl-4 italic text-muted-foreground" data-testid="example">
            "{word.example}"
          </blockquote>
        </div>

        {/* Synonyms */}
        {word.synonyms && word.synonyms.length > 0 && (
          <div className="space-y-2" data-testid="synonyms-section">
            <h3 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
              Similar Words <span className="normal-case">(Synonyms)</span>
            </h3>
            <div className="flex flex-wrap gap-2">
              {word.synonyms.map((synonym, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="rounded-sm text-sm font-normal px-3 py-1 border-border hover:bg-secondary transition-colors"
                  data-testid={`synonym-${index}`}
                >
                  {synonym}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Origin Popup Link */}
        {word.origin && (
          <Dialog>
            <DialogTrigger asChild>
              <button 
                className="inline-flex items-center gap-2 text-accent hover:text-accent/80 transition-colors text-sm font-medium underline underline-offset-4"
                data-testid="origin-link"
              >
                <History className="w-4 h-4" />
                Origin
              </button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg" data-testid="origin-dialog">
              <DialogHeader>
                <DialogTitle className="font-serif text-2xl flex items-center gap-2">
                  <History className="w-5 h-5 text-accent" />
                  Origin of "{word.word}"
                </DialogTitle>
              </DialogHeader>
              <div className="mt-4">
                <p className="text-muted-foreground leading-relaxed" data-testid="origin-text">
                  {word.origin}
                </p>
              </div>
            </DialogContent>
          </Dialog>
        )}

        {/* Action */}
        {!word.is_learned && (
          <Button 
            onClick={() => onMarkLearned(word.id)}
            className="btn-brutalist rounded-none uppercase tracking-wider"
            data-testid="mark-learned-btn"
          >
            <Check className="w-4 h-4 mr-2" />
            Mark as Learned
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

// Quiz Component
const QuizMode = ({ onComplete }) => {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [quizComplete, setQuizComplete] = useState(false);

  useEffect(() => {
    fetchQuiz();
  }, []);

  const fetchQuiz = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/quiz?count=5`);
      setQuestions(response.data);
      setCurrentIndex(0);
      setScore(0);
      setQuizComplete(false);
    } catch (error) {
      toast.error("Failed to load quiz");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer) => {
    if (showResult) return;
    
    setSelectedAnswer(answer);
    setShowResult(true);
    
    const currentQuestion = questions[currentIndex];
    const correct = answer === currentQuestion.correct_definition;
    setIsCorrect(correct);
    
    if (correct) {
      setScore(s => s + 1);
    }

    try {
      await axios.post(`${API}/quiz/submit`, {
        word_id: currentQuestion.word_id,
        selected_answer: answer,
        correct_answer: currentQuestion.correct_definition
      });
    } catch (error) {
      console.error("Failed to submit answer");
    }
  };

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(i => i + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      setQuizComplete(true);
      onComplete && onComplete(score, questions.length);
    }
  };

  if (loading) {
    return (
      <Card className="card-hover">
        <CardContent className="p-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-48"></div>
            <div className="h-32 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (quizComplete) {
    const percentage = Math.round((score / questions.length) * 100);
    return (
      <Card className="card-hover animate-fade-in-up" data-testid="quiz-complete-card">
        <CardContent className="p-8 md:p-12 text-center space-y-8">
          <div className="space-y-4">
            <Trophy className="w-16 h-16 mx-auto text-accent" />
            <h2 className="text-3xl md:text-4xl font-serif font-bold">Quiz Complete!</h2>
          </div>
          
          <div className="space-y-2">
            <p className="text-6xl font-bold text-accent" data-testid="final-score">{score}/{questions.length}</p>
            <p className="text-muted-foreground">Correct Answers</p>
            <Progress value={percentage} className="h-2 mt-4" />
          </div>

          <p className="text-lg text-muted-foreground">
            {percentage >= 80 ? "Excellent! You're mastering these words!" :
             percentage >= 60 ? "Good job! Keep practicing!" :
             "Keep learning! You'll get better!"}
          </p>

          <Button 
            onClick={fetchQuiz}
            className="btn-brutalist rounded-none uppercase tracking-wider"
            data-testid="try-again-btn"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;

  return (
    <div className="space-y-6 animate-fade-in-up" data-testid="quiz-container">
      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Question {currentIndex + 1} of {questions.length}</span>
          <span data-testid="current-score">Score: {score}</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Question Card */}
      <Card className="card-hover">
        <CardContent className="p-8 space-y-8">
          <div className="text-center space-y-4">
            <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
              What does this word mean?
            </p>
            <h2 className="text-4xl md:text-5xl font-serif font-bold" data-testid="quiz-word">
              {currentQuestion.word}
            </h2>
          </div>

          {/* Options */}
          <div className="grid gap-4" data-testid="quiz-options">
            {currentQuestion.options.map((option, index) => {
              let optionClass = "quiz-option";
              if (showResult) {
                if (option === currentQuestion.correct_definition) {
                  optionClass += " correct";
                } else if (option === selectedAnswer && !isCorrect) {
                  optionClass += " incorrect";
                }
              } else if (option === selectedAnswer) {
                optionClass += " selected";
              }

              return (
                <button
                  key={index}
                  onClick={() => handleAnswer(option)}
                  disabled={showResult}
                  className={optionClass}
                  data-testid={`quiz-option-${index}`}
                >
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full border border-current flex items-center justify-center text-sm font-medium">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span className="text-left">{option}</span>
                  </div>
                  {showResult && option === currentQuestion.correct_definition && (
                    <Check className="w-5 h-5 text-green-500 ml-auto flex-shrink-0" />
                  )}
                  {showResult && option === selectedAnswer && !isCorrect && option !== currentQuestion.correct_definition && (
                    <X className="w-5 h-5 text-destructive ml-auto flex-shrink-0" />
                  )}
                </button>
              );
            })}
          </div>

          {/* Result & Next */}
          {showResult && (
            <div className="flex items-center justify-between pt-4 border-t border-border">
              <p className={`font-medium ${isCorrect ? 'text-green-500' : 'text-destructive'}`}>
                {isCorrect ? "Correct!" : "Incorrect"}
              </p>
              <Button 
                onClick={nextQuestion}
                className="btn-brutalist rounded-none uppercase tracking-wider"
                data-testid="next-question-btn"
              >
                {currentIndex < questions.length - 1 ? 'Next' : 'See Results'}
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Progress Component
const ProgressView = () => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`${API}/progress`);
      setProgress(response.data);
    } catch (error) {
      toast.error("Failed to load progress");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2">
        {[1,2,3,4].map(i => (
          <Card key={i} className="card-hover">
            <CardContent className="p-6">
              <div className="animate-pulse h-20 bg-muted rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in-up" data-testid="progress-container">
      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="card-hover" data-testid="stat-streak">
          <CardContent className="p-6 text-center space-y-2">
            <Flame className="w-8 h-8 mx-auto text-accent" />
            <p className="text-3xl font-bold">{progress?.current_streak || 0}</p>
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Day Streak</p>
          </CardContent>
        </Card>

        <Card className="card-hover" data-testid="stat-words">
          <CardContent className="p-6 text-center space-y-2">
            <Book className="w-8 h-8 mx-auto text-accent" />
            <p className="text-3xl font-bold">{progress?.total_words_learned || 0}</p>
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Words Learned</p>
          </CardContent>
        </Card>

        <Card className="card-hover" data-testid="stat-quizzes">
          <CardContent className="p-6 text-center space-y-2">
            <Brain className="w-8 h-8 mx-auto text-accent" />
            <p className="text-3xl font-bold">{progress?.total_quizzes_taken || 0}</p>
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Quizzes Taken</p>
          </CardContent>
        </Card>

        <Card className="card-hover" data-testid="stat-correct">
          <CardContent className="p-6 text-center space-y-2">
            <Trophy className="w-8 h-8 mx-auto text-accent" />
            <p className="text-3xl font-bold">{progress?.total_correct_answers || 0}</p>
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Correct Answers</p>
          </CardContent>
        </Card>
      </div>

      {/* Learned Words */}
      <Card className="card-hover">
        <CardHeader>
          <CardTitle className="font-serif text-2xl">Learned Words</CardTitle>
        </CardHeader>
        <CardContent>
          {progress?.learned_words?.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2" data-testid="learned-words-list">
              {progress.learned_words.map((word, index) => (
                <div 
                  key={word.id} 
                  className="p-4 border border-border rounded-sm hover:bg-secondary transition-colors"
                  data-testid={`learned-word-${index}`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-serif font-semibold text-lg">{word.word}</h4>
                      <p className="text-sm text-muted-foreground">{word.part_of_speech}</p>
                    </div>
                    <Check className="w-4 h-4 text-green-500" />
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground line-clamp-2">{word.definition}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" data-testid="no-learned-words">
              <Book className="w-12 h-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No words learned yet</p>
              <p className="text-sm text-muted-foreground">Start by learning today's word!</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Archive Component
const WordArchive = () => {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchWords();
  }, []);

  const fetchWords = async () => {
    try {
      const response = await axios.get(`${API}/words`);
      setWords(response.data);
    } catch (error) {
      toast.error("Failed to load words");
    } finally {
      setLoading(false);
    }
  };

  const filteredWords = filter === 'all' ? words : 
    filter === 'learned' ? words.filter(w => w.is_learned) :
    words.filter(w => !w.is_learned);

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1,2,3,4,5,6].map(i => (
          <Card key={i} className="card-hover">
            <CardContent className="p-6">
              <div className="animate-pulse space-y-3">
                <div className="h-6 bg-muted rounded w-24"></div>
                <div className="h-16 bg-muted rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in-up" data-testid="archive-container">
      {/* Filter */}
      <div className="flex gap-2">
        {['all', 'learned', 'unlearned'].map((f) => (
          <Button
            key={f}
            variant={filter === f ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter(f)}
            className={`rounded-none uppercase tracking-wider text-xs ${filter === f ? 'btn-brutalist' : ''}`}
            data-testid={`filter-${f}`}
          >
            {f}
          </Button>
        ))}
      </div>

      {/* Word Count */}
      <p className="text-sm text-muted-foreground">
        Showing {filteredWords.length} words
      </p>

      {/* Words Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3" data-testid="words-grid">
        {filteredWords.map((word, index) => (
          <Card 
            key={word.id} 
            className={`card-hover transition-all ${word.is_learned ? 'border-green-500/30' : ''}`}
            data-testid={`archive-word-${index}`}
          >
            <CardContent className="p-6 space-y-3">
              <div className="flex items-start justify-between">
                <h3 className="font-serif font-semibold text-xl">{word.word}</h3>
                {word.is_learned && (
                  <Badge variant="outline" className="learned-badge text-xs">
                    <Check className="w-3 h-3" />
                  </Badge>
                )}
              </div>
              <p className="font-mono text-xs text-muted-foreground">[{word.pronunciation}]</p>
              <Badge variant="secondary" className="rounded-sm text-xs">
                {word.part_of_speech}
              </Badge>
              <p className="text-sm text-muted-foreground line-clamp-3">{word.definition}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Main App
function App() {
  const [isDark, setIsDark] = useTheme();
  const [activeTab, setActiveTab] = useState('today');
  const [todayWord, setTodayWord] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTodayWord();
  }, []);

  const fetchTodayWord = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/word/today`);
      setTodayWord(response.data);
    } catch (error) {
      toast.error("Failed to load today's word");
    } finally {
      setLoading(false);
    }
  };

  const handleMarkLearned = async (wordId) => {
    try {
      await axios.post(`${API}/progress/mark-learned`, { word_id: wordId });
      setTodayWord(prev => ({ ...prev, is_learned: true }));
      toast.success("Word marked as learned!");
    } catch (error) {
      toast.error("Failed to mark word as learned");
    }
  };

  return (
    <div className="min-h-screen bg-background grain-overlay" data-testid="app-container">
      <Toaster position="top-center" />
      
      {/* Header */}
      <header className="border-b border-border sticky top-0 bg-background/95 backdrop-blur-sm z-40">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Book className="w-6 h-6 text-accent" />
            <h1 className="text-xl font-serif font-bold tracking-tight" data-testid="app-title">Lexicon</h1>
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsDark(!isDark)}
            className="rounded-none"
            data-testid="theme-toggle"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-8 md:py-12">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid grid-cols-4 w-full max-w-md mx-auto bg-muted rounded-none" data-testid="main-tabs">
            <TabsTrigger 
              value="today" 
              className="rounded-none data-[state=active]:bg-background data-[state=active]:shadow-sm uppercase text-xs tracking-wider"
              data-testid="tab-today"
            >
              <Book className="w-4 h-4 mr-2 hidden sm:block" />
              Today
            </TabsTrigger>
            <TabsTrigger 
              value="quiz"
              className="rounded-none data-[state=active]:bg-background data-[state=active]:shadow-sm uppercase text-xs tracking-wider"
              data-testid="tab-quiz"
            >
              <Brain className="w-4 h-4 mr-2 hidden sm:block" />
              Quiz
            </TabsTrigger>
            <TabsTrigger 
              value="progress"
              className="rounded-none data-[state=active]:bg-background data-[state=active]:shadow-sm uppercase text-xs tracking-wider"
              data-testid="tab-progress"
            >
              <Trophy className="w-4 h-4 mr-2 hidden sm:block" />
              Stats
            </TabsTrigger>
            <TabsTrigger 
              value="archive"
              className="rounded-none data-[state=active]:bg-background data-[state=active]:shadow-sm uppercase text-xs tracking-wider"
              data-testid="tab-archive"
            >
              <Archive className="w-4 h-4 mr-2 hidden sm:block" />
              Archive
            </TabsTrigger>
          </TabsList>

          <TabsContent value="today" className="mt-8">
            <WordOfTheDay 
              word={todayWord} 
              onMarkLearned={handleMarkLearned}
              loading={loading}
            />
          </TabsContent>

          <TabsContent value="quiz" className="mt-8">
            <QuizMode onComplete={() => {}} />
          </TabsContent>

          <TabsContent value="progress" className="mt-8">
            <ProgressView />
          </TabsContent>

          <TabsContent value="archive" className="mt-8">
            <WordArchive />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 mt-auto">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <p className="text-xs text-muted-foreground uppercase tracking-widest">
            Build your vocabulary, one word at a time
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
