import requests
import sys
from datetime import datetime
import json

class VocabularyAPITester:
    def __init__(self, base_url="https://daily-vocab-27.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, validation_func=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    if validation_func:
                        validation_result = validation_func(response_data)
                        if not validation_result:
                            success = False
                            self.errors.append(f"{name}: Validation failed")
                            print(f"❌ Failed - Validation failed")
                        else:
                            print(f"✅ Passed - Validation successful")
                    else:
                        print(f"✅ Passed - Status: {response.status_code}")
                except json.JSONDecodeError:
                    success = False
                    self.errors.append(f"{name}: Invalid JSON response")
                    print(f"❌ Failed - Invalid JSON response")
            else:
                self.errors.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            if success:
                self.tests_passed += 1
                return True, response.json() if response.text else {}
            else:
                return False, {}

        except Exception as e:
            self.errors.append(f"{name}: {str(e)}")
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def validate_word_structure(self, word):
        """Validate word object structure"""
        required_fields = ['id', 'word', 'pronunciation', 'part_of_speech', 'definition', 'example']
        return all(field in word and word[field] for field in required_fields)

    def validate_word_response(self, response):
        """Validate word response structure"""
        if not isinstance(response, dict):
            return False
        
        required_fields = ['id', 'word', 'pronunciation', 'part_of_speech', 'definition', 'example', 'is_learned']
        return all(field in response for field in required_fields)

    def validate_words_list(self, response):
        """Validate words list response"""
        if not isinstance(response, list):
            return False
        
        if len(response) == 0:
            print("   Warning: No words in response")
            return True
        
        # Validate first word structure
        return self.validate_word_response(response[0])

    def validate_progress_structure(self, response):
        """Validate progress response structure"""
        if not isinstance(response, dict):
            return False
        
        required_fields = ['total_words_learned', 'current_streak', 'total_quizzes_taken', 'total_correct_answers']
        return all(field in response for field in required_fields)

    def validate_quiz_structure(self, response):
        """Validate quiz response structure"""
        if not isinstance(response, list) or len(response) == 0:
            return False
        
        question = response[0]
        required_fields = ['word_id', 'word', 'correct_definition', 'options']
        
        if not all(field in question for field in required_fields):
            return False
        
        # Validate options (should have 4 options)
        if not isinstance(question['options'], list) or len(question['options']) != 4:
            return False
        
        # Correct definition should be in options
        return question['correct_definition'] in question['options']

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test(
            "API Root",
            "GET",
            "",
            expected_status=200,
            validation_func=lambda x: isinstance(x, dict) and 'message' in x
        )

    def test_word_of_today(self):
        """Test word of the day endpoint"""
        success, response = self.run_test(
            "Word of Today",
            "GET",
            "word/today",
            expected_status=200,
            validation_func=self.validate_word_response
        )
        
        if success:
            print(f"   Today's word: {response.get('word', 'N/A')}")
            
        return success, response

    def test_all_words(self):
        """Test get all words endpoint"""
        success, response = self.run_test(
            "All Words",
            "GET",
            "words",
            expected_status=200,
            validation_func=self.validate_words_list
        )
        
        if success:
            print(f"   Total words: {len(response)}")
            
        return success, response

    def test_initial_progress(self):
        """Test initial progress endpoint"""
        success, response = self.run_test(
            "Initial Progress",
            "GET",
            "progress",
            expected_status=200,
            validation_func=self.validate_progress_structure
        )
        
        if success:
            print(f"   Words learned: {response.get('total_words_learned', 0)}")
            print(f"   Current streak: {response.get('current_streak', 0)}")
            
        return success, response

    def test_mark_learned(self, word_id):
        """Test mark word as learned"""
        success, response = self.run_test(
            "Mark Word Learned",
            "POST",
            "progress/mark-learned",
            expected_status=200,
            data={"word_id": word_id},
            validation_func=lambda x: 'success' in x and 'total_learned' in x
        )
        
        return success, response

    def test_generate_quiz(self):
        """Test quiz generation"""
        success, response = self.run_test(
            "Generate Quiz",
            "GET",
            "quiz?count=5",
            expected_status=200,
            validation_func=self.validate_quiz_structure
        )
        
        if success:
            print(f"   Quiz questions: {len(response)}")
            if len(response) > 0:
                print(f"   First question word: {response[0].get('word', 'N/A')}")
        
        return success, response

    def test_submit_quiz(self, word_id, selected_answer, correct_answer):
        """Test quiz submission"""
        success, response = self.run_test(
            "Submit Quiz Answer",
            "POST",
            "quiz/submit",
            expected_status=200,
            data={
                "word_id": word_id,
                "selected_answer": selected_answer,
                "correct_answer": correct_answer
            },
            validation_func=lambda x: 'is_correct' in x and 'correct_answer' in x and 'streak' in x
        )
        
        if success:
            print(f"   Answer correct: {response.get('is_correct', False)}")
            
        return success, response

    def test_progress_reset(self):
        """Test progress reset endpoint"""
        return self.run_test(
            "Reset Progress",
            "POST",
            "progress/reset",
            expected_status=200,
            validation_func=lambda x: 'success' in x
        )

def main():
    print("🚀 Starting Lexicon Vocabulary Builder API Tests")
    print("="*50)
    
    tester = VocabularyAPITester()
    
    # Test 1: API Root
    tester.test_root_endpoint()
    
    # Test 2: Word of Today
    success, today_word = tester.test_word_of_today()
    word_id = today_word.get('id') if success else None
    
    # Test 3: All Words
    success, all_words = tester.test_all_words()
    
    # Test 4: Initial Progress
    tester.test_initial_progress()
    
    # Test 5: Mark Word as Learned (if we have a word)
    if word_id:
        tester.test_mark_learned(word_id)
        
        # Test updated progress after marking learned
        success, updated_progress = tester.run_test(
            "Updated Progress After Learning",
            "GET", 
            "progress",
            validation_func=lambda x: x.get('total_words_learned', 0) > 0
        )
    
    # Test 6: Generate Quiz
    success, quiz_questions = tester.test_generate_quiz()
    
    # Test 7: Submit Quiz Answer (if we have questions)
    if success and quiz_questions and len(quiz_questions) > 0:
        question = quiz_questions[0]
        tester.test_submit_quiz(
            question['word_id'],
            question['correct_definition'],  # Submit correct answer
            question['correct_definition']
        )
    
    # Test 8: Reset Progress (for clean testing)
    tester.test_progress_reset()
    
    # Final Results
    print("\n" + "="*50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.errors:
        print("\n❌ Errors encountered:")
        for error in tester.errors:
            print(f"   • {error}")
    else:
        print("\n✅ All tests passed successfully!")
    
    # Return appropriate exit code
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())