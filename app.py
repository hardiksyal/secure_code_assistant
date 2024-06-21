import errno
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from git import Repo
import tempfile
import shutil
import stat

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if 'buffer_memory' not in st.session_state:
    st.session_state.buffer_memory = ConversationBufferMemory()
if 'current_session' not in st.session_state:
    st.session_state.current_session = {"generated": [], "past": [], "chat_history": []}
if 'uploaded_file_content' not in st.session_state:
    st.session_state.uploaded_file_content = ""
if 'file_uploader_key' not in st.session_state:
    st.session_state["file_uploader_key"] = str(os.urandom(24))

# Function to create a conversational chain with a given prompt template
def get_conversational_chain(prompt_template):
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    prompt = PromptTemplate(template=prompt_template, input_variables=["insecure_code"])
    chain = LLMChain(llm=model, prompt=prompt, memory=st.session_state.buffer_memory)
    return chain

# Function to handle user input and generate responses
def user_input(insecure_code):
    # Prompt template for conversational chain
    prompt_template = """
    You are an expert AI assistant specializing in code security analysis and improvement. Your task is to analyze the provided insecure code snippet, identify any security vulnerabilities, add comments to highlight these vulnerabilities, and then provide a secure version of the code.

    Insecure Code:
    {insecure_code}

    Security Analysis and Recommendations:
    - Identify and explain any security vulnerabilities present in the code.
    - Add comments where necessary to indicate insecure parts and explain why they are insecure.
    - Provide a secure version of the code snippet below, ensuring it addresses all identified vulnerabilities.

    Answer:
    """
    
    chain = get_conversational_chain(prompt_template)

    try:
        response = chain.run({
            "insecure_code": insecure_code,
        })
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        response = "An error occurred while processing your request. Please try again later."

    return response

# Function to start a new chat
def new_chat():
    if st.session_state.current_session["generated"] or st.session_state.current_session["past"]:
        st.session_state["stored_session"].append(st.session_state.current_session)
    st.session_state.current_session = {"generated": [], "past": [], "chat_history": []}
    st.session_state.buffer_memory.clear()
    st.session_state.uploaded_file_content = ""
    st.session_state["file_uploader_key"] = str(os.urandom(24))

# Function to load a previous chat session
def load_session(session_index):
    st.session_state.current_session = st.session_state["stored_session"][session_index]
    st.session_state.buffer_memory.clear()
    for message in st.session_state.current_session["chat_history"]:
        st.session_state.buffer_memory.save_context({"insecure_code": message["content"]}, {"response": message["content"]})

# Handle permission errors during deletion
def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

# Function to analyze GitHub repository
def analyze_github_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    secure_dir = os.path.join(os.getcwd(), "secure_repo")
    os.makedirs(secure_dir, exist_ok=True)
    try:
        # Clone the GitHub repository
        Repo.clone_from(repo_url, temp_dir)
        
        # Read and analyze all code files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.sh', '.php', '.java', '.cpp', '.c', '.rb', '.go')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        insecure_code = f.read()
                    
                    with st.spinner(f"Analyzing {file}..."):
                        answer = user_input(insecure_code)

                    # Save the updated secure code to the secure directory
                    relative_path = os.path.relpath(file_path, temp_dir)
                    secure_file_path = os.path.join(secure_dir, relative_path)
                    os.makedirs(os.path.dirname(secure_file_path), exist_ok=True)
                    with open(secure_file_path, 'w', encoding='utf-8') as f:
                        f.write(answer)

                    # Update chat history
                    user_message = {"role": "user", "content": f"File: {file}\n```\n{insecure_code}\n```"}
                    assistant_message = {"role": "assistant", "content": answer}
                    st.session_state.current_session["chat_history"].extend([user_message, assistant_message])
                    st.session_state.current_session["past"].append(insecure_code)
                    st.session_state.current_session["generated"].append(answer)
                    st.session_state.buffer_memory.save_context({"insecure_code": insecure_code}, {"response": answer})

                    # Display the file name and AI response
                    with st.chat_message("user"):
                        st.markdown(f"File: {file}\n```\n{insecure_code}\n```")
                    with st.chat_message("assistant"):
                        st.markdown(f"```\n{answer}\n```")

    except Exception as e:
        logging.error(f"Error while analyzing GitHub repo: {e}")
        st.error("Failed to analyze the GitHub repository. Please check the URL and try again.")
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

# Main function to run the Streamlit app
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
    if st.button("Analyze GitHub Repository"):
        if github_repo_url:
            analyze_github_repo(github_repo_url)
        else:
            st.error("Please enter a valid GitHub repository URL.")

if __name__ == "__main__":
    main()
