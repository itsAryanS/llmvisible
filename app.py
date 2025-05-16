import streamlit as st
import requests
import json

st.set_page_config(page_title="LLMVisible.com", layout="centered")
st.title("🤖 LLMVisible.com – Be Seen by AI")

tab1, tab2 = st.tabs(["🔍 Prompt Tester", "✍️ AI Content Generator"])
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# ---------------- TAB 1: Prompt Tester ---------------- #
with tab1:
    st.header("🔍 Test if your brand appears in LLM responses")

    prompt = st.text_input("Enter a ChatGPT-like prompt (e.g. 'Best AI tools for students')", key="prompt1")
    brand = st.text_input("Your brand name (e.g. LLMVisible)", key="brand1")

    if st.button("Run Prompt Test"):
        if not GROQ_API_KEY:
            st.warning("Groq API key missing. Set it in Streamlit Cloud > Secrets.")
        else:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",  # ✅ RECOMMENDED by Groq (as of May 2025)
                "messages": [{"role": "user", "content": prompt}]
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers=headers, data=json.dumps(payload))
            if r.status_code == 200:
                reply = r.json()['choices'][0]['message']['content']
                st.subheader("🧠 Groq (LLaMA 3) Response")
                st.write(reply)
                if brand.lower() in reply.lower():
                    st.success(f"✅ Yes! Your brand '{brand}' was mentioned.")
                else:
                    st.error(f"❌ No mention of '{brand}' in this response.")
            else:
                st.error(f"Groq API Error: {r.text}")

# ---------------- TAB 2: Content Generator ---------------- #
with tab2:
    st.header("✍️ Generate LLM-optimized content")

    desc = st.text_area("Describe your service (e.g., 'an AI tool that helps students build resumes')")
    if st.button("Generate Content"):
        if not GROQ_API_KEY:
            st.warning("Groq API key missing. Set it in Streamlit Cloud > Secrets.")
        else:
            content_prompt = f"""
You are an LLM-focused SEO content expert. Given the following product: "{desc}", do the following:
1. Suggest 3 blog titles ChatGPT or Groq might mention in answers.
2. Give 2 FAQ questions with short, helpful answers.
3. Write a 2-sentence blurb ChatGPT might generate when asked about this product.
"""
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": content_prompt}]
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers=headers, data=json.dumps(payload))
            if r.status_code == 200:
                reply = r.json()['choices'][0]['message']['content']
                st.markdown("### 🧠 AI-Generated Content")
                st.write(reply)
            else:
                st.error(f"Groq API Error: {r.text}")
