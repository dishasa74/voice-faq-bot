import os
import tempfile
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Voice FAQ Bot", layout="centered")

st.title("Voice FAQ Bot")
st.write("Ask a question using your voice and get an AI-powered answer.")

FAQ_CONTEXT = """
This is a demo FAQ bot for a college tech club.

Frequently asked questions:

1. What is the club?
Answer: The club is a student community focused on technology, projects, workshops and peer learning.

2. How can I join the club?
Answer: Students can join by filling out the club registration form or contacting the club coordinator.

3. Are workshops free?
Answer: Most student workshops are free. Any paid event will clearly mention its fee before registration.

4. Can beginners join?
Answer: Yes. Beginners are welcome and can learn through workshops, projects and peer support.

5. How can I contact the club?
Answer: Students can contact the club coordinator through the official college communication channel.
"""

api_key = st.text_input(
    "Gemini API Key",
    type="password",
    help="Do not publish your API key on GitHub."
)

audio = st.audio_input("Record your question")

if audio:
    st.audio(audio)

    if not api_key:
        st.warning("Please enter your Gemini API key.")
    else:
        audio_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio.getvalue())
                audio_path = tmp.name

            client = genai.Client(api_key=api_key)
            uploaded_file = client.files.upload(file=audio_path)

            prompt = f"""
You are a helpful Voice FAQ Bot.

Understand the user's spoken question from the attached audio.
Then answer ONLY using the FAQ information below.

If the answer is not available in the FAQ, say:
"Sorry, I don't have that information in my FAQ."

Keep the answer short, clear and friendly.

FAQ:
{FAQ_CONTEXT}
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=uploaded_file.mime_type
                    ),
                    prompt
                ]
            )

            st.subheader("AI Answer")
            st.success(response.text)

        except Exception as error:
            st.error("Something went wrong while processing the voice input.")
            st.code(str(error))

        finally:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

st.divider()
st.caption("Built with Python, Streamlit and Google Gemini API.")
