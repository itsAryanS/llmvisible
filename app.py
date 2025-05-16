import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

# ------------------ DuckDuckGo HTML Search ------------------ #
def duckduckgo_search(query, max_results=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"q": query}
    try:
        response = requests.get("https://html.duckduckgo.com/html/", headers=headers, params=params, timeout=5)
        response.raise_for_status()
    except Exception as e:
        st.warning(f"DuckDuckGo request failed: {e}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for a in soup.find_all("a", class_="result__a", limit=max_results):
        title = a.get_text()
        href = a.get("href", "")
        snippet_tag = a.find_parent("div", class_="result__body").find("a", class_="result__snippet")
        snippet = snippet_tag.get_text() if snippet_tag else ""
        results.append({"title": title, "href": href, "snippet": snippet})
    return results

# ------------------ Streamlit UI ------------------ #
st.set_page_config(page_title="LLMVisible GEO Analyzer", layout="centered")
st.title("🛠️ LLMVisible.com – Free GEO Analyzer & Advisor")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Create tabs
tab1, tab2 = st.tabs(["🔍 Prompt & Brand Tester", "🧑‍💼 GEO Expert Advice"])

# ------------------ Tab 1: Prompt Testing ------------------ #
with tab1:
    st.header("Step 1: Check Visibility in LLMs & DuckDuckGo")
    prompt = st.text_input("Prompt to test (e.g. Best CRM tools):", key="prompt")
    brand = st.text_input("Your Brand Name:", key="brand")
    domain = st.text_input("Your Website (optional):", key="domain")

    if st.button("Run GEO Analysis"):
        # Initialize
        llm_response = ""
        llm_found = False
        ddg_prompt_results = []
        ddg_brand_results = []
        ddg_prompt_found = False
        ddg_brand_found = False

        # 1. LLM Check with Groq
        if GROQ_API_KEY:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt} ]}
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=10)
                r.raise_for_status()
                llm_response = r.json()["choices"][0]["message"]["content"]
                llm_found = brand.lower() in llm_response.lower()
            except Exception as e:
                st.error(f"Groq API Error: {e}")
        else:
            st.error("Missing GROQ_API_KEY. Add it under Settings → Secrets.")

        # 2. DuckDuckGo Prompt Search
        ddg_prompt_results = duckduckgo_search(prompt)
        ddg_prompt_found = any(brand.lower() in (res["title"] + res["snippet"]).lower() for res in ddg_prompt_results)

        # 3. DuckDuckGo Brand/Domain Search
        search_term = f"site:{domain}" if domain else brand
        ddg_brand_results = duckduckgo_search(search_term)
        ddg_brand_found = any(brand.lower() in (res["title"] + res["snippet"]).lower() for res in ddg_brand_results)

        # 4. Compute Geo Score
        checks = [llm_found, ddg_prompt_found, ddg_brand_found]
        geo_score = round((sum(checks) / len(checks)) * 100, 2)

        # Display
        st.subheader("🧠 LLM (Groq) Response")
        st.write(llm_response)
        if llm_found:
            st.success("✅ Brand found in LLM response")
        else:
            st.error("❌ Brand NOT found in LLM response")

        st.subheader("🔍 DuckDuckGo Prompt Results")
        for res in ddg_prompt_results:
            st.markdown(f"- [{res['title']}]({res['href']})  \n  {res['snippet']}")
        if ddg_prompt_found:
            st.success("✅ Brand found in Prompt results")
        else:
            st.error("❌ Brand NOT in Prompt results")

        st.subheader("🌐 DuckDuckGo Brand/Domain Results")
        for res in ddg_brand_results:
            st.markdown(f"- [{res['title']}]({res['href']})  \n  {res['snippet']}")
        if ddg_brand_found:
            st.success("✅ Brand found in Brand/Domain results")
        else:
            st.error("❌ Brand NOT in Brand/Domain results")

        st.markdown(f"## 📊 Pre-Optimization GEO Score: **{geo_score}%**")

        # Save analysis for Tab 2
        st.session_state.analysis = {
            "prompt": prompt,
            "brand": brand,
            "domain": domain,
            "llm_response": llm_response,
            "llm_found": llm_found,
            "ddg_prompt_results": ddg_prompt_results,
            "ddg_brand_results": ddg_brand_results,
            "ddg_prompt_found": ddg_prompt_found,
            "ddg_brand_found": ddg_brand_found,
            "geo_score": geo_score
        }

# ------------------ Tab 2: GEO Expert ------------------ #
with tab2:
    st.header("Step 2: PhD-Level GEO Expert Advice & Forecast")
    data = st.session_state.get("analysis")
    if not data:
        st.info("Please complete the analysis in Tab 1 first.")
    else:
        if st.button("Get Expert GEO Advice"):
            expert_prompt = f"""
You are the world's leading Generative Engine Optimization (GEO) expert. You’ve authored PhDs and real-world handbooks on how to appear in AI-generated answers from LLMs. Using Tab 1 results below, perform an in-depth expert analysis.

PROMPT: {data['prompt']}
BRAND: {data['brand']}
DOMAIN: {data['domain']}
GEO SCORE: {data['geo_score']}%

LLM Response:
{data['llm_response']}
Brand present in LLM: {data['llm_found']}
DuckDuckGo prompt visibility: {data['ddg_prompt_found']}
DuckDuckGo brand/domain visibility: {data['ddg_brand_found']}

INSTRUCTIONS:
Please analyze:
1. Why this brand did/didn't appear in the LLM response. Use content from the LLM to explain it.
2. Give deep, GEO-specific advice to make it appear in LLMs. Do not talk about SEO. Go into strategies like:
   - Entity injection via embeddings, schema context, or fine-tuned RAG
   - Systematic prompt-style alignment with what LLMs are likely trained on
   - Data distribution to LLM training surfaces like Reddit, Wikipedia, Medium
   - Feed-forward citation embedding methods to push citations in.

STRUCTURE OUTPUT INTO THE FOLLOWING SECTIONS:

### 1. LLM Visibility Diagnosis
- Explain why the brand appeared or didn't in the LLM
- Reference text snippets from the LLM response

### 2. Prompt Engineering Optimization
- Suggest 3 expert ways to format prompts so LLMs pull in the brand
- Give 3 examples

### 3. Embedding-RAG Optimization
- Recommend 3 ways to embed the brand in vector DB / knowledge stores
- Give 3 real-world examples (like LangChain, Haystack, Pinecone)

### 4. Content Injection to LLM Surfaces
- Identify 3 platforms where content should be seeded for long-term LLM ingestion
- Give content format + example per platform (e.g. Reddit AMA, Wikipedia stub)

### 5. Plugin / API Feed Strategy
- Give 3 plugin or API data exposure ideas that LLMs can call live
- Use realistic endpoint naming

### 6. Memory or Tool Bias Strategy
- Give 3 examples of how to bias memory/context (e.g. assistant memory, tool-use triggers)

### 7. Monitoring & GEO Score Forecasting
- Recommend 3 metrics (brand recall rate, LLM citation %, prompt hit rate)
- Forecast post-optimization GEO score and explain why it increased

BE SPECIFIC. BE IN-DEPTH. DO NOT GIVE SEO TIPS. THIS IS PURE GEO.
"""
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": expert_prompt}]}
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=30)
                r.raise_for_status()
                report = r.json()["choices"][0]["message"]["content"]
                st.markdown("### 📋 GEO Expert Advisory Report")
                st.markdown(report)
            except Exception as e:
                st.error(f"Groq API Error: {e}")
