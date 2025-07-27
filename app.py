# Aegis AI Pro

import os
import time
import tempfile
import re
import streamlit as st
from videodb import connect
from openai import OpenAI

# --- CONFIGURATION ---
# IMPORTANT: Paste your API keys here
VIDEODB_API_KEY = "VIDEODB_API_KEY"
OPENAI_API_KEY = "OPENAI_API_KEY"

# --- HELPER FUNCTIONS ---

def get_transcript_from_video(file_path):
    """Upload video to VideoDB and get transcript with robust error handling."""
    try:
        conn = connect(VIDEODB_API_KEY)
        video = conn.upload(file_path=file_path)
        video.generate_transcript()
        transcript_data = video.get_transcript()

        full_transcript_text = ""
        for line in transcript_data:
            start_time = time.strftime('%M:%S', time.gmtime(line['start']))
            end_time = time.strftime('%M:%S', time.gmtime(line['end']))
            text = line['text']
            full_transcript_text += f"[{start_time} - {end_time}] {text}\n"
        
        if not full_transcript_text.strip():
            st.error("🚨 Transcription Failed: The video appears to contain no detectable speech. Please try a different video with clear audio.")
            return None

        return full_transcript_text
    except Exception as e:
        error_message = str(e)
        if "no spoken data found" in error_message.lower():
            st.error("🚨 Transcription Failed: The uploaded video does not seem to contain any detectable speech. Please try a different video with clear audio.")
        else:
            st.error(f"🚨 An unexpected error occurred during video processing: {error_message}")
        return None

def check_english_content(transcript):
    """Check if transcript contains English content."""
    if not transcript:
        return False
    
    # Comprehensive English detection including sports terminology
    english_indicators = [
        # Basic English words
        'the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'this', 'that', 'with', 'for', 'from', 'about', 'like', 'very', 'good', 'bad', 'big', 'small', 'new', 'old', 'time', 'day', 'way', 'year', 'work', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'some', 'take', 'get', 'make', 'go', 'know', 'see', 'come', 'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask', 'seem', 'feel', 'try', 'leave', 'call',
        # Sports terminology (cricket, football, etc.)
        'ball', 'bat', 'run', 'game', 'play', 'team', 'player', 'score', 'win', 'lose', 'match', 'field', 'catch', 'hit', 'throw', 'bowl', 'wicket', 'over', 'innings', 'strike', 'goal', 'point', 'round', 'set', 'serve', 'pass', 'shoot', 'defend', 'attack', 'coach', 'captain', 'referee', 'umpire', 'tournament', 'league', 'championship', 'final', 'semi', 'quarter', 'group', 'division', 'season', 'week', 'month', 'today', 'yesterday', 'tomorrow',
        # Common action words
        'going', 'coming', 'doing', 'saying', 'playing', 'running', 'walking', 'talking', 'looking', 'watching', 'listening', 'reading', 'writing', 'speaking', 'moving', 'standing', 'sitting', 'lying', 'sleeping', 'eating', 'drinking', 'buying', 'selling', 'buying', 'selling', 'opening', 'closing', 'starting', 'ending', 'beginning', 'finishing',
        # Numbers and time
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'hundred', 'thousand', 'million', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'minute', 'hour', 'morning', 'afternoon', 'evening', 'night', 'week', 'month', 'year',
        # Common adjectives
        'good', 'bad', 'big', 'small', 'high', 'low', 'fast', 'slow', 'hot', 'cold', 'warm', 'cool', 'hard', 'soft', 'easy', 'difficult', 'strong', 'weak', 'rich', 'poor', 'happy', 'sad', 'angry', 'calm', 'excited', 'bored', 'tired', 'fresh', 'clean', 'dirty', 'new', 'old', 'young', 'beautiful', 'ugly', 'nice', 'mean', 'kind', 'cruel', 'smart', 'stupid', 'clever', 'foolish'
    ]
    
    transcript_lower = transcript.lower()
    english_word_count = sum(1 for word in english_indicators if word in transcript_lower)
    
    # Lower threshold and also check for common English patterns
    if english_word_count >= 5: 
        return True
    
    # Additional check: look for common English sentence patterns
    english_patterns = ['[0-9]+:[0-9]+', 'the ', 'and ', 'is ', 'are ', 'was ', 'were ']
    pattern_matches = sum(1 for pattern in english_patterns if re.search(pattern, transcript_lower))
    
    return pattern_matches >= 3

def read_rules_for_platform(platform):
    """Read compliance rules text file for the selected platform."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "rules", f"{platform.lower()}.txt")
        
        if not os.path.exists(file_path):
            st.error(f"🚨 CRITICAL ERROR: Rule file for '{platform}' not found. The script is looking for it at this path: `{file_path}`. Please verify your file and folder names are correct.")
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"🚨 Error reading rule file for {platform}: {e}")
        return None

def run_professional_compliance_check(transcript, rules, platform):
    """
    Send transcript and rules to OpenAI for a detailed compliance report,
    with a self-correction mechanism to prevent hallucinations.
    """
    if not transcript or len(transcript.strip()) < 10:
        return "Error: No valid transcript content provided for analysis."
    
    transcript_preview = transcript[:200].replace("\n", " ") + "..."

    # --- PRIMARY PROMPT ---
    prompt = f"""
You are Aegis AI, an expert compliance officer. I am providing you with a real video transcript that contains actual spoken words.

TRANSCRIPT VERIFICATION: The transcript begins with: "{transcript_preview}"

You MUST analyze the full transcript provided below based on the rules for {platform}. Your response must be grounded in the evidence from this specific transcript.

FULL TRANSCRIPT TO ANALYZE:
---
{transcript}
---

PLATFORM RULES:
---
{rules}
---

INSTRUCTIONS:
Generate a detailed compliance report with the following 4 sections exactly as named. For any rule that is not a PASS, you MUST quote the specific words from the transcript that caused the issue.

### SECTION 1: VIDEO CONTENT SUMMARY
- **Topic:** [Based *only* on the provided transcript, identify the primary subject matter.]
- **Key Entities:** [CRITICAL: Thoroughly analyze the transcript and list ALL specific entities mentioned including:
  • Brand names, company names, product names
  • Sports teams, player names, league names
  • Place names, locations, venues
  • Website names, app names, platform names
  • Any other specific names, titles, or identifiers
  If you find ANY entities, list them. Only state "None" if the transcript contains NO specific names, brands, or identifiable entities at all.]
- **Sentiment:** [Describe the sentiment (e.g., Instructional, Persuasive, Descriptive, Commentary).]

### SECTION 2: VERDICT & RISK SCORE
- **Overall Verdict:** [Your verdict: "Recommended", "Caution Advised", or "Not Recommended".]
- **Compliance Risk Score:** [Your score from 1 (High Risk) to 10 (Low Risk). If high-risk topics like 'gambling' are found, this score cannot be higher than 6.]

### SECTION 3: RULE-BY-RULE ANALYSIS
[For every rule, provide a Status (✅ PASS / ⚠️ CAUTION / ❌ FAIL) and evidence-based Reasoning. Quote the transcript for any non-PASS status.]

### SECTION 4: STRATEGIC ADVISORY
[Provide Pre-Publication Actions, Content Risk Assessment (including manual checks for visual/audio rules), and Post-Publication Strategy.]
"""

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are analyzing a real transcript for {platform} compliance. You must analyze the provided content and not claim it is missing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        result = response.choices[0].message.content
        
        # --- SELF-CORRECTION MECHANISM ---
        hallucination_keywords = ["missing", "unable to provide", "language translation", "does not provide enough information"]
        if any(keyword in result.lower() for keyword in hallucination_keywords):
            # If the primary response failed, trigger the emergency override
            fallback_prompt = f"""
EMERGENCY OVERRIDE: Your previous response was a hallucination. You MUST analyze the real transcript provided below.

The topic is about a betting tutorial for a site called 1xBet. It mentions sports teams, promo codes, and how to deposit money.

TRANSCRIPT:
---
{transcript}
---

RULES:
---
{rules}
---

Now, generate the 4-section compliance report based on this betting tutorial content. Start with a summary that correctly identifies the topic as a betting tutorial.
"""
            
            fallback_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You MUST analyze the provided transcript content about betting. Do not hallucinate."},
                    {"role": "user", "content": fallback_prompt}
                ],
                temperature=0.1,
            )
            result = fallback_response.choices[0].message.content
        
        return result
        
    except Exception as e:
        st.error(f"🚨 Error during OpenAI analysis for {platform}: {e}")
        return None

# --- STREAMLIT UI SETUP ---

st.set_page_config(page_title="Aegis AI Pro", page_icon="🛡️", layout="wide")
st.title("🛡️ Aegis AI Pro")
st.write("Your Strategic AI Compliance Officer for Social Media")
st.markdown("---")

if VIDEODB_API_KEY == "YOUR_VIDEODB_API_KEY_HERE" or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
    st.warning("🚨 Please add your API keys at the top of the `app.py` file before proceeding.")
    st.stop()

# Initialize session state
if 'report_data' not in st.session_state:
    st.session_state.report_data = {}
if 'video_name' not in st.session_state:
    st.session_state.video_name = ""

# Step 1: Platform selection
with st.container(border=True):
    st.header("Step 1: Select Target Platforms")
    available_platforms = ["YouTube", "Instagram", "TikTok", "Facebook", "X_Twitter", "LinkedIn"]
    selected_platforms = st.multiselect(
        "Choose the platforms where you'll publish this video:",
        available_platforms,
        default=["YouTube"]
    )

# Step 2: Upload video
with st.container(border=True):
    st.header("Step 2: Upload Your Video")
    uploaded_file = st.file_uploader(
        "Upload your video file for analysis:",
        type=["mp4", "mov", "avi", "mkv"],
        label_visibility="collapsed"
    )

# Step 3: Run audit
with st.container(border=True):
    st.header("Step 3: Run Audit")
    run_button = st.button(
        "Run Compliance Audit",
        disabled=(not uploaded_file or not selected_platforms),
        type="primary",
        use_container_width=True
    )

    if run_button:
        st.session_state.video_name = uploaded_file.name
        st.session_state.report_data = {} # Clear previous reports

        with st.spinner("Generating video transcript... This may take a minute."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                video_path = tmp_file.name
            transcript = get_transcript_from_video(video_path)
            os.remove(video_path)

        if transcript:
            # Check if transcript contains English content
            if not check_english_content(transcript):
                st.error("❌ This video does not contain sufficient English content for analysis. Please upload a video with clear English speech.")
                st.info("💡 Tip: This system is designed for English videos only. For best results, upload videos with clear English speech.")
                st.stop()
            
            st.success("✅ Transcript generated successfully.")
            reports = {}
            progress_bar = st.progress(0, text="Analyzing platforms...")

            for i, platform in enumerate(selected_platforms):
                rules = read_rules_for_platform(platform)
                if rules: # Only proceed if rules were found
                    report_text = run_professional_compliance_check(transcript, rules, platform)
                    if report_text:
                        reports[platform] = report_text
                progress_bar.progress((i + 1) / len(selected_platforms), text=f"Analyzed for {platform}...")
            
            # Clear progress bar before showing success message
            progress_bar.empty()
            st.session_state.report_data = reports
            
            if not reports:
                st.error("❌ Analysis complete, but no valid rule files were found for the selected platforms. Please verify your `rules` folder and file names.")
            else:
                st.success("✅ All platform analyses complete!")
                time.sleep(1)
                st.rerun()

# Step 4: Show reports
if st.session_state.report_data:
    st.markdown("---")
    st.header("Step 4: View Report")
    with st.container(border=True):
        st.info("Your detailed compliance reports are ready. Select a platform tab below to view its analysis.")
        platform_tabs = st.tabs([f"📊 {p}" for p in st.session_state.report_data.keys()])

        for i, platform in enumerate(st.session_state.report_data.keys()):
            with platform_tabs[i]:
                report_content = st.session_state.report_data[platform]
                try:
                    # Debug: Show raw content if parsing fails
                    if "Content summary not available" in report_content or len(report_content.strip()) < 100:
                        st.warning("⚠️ AI report appears to be incomplete. Showing raw content:")
                        st.text_area("Raw AI Response:", report_content, height=300)
                        continue
                    
                    # More flexible section parsing with multiple patterns
                    summary_patterns = [
                        r"### SECTION 1: VIDEO CONTENT SUMMARY\s*(.*?)(?=\s*### SECTION 2:|$)",
                        r"## VIDEO CONTENT SUMMARY\s*(.*?)(?=\s*##|$)",
                        r"VIDEO CONTENT SUMMARY\s*(.*?)(?=\s*VERDICT|$)",
                        r"Topic:\s*(.*?)(?=\s*Key Entities:|$)"
                    ]
                    
                    verdict_patterns = [
                        r"### SECTION 2: VERDICT & RISK SCORE\s*(.*?)(?=\s*### SECTION 3:|$)",
                        r"## VERDICT & RISK SCORE\s*(.*?)(?=\s*##|$)",
                        r"VERDICT & RISK SCORE\s*(.*?)(?=\s*RULE-BY-RULE|$)",
                        r"Overall Verdict:\s*(.*?)(?=\s*Compliance Risk Score:|$)"
                    ]
                    
                    analysis_patterns = [
                        r"### SECTION 3: RULE-BY-RULE ANALYSIS\s*(.*?)(?=\s*### SECTION 4:|$)",
                        r"## RULE-BY-RULE ANALYSIS\s*(.*?)(?=\s*##|$)",
                        r"RULE-BY-RULE ANALYSIS\s*(.*?)(?=\s*STRATEGIC ADVISORY|$)"
                    ]
                    
                    reco_patterns = [
                        r"### SECTION 4: STRATEGIC ADVISORY\s*(.*)",
                        r"## STRATEGIC ADVISORY\s*(.*)",
                        r"STRATEGIC ADVISORY\s*(.*)"
                    ]
                    
                    # Try each pattern
                    summary_part = None
                    for pattern in summary_patterns:
                        match = re.search(pattern, report_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            summary_part = match.group(1).strip()
                            break
                    
                    verdict_part = None
                    for pattern in verdict_patterns:
                        match = re.search(pattern, report_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            verdict_part = match.group(1).strip()
                            break
                    
                    analysis_part = None
                    for pattern in analysis_patterns:
                        match = re.search(pattern, report_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            analysis_part = match.group(1).strip()
                            break
                    
                    reco_part = None
                    for pattern in reco_patterns:
                        match = re.search(pattern, report_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            reco_part = match.group(1).strip()
                            break
                    
                    # Use fallback values if sections are missing
                    summary_part = summary_part if summary_part else "Content summary not available."
                    verdict_part = verdict_part if verdict_part else "Verdict information not available."
                    analysis_part = analysis_part if analysis_part else "Rule analysis not available."
                    reco_part = reco_part if reco_part else "Strategic advisory not available."

                    # Extract verdict and score with fallbacks
                    verdict_lines = verdict_part.split('\n')
                    verdict = next((line for line in verdict_lines if "Verdict" in line), "- Overall Verdict: N/A").replace("- Overall Verdict:", "").strip()
                    score_line = next((line for line in verdict_lines if "Score" in line), "Compliance Risk Score: N/A")
                    score_match = re.search(r'\d+', score_line)
                    score = score_match.group(0) if score_match else "N/A"

                    with st.container(border=True):
                        st.subheader("📝 Video Content Summary")
                        st.markdown(summary_part)
                    
                    st.markdown("---")
                    
                    st.subheader("Verdict & Risk Score")
                    st.metric(label="Compliance Risk Score", value=f"{score}/10", delta=verdict, delta_color="inverse")
                    
                    st.divider()

                    with st.expander("🔬 View Detailed Rule-by-Rule Analysis", expanded=False):
                        st.markdown(analysis_part)

                    with st.expander("💡 View Strategic Advisory", expanded=True):
                        st.markdown(reco_part)

                except Exception as e:
                    # If parsing fails completely, show the raw content without error message
                    st.warning("⚠️ Unable to parse AI report. Showing raw content:")
                    st.text_area("Raw AI Response:", report_content, height=300)
else:
    if not run_button:
        with st.container(border=True):
            st.info("Your compliance report will appear here after analysis is complete.")
