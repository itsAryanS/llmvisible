import streamlit as st
import requests
import json

# — Page Configuration —
st.set_page_config(page_title="LLMVisible.com", layout="centered")
st.title("🤖 LLMVisible.com – Be Seen by AI")

# — Load API Key from Secrets —
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# — Create Tabs —
tab1, tab2 = st.tabs(["🔍 Prompt Tester", "✍️ Ultra-GEO Content Generator"])

# — Tab 1: Prompt Tester —
with tab1:
    st.header("🔍 Test Brand Visibility in LLM Responses")
    prompt = st.text_input("Enter a user prompt (e.g., 'Best AI resume tools')", key="prompt1")
    brand = st.text_input("Your brand name (e.g., LLMVisible)", key="brand1")

    if st.button("Run Prompt Test"):
        if not GROQ_API_KEY:
            st.warning("Groq API key missing. Add it under Settings → Secrets.")
        else:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}]
            }
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            if r.status_code == 200:
                reply = r.json()["choices"][0]["message"]["content"]
                st.subheader("🧠 Groq Response")
                st.write(reply)
                if brand.lower() in reply.lower():
                    st.success(f"✅ Your brand '{brand}' was mentioned!")
                else:
                    st.error(f"❌ '{brand}' not found in the response.")
            else:
                st.error(f"Groq API Error: {r.text}")

# — Tab 2: Ultra-GEO Content Generator —
with tab2:
    st.header("✍️ Generate Full GEO Playbook")

    desc = st.text_area(
        "Describe your product/service",
        placeholder="e.g., 'An AI resume builder for students'",
        height=120
    )
    keyword = st.text_input("Primary SEO keyword", placeholder="e.g., 'AI resume builder'")

    if st.button("Generate GEO Playbook"):
        if not GROQ_API_KEY:
            st.warning("Groq API key missing. Add it under Settings → Secrets.")
        else:
            geo_prompt = f"""
You are a top Generative Engine Optimization (GEO) expert. For this service:
\"\"\"{desc}\"\"\"
and the target keyword: "{keyword}", generate the following in markdown:

1. **3–5 SEO-Friendly Blog Titles** (<60 chars) with the keyword.
2. **Meta Tags**: <title> and <meta name="description"> optimized for AI snippets.
3. **URL Slug Suggestions**: 2–3 concise, keyword-rich paths.
4. **Content Outline**: H2/H3 headings with suggested word counts.
5. **5–7 FAQs** formatted as JSON-LD for schema.org/FAQPage.
6. **Why Choose Us?**: 4–6 bullet-point value propositions.
7. **3–5 CTAs** tailored for conversational AI.
8. **Linking Plan**: 3 internal pages + 2 external authority references.
9. **Image Ideas & Alt Text** for 2–3 images.
10. **Social Preview**: Open Graph & Twitter tags + 2 sample social posts.
11. **Breadcrumb JSON-LD** block.
12. **Organization JSON-LD** block.
13. **2–3 Snippet Teasers** (40–50 words each).
14. **Competitor Comparison**: Markdown table vs. 2–3 competitors.
15. **Schema.org Checklist**: bullet list of additional schemas.
16. **GEO Best Practices**: bullet summary of research, E-E-A-T, schema, tech SEO, PR, iteration, and AI tools.
"""
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": geo_prompt}]
            }
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            if r.status_code == 200:
                output = r.json()["choices"][0]["message"]["content"]
                st.markdown("### 🏆 Ultra-GEO Playbook")
                st.write(output)
            else:
                st.error(f"Groq API Error: {r.text}")
