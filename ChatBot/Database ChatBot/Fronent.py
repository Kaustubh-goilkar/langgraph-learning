import streamlit as st
from Backend import chatBotWorkflow,retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# Initialize global history (though session_state is used for persistence across reruns)
message_history = []

def generate_threadId():
    """Generates a unique ID to track separate conversation sessions in LangGraph's checkpointer."""
    thread_id = uuid.uuid4()
    if 'threads' not in st.session_state:
        st.session_state['threads'] = retrieve_all_threads()

    st.session_state['threads'].append(thread_id)
    return thread_id

def reset_Messages():
    """Clears the current chat display history when starting a new session."""
    st.session_state['message_history'] = []

def load_chatConverSession(thread_id):
    """
    Fetches historical messages from the LangGraph persistent checkpointer 
    using a specific thread_id.
    """
    st.session_state['thread_id'] = thread_id
    config = { 'configurable': {'thread_id': st.session_state['thread_id']} }

    # Defensive check: Access state safely using .get() to avoid KeyErrors on new threads
    state_values = chatBotWorkflow.get_state(config=config).values
    messages = state_values.get('messages', [])
    
    temp_messages = []
    for message in messages:
        # Map LangChain message classes back to Streamlit-friendly roles ('user'/'assistant')
        if isinstance(message, HumanMessage):
            role = 'user'
        else:
            role = 'assistant'
        temp_messages.append(
            {
                'role': role,
                'content': message.content
            }
        )
    return temp_messages

# --- Session State Initialization ---
# Ensures that variables persist even when Streamlit reruns the script on every interaction
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_threadId()


# --- Sidebar UI ---
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    st.session_state['thread_id'] = generate_threadId()
    reset_Messages()

st.sidebar.header('My Conversation')

# Render dynamic buttons for previous chat threads
for thread_id in st.session_state['threads']:
    if st.sidebar.button(str(thread_id)):
        # Switch the current context to an old thread and load its history
        st.session_state['message_history'] = load_chatConverSession(thread_id=thread_id)


# --- Chat Interface ---
# Display all existing messages in the current session state
for messsage in st.session_state['message_history']:
    with st.chat_message(messsage['role']):
        st.markdown(messsage['content'])

user_input = st.chat_input('Type here')

if user_input:
    # 1. Update UI and Session State with User Input
    st.session_state['message_history'].append(
        {'role': 'user', 'content': user_input}
    )
    with st.chat_message('user'):
        st.text(user_input)

    # 2. Configure the LangGraph run with the current thread ID for persistence
    config = { 'configurable': {'thread_id': st.session_state['thread_id']} }

    # 3. Stream AI response from LangGraph
    # We use stream_mode="messages" to get real-time token chunks for a "typing" effect
    with st.chat_message('assistant'):
       AI_response = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatBotWorkflow.stream(
                {'messages': [HumanMessage(user_input)]}, 
                config=config, 
                stream_mode="messages"
            )
        )

    # 4. Finalize history for this session so it persists on next rerun
    st.session_state['message_history'].append(
        {'role': 'assistant', 'content': AI_response}
    )