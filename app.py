import streamlit as st
import requests
import json

st.set_page_config(page_title="LLMVisible.com", layout="centered")
st.title("🤖 LLMVisible.com – Be Seen by AI!")

tab1, tab2 = st.tabs(["🔍 Prompt Tester", "AI Content Generator"])
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# --- TAB 1: Prompt Tester ---
with tab1:
    st.header("Check if your brand appears in LLM answers")

    prompt = st.text_input("Enter a prompt a user might type (e.g., 'Best resume tools')", key="prompt1")
    brand = st.text_input("Your brand name (e.g., LLMVisible)", key="brand1")

    if st.button("Run Test (Groq)"):
        if not GROQ_API_KEY:
            st.warning("API key missing. Set it in Streamlit secrets.")
        else:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}]
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload))
            if r.status_code == 200:
                reply = r.json()['choices'][0]['message']['content']
                st.subheader("🤖 Groq Response:")
                st.write(reply)
                if brand.lower() in reply.lower():
                    st.success(f"Brand '{brand}' was mentioned!")
                else:
                    st.error(f"Brand '{brand}' not found.")
            else:
                st.error(f"Groq API Error: {r.text}")

# --- TAB 2: Content Generator ---
with tab2:
    st.header("Create LLM-friendly Content")

    desc = st.text_area("Describe your product (e.g., 'An AI resume builder for students')")

    if st.button("Generate Content (Groq)"):
        if not GROQ_API_KEY:
            st.warning("API key missing.")
        else:
            content_prompt = f"""
You're an expert in LLM SEO. Based on this product: {desc}
1. Give 3 blog titles ChatGPT/Groq might mention
2. Give 2 FAQ questions and answers
3. Write a 2-sentence ChatGPT-style product description
"""
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": content_prompt}]
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload))
            if r.status_code == 200:
                reply = r.json()['choices'][0]['message']['content']
                st.markdown("### AI-Generated Content:")
                st.write(reply)
            else:
                st.error(f"Groq API Error: {r.text}")
