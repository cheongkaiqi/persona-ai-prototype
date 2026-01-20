import os
import streamlit as st
from openai import OpenAI
import json
import utils
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
CHAT_HISTORY_DIR = os.path.join(PROFILES_DIR, "chat_history")
EXTRACTED_PREFS_FILE = os.path.join(BASE_DIR, "profiles", "extractedPreferences.json")
INTERVIEW_RESPONSES_FILE = os.path.join(BASE_DIR, "profiles", "interviewResponse.json")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =============================================================================
# SECTION 1: UNCHANGED - HELPER FUNCTIONS
# =============================================================================
def load_user_profile():
    """Load extracted preferences with proper error handling."""
    if not os.path.exists(EXTRACTED_PREFS_FILE):
        return None

    try:
        if os.path.getsize(EXTRACTED_PREFS_FILE) == 0:
            return None

        with open(EXTRACTED_PREFS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            return utils.safe_json_loads(content) if content.strip() else None
    except json.JSONDecodeError as e:
        st.error(f"⚠️ AI profile JSON is corrupted: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error loading extracted preferences: {str(e)}")
        return None

def load_subjects():
    if not os.path.exists(INTERVIEW_RESPONSES_FILE):
        return ["general"]

    try:
        with open(INTERVIEW_RESPONSES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Assuming "SECTION 1 — Personal Background-1" contains topics
        topics = data.get("SECTION 1 — Personal Background-1", "")
        if topics:
            # Split by comma and strip whitespace
            subjects = [t.strip() for t in topics.split(",")]
            return subjects
        else:
            return ["general"]

    except Exception as e:
        st.error(f"❌ Could not load subjects: {e}")
        return ["general"]

# =============================================================================
# SECTION 2: NEW - SYSTEM PROMPT BUILDER
# =============================================================================
# WHY: Instead of dumping entire JSON, we extract specific fields and give
#      the LLM clear instructions on HOW to use each piece of information.

def build_system_prompt(profile, subject, emotional_state=None):
    """
    Build a specific system prompt using profile fields directly.

    Args:
        profile: The user's learning profile dictionary
        subject: Current subject being discussed
        emotional_state: Dict with 'confidence' and 'motivation' (0-10 scale)

    Returns:
        A detailed system prompt string
    """
    if not profile:
        return """You are Persona AI, a helpful learning assistant. 
        Be supportive and provide clear explanations."""

    # Navigate to learning_profile if it exists (handles your JSON structure)
    lp = profile.get("learning_profile", profile)

    # --- Extract Background Information ---
    background = lp.get("background", {})
    name = background.get("name", "student")
    program = background.get("academic_program", "unknown program")
    semester = background.get("semester", "unknown")
    current_focus = background.get("current_focus", "")
    goals = background.get("goals", "")

    # --- Extract Learning Preferences ---
    learning_prefs = lp.get("learning_preferences", {})
    explanation_pref = learning_prefs.get("explanation_preference", ["balanced"])
    examples_pref = learning_prefs.get("examples_preference", ["mixed"])
    example_types = learning_prefs.get("example_type", ["general"])
    detail_level = learning_prefs.get("detail_level", 5)  # 0-10 scale
    guidance_pref = learning_prefs.get("guidance_preference", ["balanced"])
    uses_analogies = learning_prefs.get("uses_analogies", False)
    practice_problems = learning_prefs.get("practice_problems", False)
    code_examples = learning_prefs.get("code_examples", ["no"])
    pacing = learning_prefs.get("pacing", ["moderate"])
    learner_type = learning_prefs.get("learner_type", ["mixed"])
    repetition_pref = learning_prefs.get("repetition_preference", ["standard"])

    # --- Extract Communication Style ---
    comm_style = lp.get("communication_style", {})
    tone = comm_style.get("tone", ["neutral"])
    feedback_style = comm_style.get("feedback_style", ["balanced"])
    response_depth = comm_style.get("response_depth", ["moderate"])
    question_engagement = comm_style.get("question_engagement", False)
    summaries_after = comm_style.get("summaries_after_explanation", False)

    # --- Extract Emotional Patterns ---
    emotional_patterns = lp.get("emotional_patterns", {})
    stress_response = emotional_patterns.get("stress_response", ["unknown"])
    overwhelm_support = emotional_patterns.get("overwhelm_support", ["step-by-step"])
    base_confidence = emotional_patterns.get("confidence_level", 5)
    motivation_drivers = emotional_patterns.get("motivation_drivers", "")
    common_blockers = emotional_patterns.get("common_blockers", "")
    learning_challenges = emotional_patterns.get("learning_challenges", "")

    # --- Extract Study Behavior ---
    study_behavior = lp.get("study_behavior", {})
    focus_duration = study_behavior.get("focus_duration", "unknown")
    attention_span = study_behavior.get("attention_span", 5)
    recovery_strategy = study_behavior.get("recovery_strategy", ["break"])

    # --- Build the System Prompt ---
    prompt = f"""You are Persona AI, a personalized learning assistant for a {program} student in semester {semester}.

## YOUR ROLE
You are helping this student learn about "{subject}". Adapt all responses based on the preferences below.

## STUDENT CONTEXT
- Academic Focus: {current_focus}
- Learning Goals: {goals}

## HOW TO EXPLAIN CONCEPTS
"""

    # Add explanation style instructions
    if "step-by-step" in explanation_pref:
        prompt += "- Break down every explanation into numbered steps\n"
    if "examples-first" in examples_pref:
        prompt += "- START with an example before explaining the theory\n"
    else:
        prompt += "- Explain the concept first, then provide examples\n"

    # Add example type instructions
    if example_types:
        example_instructions = []
        if "real-world" in example_types:
            example_instructions.append("practical real-world scenarios")
        if "diagrams" in example_types:
            example_instructions.append("visual descriptions or ASCII diagrams")
        if "code-based" in example_types:
            example_instructions.append("code snippets with comments")
        if example_instructions:
            prompt += f"- Include these types of examples: {', '.join(example_instructions)}\n"

    # Add detail level instruction
    if detail_level >= 7:
        prompt += "- Provide DETAILED explanations with thorough coverage\n"
    elif detail_level <= 3:
        prompt += "- Keep explanations CONCISE and to the point\n"
    else:
        prompt += "- Use moderate detail - thorough but not overwhelming\n"

    # Add analogies instruction
    if uses_analogies:
        prompt += "- Use analogies to connect new concepts to familiar ideas\n"

    # Add practice problems instruction
    if practice_problems:
        prompt += "- Offer practice problems when appropriate to reinforce learning\n"

    # Add code examples instruction
    if "yes" in code_examples:
        prompt += "- Include code examples when relevant to the topic\n"

    prompt += f"""
## COMMUNICATION STYLE
- Tone: {', '.join(tone) if isinstance(tone, list) else tone}
- Feedback approach: {', '.join(feedback_style) if isinstance(feedback_style, list) else feedback_style}
- Response depth: {', '.join(response_depth) if isinstance(response_depth, list) else response_depth}
"""

    if question_engagement:
        prompt += "- Ask follow-up questions to check understanding\n"

    if summaries_after:
        prompt += "- End explanations with a brief summary of key points\n"

    prompt += f"""
## EMOTIONAL AWARENESS
- Known challenges: {learning_challenges}
- What blocks progress: {common_blockers}
- What motivates: {motivation_drivers}
- When overwhelmed, provide: {', '.join(overwhelm_support) if isinstance(overwhelm_support, list) else overwhelm_support} support
"""

    # --- Add Current Mood State (Control-Value Theory via mood) ---
    if emotional_state:
        mood_value = emotional_state.get("confidence", 5)  # mood maps to confidence

        # Get mood description
        if mood_value <= 2:
            mood_desc = "😰 Stressed/Anxious"
        elif mood_value <= 4:
            mood_desc = "😟 Worried/Unsure"
        elif mood_value <= 6:
            mood_desc = "😐 Neutral/Okay"
        elif mood_value <= 8:
            mood_desc = "🙂 Good/Confident"
        else:
            mood_desc = "😊 Great/Very Confident"

        prompt += f"""
## CURRENT SESSION MOOD
The student indicated they're feeling: {mood_desc} ({mood_value}/10)
"""
        # Add specific adaptations based on mood
        if mood_value <= 3:
            prompt += """
⚠️ STUDENT IS FEELING STRESSED OR ANXIOUS:
- Be extra warm, encouraging, and supportive
- Break concepts into smaller, manageable pieces  
- Celebrate small wins and progress
- Use simpler language and avoid overwhelming them
- Remind them that confusion is a normal part of learning
- Check in: "Does this make sense so far?"
"""
        elif mood_value <= 5:
            prompt += """
📝 STUDENT IS FEELING NEUTRAL/UNCERTAIN:
- Provide clear, structured explanations
- Use encouraging language
- Offer to clarify if anything is confusing
- Balance challenge with support
"""
        elif mood_value >= 8:
            prompt += """
✓ STUDENT IS FEELING CONFIDENT AND READY:
- Can introduce more challenging aspects
- Okay to move at a faster pace
- Can ask more probing questions
- Good time for practice problems
- Can explore advanced concepts
"""

    prompt += """
## RESPONSE GUIDELINES
1. Always acknowledge the student's question before diving into the explanation
2. If they seem confused, offer to break it down further
3. Be patient and never make them feel bad for not understanding
4. If a topic relates to their stated goals, make that connection explicit
"""

    return prompt

# =============================================================================
# SECTION 3: NEW - EMOTION TRACKING FUNCTIONS
# =============================================================================

def get_mood_emoji(value):
    """
    Get the appropriate emoji based on mood value (0-10).
    Returns emoji and description.
    """
    if value <= 2:
        return "😰", "Stressed/Anxious"
    elif value <= 4:
        return "😟", "Worried/Unsure"
    elif value <= 6:
        return "😐", "Neutral/Okay"
    elif value <= 8:
        return "🙂", "Good/Confident"
    else:
        return "😊", "Great/Very Confident"


def show_emotion_checkin():
    """
    Display emoji-based mood check-in at the start of a session.
    Uses a single confidence slider with emoji feedback.
    Returns dict with confidence value (mood maps to confidence internally).
    """
    # Header section
    st.markdown("### 🌟 Before we start...")
    st.markdown("### 😊 How are you feeling about studying today?")

    # Slider with emoji display
    slider_col, emoji_col = st.columns([5, 1])

    with slider_col:
        confidence = st.slider(
            "Confidence level",
            min_value=0,
            max_value=10,
            value=5,
            help="Slide to show how confident you feel about studying today",
            key="emotion_confidence"
        )

    with emoji_col:
        # Display emoji based on the current value
        emoji, description = get_mood_emoji(confidence)
        st.markdown(f"<div style='font-size: 40px; text-align: center; padding-top: 25px;'>{emoji}</div>",
                    unsafe_allow_html=True)

    # Show description below slider
    emoji, description = get_mood_emoji(confidence)
    st.caption(f"You're feeling: **{description}**")

    # Add spacing
    st.markdown("")

    # Start Learning button
    if st.button("Start Learning! 🚀", key="save_emotion", type="primary"):
        # Map single mood value to both confidence and motivation
        # (simplified approach - mood affects both dimensions)
        return {
            "confidence": confidence,
            "motivation": confidence,  # Using the same value for simplicity
            "mood_emoji": emoji,
            "saved": True
        }

    return {"confidence": confidence, "motivation": confidence, "saved": False}


def show_compact_mood_display(emotional_state):
    """
    Show a compact mood display after check-in is complete.
    Returns True if the user wants to update.
    """
    confidence = emotional_state.get("confidence", 5)
    emoji, description = get_mood_emoji(confidence)

    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        st.markdown(f"<div style='font-size: 30px;'>{emoji}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"**Today's mood:** {description} ({confidence}/10)")

    with col3:
        # Use on_click callback instead of checking return value
        # This prevents the RerunData error from handling state change properly
        st.button(
            "✏️",
            key="update_mood_btn",
            help="Update your mood",
            on_click=lambda: st.session_state.update({"show_emotion_update": True})
        )

def show_past_session_checkin(session_date):
    """
    Display mood check-in when the user wants to CONTINUE a past session.
    Different messaging than the new session - acknowledges they're returning to a topic.
    """
    # Header section - different messaging for continuing past session
    st.markdown("### 🔄 Continuing from a previous session...")
    st.markdown(f"### 😊 How are you feeling about this topic now?")
    st.caption(f"_You're returning to your session from {session_date}_")

    # Slider with emoji display
    slider_col, emoji_col = st.columns([5, 1])

    with slider_col:
        confidence = st.slider(
            "Current confidence level",
            min_value=0,
            max_value=10,
            value=5,
            help="How confident do you feel about this topic right now?",
            key="past_session_confidence"
        )

    with emoji_col:
        # Display emoji based on the current value
        emoji, description = get_mood_emoji(confidence)
        st.markdown(f"<div style='font-size: 40px; text-align: center; padding-top: 25px;'>{emoji}</div>",
                    unsafe_allow_html=True)

    # Show description below slider
    emoji, description = get_mood_emoji(confidence)
    st.caption(f"You're feeling: **{description}**")

    # Add spacing
    st.markdown("")

    # Continue Learning button
    if st.button("Continue Learning! 📚", key="save_past_emotion", type="primary"):
        return {
            "confidence": confidence,
            "motivation": confidence,
            "mood_emoji": emoji,
            "saved": True
        }

    return {"confidence": confidence, "motivation": confidence, "saved": False}


def show_global_context(chat_data, subject):
    """
    Display global context info in an expandable section.
    Shows topics covered, total sessions, and learning progress.
    """
    global_context = chat_data.get("global_context", {})
    sessions = chat_data.get("sessions", {})

    # Calculate stats if global_context is empty or outdated
    total_sessions = len(sessions)

    # Collect all topics from sessions
    all_topics = set()
    for date, session in sessions.items():
        topics = session.get("topics", [])
        all_topics.update(topics)

    # Collect all emotional data for progress tracking
    mood_history = []
    for date, session in sorted(sessions.items()):
        emotional_data = session.get("emotional_data", {})
        if "pre_session" in emotional_data:
            mood_history.append({
                "date": date,
                "confidence": emotional_data["pre_session"].get("confidence", 5)
            })

    # Display in expandable section
    with st.expander(f"📈 Learning Progress: {subject}", expanded=False):
        # Stats row
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Sessions", total_sessions)

        with col2:
            st.metric("Topics Covered", len(all_topics))

        with col3:
            # Calculate average confidence
            if mood_history:
                avg_confidence = sum(m["confidence"] for m in mood_history) / len(mood_history)
                st.metric("Avg. Confidence", f"{avg_confidence:.1f}/10")
            else:
                st.metric("Avg. Confidence", "N/A")

        # Topics covered
        if all_topics:
            st.markdown("**Topics you've explored:**")
            # Display as tags/chips
            topics_str = " • ".join(sorted(all_topics))
            st.markdown(f"_{topics_str}_")

        # Mood trend (if enough data)
        if len(mood_history) >= 2:
            st.markdown("**Confidence over time:**")
            # Simple text-based trend
            first_mood = mood_history[0]["confidence"]
            last_mood = mood_history[-1]["confidence"]

            if last_mood > first_mood:
                st.markdown(f"📈 Your confidence has **improved** from {first_mood}/10 to {last_mood}/10!")
            elif last_mood < first_mood:
                st.markdown(f"📉 Your confidence went from {first_mood}/10 to {last_mood}/10. Keep practicing!")
            else:
                st.markdown(f"➡️ Your confidence has stayed steady at {last_mood}/10.")

        # Last activity
        if sessions:
            last_date = max(sessions.keys())
            st.caption(f"Last activity: {last_date}")

def get_session_emotional_state(chat_data, date):
    """
    Get the emotional state for a specific session date.
    Returns None if no emotional data exists.
    """
    # Handle new format with sessions structure
    if "sessions" in chat_data and date in chat_data["sessions"]:
        session = chat_data["sessions"][date]
        emotional_data = session.get("emotional_data", {})
        if "pre_session" in emotional_data:
            return {
                "confidence": emotional_data["pre_session"].get("confidence", 5),
                "motivation": emotional_data["pre_session"].get("motivation", 5)
            }
    return None


def save_emotional_state(subject, date, emotional_state):
    """
    Save emotional state to the chat history file.
    Updates the sessions structure with emotional_data.
    """
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{subject}.json")

    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Ensure sessions structure exists
    if "sessions" not in data:
        data["sessions"] = {}

    # Ensure date entry exists in sessions
    if date not in data["sessions"]:
        data["sessions"][date] = {
            "messages": [],
            "summary": "",
            "topics": [],
            "emotional_data": {}
        }

    # Save pre-session emotional state
    data["sessions"][date]["emotional_data"]["pre_session"] = {
        "confidence": emotional_state.get("confidence", 5),
        "motivation": emotional_state.get("motivation", 5),
        "timestamp": datetime.now().isoformat()
    }

    # Save back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =============================================================================
# SECTION 4: UPDATED - CHAT STORAGE FUNCTIONS
# =============================================================================

def save_chat(subject, role, content, date=None, msg_index=None):
    """
    Save a chat message or update feedback in the chat JSON file.
    
    Args:
        subject (str): Subject name.
        Role (str): 'user' or 'assistant'.
        Content (str): Message content.
        Date (str, optional): Date string 'YYYY-MM-DD'. Defaults to today.
        Msg_index (int, optional): Index of message to update (for feedback). If None, append new message.
    """
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{subject}.json")

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Ensure sessions structure exists
    if "sessions" not in data:
        data["sessions"] = {}

    # Ensure date entry exists in sessions
    if date not in data["sessions"]:
        data["sessions"][date] = {
            "messages": [],
            "summary": "",
            "topics": [],
            "emotional_data": {}
        }

    # If msg_index is provided, update that message (for feedback)
    if msg_index is not None:
        messages = data["sessions"][date]["messages"]
        if 0 <= msg_index < len(messages):
            messages[msg_index] = content
        else:
            messages.append(content)
    else:
        # Append a new message
        new_message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "feedback": {"thumbs_up": 0, "thumbs_down": 0} if role == "assistant" else {}
        }
        data["sessions"][date]["messages"].append(new_message)

    # Save back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_chat(subject):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{subject}.json")

    if not os.path.exists(file_path):
        return {"sessions": {}}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # If already in new format, return as-is
        if "sessions" in data:
            return data

        # Convert old format to new format
        # Old format: {"2025-12-10": [messages...], "2025-12-11": [messages...]}
        # New format: {"sessions": {"2025-12-10": {"messages": [...], ...}}}
        converted = {"sessions": {}, "global_context": data.get("global_context", {})}

        for key, value in data.items():
            if key in ["sessions", "global_context"]:
                continue
            if isinstance(value, list):
                # This is old format date -> messages array
                converted["sessions"][key] = {
                    "messages": value,
                    "summary": "",
                    "topics": [],
                    "emotional_data": {}
                }

        return converted

    except Exception as e:
        st.error(f"Error loading chat: {e}")
        return {"sessions": {}}

def save_feedback(subject, date):
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{subject}.json")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Ensure sessions structure
    if "sessions" not in data:
        data["sessions"] = {}

    if date not in data["sessions"]:
        data["sessions"][date] = {
            "messages": [],
            "summary": "",
            "topics": [],
            "emotional_data": {}
        }

    # Update feedback counts
    if "feedback_summary" in st.session_state and subject in st.session_state.feedback_summary:
        if date in st.session_state.feedback_summary[subject]:
            counts = st.session_state.feedback_summary[subject][date]
            data["sessions"][date]["feedback_summary"] = counts

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =============================================================================
# SECTION 5: NEW - CHAT HISTORY NAVIGATION
# =============================================================================
# Features:
# - LLM-generated session titles
# - Enhanced dropdown with titles
# - Search functionality

def generate_session_title(messages):
    """
    Use LLM to generate a short 3-5 word title for a session based on the conversation.
    Called after the first user-assistant exchange.

    Args:
        messages: List of message dicts with 'role' and 'content'

    Returns:
        A short title string (3-5 words)
    """
    if not messages or len(messages) < 2:
        return ""

    # Get first user message and first assistant response
    first_user_msg = None
    first_assistant_msg = None

    for msg in messages:
        if msg["role"] == "user" and not first_user_msg:
            first_user_msg = msg["content"]
        elif msg["role"] == "assistant" and not first_assistant_msg:
            first_assistant_msg = msg["content"]

        if first_user_msg and first_assistant_msg:
            break

    if not first_user_msg:
        return ""

    # Create prompt for title generation
    title_prompt = f"""Based on this conversation start, generate a SHORT title (3-5 words only).
The title should capture the main topic being discussed.

User asked: "{first_user_msg[:500]}"
{"Assistant responded about: " + first_assistant_msg[:300] if first_assistant_msg else ""}

Rules:
- Maximum 5 words
- No quotes or punctuation
- Be specific and descriptive
- Examples: "Matrix Multiplication Basics", "Binary Search Tutorial", "Vector Spaces Introduction"

Return ONLY the title, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": title_prompt}], # type: ignore
            temperature=0.3,
            max_tokens=20
        )
        title = response.choices[0].message.content.strip()
        # Clean up the title - remove quotes if present
        title = title.strip('"\'')
        # Limit length just in case
        words = title.split()
        if len(words) > 6:
            title = ' '.join(words[:5])
        return title
    except Exception as e:
        print(f"Error generating session title: {e}")
        return ""


def save_session_summary(subject, date, summary):
    """
    Save a generated summary/title for a session.

    Args:
        subject: Subject name
        date: Session date string
        summary: The generated title/summary
    """
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{subject}.json")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Ensure structure exists
    if "sessions" not in data:
        data["sessions"] = {}
    if date not in data["sessions"]:
        data["sessions"][date] = {
            "messages": [],
            "summary": "",
            "topics": [],
            "emotional_data": {}
        }

    # Update summary
    data["sessions"][date]["summary"] = summary

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def format_session_label(date, summary, today):
    """
    Format a session label for the dropdown.

    Args:
        date: Session date string (e.g., "2026-01-15")
        summary: Session summary/title (can be empty)
        today: Today's date string

    Returns:
        Formatted label like "2026-01-15 (Today) - Vector Spaces Basics"
    """
    # Add (Today) indicator if applicable
    if date == today:
        date_part = f"{date} (Today)"
    else:
        date_part = date

    # Add summary if available
    if summary:
        return f"{date_part} - {summary}"
    else:
        return date_part


def get_session_labels(chat_data, today):
    """
    Generate formatted labels for all sessions in dropdown.

    Args:
        chat_data: The chat data dictionary
        today: Today's date string

    Returns:
        Tuple of (labels_list, date_to_label_map, label_to_date_map)
    """
    sessions = chat_data.get("sessions", {})
    dates = sorted(sessions.keys(), reverse=True)

    labels = []
    date_to_label = {}
    label_to_date = {}

    for date in dates:
        session = sessions[date]
        summary = session.get("summary", "")
        label = format_session_label(date, summary, today)

        labels.append(label)
        date_to_label[date] = label
        label_to_date[label] = date

    return labels, date_to_label, label_to_date


def search_chat_history(chat_data, query):
    """
    Search through the chat history for matching sessions.

    Args:
        chat_data: The chat data dictionary
        query: Search query string

    Returns:
        List of matching sessions with format:
        [{"date": "2026-01-15", "summary": "...", "matches": ["snippet1", "snippet2"]}]
    """
    if not query or len(query.strip()) < 2:
        return []

    query_lower = query.lower().strip()
    sessions = chat_data.get("sessions", {})
    results = []

    for date, session in sessions.items():
        matches = []

        # Search in summary
        summary = session.get("summary", "")
        if query_lower in summary.lower():
            matches.append(f"Title: {summary}")

        # Search in topics
        topics = session.get("topics", [])
        for topic in topics:
            if query_lower in topic.lower():
                matches.append(f"Topic: {topic}")

        # Search in messages
        messages = session.get("messages", [])
        for msg in messages:
            content = msg.get("content", "")
            if query_lower in content.lower():
                # Extract a snippet around the match
                idx = content.lower().find(query_lower)
                start = max(0, idx - 30)
                end = min(len(content), idx + len(query) + 30)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."

                role_prefix = "You" if msg["role"] == "user" else "Persona"
                matches.append(f"{role_prefix}: {snippet}")

                # Limit matches per session
                if len(matches) >= 3:
                    break

        if matches:
            results.append({
                "date": date,
                "summary": summary,
                "matches": matches[:3]  # Max 3 matches shown
            })

    # Sort by date (newest first)
    results.sort(key=lambda x: x["date"], reverse=True)

    return results


def show_search_bar(chat_data, today):
    """
    Display search bar and results for chat history.

    Args:
        chat_data: The chat data dictionary
        today: Today's date string

    Returns:
        Selected date if user clicks a result, None otherwise
    """
    # Search input
    search_query = st.text_input(
        "🔍 Search this subject's chat history",
        placeholder="Search for topics, questions, or keywords...",
        key="chat_search_input"
    )

    selected_date = None

    if search_query and len(search_query.strip()) >= 2:
        results = search_chat_history(chat_data, search_query)

        if results:
            st.markdown(f"**Found {len(results)} matching session(s):**")

            for result in results[:5]:  # Show max 5 results
                date = result["date"]
                summary = result["summary"]
                matches = result["matches"]

                # Format display
                if date == today:
                    date_display = f"{date} (Today)"
                else:
                    date_display = date

                with st.container():
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        if summary:
                            st.markdown(f"**📅 {date_display} - {summary}**")
                        else:
                            st.markdown(f"**📅 {date_display}**")

                        # Show match snippets
                        for match in matches:
                            st.caption(f"  └ {match}")

                    with col2:
                        # Use callback to set the session state directly
                        def navigate_to_session(target_date):
                            st.session_state.selected_session_date = target_date

                        st.button(
                            "Go →",
                            key=f"search_result_{date}",
                            on_click=navigate_to_session,
                            args=(date,)
                        )

                    st.divider()
        else:
            st.caption("No matching sessions found.")

    return selected_date

# =============================================================================
# SECTION 6: MAIN FUNCTION - UPDATED WITH EMOTION TRACKING
# =============================================================================

def generate_content():
    """
    Chatbot page with:
    - right-side subject selector
    - daily chat sessions stored inside the subject JSON
    - ability to view old chats
    - Emotional state check-in (NEW!)
    - Improved system prompt (NEW!)
    - thumbs up/down feedback per AI response
    """
    # ---------------- Layout ----------------
    left, right = st.columns([3, 1])

    with left:
        st.title("💬 Chat with Persona AI")
        st.markdown("Ask anything — I'm here to help! 😇")

    # ---------------- Dropdown Row ----------------
    col1, col2 = st.columns([1, 1])

    with col1:
        subjects = load_subjects()
        subjects.insert(0, "General")
        subject = st.selectbox(
            "Subject",
            subjects,
            key="subject_dropdown"
        )

    # Load chat history after subject loads
    profile = load_user_profile()

    # ---------------- Manage Session State ----------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    # NEW: Track if emotion check-in was completed for today
    if "emotion_checkin_done" not in st.session_state:
        st.session_state.emotion_checkin_done = {}

    # Load subject chat history (from file if first time)
    if subject not in st.session_state.chat_history:
        st.session_state.chat_history[subject] = load_chat(subject)

    chat_data = st.session_state.chat_history[subject]
    today = datetime.now().strftime("%Y-%m-%d")

    # Ensure today's session exists
    if "sessions" not in chat_data:
        chat_data["sessions"] = {}

    if today not in chat_data["sessions"]:
        chat_data["sessions"][today] = {
            "messages": [],
            "summary": "",
            "topics": [],
            "emotional_data": {}
        }

    # Get formatted session labels for dropdown
    session_labels, date_to_label, label_to_date = get_session_labels(chat_data, today)

    # Safety check: if somehow still empty, add today
    if not session_labels:
        session_labels = [format_session_label(today, "", today)]
        date_to_label[today] = session_labels[0]
        label_to_date[session_labels[0]] = today

    # Track selected session via session state for search navigation
    if "selected_session_date" not in st.session_state:
        st.session_state.selected_session_date = None

    with col2:
        # Find current index based on session state or default to first
        default_index = 0
        if st.session_state.selected_session_date:
            target_label = date_to_label.get(st.session_state.selected_session_date)
            if target_label and target_label in session_labels:
                default_index = session_labels.index(target_label)
            # Reset after using
            st.session_state.selected_session_date = None

        selected_label = st.selectbox(
            "Chat session",
            session_labels,
            index=default_index,
            key="date_dropdown"
        )

        # Convert label back to date
        active_date = label_to_date.get(selected_label, today)

    # ---------------- Search Bar ----------------
    # The Go button's callback handles setting selected_session_date
    # Streamlit automatically reruns after callback
    show_search_bar(chat_data, today)

    # ---------------- Global Context Display ----------------
    # Show learning progress in expandable section
    show_global_context(chat_data, subject)

    # ---------------- NEW: Mood Check-in ----------------
    # Now triggers for BOTH today's sessions AND past sessions (when continuing)
    # IF New session today: "How are you feeling about studying today?"
    # IF Past session: "How are you feeling about this topic NOW?"

    session_key = f"{subject}_{today}"
    current_emotional_state = None

    # Check if emotional state already exists for today
    existing_emotional_state = get_session_emotional_state(chat_data, today)

    # Track if user wants to update their check-in
    if "show_emotion_update" not in st.session_state:
        st.session_state.show_emotion_update = False

    # Track which past sessions have been "continued" (checked in for current visit)
    if "past_session_checkin_done" not in st.session_state:
        st.session_state.past_session_checkin_done = {}

    if active_date == today:
        # ============ TODAY'S SESSION ============
        if existing_emotional_state and not st.session_state.show_emotion_update:
            # Already have emotional state - show compact emoji display
            current_emotional_state = existing_emotional_state

            # Use the new compact mood display
            # NEW - just call it, callback handles everything
            show_compact_mood_display(current_emotional_state)

        elif (session_key not in st.session_state.emotion_checkin_done
              or not st.session_state.emotion_checkin_done.get(session_key, False)
              or st.session_state.show_emotion_update):
            # Show check-in form (either first time or updating)
            emotion_result = show_emotion_checkin()

            if emotion_result.get("saved"):
                current_emotional_state = {
                    "confidence": emotion_result["confidence"],
                    "motivation": emotion_result["motivation"]
                }
                save_emotional_state(subject, today, current_emotional_state)
                st.session_state.emotion_checkin_done[session_key] = True
                st.session_state.show_emotion_update = False  # Reset update flag

                # Update local chat_data
                chat_data["sessions"][today]["emotional_data"]["pre_session"] = {
                    "confidence": current_emotional_state["confidence"],
                    "motivation": current_emotional_state["motivation"],
                    "timestamp": datetime.now().isoformat()
                }

                try:
                    st.rerun()
                except Exception:
                    pass  # Ignore rerun errors in fragment context

            else:
                # Use the current slider values even if not saved
                current_emotional_state = {
                    "confidence": emotion_result["confidence"],
                    "motivation": emotion_result["motivation"]
                }

    else:
        # ============ PAST SESSION (Continuing) ============
        # Check if user has already checked in for this past session during current visit
        past_session_key = f"{subject}_{active_date}_continued"

        if past_session_key in st.session_state.past_session_checkin_done:
            # Already checked in for this past session - show compact display
            current_emotional_state = st.session_state.past_session_checkin_done[past_session_key]

            # Show compact display with original session info in sidebar
            col1, col2, col3 = st.columns([1, 4, 1])
            emoji, description = get_mood_emoji(current_emotional_state["confidence"])

            with col1:
                st.markdown(f"<div style='font-size: 30px;'>{emoji}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Current mood:** {description} ({current_emotional_state['confidence']}/10)")
            with col3:
                # Define a callback function to handle the state update
                def clear_past_checkin(key_to_delete):
                    if key_to_delete in st.session_state.past_session_checkin_done:
                        del st.session_state.past_session_checkin_done[key_to_delete]

                st.button(
                    "✏️",
                    key="update_past_mood_btn",
                    help="Update your mood",
                    on_click=clear_past_checkin,
                    args=(past_session_key,)
                )

            # Show original session mood in sidebar for comparison
            original_state = get_session_emotional_state(chat_data, active_date)
            if original_state:
                with st.sidebar:
                    st.markdown(f"### 📊 Original Session ({active_date})")
                    st.metric("Original Confidence", f"{original_state['confidence']}/10")

                    # Show change
                    change = current_emotional_state["confidence"] - original_state["confidence"]
                    if change > 0:
                        st.success(f"📈 +{change} from original!")
                    elif change < 0:
                        st.warning(f"📉 {change} from original")
                    else:
                        st.info("➡️ Same as original")

        else:
            # First time continuing this past session - ask for current mood
            emotion_result = show_past_session_checkin(active_date)

            if emotion_result.get("saved"):
                current_emotional_state = {
                    "confidence": emotion_result["confidence"],
                    "motivation": emotion_result["motivation"]
                }
                # Store in a session state (not in file - this is current visit mood, not historical)
                st.session_state.past_session_checkin_done[past_session_key] = current_emotional_state
                try:
                    st.rerun()
                except Exception:
                    pass  # Ignore rerun errors in fragment context
            else:
                # Use the current slider values even if not saved
                current_emotional_state = {
                    "confidence": emotion_result["confidence"],
                    "motivation": emotion_result["motivation"]
                }

    # ---------------- Chat Input ----------------
    user_input = st.text_input(
        "You:",
        placeholder="Type your question here...",
        key="user_input"
    )

    # ---------------- Chat Send Logic ----------------
    if st.button("Send", key="send_button") and user_input.strip():
        # Get messages for current session
        messages = chat_data["sessions"][active_date]["messages"]

        # Check if this is the first message (for title generation later)
        is_first_exchange = len(messages) == 0

        # Append user message
        messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
            "feedback": {}
        })
        save_chat(subject, "user", user_input, date=active_date)

        # ========== NEW: Build improved system prompt ==========
        system_prompt = build_system_prompt(
            profile=profile,
            subject=subject,
            emotional_state=current_emotional_state
        )

        # Prepare messages for API (only role and content)
        api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

        # Generate AI response
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}] + api_messages, # type: ignore
                temperature=0.7,
            )
            ai_message = response.choices[0].message.content
            print("AI Response:", ai_message)

            messages.append({
                "role": "assistant",
                "content": ai_message,
                "timestamp": datetime.now().isoformat(),
                "feedback": {"thumbs_up": 0, "thumbs_down": 0}
            })
            save_chat(subject, "assistant", ai_message, date=active_date)

            # ========== Generate session title after first exchange ==========
            current_summary = chat_data["sessions"][active_date].get("summary", "")
            if is_first_exchange and not current_summary:
                # Generate title for this session
                session_title = generate_session_title(messages)
                if session_title:
                    chat_data["sessions"][active_date]["summary"] = session_title
                    save_session_summary(subject, active_date, session_title)
                    print(f"Generated session title: {session_title}")

        except Exception as e:
            ai_message = f"❌ Error generating response: {str(e)}"
            st.error(ai_message)
            messages.append({
                "role": "assistant",
                "content": "Error generating response.",
                "timestamp": datetime.now().isoformat(),
                "feedback": {"thumbs_up": 0, "thumbs_down": 0}
            })
            save_chat(subject, "assistant", "Error generating response.", date=active_date)

    # ---------------- Display Chat ----------------
    messages = chat_data["sessions"].get(active_date, {}).get("messages", [])

    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Persona:** {msg['content']}")

            # -------- Feedback Buttons per AI message --------
            col_up, col_down, _ = st.columns([1, 1, 7])

            thumbs_up_key = f"up_{active_date}_{i}"
            thumbs_down_key = f"down_{active_date}_{i}"

            thumbs_up_clicked = col_up.button("👍", key=thumbs_up_key, help="Press to like")
            thumbs_down_clicked = col_down.button("👎", key=thumbs_down_key, help="Press to dislike")

            if thumbs_up_clicked:
                msg["feedback"]["thumbs_up"] = 1
                msg["feedback"]["thumbs_down"] = 0
                save_chat(subject, "assistant", msg, date=active_date, msg_index=i)

            if thumbs_down_clicked:
                msg["feedback"]["thumbs_down"] = 1
                msg["feedback"]["thumbs_up"] = 0
                save_chat(subject, "assistant", msg, date=active_date, msg_index=i)
