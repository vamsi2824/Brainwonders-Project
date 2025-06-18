import streamlit as st
import google.generativeai as genai
import json
import re

# Gemini API key
genai.configure(api_key="AIzaSyB5b-n_XMkW-2sNt4QFfjRIqhrx7OZKohk")
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# Tasks:

# Design prompt templates to extract preferences from conversation.

# Map interests to pre-defined career paths (e.g., STEM, Arts, Sports).

# Generate a short explanation for each recommended path

# Include fallback prompts to ask clarifying questions.Tools: OpenAI / Mistral, LangChain, embedding search


def extract_preferences(user_input):
    prompt = f"""
You are a helpful career guidance assistant.

Extract the user's career-related:
- Interests
- Skills
- Values

Return the output as a JSON object with keys: "interests", "skills", and "values".

User: "{user_input}"
"""
    response = model.generate_content(prompt)
    return response.text.strip()


def safe_parse_json(raw_input):
    if isinstance(raw_input, list):
        raw_string = "\n".join(raw_input)
    else:
        raw_string = raw_input

    cleaned = re.sub(r"^```json|```$", "", raw_string.strip(),
                     flags=re.MULTILINE).strip()
    return json.loads(cleaned)


career_paths = {
    "STEM": ["coding", "math", "technology", "science", "engineering", "building", "analyzing", "data"],
    "Arts": ["drawing", "painting", "writing", "storytelling", "creativity", "acting", "design"],
    "Sports": ["fitness", "football", "athletics", "teamwork", "discipline", "coaching"],
    "Business": ["sales", "marketing", "entrepreneurship", "negotiation", "leadership"],
    "Healthcare": ["helping", "medicine", "nursing", "biology", "caregiving"],
    "Social Work": ["helping others", "volunteering", "community", "support", "people"]
}


def map_to_career_paths(preferences):
    matched_paths = set()
    all_prefs = preferences.get(
        "interests", []) + preferences.get("skills", []) + preferences.get("values", [])
    for word in all_prefs:
        word_lower = word.lower()
        for path, keywords in career_paths.items():
            for keyword in keywords:
                if keyword in word_lower:
                    matched_paths.add(path)
    return list(matched_paths)


def generate_explanation(preferences, path):
    joined_prefs = ", ".join(
        preferences.get("interests", []) +
        preferences.get("skills", []) +
        preferences.get("values", [])
    )
    prompt = f"""
You are a career advisor. Based on the following preferences: {joined_prefs}, explain in 2–3 lines why the user is suited for the '{path}' career path.
"""
    response = model.generate_content(prompt)
    return response.text.strip()


def needs_fallback(preferences, matched_paths):
    is_empty = (
        not preferences.get("interests") and
        not preferences.get("skills") and
        not preferences.get("values")
    )
    return is_empty or not matched_paths


def get_fallback_prompt():
    return (
        "Thanks for sharing! Could you tell me a bit more about what you enjoy doing, "
        "what subjects or activities you like, or what kind of work you see yourself doing in the future?"
    )


# Streamlit UI
st.set_page_config(page_title="Career Guidance Bot")
st.title("🔬 Career Guidance Assistant")

user_input = st.text_area("Tell me about yourself:", height=150)

if st.button("Analyze") and user_input:
    with st.spinner("Analyzing your input..."):
        try:
            extracted_json_str = extract_preferences(user_input)
            preferences = safe_parse_json(extracted_json_str)
        except Exception as e:
            st.error("Could not parse preferences.\n\nRaw Output:")
            st.code(extracted_json_str)
            st.stop()

        st.subheader("📓 Extracted Preferences")
        st.json(preferences)

        matched_paths = map_to_career_paths(preferences)

        if needs_fallback(preferences, matched_paths):
            st.warning(get_fallback_prompt())
            st.stop()

        st.subheader("🌟 Suggested Career Paths")
        st.write(", ".join(matched_paths))

        st.subheader("🖋️ Explanations")
        for path in matched_paths:
            explanation = generate_explanation(preferences, path)
            st.markdown(f"**{path}:** {explanation}")
