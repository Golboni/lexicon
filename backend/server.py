from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============ MODELS ============

class Word(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    word: str
    pronunciation: str
    part_of_speech: str
    definition: str
    example: str
    synonyms: List[str] = []
    origin: str = ""
    date_added: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WordResponse(BaseModel):
    id: str
    word: str
    pronunciation: str
    part_of_speech: str
    definition: str
    example: str
    synonyms: List[str] = []
    origin: str = ""
    date_added: str
    is_learned: bool = False


class Progress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    learned_words: List[str] = []  # List of word IDs
    quiz_scores: List[dict] = []  # [{date, score, total}]
    current_streak: int = 0
    last_active_date: str = ""
    total_words_learned: int = 0
    total_quizzes_taken: int = 0
    total_correct_answers: int = 0


class MarkLearnedRequest(BaseModel):
    word_id: str


class QuizQuestion(BaseModel):
    word_id: str
    word: str
    correct_definition: str
    options: List[str]


class QuizSubmitRequest(BaseModel):
    word_id: str
    selected_answer: str
    correct_answer: str


class QuizSubmitResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    streak: int


# ============ SEED DATA ============

VOCABULARY_WORDS = [
    {
        "word": "eudemonic",
        "pronunciation": "yoo-di-MON-ik",
        "part_of_speech": "adjective",
        "definition": "pertaining or conducive to happiness and well-being",
        "example": "The artist was guided by eudemonic ideals, believing that creative fulfillment mattered more than wealth.",
        "synonyms": ["blissful", "felicitous"],
        "origin": "From Greek 'eudaimonia' meaning 'happiness' or 'welfare', derived from 'eu' (good) + 'daimon' (spirit). In ancient Greek philosophy, particularly Aristotle's ethics, eudaimonia represented the highest human good."
    },
    {
        "word": "vilipend",
        "pronunciation": "VIL-uh-pend",
        "part_of_speech": "verb",
        "definition": "to regard or treat as of little value or account",
        "example": "Don't vilipend your colleague's innovative idea just because you prefer traditional methods.",
        "synonyms": ["disparage", "belittle"],
        "origin": "From Latin 'vilipendere', combining 'vilis' (cheap, worthless) + 'pendere' (to weigh, consider). First appeared in English in the 15th century, originally used in formal or literary contexts."
    },
    {
        "word": "equanimous",
        "pronunciation": "ih-KWAN-uh-muhs",
        "part_of_speech": "adjective",
        "definition": "having or showing mental and emotional composure",
        "example": "The equanimous leader calmly addressed the crisis, never losing her composure.",
        "synonyms": ["composed", "serene"],
        "origin": "From Latin 'aequanimitas', from 'aequus' (equal) + 'animus' (mind, spirit). The concept was highly valued in Stoic philosophy as a key virtue for maintaining inner peace."
    },
    {
        "word": "xylography",
        "pronunciation": "zahy-LOG-ruh-fee",
        "part_of_speech": "noun",
        "definition": "the art of engraving on wood",
        "example": "The artist displayed his skill in xylography by creating detailed prints from carved wood.",
        "synonyms": ["woodcutting", "wood engraving"],
        "origin": "From Greek 'xylon' (wood) + 'graphein' (to write). The art form originated in China around the 7th century and spread to Europe in the 14th century for printing images and text."
    },
    {
        "word": "perspicacious",
        "pronunciation": "pur-spi-KAY-shuhs",
        "part_of_speech": "adjective",
        "definition": "having a ready insight into and understanding of things; shrewd",
        "example": "Her perspicacious analysis of the market trends saved the company millions.",
        "synonyms": ["astute", "discerning"],
        "origin": "From Latin 'perspicax' (sharp-sighted), from 'perspicere' (to look through), combining 'per' (through) + 'specere' (to look). Entered English in the early 17th century."
    },
    {
        "word": "ephemeral",
        "pronunciation": "ih-FEM-er-uhl",
        "part_of_speech": "adjective",
        "definition": "lasting for a very short time",
        "example": "The ephemeral beauty of cherry blossoms reminds us to appreciate fleeting moments.",
        "synonyms": ["fleeting", "transient"],
        "origin": "From Greek 'ephemeros' meaning 'lasting only a day', from 'epi' (on) + 'hemera' (day). Originally used in biology to describe organisms with very short lifespans, like mayflies."
    },
    {
        "word": "obfuscate",
        "pronunciation": "OB-fuh-skayt",
        "part_of_speech": "verb",
        "definition": "to render obscure, unclear, or unintelligible",
        "example": "Politicians often obfuscate their true intentions with complex language.",
        "synonyms": ["obscure", "confuse"],
        "origin": "From Latin 'obfuscare', from 'ob' (over) + 'fuscare' (to darken), derived from 'fuscus' (dark). First recorded in English in the 16th century."
    },
    {
        "word": "sanguine",
        "pronunciation": "SANG-gwin",
        "part_of_speech": "adjective",
        "definition": "optimistic or positive, especially in a difficult situation",
        "example": "Despite the setbacks, she remained sanguine about the project's success.",
        "synonyms": ["optimistic", "hopeful"],
        "origin": "From Latin 'sanguineus' (of blood), from 'sanguis' (blood). In medieval medicine, a 'sanguine' temperament was associated with an excess of blood, believed to make one cheerful and confident."
    },
    {
        "word": "laconic",
        "pronunciation": "luh-KON-ik",
        "part_of_speech": "adjective",
        "definition": "using very few words; terse",
        "example": "His laconic response of 'no' ended the lengthy debate.",
        "synonyms": ["terse", "succinct"],
        "origin": "From Greek 'Lakonikos' meaning 'from Laconia' (the region of Sparta). Spartans were famous for their brief, pithy speech. When Philip II threatened 'If I invade, I will destroy you,' Sparta replied simply: 'If.'"
    },
    {
        "word": "ubiquitous",
        "pronunciation": "yoo-BIK-wi-tuhs",
        "part_of_speech": "adjective",
        "definition": "present, appearing, or found everywhere",
        "example": "Smartphones have become ubiquitous in modern society.",
        "synonyms": ["omnipresent", "pervasive"],
        "origin": "From Latin 'ubique' meaning 'everywhere', from 'ubi' (where) + '-que' (and, also). First used in English in the early 19th century, originally in theological contexts about divine omnipresence."
    },
    {
        "word": "ineffable",
        "pronunciation": "in-EF-uh-buhl",
        "part_of_speech": "adjective",
        "definition": "too great or extreme to be expressed or described in words",
        "example": "The view from the mountaintop filled her with ineffable joy.",
        "synonyms": ["indescribable", "unspeakable"],
        "origin": "From Latin 'ineffabilis', from 'in-' (not) + 'effabilis' (utterable), from 'effari' (to speak out). Originally used in religious contexts to describe the unutterable name of God."
    },
    {
        "word": "pernicious",
        "pronunciation": "per-NISH-uhs",
        "part_of_speech": "adjective",
        "definition": "having a harmful effect, especially in a gradual or subtle way",
        "example": "The pernicious influence of misinformation undermines public trust.",
        "synonyms": ["harmful", "detrimental"],
        "origin": "From Latin 'perniciosus' (destructive), from 'pernicies' (ruin, death), combining 'per-' (thoroughly) + 'nex' (death, slaughter). Entered English in the early 16th century."
    },
    {
        "word": "mellifluous",
        "pronunciation": "muh-LIF-loo-uhs",
        "part_of_speech": "adjective",
        "definition": "sweet or musical; pleasant to hear",
        "example": "The singer's mellifluous voice captivated the entire audience.",
        "synonyms": ["melodious", "dulcet"],
        "origin": "From Latin 'mellifluus', from 'mel' (honey) + 'fluere' (to flow). Literally means 'flowing with honey.' Used since the 15th century to describe sweet-sounding speech or music."
    },
    {
        "word": "serendipity",
        "pronunciation": "ser-uhn-DIP-i-tee",
        "part_of_speech": "noun",
        "definition": "the occurrence of events by chance in a happy way",
        "example": "Finding that rare book at the garage sale was pure serendipity.",
        "synonyms": ["fortune", "happenstance"],
        "origin": "Coined by Horace Walpole in 1754, based on the Persian fairy tale 'The Three Princes of Serendip' (ancient name for Sri Lanka), whose heroes made discoveries by accident and sagacity."
    },
    {
        "word": "quintessential",
        "pronunciation": "kwin-tuh-SEN-shuhl",
        "part_of_speech": "adjective",
        "definition": "representing the most perfect or typical example of something",
        "example": "The small café was the quintessential Parisian experience.",
        "synonyms": ["archetypal", "exemplary"],
        "origin": "From Medieval Latin 'quinta essentia' (fifth essence). Ancient philosophers believed there were four elements (earth, water, fire, air), and a fifth 'quintessence' was the pure essence of heavenly bodies."
    },
    {
        "word": "loquacious",
        "pronunciation": "loh-KWAY-shuhs",
        "part_of_speech": "adjective",
        "definition": "tending to talk a great deal; talkative",
        "example": "The loquacious host kept guests entertained with endless stories.",
        "synonyms": ["garrulous", "voluble"],
        "origin": "From Latin 'loquax' (talkative), from 'loqui' (to speak). Related to 'eloquent' and 'soliloquy.' First appeared in English in the mid-17th century."
    },
    {
        "word": "insouciant",
        "pronunciation": "in-SOO-see-uhnt",
        "part_of_speech": "adjective",
        "definition": "showing a casual lack of concern; indifferent",
        "example": "Her insouciant attitude toward the deadline worried her colleagues.",
        "synonyms": ["nonchalant", "carefree"],
        "origin": "From French 'insouciant', from 'in-' (not) + 'soucier' (to worry), ultimately from Latin 'sollicitare' (to disturb). Borrowed into English in the early 19th century."
    },
    {
        "word": "recalcitrant",
        "pronunciation": "ri-KAL-si-truhnt",
        "part_of_speech": "adjective",
        "definition": "having an obstinately uncooperative attitude",
        "example": "The recalcitrant employee refused to follow the new protocols.",
        "synonyms": ["defiant", "stubborn"],
        "origin": "From Latin 'recalcitrare' (to kick back), from 're-' (back) + 'calcitrare' (to kick), from 'calx' (heel). Originally described horses that kicked when being shod."
    },
    {
        "word": "munificent",
        "pronunciation": "myoo-NIF-uh-suhnt",
        "part_of_speech": "adjective",
        "definition": "larger or more generous than usual or necessary",
        "example": "The munificent donation transformed the struggling charity.",
        "synonyms": ["generous", "lavish"],
        "origin": "From Latin 'munificus' (bountiful), from 'munus' (gift, duty) + 'facere' (to make). Related to 'municipal' (originally meaning 'taking on duties'). Entered English in the 16th century."
    },
    {
        "word": "perfunctory",
        "pronunciation": "per-FUNGK-tuh-ree",
        "part_of_speech": "adjective",
        "definition": "carried out with minimum effort or reflection",
        "example": "His perfunctory apology failed to convince anyone of his sincerity.",
        "synonyms": ["cursory", "superficial"],
        "origin": "From Latin 'perfunctorius' (careless), from 'perfungi' (to get through with), combining 'per-' (through) + 'fungi' (to perform). Originally meant 'done merely to get rid of a duty.'"
    },
    {
        "word": "gregarious",
        "pronunciation": "gri-GAIR-ee-uhs",
        "part_of_speech": "adjective",
        "definition": "fond of company; sociable",
        "example": "The gregarious host made sure everyone at the party felt welcome.",
        "synonyms": ["sociable", "outgoing"],
        "origin": "From Latin 'gregarius' (belonging to a flock), from 'grex' (flock, herd). Originally used in biology to describe animals that live in groups. Extended to human sociability in the 17th century."
    },
    {
        "word": "soporific",
        "pronunciation": "sop-uh-RIF-ik",
        "part_of_speech": "adjective",
        "definition": "tending to induce drowsiness or sleep",
        "example": "The professor's soporific lecture had half the class nodding off.",
        "synonyms": ["sedative", "hypnotic"],
        "origin": "From Latin 'sopor' (deep sleep) + '-ficus' (making), from 'facere' (to make). Related to 'Morpheus,' the Greek god of dreams. First used in English in the 17th century."
    },
    {
        "word": "capricious",
        "pronunciation": "kuh-PRISH-uhs",
        "part_of_speech": "adjective",
        "definition": "given to sudden and unaccountable changes of mood or behavior",
        "example": "The capricious weather ruined our outdoor wedding plans.",
        "synonyms": ["fickle", "unpredictable"],
        "origin": "From Italian 'capriccio' (sudden shiver, whim), possibly from 'capo' (head) + 'riccio' (hedgehog), suggesting hair standing on end. Originally described a shuddering sensation."
    },
    {
        "word": "prodigious",
        "pronunciation": "pruh-DIJ-uhs",
        "part_of_speech": "adjective",
        "definition": "remarkably great in extent, size, or degree",
        "example": "The child prodigy showed prodigious talent in mathematics.",
        "synonyms": ["enormous", "extraordinary"],
        "origin": "From Latin 'prodigiosus' (marvelous, unnatural), from 'prodigium' (omen, portent). Originally meant 'ominous' or 'portentous,' but shifted to mean 'amazing' by the 16th century."
    },
    {
        "word": "sagacious",
        "pronunciation": "suh-GAY-shuhs",
        "part_of_speech": "adjective",
        "definition": "having or showing keen mental discernment and good judgment",
        "example": "The sagacious investor predicted the market crash months in advance.",
        "synonyms": ["wise", "shrewd"],
        "origin": "From Latin 'sagax' (of quick perception), from 'sagire' (to perceive keenly). Originally used to describe hunting dogs with a keen sense of smell, then extended to human wisdom."
    },
    {
        "word": "ebullient",
        "pronunciation": "ih-BULL-yuhnt",
        "part_of_speech": "adjective",
        "definition": "cheerful and full of energy",
        "example": "Her ebullient personality brightened even the dullest meetings.",
        "synonyms": ["exuberant", "vivacious"],
        "origin": "From Latin 'ebullire' (to bubble out), from 'e-' (out) + 'bullire' (to boil). The metaphor of bubbling over with enthusiasm perfectly captures the word's meaning."
    },
    {
        "word": "truculent",
        "pronunciation": "TRUK-yuh-luhnt",
        "part_of_speech": "adjective",
        "definition": "eager or quick to argue or fight; aggressively defiant",
        "example": "The truculent customer demanded to speak with the manager.",
        "synonyms": ["belligerent", "combative"],
        "origin": "From Latin 'truculentus' (fierce, savage), from 'trux' (fierce). Originally described wild, savage behavior. The word has softened somewhat in modern usage to mean aggressively defiant."
    },
    {
        "word": "vicissitude",
        "pronunciation": "vi-SIS-i-tood",
        "part_of_speech": "noun",
        "definition": "a change of circumstances or fortune, typically unwelcome",
        "example": "The vicissitudes of life taught her to be resilient and adaptable.",
        "synonyms": ["fluctuation", "upheaval"],
        "origin": "From Latin 'vicissitudo' (change, alternation), from 'vicis' (turn, change). Related to 'vice versa.' Often used in the plural to describe life's ups and downs."
    },
    {
        "word": "pusillanimous",
        "pronunciation": "pyoo-suh-LAN-uh-muhs",
        "part_of_speech": "adjective",
        "definition": "showing a lack of courage or determination; timid",
        "example": "His pusillanimous response to the bully disappointed his friends.",
        "synonyms": ["cowardly", "timorous"],
        "origin": "From Latin 'pusillanimis', from 'pusillus' (very small, petty) + 'animus' (spirit, mind). Literally means 'small-spirited' or 'having a tiny soul.' Used in English since the 16th century."
    },
    {
        "word": "pulchritudinous",
        "pronunciation": "puhl-kri-TOOD-n-uhs",
        "part_of_speech": "adjective",
        "definition": "physically beautiful; comely",
        "example": "The pulchritudinous sunset painted the sky in shades of gold and crimson.",
        "synonyms": ["gorgeous", "stunning"],
        "origin": "From Latin 'pulchritudo' (beauty), from 'pulcher' (beautiful). Ironically, this word for beauty is itself quite ungainly. It entered English in the 15th century and is often used humorously today."
    }
]


async def seed_words():
    """Seed the database with vocabulary words if empty"""
    count = await db.words.count_documents({})
    if count == 0:
        logger.info("Seeding vocabulary words...")
        for word_data in VOCABULARY_WORDS:
            word = Word(**word_data)
            doc = word.model_dump()
            await db.words.insert_one(doc)
        logger.info(f"Seeded {len(VOCABULARY_WORDS)} words")


async def get_or_create_progress():
    """Get or create the single user's progress"""
    progress = await db.progress.find_one({}, {"_id": 0})
    if not progress:
        new_progress = Progress()
        doc = new_progress.model_dump()
        await db.progress.insert_one(doc)
        return new_progress.model_dump()
    return progress


# ============ ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "Lexicon Vocabulary Builder API"}


@api_router.get("/word/today", response_model=WordResponse)
async def get_word_of_today():
    """Get today's word based on date rotation"""
    await seed_words()
    
    # Get all words
    words = await db.words.find({}, {"_id": 0}).to_list(1000)
    if not words:
        raise HTTPException(status_code=404, detail="No words available")
    
    # Use day of year to rotate through words
    today = datetime.now(timezone.utc)
    day_of_year = today.timetuple().tm_yday
    word_index = day_of_year % len(words)
    
    word = words[word_index]
    
    # Check if learned
    progress = await get_or_create_progress()
    is_learned = word['id'] in progress.get('learned_words', [])
    
    return WordResponse(**word, is_learned=is_learned)


@api_router.get("/words", response_model=List[WordResponse])
async def get_all_words():
    """Get all vocabulary words for the archive"""
    await seed_words()
    
    words = await db.words.find({}, {"_id": 0}).to_list(1000)
    progress = await get_or_create_progress()
    learned_ids = progress.get('learned_words', [])
    
    result = []
    for word in words:
        result.append(WordResponse(**word, is_learned=word['id'] in learned_ids))
    
    return result


@api_router.post("/progress/mark-learned")
async def mark_word_learned(request: MarkLearnedRequest):
    """Mark a word as learned"""
    progress = await get_or_create_progress()
    learned_words = progress.get('learned_words', [])
    
    if request.word_id not in learned_words:
        learned_words.append(request.word_id)
        
        # Update streak logic
        today = datetime.now(timezone.utc).date().isoformat()
        last_active = progress.get('last_active_date', '')
        current_streak = progress.get('current_streak', 0)
        
        if last_active:
            last_date = datetime.fromisoformat(last_active).date()
            today_date = datetime.now(timezone.utc).date()
            diff = (today_date - last_date).days
            
            if diff == 1:
                current_streak += 1
            elif diff > 1:
                current_streak = 1
        else:
            current_streak = 1
        
        await db.progress.update_one(
            {"id": progress['id']},
            {
                "$set": {
                    "learned_words": learned_words,
                    "total_words_learned": len(learned_words),
                    "current_streak": current_streak,
                    "last_active_date": today
                }
            }
        )
    
    return {"success": True, "total_learned": len(learned_words)}


@api_router.get("/progress")
async def get_progress():
    """Get user progress and statistics"""
    progress = await get_or_create_progress()
    
    # Get learned words details
    learned_ids = progress.get('learned_words', [])
    learned_words = []
    if learned_ids:
        learned_words = await db.words.find(
            {"id": {"$in": learned_ids}},
            {"_id": 0}
        ).to_list(1000)
    
    return {
        "total_words_learned": progress.get('total_words_learned', 0),
        "current_streak": progress.get('current_streak', 0),
        "total_quizzes_taken": progress.get('total_quizzes_taken', 0),
        "total_correct_answers": progress.get('total_correct_answers', 0),
        "quiz_scores": progress.get('quiz_scores', [])[-10:],  # Last 10 quizzes
        "learned_words": learned_words
    }


@api_router.get("/quiz", response_model=List[QuizQuestion])
async def generate_quiz(count: int = 5):
    """Generate a quiz with multiple choice questions"""
    await seed_words()
    
    words = await db.words.find({}, {"_id": 0}).to_list(1000)
    if len(words) < 4:
        raise HTTPException(status_code=400, detail="Not enough words for quiz")
    
    # Select random words for quiz
    quiz_words = random.sample(words, min(count, len(words)))
    questions = []
    
    for word in quiz_words:
        # Get 3 wrong definitions
        other_words = [w for w in words if w['id'] != word['id']]
        wrong_options = random.sample(other_words, min(3, len(other_words)))
        wrong_definitions = [w['definition'] for w in wrong_options]
        
        # Create options (correct + 3 wrong)
        options = wrong_definitions + [word['definition']]
        random.shuffle(options)
        
        questions.append(QuizQuestion(
            word_id=word['id'],
            word=word['word'],
            correct_definition=word['definition'],
            options=options
        ))
    
    return questions


@api_router.post("/quiz/submit", response_model=QuizSubmitResponse)
async def submit_quiz_answer(request: QuizSubmitRequest):
    """Submit a quiz answer and update progress"""
    progress = await get_or_create_progress()
    
    is_correct = request.selected_answer == request.correct_answer
    
    # Update progress
    total_correct = progress.get('total_correct_answers', 0)
    total_quizzes = progress.get('total_quizzes_taken', 0)
    current_streak = progress.get('current_streak', 0)
    
    if is_correct:
        total_correct += 1
    
    total_quizzes += 1
    
    # Update streak on correct answer
    today = datetime.now(timezone.utc).date().isoformat()
    last_active = progress.get('last_active_date', '')
    
    if is_correct:
        if last_active:
            last_date = datetime.fromisoformat(last_active).date()
            today_date = datetime.now(timezone.utc).date()
            diff = (today_date - last_date).days
            
            if diff == 1:
                current_streak += 1
            elif diff > 1:
                current_streak = 1
        else:
            current_streak = 1
    
    await db.progress.update_one(
        {"id": progress['id']},
        {
            "$set": {
                "total_correct_answers": total_correct,
                "total_quizzes_taken": total_quizzes,
                "current_streak": current_streak,
                "last_active_date": today
            }
        }
    )
    
    return QuizSubmitResponse(
        is_correct=is_correct,
        correct_answer=request.correct_answer,
        streak=current_streak
    )


@api_router.post("/progress/reset")
async def reset_progress():
    """Reset all progress (for testing/demo)"""
    await db.progress.delete_many({})
    new_progress = Progress()
    doc = new_progress.model_dump()
    await db.progress.insert_one(doc)
    return {"success": True, "message": "Progress reset"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Seed database on startup"""
    await seed_words()
    await get_or_create_progress()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
