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
            # Craft an expert-level GEO prompt focusing purely on LLM visibility
            expert_prompt = f"""
You are a PhD-level Generative Engine Optimization (GEO) expert. Analyze the following LLM and DuckDuckGo findings for brand '{data['brand']}' on prompt '{data['prompt']}':

LLM findings:
{data['llm_response']}
Brand present in LLM: {data['llm_found']}

DuckDuckGo Prompt URLs:
{json.dumps([r['href'] for r in data['ddg_prompt_results']], indent=2)}
Brand in Prompt URLs: {data['ddg_prompt_found']}

DuckDuckGo Brand/Domain URLs:
{json.dumps([r['href'] for r in data['ddg_brand_results']], indent=2)}
Brand in Brand URLs: {data['ddg_brand_found']}
Pre-Optimization GEO Score: {data['geo_score']}%

As a GEO expert, provide:

1. **LLM Prompt Strategy**: Three advanced prompt-engineering techniques to surface the brand in LLM responses, with concrete examples.
2. **RAG Integration**: Three methods to incorporate brand-specific documents into retrieval-augmented pipelines (e.g., embeddings, vector DB usage, selective chunking).
3. **Custom LLM Plugins/APIs**: Three illustrative examples of API endpoints or plugin actions that expose brand data to an LLM at query time.
4. **Contextual Memory & Fine-Tuning**: Three approaches to fine-tune or cache context (e.g., embeddings-based memory, user persona injection, dynamic context windows).
5. **Evaluation & Iteration**: Three metrics (e.g., hit rate, brand mention frequency, response relevance) and three tools/techniques for monitoring LLM visibility over time.

Finally, forecast the **post-optimization GEO Score** based on implementing these tactics, with rationale for each improvement area.
"""
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": expert_prompt} ]}
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=30)
                r.raise_for_status()
                report = r.json()["choices"][0]["message"]["content"]
                st.markdown("### 📋 GEO Expert Advisory Report")
                st.write(report)
            except Exception as e:
                st.error(f"Groq API Error: {e}")
