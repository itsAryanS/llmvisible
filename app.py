import streamlit as st
import requests, json

# — Page Config —
st.set_page_config(page_title="LLMVisible GEO Analyzer", layout="centered")
st.title("🛠️ LLMVisible GEO Analyzer")

# — Secrets —
GROQ_API_KEY   = st.secrets.get("GROQ_API_KEY")
SERPAPI_API_KEY= st.secrets.get("SERPAPI_API_KEY")

# — Tabs —
tab1, tab2 = st.tabs(["🔍 GEO Analyzer", "🧑‍💼 GEO Expert Advice"])

# --- Tab 1: GEO Analyzer ---
with tab1:
    st.header("Step 1: Analyze Your Domain & Brand")
    domain = st.text_input("Domain (optional)", placeholder="example.com")
    brand  = st.text_input("Brand name", placeholder="LLMVisible")
    if st.button("Run GEO Analysis"):
        # Google SERP via SerpApi
        google_results = []
        if domain:
            if not SERPAPI_API_KEY:
                st.error("🔒 Set SERPAPI_API_KEY in Settings → Secrets")
            else:
                params = {
                    "engine": "google",
                    "q": f"site:{domain}",
                    "api_key": SERPAPI_API_KEY,
                }
                resp = requests.get("https://serpapi.com/search", params=params)
                if resp.ok:
                    data = resp.json().get("organic_results", [])[:5]
                    for r in data:
                        google_results.append({
                            "title":   r.get("title"),
                            "link":    r.get("link"),
                            "snippet": r.get("snippet"),
                        })
                else:
                    st.error("❌ SerpApi error: " + resp.text)

        # Display Google results
        if google_results:
            st.subheader("🔎 Google Top 5 Results")
            for item in google_results:
                st.markdown(f"- [{item['title']}]({item['link']})  \n  {item['snippet']}")
        else:
            st.info("No Google data (provide domain & SerpApi key)")

        # LLM Brand Description via Groq
        llm_output = ""
        if not brand:
            st.error("Enter your brand name for LLM analysis")
        elif not GROQ_API_KEY:
            st.error("🔒 Set GROQ_API_KEY in Settings → Secrets")
        else:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": f"What is {brand}? Provide a concise description."}]
            }
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, data=json.dumps(payload)
            )
            if r.ok:
                llm_output = r.json()["choices"][0]["message"]["content"]
                st.subheader("🤖 LLM Brand Description")
                st.write(llm_output)
            else:
                st.error("❌ Groq error: " + r.text)

        # Save to session for Tab 2
        st.session_state.google_results = google_results
        st.session_state.llm_output     = llm_output

# --- Tab 2: GEO Expert Advice ---
with tab2:
    st.header("Step 2: GEO Expert Advice")
    if not st.session_state.get("llm_output"):
        st.info("Run the GEO Analysis in Tab 1 first")
    else:
        if st.button("Generate GEO Advice"):
            google_results = st.session_state.get("google_results", [])
            llm_output     = st.session_state.get("llm_output", "")

            # Build expert prompt
            advice_prompt = f"""
You are a PhD-level Generative Engine Optimization (GEO) expert consulting a business owner.
Domain: {domain}
Brand: {brand}

Top 5 Google results (title, link, snippet):
{json.dumps(google_results, indent=2)}

LLM Output:
{llm_output}

Provide detailed, actionable suggestions and strategic advice covering:
- Why GEO is critical
- Content structure & schema
- Technical SEO for AI
- Authority & citations (E-E-A-T)
- Distribution & PR
- Monitoring & iteration
- Any other GEO best practices
Format as a clear, bullet-pointed advisory report.
"""

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": advice_prompt}]
            }
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, data=json.dumps(payload)
            )
            if r.ok:
                advice = r.json()["choices"][0]["message"]["content"]
                st.markdown("### 📋 GEO Expert Report")
                st.write(advice)
            else:
                st.error("❌ Groq error: " + r.text)
