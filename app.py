# -------- TAB 2: Ultra-GEO Content Generator -------- #
with tab2:
    st.header("✍️ Ultra-GEO Content Generator")

    desc = st.text_area(
        "Describe your product/service (e.g., 'an AI resume builder for students')",
        height=120
    )
    keyword = st.text_input("Enter your primary SEO keyword (e.g., 'AI resume builder')")

    if st.button("Generate Ultra-GEO Content"):
        if not GROQ_API_KEY:
            st.warning("Groq API key missing. Set it in Streamlit Cloud > Secrets.")
        else:
            geo_prompt = f"""
You are a Generative Engine Optimization expert. For this service:

\"\"\"{desc}\"\"\"

and target keyword: "{keyword}", produce all of the following in markdown, using code blocks where indicated:

1. **SEO-Friendly Blog Titles**: 3–5 titles (<60 chars).
2. **Meta Tags**: <title> and <meta name="description">.
3. **URL Slug**: 2–3 concise slug suggestions.
4. **Content Outline**: H2/H3 headings with word-count estimates.
5. **FAQs**: 5–7 Q&A pairs formatted as JSON-LD for schema.org/FAQPage.
6. **Why Choose Us?**: 4–6 bullet-pointed value propositions.
7. **CTAs**: 3–5 call-to-action lines.
8. **Linking Plan**: List 3 internal pages to link + 2 external authority references.
9. **Images & Alt Text**: Suggest 2–3 images and provide alt text.
10. **Social Preview**: Open Graph & Twitter Card tags + 2 sample social posts.
11. **Breadcrumb JSON-LD**: A code block for breadcrumb structured data.
12. **Organization JSON-LD**: A code block with your brand’s org data.
13. **Snippet Teasers**: 2–3 short answer teasers (40–50 words).
14. **Competitor Comparison**: A mini-markdown table vs. 2–3 competitors.
15. **Schema Checklist**: A bullet list of additional schema types to add.

Ensure each section is clearly labeled with markdown headings.
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
                headers=headers, data=json.dumps(payload)
            )
            if r.status_code == 200:
                geo_output = r.json()['choices'][0]['message']['content']
                st.markdown("### 🏆 Ultra-GEO Expert Output")
                st.write(geo_output)
            else:
                st.error(f"Groq API Error: {r.text}")
