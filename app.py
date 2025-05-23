import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

st.title("🛠️ LLMVisible.com – Free GEO Analyzer & Advisor")
tab1, tab2 = st.tabs(["🔍 Prompt & Brand Tester", "🧑‍💼 GEO Expert Advice"])

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

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# ------------------ Tab 1: Prompt Testing ------------------ #
with tab1:
    st.header("Step 1: Check Visibility in LLMs & DuckDuckGo")
    prompt = st.text_input("Prompt to test (e.g. Best CRM tools):", key="prompt")
    brand = st.text_input("Your Brand Name:", key="brand")
    domain = st.text_input("Your Website (optional):", key="domain")

    if st.button("Run GEO Analysis"):
        llm_response = ""
        llm_found = False
        ddg_prompt_results = []
        ddg_brand_results = []
        ddg_prompt_found = False
        ddg_brand_found = False

        # LLM Check with Groq
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

        # DuckDuckGo Prompt Search
        ddg_prompt_results = duckduckgo_search(prompt)
        ddg_prompt_found = any(brand.lower() in (res["title"] + res["snippet"]).lower() for res in ddg_prompt_results)

        # DuckDuckGo Brand/Domain Search
        search_term = f"site:{domain}" if domain else brand
        ddg_brand_results = duckduckgo_search(search_term)
        ddg_brand_found = any(brand.lower() in (res["title"] + res["snippet"]).lower() for res in ddg_brand_results)

        # Compute Geo Score
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
            st.markdown(f"- [{res['title']}]({res['href']})<br>{res['snippet']}", unsafe_allow_html=True)
        if ddg_prompt_found:
            st.success("✅ Brand found in Prompt results")
        else:
            st.error("❌ Brand NOT in Prompt results")

        st.subheader("🌐 DuckDuckGo Brand/Domain Results")
        for res in ddg_brand_results:
            st.markdown(f"- [{res['title']}]({res['href']})<br>{res['snippet']}", unsafe_allow_html=True)
        if ddg_brand_found:
            st.success("✅ Brand found in Brand/Domain results")
        else:
            st.error("❌ Brand NOT found in Brand/Domain results")

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
            # Build an expert-level GEO prompt with deep analysis and three examples per recommendation
            llm_snippet = data['llm_response'][:500].replace('"', '\"').replace("\n", " ")
            expert_prompt = f"""
You are the world's leading PhD-level Generative Engine Optimization (GEO) expert. Based on the following analysis, provide an in-depth GEO advisory report with three concrete examples for each section. Do NOT give SEO tips—focus solely on LLM visibility strategies.

ANALYSIS:
- Prompt: {data['prompt']}
- Brand: {data['brand']}
- Pre-Optimization GEO Score: {data['geo_score']}%

LLM Response Snippet:
"{llm_snippet}..."
Brand present in LLM: {data['llm_found']}
DuckDuckGo Prompt Visibility: {data['ddg_prompt_found']}
DuckDuckGo Brand/Domain Visibility: {data['ddg_brand_found']}

REPORT STRUCTURE:

1. **LLM Visibility Diagnosis**
   - Explain why the brand did or did not appear, referencing specific phrases from the LLM response.
   - Provide 3 in-depth diagnostic points with direct quotes.

2. **Prompt Engineering Strategies**
   - Create content that aligns with these prompt formats.
   - Present 3 advanced prompt templates designed to surface the brand name, with usage examples:
     1. Template and example invocation
     2. Template and example invocation
     3. Template and example invocation

3. **How to Help AI Understand & Remember Your Brand (RAG & Embedding Integration)**
   - Problem:
     Most business owners don’t know what RAG, Pinecone, Weaviate, or LangChain mean.
   - Fix:
     Reframe this section as "How to help AI better understand and remember your brand."

     Use analogies:
     "We store your brand content in a memory system that helps AI recall your name when relevant."

     Then say:
     "We can connect your brand docs to an AI memory system like Pinecone or LangChain, so that when someone asks about the best cake shop, AI includes you."
     1. Embed FAQ and about pages into Pinecone as memory vectors
     2. Use LangChain to build an AI agent with your knowledge base
     3. Chunk website content and store in a retriever for LLM memory

4. **Content Injection into LLM Training Surfaces**
   - Identify 3 platforms for seeding authoritative brand content, with format guidelines:
     1. Reddit AMA post with brand mention
     2. Wikipedia stub creation for brand
     3. Medium article titled in prompt style

5. **Live Brand Data via Plugins or APIs**
   - Problem:
     Non-technical clients won’t know how to implement `/api/v1/brand-info?name=...`
   - Fix:
     Rephrase as:
     "Build a tiny backend that AI tools can pull data from. This helps AI recommend your brand based on live info like your prices, menu, and FAQs."

     Then say:
     "We can help create these small data endpoints or plugins for AI tools to use."
     1. API that returns your current product list and prices in JSON
     2. Plugin that gives live responses to "What’s on sale this week?"
     3. Feed that returns top FAQs with answers for direct use in chatbots

6. **Contextual Memory & Fine-Tuning Approaches**
   - Provide 3 strategies to maintain brand context:
     1. Embedding-based convo memory example
     2. User persona injection through system messages
     3. Dynamic context window expansion example

7. **Monitoring & Iteration Framework**
   - Problem:
     “Prompt hit rate,” “Peec.ai,” and “retrieval success rate” are too abstract for most clients.
   - Fix:
     Keep the idea but reframe it as:
     "We’ll track how often AI mentions your brand. If it’s low, we’ll adjust the content, prompts, or exposure until visibility improves."
     1. Manually test common prompts and log if your brand is mentioned
     2. Track changes in mention frequency month-over-month
     3. Adjust prompts or push more citations based on underperforming topics

8. **Post-Optimization GEO Score Forecast**
   - Forecast the expected GEO Score after implementing above tactics.
   - For each tactic, estimate its score impact (e.g., +20% from prompt strategies, +15% from RAG, etc.).

Provide the advisory report in **clear, numbered sections** and **bullet points**.
"""
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": expert_prompt}]}
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=30)
                r.raise_for_status()
                report = r.json()["choices"][0]["message"]["content"]
                st.markdown("### 📋 GEO Expert Advisory Report")
                st.markdown(report, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Groq API Error: {e}")
