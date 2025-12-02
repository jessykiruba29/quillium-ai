import os
import json
import requests
from typing import List, Dict, Optional
import google.generativeai as genai

def make_mcqs(text: str, language: str = "English", max_questions: int = 20) -> List[Dict]:
    """Generate MCQs directly using Gemini API - SIMPLE VERSION"""
    
    # Clean text
    text = text.strip()
    if len(text) < 50:
        return []
    
    # If text is too long, truncate it
    if len(text) > 6000:
        text = text[:6000] + "... [text truncated]"
    
    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return generate_fallback_mcqs(text, max_questions)
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Use the latest available model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Create a clear, strict prompt
        prompt = f"""
Generate exactly {max_questions} multiple choice questions (MCQs) from the following text.
Each question MUST have exactly 4 options, with ONE correct answer.

IMPORTANT RULES:
1. Make questions MEANINGFUL - test real understanding, not just trivia
2. Make ALL options PLAUSIBLE and SPECIFIC
3. NEVER use vague options like: "wrong answer", "incorrect concept", "different perspective", "alternative interpretation", "common misconception"
4. For "Who" questions: Use SPECIFIC PERSON NAMES as distractors
5. For "What/When/Where/Why" questions: Use SPECIFIC facts/terms/concepts as distractors
6. All options should be complete phrases/sentences (not single words unless appropriate)
7. Difficulty should vary: easy, medium, hard

FORMAT STRICTLY AS JSON:
[
  {{
    "question": "Clear question here?",
    "answer": "The exact correct answer (must match one option exactly)",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "difficulty": "easy|medium|hard"
  }}
]

EXAMPLES OF GOOD OPTIONS:
Question: "Who coined the term 'Artificial Intelligence'?"
Good options: ["John McCarthy", "Alan Turing", "Marvin Minsky", "Herbert Simon"]
Bad options: ["A different scientist", "Not John McCarthy", "Someone else", "Wrong person"]

Question: "What is the capital of France?"
Good options: ["Paris", "London", "Berlin", "Madrid"]
Bad options: ["Not Paris", "Different city", "Some European capital", "Incorrect answer"]

TEXT TO ANALYZE:
{text}

IMPORTANT: Return ONLY the JSON array. No explanations, no extra text.
"""
        
        print("🤖 Asking Gemini to generate MCQs...")
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 4000,
            }
        )
        
        raw_output = response.text.strip()
        print(f"✅ Received response from Gemini")
        
        # Clean the response
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
        raw_output = raw_output.strip()
        
        # Try to parse JSON
        try:
            mcqs = json.loads(raw_output)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Raw output: {raw_output[:200]}...")
            return generate_fallback_mcqs(text, max_questions)
        
        # Validate and clean each MCQ
        validated_mcqs = []
        for mcq in mcqs[:max_questions]:  # Ensure we don't exceed max_questions
            validated = validate_mcq(mcq)
            if validated:
                validated_mcqs.append(validated)
        
        print(f"✅ Generated {len(validated_mcqs)} valid MCQs")
        
        # Translate if needed
        if language != "English" and validated_mcqs:
            validated_mcqs = translate_mcqs_gemini(validated_mcqs, language, api_key)
        
        return validated_mcqs[:max_questions]
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return generate_fallback_mcqs(text, max_questions)

def validate_mcq(mcq: Dict) -> Optional[Dict]:
    """Validate and clean a single MCQ."""
    if not mcq or not isinstance(mcq, dict):
        return None
    
    question = mcq.get("question", "").strip()
    answer = mcq.get("answer", "").strip()
    options = mcq.get("options", [])
    difficulty = mcq.get("difficulty", "medium").strip().lower()
    
    # Basic validation
    if not question or not answer or not options:
        return None
    
    if len(options) != 4:
        return None
    
    if answer not in options:
        # If answer doesn't match any option, use the first option as answer
        answer = options[0]
    
    # Clean options
    cleaned_options = []
    seen = set()
    
    for opt in options:
        opt_str = str(opt).strip()
        if not opt_str:
            continue
        
        # Skip if too vague
        opt_lower = opt_str.lower()
        vague_terms = [
            "wrong", "incorrect", "not correct", "false", "invalid",
            "different concept", "alternative perspective", "common misconception",
            "broader interpretation", "related but different", "someone else",
            "not this", "other answer", "another option"
        ]
        
        if any(term in opt_lower for term in vague_terms):
            continue
        
        # Skip duplicates
        if opt_lower in seen:
            continue
        
        seen.add(opt_lower)
        cleaned_options.append(opt_str)
    
    # Ensure we have 4 options
    if len(cleaned_options) < 4:
        # Add meaningful fillers
        while len(cleaned_options) < 4:
            filler = generate_meaningful_filler(question, answer, len(cleaned_options))
            if filler.lower() not in seen:
                seen.add(filler.lower())
                cleaned_options.append(filler)
    
    # Update answer if it was removed during cleaning
    if answer not in cleaned_options:
        answer = cleaned_options[0]
    
    # Validate difficulty
    if difficulty not in ["easy", "medium", "hard"]:
        # Auto-determine difficulty
        total_words = len(question.split()) + len(answer.split())
        if total_words < 20:
            difficulty = "easy"
        elif total_words < 40:
            difficulty = "medium"
        else:
            difficulty = "hard"
    
    return {
        "question": question,
        "answer": answer,
        "options": cleaned_options[:4],  # Ensure exactly 4
        "difficulty": difficulty
    }

def generate_meaningful_filler(question: str, answer: str, index: int) -> str:
    """Generate a meaningful filler option based on question context."""
    question_lower = question.lower()
    
    if question_lower.startswith("who"):
        # Person-based fillers
        people = ["Albert Einstein", "Marie Curie", "Isaac Newton", "Charles Darwin", 
                  "Alan Turing", "Stephen Hawking", "Thomas Edison", "Nikola Tesla"]
        return people[index % len(people)]
    
    elif "capital" in question_lower:
        # Capital cities
        capitals = ["London", "Berlin", "Tokyo", "Beijing", "Moscow", "Delhi", "Canberra", "Ottawa"]
        return capitals[index % len(capitals)]
    
    elif any(term in question_lower for term in ["year", "when", "date"]):
        # Years
        years = ["1945", "1969", "1776", "2001", "1492", "1914", "1989", "2008"]
        return years[index % len(years)]
    
    else:
        # Generic but meaningful fillers
        generic = [
            "A closely related but distinct concept",
            "An important but different aspect",
            "A frequently confused alternative",
            "A similar but not identical element"
        ]
        return generic[index % len(generic)]

def translate_mcqs_gemini(mcqs: List[Dict], target_lang: str, api_key: str) -> List[Dict]:
    """Translate MCQs using Gemini."""
    if target_lang == "English" or not mcqs:
        return mcqs
    
    print(f"🌐 Translating MCQs to {target_lang}...")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""
Translate the following JSON array of multiple choice questions to {target_lang}.
Translate ALL text including questions, answers, and options.
Maintain the EXACT same JSON structure.

IMPORTANT: 
1. Keep the answer matching exactly one of the translated options
2. Don't change the order of options
3. Return ONLY the JSON array

JSON to translate:
{json.dumps(mcqs, ensure_ascii=False, indent=2)}
"""
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 4000,
            }
        )
        
        raw_output = response.text.strip()
        
        # Clean JSON
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
        raw_output = raw_output.strip()
        
        translated_mcqs = json.loads(raw_output)
        return translated_mcqs
        
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return mcqs  # Return original if translation fails

def generate_fallback_mcqs(text: str, max_questions: int) -> List[Dict]:
    """Generate simple fallback MCQs if Gemini fails."""
    print("⚠️ Using fallback MCQ generation")
    
    # Simple sentence-based questions
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    
    mcqs = []
    for i in range(min(max_questions, len(sentences))):
        sentence = sentences[i]
        if len(sentence) > 100:
            sentence = sentence[:100] + "..."
        
        mcqs.append({
            "question": f"What is the main idea of: '{sentence}'?",
            "answer": sentences[i],
            "options": [
                sentences[i],
                "A different concept from the text",
                "An alternative interpretation",
                "Related information not mentioned here"
            ],
            "difficulty": "medium"
        })
    
    return mcqs[:max_questions]

def make_flashcards(text: str, lang: str = "English", max_cards: int = 20) -> List[Dict]:
    """Generate flashcards from text."""
    mcqs = make_mcqs(text, language="English", max_questions=max_cards)
    
    # Convert to flashcards (just Q&A)
    flashcards = []
    for mcq in mcqs:
        flashcards.append({
            "question": mcq["question"],
            "answer": mcq["answer"]
        })
    
    # Translate if needed
    if lang != "English" and flashcards:
        # Reuse the translation function
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                # Convert flashcards to MCQ-like format for translation
                temp_mcqs = []
                for card in flashcards:
                    temp_mcqs.append({
                        "question": card["question"],
                        "answer": card["answer"],
                        "options": [card["answer"]],  # Minimal options
                        "difficulty": "medium"
                    })
                
                translated = translate_mcqs_gemini(temp_mcqs, lang, api_key)
                
                # Convert back to flashcards
                flashcards = []
                for item in translated:
                    flashcards.append({
                        "question": item["question"],
                        "answer": item["answer"]
                    })
            except:
                pass  # Keep original if translation fails
    
    return flashcards[:max_cards]

# Simple usage example
if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    Artificial Intelligence (AI) was coined by John McCarthy in 1956 at the Dartmouth Conference.
    McCarthy defined AI as "the science and engineering of making intelligent machines."
    The field has since grown to include machine learning, natural language processing, and computer vision.
    Alan Turing, another pioneer, proposed the Turing Test in 1950 to measure machine intelligence.
    """
    
    # Set your API key
    os.environ["GEMINI_API_KEY"] = "your-api-key-here"
    
    # Generate MCQs
    mcqs = make_mcqs(sample_text, language="English", max_questions=5)
    
    print(f"\nGenerated {len(mcqs)} MCQs:")
    for i, mcq in enumerate(mcqs, 1):
        print(f"\n{i}. {mcq['question']}")
        print(f"   Difficulty: {mcq['difficulty']}")
        for j, option in enumerate(mcq['options']):
            prefix = "✓" if option == mcq['answer'] else " "
            print(f"   {prefix} {chr(65+j)}. {option}")


def init_translator():
    """Dummy function to maintain compatibility with existing imports."""
    print("✅ Translator initialized (using Gemini for translations)")
    return None