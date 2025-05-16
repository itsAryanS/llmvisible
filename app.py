import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

# ------------------ DuckDuckGo HTML Search ------------------ #
def duckduckgo_search(query, max_results=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"q": query}
    response = requests.get("https://html.duckduckgo.com/html/", headers=headers, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for a in soup.find_all("a", class_="result__a", limit=max_results):
        title = a.get_text()
        href = a["href"]
        snippet_tag = a.find_parent("div", class_="result__body").find("a", class_="result__snippet")
        snippet = snippet_tag.get_text() if snippet_tag else ""
        results.append({"title": title, "href": href, "snippet": snippet})
    return results

# ------------------ Streamlit UI ------------------ #
st.set_page_config(page_title="LLMVisible GEO Analyzer", layout="centered")
st.title("🛠️ LLMVisible.com – Free GEO Analyzer & Advisor")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

tab1, tab2 = st.tabs(["🔍 Prompt & Brand Tester", "🧑‍💼 GEO Expert Advice"])

# ------------------ Tab 1: Prompt Testing ------------------ #
with tab1:
    st.header("Step 1: Check Visibility in LLMs & DuckDuckGo")
    prompt = st.text_input("Prompt to test (e.g. Best CRM tools)", key="prompt")
    brand = st.text_input("Your Brand Name", key="brand")
    domain = st.text_input("Your Website (optional)", key="domain")

    if st.button("Run GEO Analysis"):
        llm_response = ""
        llm_found = False
        ddg_prompt_results = []
        ddg_brand_results = []
        ddg_prompt_found = False
        ddg_brand_found = False

        # 1. LLM Check with Groq
        if GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}]
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload))
            if r.ok:
                llm_response = r.json()["choices"][0]["message"]["content"]
                llm_found = brand.lower() in llm_response.lower()
            else:
                st.error("Groq API Error: " + r.text)
        else:
            st.error("Missing GROQ_API_KEY. Add it in Streamlit > Settings > Secrets.")

        # 2. DuckDuckGo Prompt Search
        try:
            ddg_prompt_results = duckduckgo_search(prompt)
            ddg_prompt_found = any(brand.lower() in (r["title"] + r["snippet"]).lower() for r in ddg_prompt_results)
        except Exception as e:
            st.warning(f"DuckDuckGo prompt search failed: {e}")

        # 3. DuckDuckGo Brand/Domain Search
        search_term = f"site:{domain}" if domain else brand
        try:
            ddg_brand_results = duckduckgo_search(search_term)
            ddg_brand_found = any(brand.lower() in (r["title"] + r["snippet"]).lower() for r in ddg_brand_results)
        except Exception as e:
            st.warning(f"DuckDuckGo brand/domain search failed: {e}")

        # 4. GEO Score
        checks = [llm_found, ddg_prompt_found, ddg_brand_found]
        geo_score = round((sum(checks) / len(checks)) * 100, 2)

        # 5. Display Results
        st.subheader("🧠 LLM Response")
        st.write(llm_response)
        st.success("✅ Brand found in LLM") if llm_found else st.error("❌ Brand NOT found in LLM")

        st.subheader("🔍 DuckDuckGo Prompt Results")
        for r in ddg_prompt_results:
            st.markdown(f"- [{r['title']}]({r['href']})")
        st.success("✅ Brand found in prompt results") if ddg_prompt_found else st.error("❌ Brand NOT found in prompt results")

        st.subheader("🌐 DuckDuckGo Brand/Domain Results")
        for r in ddg_brand_results:
            st.markdown(f"- [{r['title']}]({r['href']})")
        st.success("✅ Brand found in brand results") if ddg_brand_found else st.error("❌ Brand NOT found in brand results")

        st.markdown(f"## 📊 Pre-Optimization GEO Score: **{geo_score}%**")

        # Save state for tab 2
        st.session_state.analysis = {
            "prompt": prompt,
            "brand": brand,
            "domain": domain,
            "llm_found": llm_found,
            "ddg_prompt_found": ddg_prompt_found,
            "ddg_brand_found": ddg_brand_found,
            "geo_score": geo_score
        }

# ------------------ Tab 2: GEO Expert ------------------ #
with tab2:
    st.header("Step 2: GEO Expert Advice")

    data = st.session_state.get("analysis")
    if not data:
        st.info("Please complete the analysis in Tab 1 first.")
    else:
        if st.button("Get Expert GEO Advice"):
            expert_prompt = f"""
You are a PhD-level Generative Engine Optimization (GEO) expert advising a business owner.

Prompt: {data['prompt']}
Brand: {data['brand']}
Domain: {data['domain'] or 'N/A'}

Presence in Groq LLM: {data['llm_found']}
Presence in DuckDuckGo Prompt Search: {data['ddg_prompt_found']}
Presence in DuckDuckGo Brand/Domain Search: {data['ddg_brand_found']}
Pre-Optimization GEO Score: {data['geo_score']}%

Provide:
1. Why GEO matters for this business
2. Actionable recommendations (content structure, schema, citations, tech SEO, distribution)
3. Checklist of immediate actions
4. Honest forecast of post-optimization GEO Score
"""

            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": expert_prompt}]
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload))
            if r.ok:
                response = r.json()["choices"][0]["message"]["content"]
                st.markdown("### 📋 GEO Expert Report")
                st.write(response)
            else:
                st.error("Groq API Error: " + r.text)
