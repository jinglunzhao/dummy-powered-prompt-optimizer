# AI Social Skills Training Pipeline

A comprehensive system for optimizing AI models to help students improve their social skills through simulated interactions with AI dummies.

## 🎯 **Project Overview**

This pipeline creates AI-powered "dummies" with diverse personalities and social anxiety profiles, simulates their interactions with an AI assistant, and evaluates improvements in social skills through pre/post assessments. The goal is to iteratively optimize the AI system prompt using the **TRUE GEPA approach** - starting simple and building complexity through reflection and natural language analysis.

## 🏗️ **Architecture**

### **Core Components:**
- **Character Generator**: Creates diverse AI dummies with Big Five personality traits and social anxiety modeling
- **Assessment System**: 20-question social skills evaluation on a 4-point scale
- **Conversation Simulator**: Manages multi-turn interactions between dummies and AI
- **Web Interface**: Interactive dashboard for exploring results
- **Prompt Optimizer**: TRUE GEPA approach - starts simple, uses reflection, builds complexity gradually

### **Data Flow:**
1. Generate 100 diverse AI dummies
2. Conduct pre-assessment of social skills
3. Simulate 5-round conversations with AI assistant
4. Conduct post-assessment
5. Analyze improvement patterns
6. Optimize system prompt based on results

## 🧠 **TRUE GEPA Approach**

The system implements the **Generative Evolutionary Prompt Architecture (GEPA)** approach as described in the research paper. This approach emphasizes:

### **Core Principles:**
1. **Start Simple**: Begin with minimal, uncomplicated prompts
2. **Use Reflection**: Understand WHY simple approaches work or fail
3. **Build Gradually**: Add complexity only when reflection reveals it's needed
4. **Discover Components**: Let the system identify missing elements through testing

### **How It Works:**
1. **Initial State**: Single prompt "You are a helpful coach."
2. **Testing Phase**: Evaluate with diverse AI dummies
3. **Reflection Analysis**: Natural language insights into performance
4. **Component Discovery**: Create components only when gaps are identified
5. **Population Growth**: Expand from 1 to 10 prompts as components emerge
6. **Evolution**: Use discovered components for crossover and mutation

### **Benefits:**
- **Avoids Over-Engineering**: No assumptions about needed components
- **Better Understanding**: Natural language reflection explains performance
- **More Efficient**: Population grows only when needed
- **Research-Aligned**: Follows GEPA paper principles exactly

## 📁 **Project Structure**

```
edu_chatbot/
├── config.py                 # Configuration and constants
├── models.py                 # Pydantic data models
├── character_generator.py    # AI dummy generation system
├── assessment_system.py      # Social skills assessment engine
├── conversation_simulator.py # Conversation management
├── web_interface.py         # Flask web application
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── data/                   # Data storage
│   ├── ai_dummies.json     # Generated dummy profiles
│   ├── assessments.json    # Assessment results
│   └── conversations.json  # Conversation logs
└── templates/              # Web interface templates
    ├── index.html          # Main dashboard
    └── dummy_detail.html   # Individual dummy view
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Up API Key**
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_api_key_here
```

### **3. Generate AI Dummies**
```bash
python character_generator.py
```

### **4. Run Assessments and Conversations**
```bash
python assessment_system.py
python conversation_simulator.py
```

### **5. Launch Web Interface**
```bash
python web_interface.py
```
Open your browser to `http://localhost:5000`

### **6. Optimize System Prompts (TRUE GEPA Approach)**
```bash
# Run the TRUE GEPA prompt optimizer
python prompt_optimizer.py

# The system will:
# 1. Start with a single simple prompt: "You are a helpful coach."
# 2. Test and reflect on performance with dummies
# 3. Discover components only when needed through reflection
# 4. Gradually build complexity based on actual needs
```

## 🔧 **Configuration**

Key settings in `config.py`:
- **AI Model**: DeepSeek Chat (`deepseek-chat`)
- **Assessment Questions**: 20 social skills questions
- **Scoring Scale**: 1-4 (Not True to Very True)
- **Conversation Rounds**: 5 per dummy
- **Total Dummies**: 100

## 📊 **Data Models**

### **AI Dummy Structure:**
- **Personality**: Big Five traits (Extraversion, Agreeableness, Conscientiousness, Neuroticism, Openness)
- **Social Anxiety**: Anxiety level (1-10), specific fears, avoidance behaviors, coping strategies
- **Background**: Age, gender, personal history

### **Assessment Structure:**
- **Questions**: 20 social skills evaluation items
- **Responses**: Individual question scores and notes
- **Scores**: Total score (0-80) and average score (0-4)

### **Conversation Structure:**
- **Turns**: Alternating dummy and AI responses
- **Context**: Scenario description and conversation flow
- **Analysis**: AI reasoning and final responses

## 🌐 **Web Interface Features**

### **Dashboard:**
- Overview statistics
- Search and filter dummies
- Visual personality and anxiety indicators

### **Individual Dummy View:**
- Complete personality profile
- Pre/post assessment comparison
- Full conversation history
- Improvement analysis

## 🔬 **Research Applications**

### **System Prompt Optimization (TRUE GEPA Approach):**
1. **Start Simple**: Begins with a single, minimal prompt: "You are a helpful coach."
2. **Reflection-Driven**: Uses natural language analysis to understand what works/doesn't work
3. **Component Discovery**: Creates components only when reflection reveals actual gaps
4. **Gradual Complexity**: Builds complexity based on discovered needs, not assumptions
5. **Natural Language Insights**: AI generates explanations of why simple approaches succeed/fail
6. **Evolutionary Growth**: Population grows gradually as components are discovered

### **Prompt Optimization System (TRUE GEPA):**
- **Starting Point**: Single simple prompt with no pre-defined components
- **Reflection Engine**: Natural language analysis of what works/doesn't work
- **Component Discovery**: Components emerge through reflection analysis, not pre-engineering
- **Population Strategy**: Starts with 1 prompt, grows gradually as components are discovered
- **Evolutionary Algorithm**: Reflection-guided crossover and mutation
- **Performance Tracking**: Comprehensive metrics with natural language insights
- **Adaptive Growth**: System complexity adapts to actual testing results

### **Diversity Analysis:**
- Personality trait distribution
- Social anxiety level variation
- Assessment score diversity
- Improvement pattern analysis

## 📈 **Analysis Capabilities**

- **Pre/Post Comparison**: Side-by-side assessment results
- **Improvement Metrics**: Score changes and percentage improvements
- **Pattern Recognition**: Identify which personality types benefit most
- **Question-Level Analysis**: Individual question performance tracking

## 🤝 **Collaboration Guidelines**

### **Adding New Features:**
1. Update data models in `models.py`
2. Modify core logic in respective modules
3. Update web interface templates
4. Test with sample data
5. Update documentation

### **Data Format Standards:**
- Use UTF-8 encoding for all JSON files
- Maintain consistent data structure
- Include timestamps for all records
- Validate data with Pydantic models

### **Code Style:**
- Follow PEP 8 guidelines
- Use type hints
- Document complex functions
- Maintain modular structure

## 🐛 **Troubleshooting**

### **Common Issues:**
- **API Key Errors**: Ensure `.env` file is properly configured
- **Data Loading Issues**: Check file paths and JSON format
- **Web Interface Errors**: Verify Flask dependencies are installed

### **Debug Mode:**
Enable debug output in `web_interface.py` for detailed logging.

## 📚 **References**

- **[GEPA Paper](https://arxiv.org/pdf/2507.19457)**: Generative Evolutionary Prompt Architecture - the core research this system implements
- **Big Five Personality Model**: Psychological trait theory
- **Social Anxiety Research**: Clinical assessment methodologies
- **AI Training**: System prompt optimization techniques

## 📄 **License**

This project is for research and educational purposes. Please ensure compliance with relevant API usage terms and data privacy regulations.

## 👥 **Contributors**

- **Primary Developer**: [Your Name]
- **Research Team**: [Team Members]
- **Institution**: [Your Institution]

---

**Last Updated**: December 2024  
**Version**: 2.0.0 - TRUE GEPA Implementation  
**Status**: Research Prototype with TRUE GEPA Approach
