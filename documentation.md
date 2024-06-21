## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Setup and Installation](#setup-and-installation)
   - [Prerequisites](#prerequisites)
   - [Installation Steps](#installation-steps)
   - [Environment Variables](#environment-variables)
   - [Firebase Setup](#firebase-setup)
   - [Google Generative AI API Key](#google-generative-ai-api-key)
5. [Usage](#usage)
   - [Running the App](#running-the-app)
   - [Analyze Pasted Code Snippet](#analyze-pasted-code-snippet)
   - [Analyze Uploaded Code File](#analyze-uploaded-code-file)
   - [Analyze GitHub Repository](#analyze-github-repository)
   - [Secure Code Saved in New Folder](#secure-code-saved-in-new-folder)
6. [Screenshots](#screenshots)
7. [Code Explanation](#code-explanation)
   - [Main Function](#main-function)
   - [User Input Handling](#user-input-handling)
   - [Creating a Conversational Chain](#creating-a-conversational-chain)
   - [Analyzing GitHub Repositories](#analyzing-github-repositories)
   - [Session Management](#session-management)
   - [Handling Permissions](#handling-permissions)
---

## Overview

The Code Security Assistant is a Streamlit application designed to help developers identify and fix security vulnerabilities in their code. The app can analyze code snippets, uploaded code files, and entire GitHub repositories, providing secure versions of the analyzed code and saving them in a new directory.

---

## Features

- **Analyze Pasted Code Snippets**: Enter insecure code snippets directly into the app for analysis.
- **Analyze Uploaded Code Files**: Upload code files to the app for security analysis.
- **Analyze GitHub Repositories**: Enter a GitHub repository URL to analyze all code files within the repository.
- **Generate Secure Code**: The app provides a secure version of the analyzed code.
- **Save Secure Code**: Secure code is saved in a new folder replicating the original repository structure.

---

## Architecture

The app is built using the following components:

- **Streamlit**: For the web interface.
- **Langchain**: For creating conversational AI models.
- **Google Generative AI**: For analyzing and generating secure code.
- **Firebase**: For managing session data.
- **GitPython**: For cloning and working with GitHub repositories.

---

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Installation Steps

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
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

```
GOOGLE_API_KEY=your_google_api_key
FIREBASE_CREDENTIALS_PATH=path_to_your_firebase_credentials.json
```

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

---

## Usage

### Running the App

Run the Streamlit app with the following command:

```bash
streamlit run app.py
```

### Analyze Pasted Code Snippet

1. Open the app in your browser.
2. Enter your insecure code snippet in the provided text area.
3. The app will analyze the code and display a secure version along with comments highlighting the vulnerabilities.

### Analyze Uploaded Code File

1. Click the "Upload your code file" button.
2. Select a code file from your computer.
3. The app will analyze the file and display a secure version along with comments highlighting the vulnerabilities.

### Analyze GitHub Repository

1. Enter the URL of the GitHub repository you want to analyze.
2. Click the "Analyze GitHub Repository" button.
3. The app will clone the repository, analyze each code file, and save the secure versions in a new folder named `secure_repo` in the working directory.

### Secure Code Saved in New Folder

After analyzing a GitHub repository, the app saves the secure versions of the code files in a new folder named `secure_repo` in the working directory. This folder replicates the structure of the original repository, making it easy to review and use the secure code.

---

## Screenshots

### Analyze Pasted Code Snippet

![[Pasted image 20240621152242.png]]
### Analyze Uploaded Code File

![[Pasted image 20240621144324.png]]

**Explanation given : -** ![[Pasted image 20240621144708.png]]

**And the Secure Code provided by the same :-** ![[Pasted image 20240621144806.png]]


### Analyze GitHub Repository

**New Session opened and GitHub link provided : -**![[Screenshot (9).png]] **It will analyze the repo file by file and show it accordingly**
### Secure Code Saved in New Folder

![[Pasted image 20240621152031.png]]

**Secure Code files are saved in the secure_repo file with the same name folders as in the GitHub**

---

## Code Explanation

### Main Function

The `main` function is the entry point of the Streamlit app. It configures the page, initializes session states, and handles user interactions.

```python
def main():
    st.set_page_config(page_title="Code Security Assistant")
    st.sidebar.title("Code Security Assistant")

    # Add a button to start a new chat
    st.sidebar.button("New Chat", on_click=new_chat, type='primary')

    # Display saved sessions
    if st.session_state["stored_session"]:
        st.sidebar.markdown("### Saved Sessions")
        for i, session in enumerate(st.session_state["stored_session"]):
            if st.sidebar.button(f"Load Session {i+1}"):
                load_session(i)
    
    if st.sidebar.button("Current Session"):
        st.session_state.current_session = st.session_state.current_session

    st.header("Code Security Assistant")

    # Display chat history
    for message in st.session_state.current_session["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Text area for user to input insecure code
    insecure_code = st.chat_input("Enter your insecure code snippet:", key="input_area")

    if insecure_code or st.session_state.uploaded_file_content:
        code_to_analyze = insecure_code if insecure_code else st.session_state.uploaded_file_content
        
        with st.spinner("Analyzing code..."):
            answer = user_input(code_to_analyze)

        # Clear the uploaded file content after analysis
        st.session_state.uploaded_file_content = ""
        st.session_state["file_uploader_key"] = str(os.urandom(24))

        # Update chat history
        user_message = {"role": "user", "content": code_to_analyze}
        assistant_message = {"role": "assistant", "content": answer}
        st.session_state.current_session["chat_history"].extend([user_message, assistant_message])
        st.session_state.current_session["past"].append(code_to_analyze)
        st.session_state.current_session["generated"].append(answer)
        st.session_state.buffer_memory.save_context({"insecure_code": code_to_analyze}, {"response": answer})

        # Display the user input
        with st.chat_message("user"):
            st.markdown(f"```\n{code_to_analyze}\n```")

        # Display the AI response
        with st.chat_message("assistant"):
            st.markdown(f"```\n{answer}\n```")

    # File uploader for user to input insecure code
    uploaded_file = st.file_uploader("Upload your code file:", type=["txt", "py", "java", "js", "cpp", "php", "go", "ruby"], key="file_uploader" if "file_uploader_key" not in st.session_state else st.session_state["file_uploader_key"])

    if uploaded_file:
        st.session_state.uploaded_file_content = uploaded_file.read().decode("utf-8")
        st.text_area("File content:", st.session_state.uploaded_file_content, height=200)

    # GitHub repository input for user to input repository link
    github_repo_url = st.text_input("Enter the GitHub repository URL:")
    if st.button

("Analyze GitHub Repository"):
        with st.spinner("Cloning repository..."):
            analysis_result = analyze_github_repo(github_repo_url)
        st.markdown(analysis_result)

if __name__ == "__main__":
    main()
```

### User Input Handling

The `user_input` function takes an insecure code snippet as input, processes it using a prompt template, and uses the Google Generative AI API to generate a secure version of the code.

```python
def user_input(insecure_code):
    prompt_template = PromptTemplate(
        input_variables=["insecure_code"],
        template="Analyze the following code and fix any security vulnerabilities:\n\n{insecure_code}"
    )

    llm_chain = LLMChain(
        llm=chat_model,
        prompt=prompt_template
    )

    answer = llm_chain.run(insecure_code)
    return answer
```

### Creating a Conversational Chain

The `create_conversation_chain` function sets up the conversational AI model using the LangChain library, integrating the Google Generative AI model and Firebase session manager.

```python
def create_conversation_chain(api_key):
    chat_model = ChatGooglePalm(api_key=api_key)
    conversation_chain = ConversationChain(
        llm=chat_model,
        verbose=True,
        memory=st.session_state.buffer_memory
    )
    return conversation_chain
```

### Analyzing GitHub Repositories

The `analyze_github_repo` function clones a GitHub repository, iterates through its files, analyzes each file for security vulnerabilities, and saves the secure versions in a new folder named `secure_repo`.

```python
def analyze_github_repo(repo_url):
    try:
        # Clone the repository
        repo_path = "temp_repo"
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        Repo.clone_from(repo_url, repo_path)

        # Analyze each code file in the repository
        secure_repo_path = "secure_repo"
        if os.path.exists(secure_repo_path):
            shutil.rmtree(secure_repo_path)
        os.makedirs(secure_repo_path)

        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    insecure_code = f.read()

                secure_code = user_input(insecure_code)

                # Save the secure code in the new folder
                relative_path = os.path.relpath(root, repo_path)
                secure_file_dir = os.path.join(secure_repo_path, relative_path)
                os.makedirs(secure_file_dir, exist_ok=True)
                secure_file_path = os.path.join(secure_file_dir, file)
                with open(secure_file_path, "w") as f:
                    f.write(secure_code)

        return "GitHub repository analyzed and secure code saved in 'secure_repo' folder."
    except Exception as e:
        return f"Error analyzing GitHub repository: {str(e)}"
```

### Session Management

Session states are used to store user inputs, chat history, and analysis results. This allows the app to maintain state across different user interactions.

### Handling Permissions

The `handle_remove_readonly` function ensures that read-only files can be deleted during the cleanup of temporary directories.

```python
def handle_remove_readonly(func, path, exc):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)
```
