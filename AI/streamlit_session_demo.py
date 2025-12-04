import	streamlit	as	st 
	 
st.title("Chat	History	with	Session	State") 
	 
#	Initialize	session	state	for	messages 
if	'messages'	not	in	st.session_state: 
				st.session_state.messages	=	[] 
	 
#	Display	all	historical	messages 
for	message	in	st.session_state.messages: 
				with	st.chat_message(message["role"]): 
								st.markdown(message["content"]) 
	 
#	Get	user	input 
prompt	=	st.chat_input("Say	something...") 
	 
if	prompt: 
				#	Save	user	message 
				st.session_state.messages.append({ 
								"role":	"user", 
								"content":	prompt 
				}) 
				 
				#	Display	user	message 
with	st.chat_message("user"): st.markdown(prompt) 
#	Simulate	AI	response	(we'll	replace	this	with	real	API	call	later) 
ai_response	=	f"You	said:	{prompt}" 
#	Save	AI	response 
st.session_state.messages.append({ 
"role":	"assistant", 
"content":	ai_response
}) 
#	Display	AI	response 
with	st.chat_message("assistant"): st.markdown(ai_response) 