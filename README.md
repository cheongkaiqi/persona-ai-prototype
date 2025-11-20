# 🎓 Persona AI - Personalized Learning Assistant

> An emotionally-aware AI tutor that adapts to individual knowledge background, energy levels, and academic emotions, with human oversight at every step.

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Team](#-team)
- [Development Timeline](#-development-timeline)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

Current AI assistants provide one-size-fits-all responses, ignoring individual learning preferences and emotional states. **Persona AI** addresses this by creating a **three-dimensional personalization system**:

### **The Three Dimensions:**

1. **Static Profile** (Who you are as a learner)
   - Learning style preferences
   - Content format preferences
   - Communication style preferences

2. **Dynamic State** (How you feel right now)
   - Current energy level (high/medium/low)
   - Academic emotion (curious, anxious, frustrated, bored, confused, neutral)

3. **Human Oversight** (Keeping you in control)
   - Validate your preferences before they're saved
   - Review and edit all generated content
   - Provide ongoing feedback

### **Example:**

**Generic AI Response:**
> "A derivative measures the rate of change of a function. It is defined as the limit of..."

**Persona AI Response** (for visual learner, low energy, anxious about exam):
> "Think of a derivative like your car's speedometer 🚗
>
> **Quick essentials for your exam:**
> - It tells you how fast something is changing
> - Formula: f'(x) = lim[h→0] (f(x+h) - f(x))/h
> - [Simple diagram showing slope]
>
> You've got this! This concept is more intuitive than it looks."

---

## ✨ Key Features

### **🧠 Intelligent Profiling**
- Structured interview process to capture learning preferences
- LLM-powered extraction of preferences from natural language
- User validation and editing of extracted preferences

### **🎭 Emotional Adaptation**
- Detects six academic emotions (based on Pekrun's Control-Value Theory)
- Adapts tone, complexity, and approach based on emotional state
- Real-time adjustment for energy levels

### **👥 Human-in-the-Loop**
- **Checkpoint 1:** Preference Validation (review extracted preferences)
- **Checkpoint 2:** Content Review (edit before accepting)
- **Checkpoint 3:** Continuous Feedback (rate responses)

### **🔒 Privacy-First**
- Local storage of user profiles
- No data sharing with third parties
- Transparent data practices

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git

### Setup

1. **Clone the repository:**
```bash
   git clone https://github.com/cheongkaiqi/persona-ai-prototype.git
   cd persona-ai-prototype
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API key
   # OPENAI_API_KEY=sk-proj-your-actual-key-here
```

4. **Verify installation:**
```bash
   python -c "import openai, streamlit; print('✅ All dependencies installed')"
```

### Security Note

⚠️ **Never commit your `.env` file to Git!**

The `.env` file contains sensitive API keys and is automatically ignored by Git through `.gitignore`. If you accidentally commit secrets:

1. Immediately regenerate your API key
2. Remove the file from Git history
3. Update your local `.env` with the new key

---

## 💻 Usage

### Running the Application
```bash
# Start the Streamlit app
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure
```
persona-ai-prototype/
├── .env                    # Environment variables (API keys) - NOT in Git
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── requirements.txt        # Python dependencies
│
├── src/                    # Main application code
│   ├── __init__.py
│   ├── app.py             # Streamlit UI
│   ├── interview.py       # Interview module
│   ├── extract_preferences.py  # LLM preference extraction
│   ├── generate_content.py     # Personalized content generation
│   └── utils.py           # Helper functions
│
├── profiles/              # User preference profiles
│   ├── .gitkeep          # Keeps folder in Git
│   └── *.json            # User profiles (ignored by Git)
│
├── docs/                  # Documentation
│   ├── interview_protocol.md
│   ├── evaluation_plan.md
│   └── api_documentation.md
│
├── tests/                 # Test files
│   ├── test_extraction.py
│   └── test_generation.py
│
└── practice/              # Learning exercises (Week 1-2)
    └── hello_openai.py
```

---

## 👥 Team

This project is developed by a team of 5 students for the course **"Enhancing Data Analysis with Generative AI"** at Technical University of Munich.

| Role | Responsibilities |
|------|------------------|
| **Project Manager** | Coordination, documentation, timeline management |
| **Technical Lead** | API integration, prompt engineering, architecture |
| **Interview/Oversight Lead** | Interview design, human oversight implementation |
| **UI/UX Lead** | Streamlit interface, user experience |
| **Evaluation Lead** | Testing protocol, metrics, analysis |

---

## 📅 Development Timeline

### Month 1: Foundation (Weeks 1-4)
- [x] Week 1: Setup, research, basic API integration
- [ ] Week 2: Interview system, preference extraction
- [ ] Week 3: Preference validation interface (Checkpoint 1)
- [ ] Week 4: Basic personalized content generation

**Milestone:** MVP 1.0 - Static profile system working

### Month 2: Enhancement (Weeks 5-8)
- [ ] Week 5: Add energy level detection
- [ ] Week 6: Add academic emotion detection
- [ ] Week 7: Output review interface (Checkpoint 2)
- [ ] Week 8: Integration, polish, internal testing

**Milestone:** MVP 2.0 - Full 3D personalization operational

### Month 3: Validation (Weeks 9-12)
- [ ] Week 9: User testing (5-7 participants)
- [ ] Week 10: Analysis and critical fixes
- [ ] Week 11: Deployment and presentation prep
- [ ] Week 12: Final presentation

**Milestone:** Project complete with validated results

---

## 🤝 Contributing

### For Team Members

**Before starting work:**
```bash
git pull  # Always get latest changes first
```

**Making changes:**
1. Work on your assigned module
2. Test locally
3. Commit with clear message
4. Push regularly

**Commit message format:**
```
[Action] [What] [Where]

Examples:
✅ Add preference validation to app.py
✅ Fix API timeout in generate_content.py
✅ Update README with usage instructions
```

### What NOT to commit:
- ❌ `.env` files
- ❌ API keys
- ❌ User data (profiles/*.json)
- ❌ Large files (>10MB)

---

## 📝 License

This is an educational project developed for academic purposes at Technical University of Munich.

**For academic use only.** Not licensed for commercial use.

---

**Built with ❤️ by Team Persona AI**

*Last updated: 19/11/2025*