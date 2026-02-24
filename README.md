<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/53bcce01-ca85-440a-b020-14a03a8d13bf" />



# Intelligent Digital Fraud Awareness and Detection Platform

An offline, web-based application that analyzes suspicious SMS, WhatsApp messages, and call transcripts to detect potential fraud using a hybrid approach combining rule-based pattern matching with machine learning classification.

## Features

- **Hybrid Fraud Detection**: Combines rule-based pattern matching (40%) with ML classification (60%)
- **Offline Operation**: All processing occurs locally without external API dependencies
- **Explainable Results**: Human-readable explanations and actionable safety recommendations
- **User Awareness Tracking**: Tracks and measures fraud awareness improvement over time
- **Analytics Dashboard**: Comprehensive visualizations of fraud detection statistics and trends
- **Privacy-First**: All data stays local with optional history clearing
- **RESTful API**: FastAPI backend for easy integration

## Technology Stack

- **Backend**: FastAPI (Python 3.8+)
- **Machine Learning**: Scikit-learn (TF-IDF + Logistic Regression)
- **Database**: SQLite3
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Testing**: Pytest, Hypothesis (property-based testing)

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Virtual environment** (recommended)

### Platform-Specific Notes

#### Windows
- Use `python` command (or `py` if Python Launcher is installed)
- Example: `python -m venv venv`
- Activate virtual environment: `venv\Scripts\activate`

#### macOS/Linux
- Use `python3` command (Python 2 may still be installed as `python`)
- Example: `python3 -m venv venv`
- Activate virtual environment: `source venv/bin/activate`

**Note**: Throughout this README, commands use `python` for simplicity. On macOS/Linux, replace `python` with `python3` and `pip` with `pip3` if needed.

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fraud-detection-platform
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

All dependencies are cross-platform compatible and will work on Windows, macOS, and Linux.

## Model Training

Before using the fraud detection system, you must train the ML model.

### Using Sample Data

The project includes sample training data (`training/sample_data.csv`) with 200+ labeled messages:

```bash
python training/train_model.py
```

This will:
1. Load the sample training data
2. Train a TF-IDF + Logistic Regression model
3. Save model artifacts to `backend/models/`
4. Display training metrics (accuracy, precision, recall, F1)

### Using Custom Data

To train with your own data, create a CSV file with two columns:
- `text`: The message content
- `label`: 0 for legitimate, 1 for scam

```bash
python training/train_model.py path/to/your/data.csv
```

**Minimum Requirements:**
- At least 100 samples (1000+ recommended)
- Balanced distribution of scam and legitimate messages
- Examples covering all fraud categories (OTP, KYC, Bank, Reward, Phishing)

### Evaluating the Model

To evaluate the trained model on test messages:

```bash
python training/evaluate_model.py
```

## Usage

### Starting the Backend Server

The backend API must be running before starting the frontend.

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

**API Endpoints:**
- `POST /analyze` - Analyze a message for fraud
- `GET /analytics` - Retrieve aggregated statistics
- `GET /health` - Check system health
- `DELETE /history` - Clear analysis history (requires confirmation)

### Starting the Frontend

In a new terminal (with virtual environment activated):

```bash
streamlit run frontend/app.py
```

The web interface will open automatically at `http://localhost:8501`

### Using the Application

1. **Analyze Messages**:
   - Enter or paste a suspicious message in the text area (max 5000 characters)
   - Click "Analyze" button
   - View risk score, fraud category, triggered keywords, explanation, and recommendations
   - Check your awareness score in the sidebar

2. **View Analytics**:
   - Navigate to "Analytics Dashboard" from the sidebar
   - View statistics: total messages, risk distribution, fraud categories, trends
   - See top scam keywords and your awareness progress
   - Optionally clear history for privacy

## Sample Test Messages

Try these sample messages to test the system:

### High Risk - OTP Scam
```
URGENT! Your bank account will be suspended. Share your OTP code immediately to verify: http://bit.ly/verify123
```

### High Risk - KYC Scam
```
Dear customer, your SBI account KYC update is pending. Click here to update immediately or account will be blocked: https://sbi-kyc-update.xyz
```

### High Risk - Reward Scam
```
Congratulations! You have won Rs 50,00,000 in the lottery. Share your bank details to claim your prize now!
```

### Suspicious - Phishing
```
Your package delivery failed. Click this link to reschedule: http://tinyurl.com/delivery-update
```

### Safe - Legitimate
```
Your OTP for login is 123456. Do not share this code with anyone. Valid for 10 minutes.
```

## API Documentation

### POST /analyze

Analyze a message for fraud detection.

**Request:**
```json
{
  "message": "Your suspicious message text here"
}
```

**Response:**
```json
{
  "risk_score": 85.5,
  "risk_level": "High Risk",
  "fraud_category": "OTP Scam",
  "triggered_keywords": {
    "urgency": ["urgent", "immediately"],
    "otp": ["otp", "verification code"]
  },
  "ai_probability": 92.3,
  "explanation": "This message shows multiple fraud indicators...",
  "recommendations": [
    "Never share OTP codes with anyone",
    "Verify sender through official channels"
  ],
  "awareness_score": 65.4,
  "awareness_level": "Aware",
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET /analytics

Retrieve aggregated statistics.

**Response:**
```json
{
  "total_messages": 150,
  "risk_distribution": {
    "Safe": 45,
    "Suspicious": 60,
    "High Risk": 45
  },
  "category_distribution": {
    "OTP Scam": 30,
    "KYC Scam": 25,
    "Bank Impersonation": 20,
    "Reward/Lottery Scam": 15,
    "Phishing Link Scam": 35,
    "Other/Unknown": 25
  },
  "average_risk_score": 52.3,
  "top_keywords": [
    ["urgent", 45],
    ["otp", 30],
    ["verify", 28]
  ],
  "risk_trend": [
    {"timestamp": "2024-01-15T10:00:00", "score": 45.2},
    {"timestamp": "2024-01-15T10:15:00", "score": 78.5}
  ]
}
```

### GET /health

Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=backend --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Run Property-Based Tests

```bash
pytest tests/test_properties.py -v
```

Property-based tests use Hypothesis to verify correctness properties across many randomly generated inputs.

## Project Structure

```
fraud-detection-platform/
├── backend/
│   ├── components/          # Core detection components
│   │   ├── rule_engine.py
│   │   ├── nlp_model.py
│   │   ├── risk_scorer.py
│   │   ├── category_classifier.py
│   │   ├── explainability.py
│   │   ├── awareness_tracker.py
│   │   └── database_logger.py
│   ├── models/              # ML model artifacts
│   │   ├── model.pkl
│   │   └── vectorizer.pkl
│   ├── analyzer.py          # Message analyzer orchestrator
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration constants
│   └── utils.py             # Utility functions
├── frontend/
│   ├── pages/
│   │   └── analytics.py     # Analytics dashboard
│   ├── app.py               # Main Streamlit interface
│   └── utils.py             # Frontend helpers
├── training/
│   ├── train_model.py       # Model training script
│   ├── evaluate_model.py    # Model evaluation script
│   └── sample_data.csv      # Sample training dataset
├── tests/                   # Test suite
├── fraud_detection.db       # SQLite database (created at runtime)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Architecture

The system follows a modular architecture with clear separation of concerns:

1. **Rule Engine**: Pattern matching using keyword rules (40% weight)
2. **NLP Model**: ML-based classification using TF-IDF + Logistic Regression (60% weight)
3. **Risk Scorer**: Combines rule and AI scores into final risk assessment
4. **Category Classifier**: Determines specific fraud type
5. **Explainability Module**: Generates human-readable explanations
6. **Awareness Tracker**: Calculates user awareness improvement
7. **Database Logger**: Persists results with retry logic
8. **Message Analyzer**: Orchestrates the complete pipeline
9. <img width="780" height="816" alt="image" src="https://github.com/user-attachments/assets/700d8ace-dc86-4688-a4be-20047ba2ca83" />


## Cross-Platform Compatibility

This application is fully cross-platform and works on:
- ✅ Windows (7, 8, 10, 11)
- ✅ macOS (10.14+)
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)

**Key Compatibility Features:**
- Uses `pathlib.Path` for all file path operations (no hardcoded separators)
- No platform-specific system calls or dependencies
- All Python dependencies are cross-platform compatible
- SQLite database works identically across all platforms
- Tested on Windows, macOS, and Linux environments

## Security and Privacy

### Security Features
- **Input Sanitization**: All inputs are sanitized to prevent injection attacks
- **No Code Execution**: System never executes user-provided code
- **Offline Operation**: No external API calls or data transmission
- **Local Processing**: All analysis occurs on your machine

### Privacy Features
- **Local Data Storage**: All messages and analysis results stay on your device
- **No External Transmission**: No data is sent to external servers
- **History Clearing**: Optional feature to permanently delete all stored analysis records
- **No Tracking**: No user tracking or analytics collection

## Troubleshooting

### Model Files Not Found

**Error**: `ModelNotFoundError: Model file not found`

**Solution**: Train the model first:
```bash
python training/train_model.py
```

### Backend Connection Error

**Error**: Frontend shows "Cannot connect to backend server"

**Solution**: Ensure backend is running:
```bash
uvicorn backend.main:app --reload
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**: 
- For backend: Use a different port: `uvicorn backend.main:app --port 8001`
- For frontend: Use a different port: `streamlit run frontend/app.py --server.port 8502`

### Database Locked

**Error**: `sqlite3.OperationalError: database is locked`

**Solution**: The system automatically retries up to 3 times. If the issue persists:
1. Close any other applications accessing the database
2. Restart both backend and frontend servers

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Ensure you're running commands from the project root directory and virtual environment is activated.

### Python Version Issues

**Error**: Syntax errors or compatibility issues

**Solution**: Verify Python version is 3.8 or higher:
```bash
python --version  # or python3 --version on macOS/Linux
```

## Performance

- **Analysis Time**: < 2 seconds per message
- **Rule Engine**: < 100 milliseconds
- **NLP Inference**: < 500 milliseconds
- **Database Write**: < 50 milliseconds
- **Dashboard Load**: < 3 seconds (up to 10,000 records)

## Contributing

This project was developed for a hackathon. Contributions, issues, and feature requests are welcome!

## License

[Add your license information here]

## Acknowledgments

- Built with FastAPI, Streamlit, and Scikit-learn
- Designed for offline fraud detection and user awareness education
- Developed as part of a hackathon project

## Support

For issues, questions, or feedback:
1. Check the Troubleshooting section above
2. Review the API documentation
3. Check application logs in `fraud_detection.log`
4. Open an issue in the repository

---

Project Demo: https://youtu.be/MLB5nJS1zN8







