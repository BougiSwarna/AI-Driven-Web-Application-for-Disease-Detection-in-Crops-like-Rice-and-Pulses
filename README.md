# GreenScan AI: Rice & Pulse Disease Detection 🌿

GreenScan AI is a professional plant disease diagnostics tool powered by deep learning. It helps farmers and researchers identify diseases in Rice and Pulse crops by analyzing leaf images.

## Features

- **Multi-Crop Support**: Specialized models for Rice and Pulse crops.
- **Real-time Analysis**: Instant results using TensorFlow-based deep learning models.
- **Disease History**: Secured user accounts to track and review previous scans.
- **Premium UI**: Modern, responsive dashboard built with Streamlit and custom CSS.
- **Cloud Integration**: Uses Firebase Authentication and Firestore for data persistence.

## Project Structure

```text
├── Plant_Disease_Detection_/
│   ├── .streamlit/           # Streamlit configuration and secrets
│   ├── models/               # Pre-trained Keras models (.keras)
│   ├── static/               # Static assets and class labels
│   ├── app.py                # Main Streamlit application
│   ├── utils.py              # Firebase and helper functions
│   ├── requirements.txt      # Project dependencies
│   └── ...
├── README.md                 # Project documentation
└── ...
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd ai-rice-pulse-disease-detection
```

### 2. Install dependencies
It is recommended to use a virtual environment.
```bash
pip install -r Plant_Disease_Detection_/requirements.txt
```

### 3. Configure Firebase Secrets
You need to provide your own Firebase credentials. Create a file at `Plant_Disease_Detection_/.streamlit/secrets.toml` and fill in your details:

```toml
[firebase_web]
API_KEY = "..."
AuthDomain = "..."
ProjectId = "..."
# ... (see secrets.toml.example or placeholder for details)

[firebase_service_account]
type = "service_account"
project_id = "..."
# ...
```

### 4. Run the Application
```bash
cd Plant_Disease_Detection_
streamlit run app.py
```

## Technologies Used

- **Frontend**: Streamlit
- **Deep Learning**: TensorFlow, Keras
- **Database/Auth**: Firebase Firestore, Firebase Authentication
- **Data Handling**: NumPy, Pandas, Pillow

## Authors

- **Swarna** - *Initial Work*
