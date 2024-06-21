# Secure Code Assistant

A Streamlit app for identifying and fixing security vulnerabilities in code snippets, files, and GitHub repositories.

## Features

- Analyze Pasted Code Snippets
- Analyze Uploaded Code Files
- Analyze GitHub Repositories
- Generate Secure Code
- Save Secure Code

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Installation Steps

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/code-security-assistant.git
    cd code-security-assistant
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables:

GOOGLE_API_KEY=your_google_api_key
FIREBASE_CREDENTIALS_PATH=path_to_your_firebase_credentials.json


### Firebase Setup

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Create a new project or select an existing one.
3. Navigate to Project Settings > Service Accounts.
4. Generate a new private key and download the JSON file.
5. Save the JSON file in your project directory and set the `FIREBASE_CREDENTIALS_PATH` in the `.env` file to its path.

### Google Generative AI API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to the APIs & Services > Credentials.
4. Create a new API key and restrict its usage if necessary.
5. Add the API key to your `.env` file as `GOOGLE_API_KEY`.

## Usage

### Running the App

Run the Streamlit app with the following command:

```bash
streamlit run app.py
```
Note: I chose the Gemini API because it is currently free to use and provides fast responses with the Gemini Flash model. With a few modifications, you can also configure the application to use the OpenAI API if desired.
