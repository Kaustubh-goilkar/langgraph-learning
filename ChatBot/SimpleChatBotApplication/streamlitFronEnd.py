import streamlit as st
from langraphBackend import chatBotWorkflow
from langchain_core.messages import HumanMessage


message_history = []
# Whenever the user clicks on send message or presses enter, the entire Python script is executed again.
# If the code executes again, all variables are reset to their initial state. In this case, 'message_history' would reset to an empty list '[]'.
# To avoid this data loss, we are using 'session_state', which will keep the data safe between runs.
# Note: When you click the browser's reload button, the 'session_state' also resets to its original empty state.
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'configuration' not in st.session_state:
    st.session_state['configuration'] = { 'configurable':{'thread_id': '1'} }



for messsage in st.session_state['message_history']:
    with st.chat_message(messsage['role']):
        st.markdown(messsage['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append(
        {'role':'user', 'content':user_input}
    )
    with st.chat_message('user'):
        st.text(user_input)

    config = st.session_state['configuration']
    # Without Streming
    # result = chatBotWorkflow.invoke({'messages':[HumanMessage(user_input)]},config=config)
    # content =  result['messages'][-1].content

    # st.session_state['message_history'].append(
    #     {'role':'assistant', 'content':content}
    # )
    # with st.chat_message('assistant'):
    #     st.markdown(content)

    # Stream Message
    with st.chat_message('assistant'):
       AI_response =  st.write_stream(
            message_chunk.content for message_chunk,metadata in chatBotWorkflow.stream({'messages':[HumanMessage(user_input)]},config=config,stream_mode="messages")
        )

    st.session_state['message_history'].append(
        {'role':'assistant', 'content':AI_response}
    )
   

    

    
    
    
