import os
import streamlit as st
import json
from datetime import datetime
import pandas as pd
from openai import OpenAI
from collections import Counter

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FOLDER = "profiles/chat_history"
PROGRESS_FOLDER = "profiles/progress_tracker"

def load_chat(subject):
    """Load chat history for a subject."""
    file_path = os.path.join(CHAT_FOLDER, f"{subject}.json")
    if not os.path.exists(file_path):
        return {"sessions": {}}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both old and new format
            if "sessions" in data:
                return data
            else:
                # Old format: convert to new format
                return {"sessions": {date: {"messages": msgs} for date, msgs in data.items() if isinstance(msgs, list)}}
    except (json.JSONDecodeError, Exception):
        return {"sessions": {}}

def get_sessions(subject):
    """Get all sessions for a subject as a dict of date -> session_data"""
    data = load_chat(subject)
    return data.get("sessions", {})

def load_progress(subject):
    """Load progress tracker data for a subject."""
    path = os.path.join(PROGRESS_FOLDER, f"{subject}.json")

    # If file does not exist, create an empty one
    if not os.path.exists(path):
        os.makedirs(PROGRESS_FOLDER, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        return {}

    # Load existing file
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If file is corrupted, reset safely
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        return {}

def save_progress(subject, date, entry):
    """Save a progress entry for a specific date."""
    os.makedirs(PROGRESS_FOLDER, exist_ok=True)
    path = os.path.join(PROGRESS_FOLDER, f"{subject}.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    # Save ONE object per date (overwrite allowed)
    data[date] = entry

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------- Helper Function ----------------
def load_chat(subject):
    """
    Load chat history for a subject.
    New structure: { "sessions": { "date": { "messages": [...], "summary": "...", ... } } }
    """
    file_path = os.path.join(CHAT_FOLDER, f"{subject}.json")
    if not os.path.exists(file_path):
        return {"sessions": {}}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both old and new format
            if "sessions" in data:
                return data
            else:
                # Old format: convert to new format
                return {"sessions": {date: {"messages": msgs} for date, msgs in data.items() if isinstance(msgs, list)}}
    except (json.JSONDecodeError, Exception):
        return {"sessions": {}}


def get_sessions(subject):
    """Get all sessions for a subject as a dict of date -> session_data"""
    data = load_chat(subject)
    return data.get("sessions", {})


def load_progress(subject):
    """Load progress tracker data for a subject."""
    path = os.path.join(PROGRESS_FOLDER, f"{subject}.json")
    if not os.path.exists(path):
        os.makedirs(PROGRESS_FOLDER, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        return {}


def save_progress(subject, date, entry):
    """Save a progress entry for a specific date."""
    os.makedirs(PROGRESS_FOLDER, exist_ok=True)
    path = os.path.join(PROGRESS_FOLDER, f"{subject}.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    data[date] = entry

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_mood_from_confidence(confidence_value):
    """
    Convert confidence value to mood description.
    Based on Control-Value Theory mapping from generate_content.py
    """
    if confidence_value <= 2:
        return "😰 Stressed/Anxious"
    elif confidence_value <= 4:
        return "😟 Worried/Unsure"
    elif confidence_value <= 6:
        return "😐 Neutral/Okay"
    elif confidence_value <= 8:
        return "🙂 Good/Confident"
    else:
        return "😊 Great/Very Confident"


def get_confidence_level(confidence_value):
    """Get confidence level category."""
    if confidence_value <= 3:
        return "Low (1-3)"
    elif confidence_value <= 6:
        return "Medium (4-6)"
    else:
        return "High (7-10)"


def analyze_feedback(subject):
    """Analyze thumbs up/down feedback per session."""
    sessions = get_sessions(subject)
    daily_feedback = []

    for date, session_data in sessions.items():
        messages = session_data.get("messages", [])
        if not isinstance(messages, list):
            continue

        thumbs_up = sum(m.get("feedback", {}).get("thumbs_up", 0) for m in messages)
        thumbs_down = sum(m.get("feedback", {}).get("thumbs_down", 0) for m in messages)

        # Get pre-session confidence
        emotional_data = session_data.get("emotional_data", {})
        pre_session = emotional_data.get("pre_session", {})
        confidence = pre_session.get("confidence", None)

        daily_feedback.append({
            "Date": date,
            "Thumbs Up": int(thumbs_up),
            "Thumbs Down": int(thumbs_down),
            "Pre-Session Confidence": confidence
        })

    if not daily_feedback:
        return pd.DataFrame()

    return pd.DataFrame(daily_feedback).sort_values("Date", ascending=True)


def get_all_topics(subject):
    """Extract all topics from all sessions."""
    sessions = get_sessions(subject)
    all_topics = []

    for date, session_data in sessions.items():
        topics = session_data.get("topics", [])
        if isinstance(topics, list):
            all_topics.extend(topics)

    return all_topics


def get_emotional_data(subject):
    """Extract emotional data from all sessions."""
    sessions = get_sessions(subject)
    emotional_records = []

    for date, session_data in sessions.items():
        emotional_data = session_data.get("emotional_data", {})
        pre_session = emotional_data.get("pre_session", {})

        if pre_session:
            emotional_records.append({
                "Date": date,
                "Pre-Session Confidence": pre_session.get("confidence", 5),
                "Motivation": pre_session.get("motivation", 5),
            })

    if not emotional_records:
        return pd.DataFrame()

    df = pd.DataFrame(emotional_records)
    df = df.sort_values("Date", ascending=True)
    return df


def build_chat_text(session_data):
    """Convert session messages to readable text for LLM analysis."""
    messages = session_data.get("messages", [])
    lines = []

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")

        if role == "user":
            lines.append(f"[{timestamp}] User: {content}")
        elif role == "assistant":
            lines.append(f"[{timestamp}] Assistant: {content}")

    return "\n".join(lines)


def build_session_table(subject):
    """Build a summary table of all sessions."""
    sessions = get_sessions(subject)
    rows = []

    for date, session_data in sessions.items():
        messages = session_data.get("messages", [])
        summary = session_data.get("summary", "No summary")
        topics = session_data.get("topics", [])

        # Count messages
        msg_count = len(messages) if isinstance(messages, list) else 0

        # Get emotional data
        emotional_data = session_data.get("emotional_data", {})
        pre_session = emotional_data.get("pre_session", {})
        confidence = pre_session.get("confidence", "-")

        rows.append({
            "Date": date,
            "Summary": summary,
            "Topics": ", ".join(topics) if topics else "-",
            "Messages": msg_count,
            "Confidence": confidence
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.sort_values("Date", ascending=False)
    return df

def analyze_emotional_correlation(df):
    """Analyze correlation between mood and feedback."""
    if df.empty or "Pre-Session Confidence" not in df.columns:
        return None

    # Filter rows with confidence data
    df_with_mood = df[df["Pre-Session Confidence"].notna()].copy()

    if df_with_mood.empty:
        return None

    # Categorize confidence levels
    df_with_mood["Confidence Level"] = df_with_mood["Pre-Session Confidence"].apply(get_confidence_level)

    # Calculate positive rate per confidence level
    results = []
    for level in ["Low (1-3)", "Medium (4-6)", "High (7-10)"]:
        level_df = df_with_mood[df_with_mood["Confidence Level"] == level]
        if not level_df.empty:
            total_up = level_df["Thumbs Up"].sum()
            total_down = level_df["Thumbs Down"].sum()
            total = total_up + total_down
            positive_rate = (total_up / total * 100) if total > 0 else 0
            results.append({
                "Confidence Level": level,
                "Sessions": len(level_df),
                "Positive Rate": f"{positive_rate:.0f}%"
            })

    return pd.DataFrame(results) if results else None


def render_metric_card(title, value, color="blue"):
    """Render a styled metric card."""
    color_map = {
        "blue": "#3498db",
        "green": "#27ae60",
        "red": "#e74c3c",
        "purple": "#9b59b6"
    }
    bg_color = color_map.get(color, "#3498db")

    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: {bg_color}15; border-left: 4px solid {bg_color}; margin-bottom: 10px;">
        <div style="font-size: 14px; color: #666;">{title}</div>
        <div style="font-size: 24px; font-weight: bold; color: {bg_color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------- Streamlit UI ----------------
st.title("📊 Chatbot Feedback Analysis")
st.caption("See how Persona AI is helping you learn")

# Check if chat folder exists
if not os.path.exists(CHAT_FOLDER):
    st.warning("No chat history found. Start chatting to see your analysis!")
    st.stop()

# Get available subjects
subjects = [f.replace(".json", "") for f in os.listdir(CHAT_FOLDER) if f.endswith(".json")]

if not subjects:
    st.info("No subjects found yet. Start a study session to see your analysis!")
    st.stop()

# Create tabs
tab1, tab2 = st.tabs(["📊 Learning Progress", "💭 Academic Emotions"])


# ============================================================
# TAB 1: LEARNING PROGRESS
# ============================================================

with tab1:
    # Subject selector
    subject = st.selectbox(
        "Select Subject",
        subjects,
        format_func=lambda x: x.replace("_", " ")
    )

    sessions = get_sessions(subject)

    if not sessions:
        st.info("No sessions found for this subject yet.")
    else:
        # Session History Table
        st.subheader("📅 Session History")
        session_df = build_session_table(subject)

        if not session_df.empty:
            st.dataframe(
                session_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date", width="small"),
                    "Summary": st.column_config.TextColumn("Summary", width="large"),
                    "Topics": st.column_config.TextColumn("Topics", width="medium"),
                    "Messages": st.column_config.NumberColumn("Messages", width="small"),
                    "Confidence": st.column_config.TextColumn("Confidence", width="small")
                }
            )

        st.markdown("---")

        # Response Feedback - Line Chart (FULL WIDTH, ABOVE TOPICS)
        st.subheader("👍 Response Feedback")
        feedback_df = analyze_feedback(subject)

        if not feedback_df.empty and (feedback_df["Thumbs Up"].sum() > 0 or feedback_df["Thumbs Down"].sum() > 0):
            # Prepare data for line chart
            chart_df = feedback_df[["Date", "Thumbs Up", "Thumbs Down"]].copy()
            chart_df = chart_df.set_index("Date")

            # Use Streamlit's native line chart
            st.line_chart(chart_df, use_container_width=True)
        else:
            st.info("No feedback data yet. Use 👍/👎 buttons during chat!")

        st.markdown("---")

        # Topics Covered - Simple List (BELOW FEEDBACK)
        st.subheader("📝 Topics Covered")
        all_topics = get_all_topics(subject)

        if all_topics:
            # Count topic frequency
            topic_counts = Counter(all_topics)
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)

            # Display as simple list with counts
            for topic, count in sorted_topics:
                st.markdown(f"• **{topic}** ({count}x)")
        else:
            st.info("No topics recorded yet.")

        st.markdown("---")

        # Deep Dive Analysis Section
        st.subheader("🔍 Deep Dive Analysis")
        st.caption("Get detailed AI-powered analysis of a specific session")

        # Session selector for deep dive
        available_dates = sorted(sessions.keys(), reverse=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            selected_date = st.selectbox(
                "Select a session to analyze",
                available_dates,
                format_func=lambda x: f"{x} - {sessions[x].get('summary', 'No summary')[:40]}..."
            )

        with col2:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            analyze_button = st.button("🔬 Analyze", type="primary", use_container_width=True)

        if analyze_button and selected_date:
            session_data = sessions[selected_date]
            chat_text = build_chat_text(session_data)

            if not chat_text.strip():
                st.warning("No chat content found for this session.")
            else:
                with st.spinner("Analyzing your study session..."):
                    prompt = f"""
You are an educational analyst AI helping a student understand their learning progress.

Below is a chat conversation from a study session on {selected_date}.

Your tasks:
1. Analyze the student's study behavior in 2-4 concise sentences. Talk directly to the student using "you" and "your".
2. Estimate the approximate study time based on timestamps.
3. Identify strengths and areas for improvement.

Return ONLY valid JSON with NO markdown formatting.

JSON schema:
{{
  "date": "{selected_date}",
  "summary": "<2-4 sentence analysis of study behavior>",
  "topics_covered": "<comma-separated list of topics>",
  "estimated_study_time": "<time estimate>",
  "confidence_level": <number 1-10>,
  "satisfaction_level": <number 1-10>,
  "strengths": "<what went well>",
  "improvements": "<specific suggestions>"
}}

Conversation:
{chat_text}
"""
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You analyze study behavior and return JSON only."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.4,
                        )

                        analysis_text = response.choices[0].message.content.strip()

                        # Clean up potential markdown formatting
                        if analysis_text.startswith("```"):
                            analysis_text = analysis_text.split("```")[1]
                            if analysis_text.startswith("json"):
                                analysis_text = analysis_text[4:]

                        analysis_json = json.loads(analysis_text)

                        # Display analysis in a nice card
                        st.success("Analysis Complete!")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### 📊 Session Overview")
                            st.markdown(f"**Study Time:** {analysis_json.get('estimated_study_time', 'N/A')}")
                            st.markdown(f"**Topics:** {analysis_json.get('topics_covered', 'N/A')}")
                            st.markdown(f"**Confidence:** {analysis_json.get('confidence_level', 'N/A')}/10")
                            st.markdown(f"**Satisfaction:** {analysis_json.get('satisfaction_level', 'N/A')}/10")

                        with col2:
                            st.markdown("#### 💪 Strengths")
                            st.info(analysis_json.get("strengths", "N/A"))

                            st.markdown("#### 🎯 Areas to Improve")
                            st.warning(analysis_json.get("improvements", "N/A"))

                        st.markdown("#### 📝 Summary")
                        st.write(analysis_json.get("summary", "No summary available."))

                        # Save to progress tracker
                        save_progress(
                            subject,
                            analysis_json["date"],
                            {
                                "topics_covered": analysis_json.get("topics_covered", ""),
                                "study_time": analysis_json.get("estimated_study_time", ""),
                                "confidence": analysis_json.get("confidence_level", 5),
                                "satisfaction": analysis_json.get("satisfaction_level", 5)
                            }
                        )

                    except json.JSONDecodeError as e:
                        st.error("Failed to parse analysis. Please try again.")
                        st.text(f"Raw response: {analysis_text[:500]}")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")


# ============================================================
# TAB 2: ACADEMIC EMOTIONS
# ============================================================

with tab2:
    st.subheader("😊 Emotional Correlation (CVT Analysis)")
    st.markdown("How does your pre-session mood affect learning outcomes?")

    # Combine data from all subjects
    all_data = []
    for subj in subjects:
        df = analyze_feedback(subj)
        if not df.empty:
            df["Subject"] = subj
            all_data.append(df)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        # Check if we have emotional data
        has_mood_data = combined_df["Pre-Session Confidence"].notna().any()

        if has_mood_data:
            correlation_df = analyze_emotional_correlation(combined_df)

            if correlation_df is not None and not correlation_df.empty:
                st.markdown("#### Mood vs. Feedback Correlation")

                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(correlation_df, use_container_width=True, hide_index=True)

                with col2:
                    st.markdown("""
                    **Interpretation:**
                    - Higher pre-session confidence often correlates with more positive feedback
                    - This suggests mood affects how users perceive AI responses
                    - Consider: Is the AI adapting well to different emotional states?
                    """)

                st.markdown("---")

                # Mood tracking over time
                st.markdown("#### Mood Tracking Over Time")

                # Get emotional data from all subjects
                all_emotional = []
                for subj in subjects:
                    emotional_df = get_emotional_data(subj)
                    if not emotional_df.empty:
                        emotional_df["Subject"] = subj
                        all_emotional.append(emotional_df)

                if all_emotional:
                    mood_df = pd.concat(all_emotional, ignore_index=True)
                    mood_df = mood_df.sort_values("Date")

                    # Prepare for line chart
                    chart_data = mood_df[["Date", "Pre-Session Confidence", "Motivation"]].copy()
                    chart_data = chart_data.set_index("Date")

                    st.line_chart(chart_data, use_container_width=True)

                    # Summary stats
                    avg_pre = mood_df["Pre-Session Confidence"].mean()
                    avg_motivation = mood_df["Motivation"].mean()

                    if pd.notna(avg_pre) and pd.notna(avg_motivation):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            render_metric_card("Avg Pre-Session Confidence", f"{avg_pre:.1f}/10", "blue")
                        with col2:
                            render_metric_card("Avg Motivation", f"{avg_motivation:.1f}/10", "purple")
                        with col3:
                            # Learning impact (difference between latest and first)
                            if len(mood_df) > 1:
                                first_conf = mood_df.iloc[0]["Pre-Session Confidence"]
                                last_conf = mood_df.iloc[-1]["Pre-Session Confidence"]
                                change = last_conf - first_conf
                                render_metric_card(
                                    "Confidence Change",
                                    f"{'+' if change >= 0 else ''}{change:.1f}",
                                    "green" if change >= 0 else "red"
                                )
                            else:
                                render_metric_card("Sessions", str(len(mood_df)), "green")
            else:
                st.info("Not enough mood data to analyze correlations yet.")
        else:
            st.info("""
            No emotional check-in data found yet.
            
            Start using the mood check-in feature in the chatbot to track:
            - Pre-session confidence levels
            - Motivation ratings
            - Emotional patterns over time
            
            This helps us understand how mood affects learning outcomes!
            """)
    else:
        st.info("No chat data found. Start chatting to generate analytics!")


# Footer
st.divider()
st.caption("💡 Tip: Regular tracking helps you understand your learning patterns better!")
