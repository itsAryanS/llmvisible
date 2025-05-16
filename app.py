import streamlit as st
import requests
import json
from duckduckgo_search import ddg

# --- Page Configuration ---
st.set_page_config(page_title="LLMVisible GEO Analyzer", layout="centered")
st.title("🛠️ LLMVisible.com – Free GEO Analyzer & Advisor")

# --- Load Groq API Key from Secrets ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# --- Tabs ---
tab1, tab2 = st.tabs(["🔍 Prompt & Brand Tester", "🧑‍💼 GEO Expert Advice"])

# --- Tab 1: Prompt & Brand Tester ---
with tab1:
    st.header("Step 1: Test Prompt and Brand Visibility")
    prompt = st.text_input("Enter a user prompt:", placeholder="Best CRM tools for small business")
    brand = st.text_input("Enter your brand/business name:", placeholder="MyBrand")
    domain = st.text_input("Enter your domain (optional):", placeholder="example.com")

    if st.button("Run Analysis"):
        # Containers
        llm_responses = {}
        llm_presence = {}

        # 1) Groq LLM Check (Free)
        if not GROQ_API_KEY:
            st.error("⚠️ Please set GROQ_API_KEY in Settings → Secrets.")
        else:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}]}
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                llm_responses['Groq'] = text
                llm_presence['Groq'] = brand.lower() in text.lower()
            else:
                st.error(f"Groq API Error: {r.text}")

        # 2) DuckDuckGo Search for Prompt (Free)
        ddg_prompt_results = ddg(prompt, max_results=5) or []
        ddg_prompt_presence = any(
            brand.lower() in ((res.get('title','') + res.get('body','')).lower())
            for res in ddg_prompt_results
        )

        # 3) DuckDuckGo Search for Brand/Domain (Free)
        query = f"site:{domain}" if domain else brand
        ddg_brand_results = ddg(query, max_results=5) or []
        ddg_brand_presence = any(
            brand.lower() in ((res.get('title','') + res.get('body','')).lower())
            for res in ddg_brand_results
        )

        # Compute Geo Score: checks = Groq + prompt search + brand search
        checks = []
        if 'Groq' in llm_presence:
            checks.append(llm_presence['Groq'])
        checks.append(ddg_prompt_presence)
        checks.append(ddg_brand_presence)
        geo_score = round((sum(checks) / len(checks)) * 100, 2) if checks else 0

        # Display LLM Results
        st.subheader("🤖 Groq LLM Response & Presence")
        if 'Groq' in llm_responses:
            st.write(llm_responses['Groq'])
            st.write("✅ Brand found" if llm_presence['Groq'] else "❌ Brand not found")

        # Display DuckDuckGo Prompt Results
        st.subheader("🔍 DuckDuckGo Search for Prompt")
        for res in ddg_prompt_results:
            st.markdown(f"- [{res['title']}]({res['href']})")
        st.write("✅ Brand in top prompt results" if ddg_prompt_presence else "❌ Brand not in prompt results")

        # Display DuckDuckGo Brand/Domain Results
        st.subheader("🌐 DuckDuckGo Search for Brand/Domain")
        for res in ddg_brand_results:
            st.markdown(f"- [{res['title']}]({res['href']})")
        st.write("✅ Brand found in brand/domain results" if ddg_brand_presence else "❌ Brand not found in brand/domain results")

        # Display Geo Score
        st.markdown(f"## 📊 Pre-Optimization Geo Score: **{geo_score}%**")

        # Store analysis for Tab 2
        st.session_state.analysis = {
            'prompt': prompt,
            'brand': brand,
            'domain': domain,
            'llm_response': llm_responses.get('Groq',''),
            'llm_presence': llm_presence.get('Groq', False),
            'ddg_prompt_presence': ddg_prompt_presence,
            'ddg_brand_presence': ddg_brand_presence,
            'geo_score': geo_score
        }

# --- Tab 2: GEO Expert Advice ---
with tab2:
    st.header("Step 2: PhD-Level GEO Expert Advice & Forecast")
    data = st.session_state.get('analysis')
    if not data:
        st.info("Run Step 1 in Tab 1 to get analysis data first.")
    else:
        if st.button("Generate GEO Expert Advice"):
            advice_prompt = f"""
You are a PhD-level expert in Generative Engine Optimization (GEO). Analyze the following:

Prompt: {data['prompt']}
Brand: {data['brand']}
Domain: {data['domain'] or 'N/A'}

Groq LLM Presence: {data['llm_presence']}
DuckDuckGo Prompt Presence: {data['ddg_prompt_presence']}
DuckDuckGo Brand/Domain Presence: {data['ddg_brand_presence']}
Pre-Optimization Geo Score: {data['geo_score']}%

Provide:
1. Why GEO matters for this business.
2. Deep, actionable recommendations on content structure, schema markup, citations, distribution, technical SEO for AI, and monitoring.
3. A clear checklist of immediate actions.
4. An honest forecast of the Geo Score after implementing these suggestions.

Format as a structured advisory report with headings and bullet points.
"""
            if not GROQ_API_KEY:
                st.error("⚠️ Set your GROQ_API_KEY in Settings → Secrets.")
            else:
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                payload = {"model": "llama3-70b-8192", "messages":[{"role":"user","content":advice_prompt}]}                
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload))
                if r.status_code == 200:
                    report = r.json()["choices"][0]["message"]["content"]
                    st.markdown("### 📋 GEO Expert Advisory Report")
                    st.write(report)
                else:
                    st.error(f"Groq API Error: {r.text}")
