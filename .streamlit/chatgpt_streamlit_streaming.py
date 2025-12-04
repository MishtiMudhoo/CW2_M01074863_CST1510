import	streamlit	as	st 
from	openai	import	OpenAI 
	 
#	Initialize	OpenAI	client 
client	=	OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) 
	 
#	Page	configuration 
st.set_page_config( 
				page_title="ChatGPT	Assistant", 
				page_icon="💬", 
				layout="wide" 
) 
	 
#	Title 
st.title("💬	ChatGPT	-	OpenAI	API") 
st.caption("Powered	by	GPT-4o") 
	 
#	Initialize	session	state 
if	'messages'	not	in	st.session_state: 
				st.session_state.messages	=	[] 
	 
#	Sidebar	with	controls 
with	st.sidebar: 
				st.subheader("Chat	Controls") 
				 
				#	Display	message	count 
				message_count	=	len([m	for	m	in	st.session_state.messages	if	m["role"]	!=	"system"]) 
				st.metric("Messages",	message_count) 
				 
				#	Clear	chat	button 
				if	st.button("🗑	Clear	Chat",	use_container_width=True): 
								st.session_state.messages	=	[] 
								st.rerun() 
				 
				#	Model	selection 
				model	=	st.selectbox( 
								"Model", 
								["gpt-4o",	"gpt-4o-mini"], 
								index=0 
				) 
				 
				#	Temperature	slider 
				temperature	=	st.slider( 
								"Temperature", 
								min_value=0.0, 
								max_value=2.0, 
								value=1.0, 
								step=0.1, 
								help="Higher	values	make	output	more	random" 
				) 
	 
#	Display	all	previous	messages 
for	message	in	st.session_state.messages: 
				with	st.chat_message(message["role"]): 
								st.markdown(message["content"]) 
	 
#	Get	user	input 
prompt	=	st.chat_input("Say	something...") 
	 
if	prompt: 
				#	Display	user	message 
				with	st.chat_message("user"): 
								st.markdown(prompt) 
				 
				#	Add	user	message	to	session	state 
				st.session_state.messages.append({ 
								"role":	"user", 
								"content":	prompt 
				}) 
				 
				#	Call	OpenAI	API	with	streaming 
				with	st.spinner("Thinking..."): 
								completion	=	client.chat.completions.create( 
												model=model, 
												messages=st.session_state.messages, 
												temperature=temperature, 
												stream=True 
								) 
				 
				#	Display	streaming	response 
				with	st.chat_message("assistant"): 
								container	=	st.empty() 
								full_reply	=	"" 
								 
								for	chunk	in	completion: 
												delta	=	chunk.choices[0].delta 
												if	delta.content: 
																full_reply	+=	delta.content 
																container.markdown(full_reply	+	"▌")		#	Add	cursor	effect 
								 
								#	Remove	cursor	and	show	final	response 
								container.markdown(full_reply) 
				 
				#	Save	assistant	response 
				st.session_state.messages.append({ 
"role":	"assistant", 
"content":	full_reply 
})