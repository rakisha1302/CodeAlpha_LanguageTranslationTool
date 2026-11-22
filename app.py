
"""GlobeTalk - AI-powered smart language translation assistant."""

import streamlit as st
from modules import ai, db, speech, translator
from modules.config import LANGS, TONES, lang_name, get_groq_key
from modules.phrasebook import PHRASEBOOK
from dotenv import load_dotenv
import os
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="GlobeTalk",
    page_icon="🌐",
    layout="wide"
)

db.init_db()

NAMES = list(LANGS)
S = st.session_state
GLOBE_IMAGE = Path(__file__).parent / "assets" / "globetalk_globe.webp"


# --------------------------------------------------
# PREMIUM CUSTOM CSS
# --------------------------------------------------

css_file = Path(__file__).parent / "assets" / "style.css"

if css_file.exists():
    st.markdown(
        f"<style>{css_file.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )
else:
    st.warning("Design file not found: assets/style.css")

# --------------------------------------------------
# COMMON FUNCTIONS
# --------------------------------------------------

def hero(title, sub):
    """Premium visual header shared by all GlobeTalk pages."""

    visual_icons = {
        "Translate": ("🌐", "TRANSLATION STUDIO", "Speak · Type · Connect"),
        "Grammar & Tone": ("✍️", "WRITING INTELLIGENCE", "Write with confidence"),
        "Context Translate": ("🧠", "CONTEXT INTELLIGENCE", "Meaning beyond words"),
        "Travel Phrasebook": ("🧳", "WORLD PHRASEBOOK", "Your words, anywhere"),
        "Conversation Practice": ("🤖", "AI CONVERSATION PARTNER", "Practice naturally"),
        "History": ("✨", "YOUR LANGUAGE JOURNEY", "Every conversation, saved"),
    }

    icon, eyebrow, tagline = visual_icons.get(
        title, ("🌍", "GLOBAL COMMUNICATION", "One world. Every language.")
    )

    left, right = st.columns([1.65, 1], gap="large")

    with left:
        st.markdown(
            f"""
            <section class="gt-hero-copy">
                <div class="gt-eyebrow"><span></span> {eyebrow}</div>
                <h1>{title}</h1>
                <p>{sub}</p>
                <div class="gt-hero-tags">
                    <span>✦ AI powered</span>
                    <span>◉ Voice ready</span>
                    <span>◎ Global languages</span>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

    with right:
        if title == "Welcome to GlobeTalk" and GLOBE_IMAGE.exists():
            st.image("assets/globetalk_globe.webp", use_container_width=True)
        else:
            st.markdown(
                f"""
                <div class="gt-hero-visual">
                    <div class="gt-orbit gt-orbit-one"></div>
                    <div class="gt-orbit gt-orbit-two"></div>
                    <div class="gt-visual-core">{icon}</div>
                    <div class="gt-floating-chip gt-chip-one">Hello!</div>
                    <div class="gt-floating-chip gt-chip-two">வணக்கம்</div>
                    <div class="gt-visual-caption">{tagline}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def guard(fn, *args, **kwargs):
    """Execute service calls safely."""

    try:
        with st.spinner("Working..."):
            return fn(*args, **kwargs)

    except (
        ai.AIError,
        translator.TranslationError,
        speech.SpeechError
    ) as e:
        st.error(str(e))

    except Exception as e:
        st.error(f"Unexpected error: {e}")

    return None


def tts_button(text, code, key):
    """Convert text into speech."""

    if st.button("🔊 Listen", key=key):

        audio = guard(
            speech.speak,
            text,
            code
        )

        if audio:
            st.audio(
                audio,
                format="audio/mp3",
                autoplay=True
            )



def mic(label, key, lang_code=None):
    """Record audio and convert it into text."""

    clip = st.audio_input(
        label,
        key=key
    )

    if clip is not None:

        # Get recorded audio
        data = clip.getvalue()

        # Display recording information
        st.info(
            f"Recording received: {len(data)} bytes | "
            f"Format: {clip.type}"
        )

        # Avoid processing the same recording again
        audio_hash = hash(data)

        if S.get(key + "_h") != audio_hash:

            S[key + "_h"] = audio_hash

            transcript = guard(
                ai.transcribe,
                data,
                lang_code
            )

            if isinstance(transcript, str):

                transcript = transcript.strip()

                if transcript:
                    st.success("Speech recognized successfully!")
                    return transcript

            if not transcript:
                st.warning(
                    "Could not recognize your speech. "
                    "Please record again."
                )

    return None


def translate_and_save(text, source, target):
    """Detect source language and translate text."""

    if not text or not text.strip():

        st.warning(
            "Please enter or speak something first."
        )

        return None

    # Detect source language

    if source == "Auto-detect":
        source_code = translator.detect_language(text)

    else:
        source_code = LANGS[source]

    # Get target language code

    target_code = LANGS[target]

    # Prevent same-language translation

    if source_code.lower() == target_code.lower():

        st.warning(
            "Source and target languages are the same."
        )

        return None

    # Translate text

    result = translator.translate(
        text,
        source_code,
        target_code
    )

    if not result:
        st.error("Translation returned an empty result.")
        return None

    # Save translation to database

    db.add(
        "translate",
        source_code,
        target_code,
        text,
        result
    )

    return source_code, result


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------


def dashboard():

    hero(
        "Welcome to GlobeTalk",
        "Your personal AI language companion. Translate, communicate and explore the world."
    )

    # Dashboard statistics
    stats = db.stats()

    columns = st.columns(3)

    values = [
        (stats["total"], "📚 Saved Items"),
        (stats["langs"], "🌍 Languages Used"),
        (lang_name(stats["top"]), "⭐ Most Used Language")
    ]

    for col, (value, label) in zip(columns, values):
        col.markdown(
            f"""
            <div class="stat">
                <b>{value}</b>
                <span>{label}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    st.subheader("✨ Explore GlobeTalk")

    st.caption(
        "Everything you need to understand and communicate in different languages."
    )

    # Feature cards
    features = [
        (
            "🌐 Translate",
            "Convert text between 20 languages. "
            "Use automatic language detection and voice input."
        ),
        (
            "✍️ Grammar & Tone",
            "Improve your writing with AI grammar correction "
            "and formal, friendly or casual tones."
        ),
        (
            "🧠 Context Translate",
            "Get meaningful translations based on the "
            "situation and the person you're communicating with."
        ),
        (
            "✈️ Travel Phrasebook",
            "Discover useful everyday and travel phrases "
            "with translations and audio."
        ),
        (
            "💬 Conversation Practice",
            "Practise real-life conversations with your AI "
            "partner and receive helpful corrections."
        ),
        (
            "📖 Translation History",
            "Access your previous translations, search "
            "saved items and export your history."
        )
    ]

    for start in range(0, len(features), 3):
        cols = st.columns(3)

        for col, (title, description) in zip(
            cols,
            features[start:start + 3]
        ):
            col.markdown(
                f"""
                <div class="gt-card gt-feature-card">
                    <div class="gt-card-orb">✦</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    st.markdown(
        """
        <div class="gt-card">
            <h3>💜 One world. Many languages. One GlobeTalk.</h3>
            <p>
                Break communication barriers and discover
                the power of understanding every language.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            margin-top: 28px;
            padding: 24px;
            text-align: center;
            border-radius: 20px;
            background: linear-gradient(
                110deg,
                #26183f,
                #493078,
                #6845a8
            );
            border: 1px solid rgba(196,181,253,.2);
            box-shadow: 0 10px 30px rgba(0,0,0,.16);
        ">
            <h3 style="color: white;">
                💜 One World. Every Language.
            </h3>
            <p style="color: #ddd0ff;">
                Breaking language barriers through the power of AI.
            </p>
            <p style="
                color: #bda9e9;
                font-size: 12px;
                margin-bottom: 0;
            ">
                GLOBETALK AI · POWERED BY INTELLIGENCE
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# TRANSLATE PAGE
# --------------------------------------------------

def translate_page():

    hero(
        "Translate",
        "Speak or type. GlobeTalk detects your language automatically."
    )

    # Source and target languages

    c1, c2 = st.columns(2)

    source_options = ["Auto-detect"] + NAMES

    src = c1.selectbox(
        "From",
        source_options,
        index=0,
        key="tr_source"
    )

    default_target = (
        NAMES.index("Tamil")
        if "Tamil" in NAMES
        else 0
    )

    tgt = c2.selectbox(
        "To",
        NAMES,
        index=default_target,
        key="tr_target"
    )

    # Voice recording section

    with st.expander(
        "🎤 Speak instead",
        expanded=True
    ):

        st.caption(
            "Record your sentence. GlobeTalk will recognize "
            "your speech and translate it automatically."
        )

        spoken = mic(
            "Record your message",
            "mic_tr",
            None if src == "Auto-detect" else LANGS[src]
        )

        # Automatic voice translation

        if spoken:

            S["tr_text"] = spoken

            # Clear previous result before new translation

            S.pop("tr_out", None)

            st.success(
                "Speech recognized successfully!"
            )

            st.markdown("**Recognized text:**")

            st.write(spoken)

            with st.spinner(
                "Detecting language and translating your speech..."
            ):

                voice_result = guard(
                    translate_and_save,
                    spoken,
                    src,
                    tgt
                )

            if voice_result:

                S["tr_out"] = voice_result
                S["tr_voice_mode"] = True
                S["tr_voice_source"] = voice_result[0]

                st.success(
                    "Voice translation completed!"
                )

    # Text input

    text = st.text_area(
        "Text",
        key="tr_text",
        height=160,
        placeholder="Type something to translate or use the microphone..."
    )

    # Manual translation

    if st.button(
        "🌐 Translate",
        type="primary",
        use_container_width=False
    ):

        S.pop("tr_out", None)

        result = guard(
            translate_and_save,
            text,
            src,
            tgt
        )

        if result:

            S["tr_out"] = result
            S["tr_voice_mode"] = False
            S["tr_voice_source"] = result[0]

    # Translation output

    if "tr_out" in S:

        source_code, output = S["tr_out"]

        st.divider()

        st.subheader("✨ Translation Result")

        st.caption(
            f"Detected source language: {lang_name(source_code)}"
        )

        st.markdown(
            f'<div class="result">{output}</div>',
            unsafe_allow_html=True
        )

        st.write("")

        st.code(
            output,
            language=None
        )

        # Listen to translated output

        tts_button(
            output,
            LANGS[tgt],
            "tts_tr"
        )

        # Copy translation

        if st.button(
            "📋 Copy Translation",
            key="copy_tr"
        ):

            st.code(output)

            st.info(
                "Select and copy the translated text above."
            )


# --------------------------------------------------
# GRAMMAR AND TONE
# --------------------------------------------------

def grammar_page():

    hero(
        "Grammar & Tone",
        "Correct mistakes and change how your writing sounds."
    )

    lang = st.selectbox(
        "Language of your text",
        NAMES
    )

    text = st.text_area(
        "Your text",
        height=150,
        key="gr_text"
    )

    g, t = st.columns(2)

    if g.button(
        "✔ Fix grammar",
        type="primary"
    ):

        if text.strip():

            result = guard(
                ai.correct_grammar,
                text,
                lang
            )

            if result:

                corrected = result.get(
                    "corrected",
                    ""
                )

                db.add(
                    "grammar",
                    LANGS[lang],
                    LANGS[lang],
                    text,
                    corrected
                )

                st.markdown(
                    f'<div class="result">{corrected}</div>',
                    unsafe_allow_html=True
                )

                for change in result.get("changes", []):
                    st.write("•", change)

                st.caption(
                    result.get("explanation", "")
                )

        else:
            st.warning("Enter text first.")

    tone = t.selectbox(
        "Tone",
        TONES,
        label_visibility="collapsed"
    )

    if t.button("🎭 Convert tone"):

        if text.strip():

            result = guard(
                ai.convert_tone,
                text,
                tone,
                lang
            )

            if result:

                db.add(
                    "tone",
                    LANGS[lang],
                    LANGS[lang],
                    text,
                    result,
                    tone
                )

                st.markdown(
                    f'<div class="result">{result}</div>',
                    unsafe_allow_html=True
                )

        else:
            st.warning("Enter text first.")


# --------------------------------------------------
# CONTEXT TRANSLATE
# --------------------------------------------------

def context_page():

    hero(
        "Context Translate",
        "Tell the AI where and to whom you're speaking."
    )

    c1, c2 = st.columns(2)

    src = c1.selectbox(
        "From",
        NAMES,
        key="cs"
    )

    tgt = c2.selectbox(
        "To",
        NAMES,
        index=1,
        key="ct"
    )

    context = st.text_input(
        "Context",
        placeholder="e.g. Emailing a hotel manager"
    )

    text = st.text_area(
        "Text",
        height=130,
        key="cx_text"
    )

    if st.button(
        "Translate with context",
        type="primary"
    ):

        if text.strip() and context.strip():

            result = guard(
                ai.context_translate,
                text,
                src,
                tgt,
                context
            )

            if result:

                translated = result.get(
                    "translation",
                    ""
                )

                db.add(
                    "context",
                    LANGS[src],
                    LANGS[tgt],
                    text,
                    translated,
                    context
                )

                st.markdown(
                    f'<div class="result">{translated}</div>',
                    unsafe_allow_html=True
                )

                st.info(
                    result.get("notes", "")
                )

                S["cx_out"] = (
                    translated,
                    LANGS[tgt]
                )

        else:
            st.warning(
                "Add both text and context."
            )

    if "cx_out" in S:

        tts_button(
            *S["cx_out"],
            "tts_cx"
        )


# --------------------------------------------------
# PHRASEBOOK
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def _phrase(phrase, code):

    return translator.translate(
        phrase,
        "en",
        code
    )


def phrasebook_page():

    hero(
        "Travel Phrasebook",
        "Essential phrases, translated and ready to play."
    )

    tgt = st.selectbox(
        "Destination language",
        [
            n for n in NAMES
            if n != "English"
        ]
    )

    tabs = st.tabs(
        list(PHRASEBOOK) + ["✨ AI custom"]
    )

    for tab, category in zip(
        tabs,
        PHRASEBOOK
    ):

        with tab:

            for i, phrase in enumerate(
                PHRASEBOOK[category]
            ):

                try:

                    translated = _phrase(
                        phrase,
                        LANGS[tgt]
                    )

                except Exception as e:

                    st.error(
                        f"Translation unavailable: {e}"
                    )

                    break

                a, b = st.columns([5, 1])

                a.markdown(
                    f"**{phrase}**  \n{translated}"
                )

                if b.button(
                    "🔊",
                    key=f"pb_{category}_{i}"
                ):

                    audio = guard(
                        speech.speak,
                        translated,
                        LANGS[tgt]
                    )

                    if audio:

                        st.audio(
                            audio,
                            format="audio/mp3",
                            autoplay=True
                        )

    with tabs[-1]:

        scenario = st.text_input(
            "Describe a situation",
            placeholder="Renting a scooter in Bali"
        )

        if st.button(
            "Generate phrases",
            type="primary"
        ):

            if scenario.strip():

                result = guard(
                    ai.custom_phrases,
                    scenario,
                    tgt
                )

                S["pb_ai"] = (
                    result.get("phrases", [])
                    if result else []
                )

        for phrase in S.get("pb_ai", []):

            st.markdown(
                f"**{phrase['english']}**  \n"
                f"{phrase['translation']}  \n"
                f"*{phrase.get('pronunciation', '')}*"
            )


# --------------------------------------------------
# CONVERSATION PRACTICE
# --------------------------------------------------

def practice_page():

    hero(
        "Conversation Practice",
        "Role-play with an AI partner and get gentle corrections."
    )

    c1, c2, c3 = st.columns(3)

    lang = c1.selectbox(
        "Practice language",
        [
            n for n in NAMES
            if n != "English"
        ]
    )

    level = c2.selectbox(
        "Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    scenario = c3.text_input(
        "Scenario",
        "Ordering food at a restaurant"
    )

    if st.button("Restart conversation"):

        S["chat"] = []

    S.setdefault("chat", [])

    for message in S["chat"]:

        with st.chat_message(message["role"]):

            st.write(message["content"])

            if message.get("extra"):
                st.caption(message["extra"])

    with st.expander("🎤 Answer by voice"):

        spoken = mic(
            "Record your reply",
            "mic_pr",
            LANGS[lang]
        )

    msg = st.chat_input(
        f"Write in {lang}..."
    ) or spoken

    if msg:

        S["chat"].append(
            {
                "role": "user",
                "content": msg
            }
        )

        history = [
            {
                "role": m["role"],
                "content": m["content"]
            }
            for m in S["chat"]
        ]

        result = guard(
            ai.practice_turn,
            history,
            lang,
            level,
            scenario
        )

        if result:

            extra = (
                f"🇬🇧 {result.get('english', '')}"
                + (
                    f"\n\n✏️ {result['correction']}"
                    if result.get("correction")
                    else ""
                )
            )

            S["chat"].append(
                {
                    "role": "assistant",
                    "content": result.get("reply", ""),
                    "extra": extra
                }
            )

            db.add(
                "practice",
                LANGS[lang],
                "en",
                msg,
                result.get("reply", "")
            )

        else:
            S["chat"].pop()

        st.rerun()

    if (
        S["chat"]
        and S["chat"][-1]["role"] == "assistant"
    ):

        tts_button(
            S["chat"][-1]["content"],
            LANGS[lang],
            "tts_pr"
        )


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

def history_page():

    hero(
        "History",
        "Everything you've translated or practised."
    )

    c1, c2 = st.columns([3, 1])

    query = c1.text_input(
        "Search",
        placeholder="Search text..."
    )

    kind = c2.selectbox(
        "Type",
        [
            "All",
            "translate",
            "grammar",
            "tone",
            "context",
            "practice"
        ]
    )

    rows = db.fetch(
        query,
        kind
    )

    if not rows:

        st.info(
            "Nothing here yet. Translate something to get started."
        )

        return

    st.download_button(
        "⬇ Export CSV",
        db.to_csv(rows),
        "globetalk_history.csv",
        "text/csv"
    )

    for row in rows:

        with st.expander(
            f"{row['ts']} · {row['kind']} · "
            f"{lang_name(row['src'])} → "
            f"{lang_name(row['tgt'])} · "
            f"{row['source_text'][:50]}"
        ):

            st.write(
                "**Original:**",
                row["source_text"]
            )

            st.write(
                "**Result:**",
                row["result_text"]
            )

            if st.button(
                "Delete",
                key=f"del{row['id']}"
            ):

                db.delete(row["id"])
                st.rerun()

    if st.button("Clear all history"):

        db.clear()
        st.rerun()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------


# =====================================================
# GLOBETALK — PREMIUM SIDEBAR
# =====================================================

with st.sidebar:

    # BRAND
    st.markdown("""
    <div class="gt-brand-card">
        <div class="gt-brand-orb">
            <span>🌐</span>
        </div>
        <div class="gt-brand-name">GlobeTalk</div>
        <div class="gt-brand-caption">YOUR AI LANGUAGE COMPANION</div>
        <div class="gt-brand-tagline">
            One world. Infinite conversations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # AI STATUS
    if get_groq_key():
        st.markdown("""
        <div class="gt-ai-status">
            <span class="gt-live-dot"></span>
            <span>AI ENGINE ONLINE</span>
            <span class="gt-status-live">LIVE</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="gt-ai-status gt-ai-offline">
            <span class="gt-live-dot"></span>
            <span>AI ENGINE OFFLINE</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gt-menu-heading">WORKSPACE</div>
    """, unsafe_allow_html=True)

    # NAVIGATION
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Translate",
            "Grammar & Tone",
            "Context Translate",
            "Phrasebook",
            "Conversation Practice",
            "History"
        ],
        format_func=lambda x: {
            "Dashboard": "⌂   Dashboard",
            "Translate": "◎   Translate",
            "Grammar & Tone": "✧   Grammar & Tone",
            "Context Translate": "◈   Context Translate",
            "Phrasebook": "▤   Phrasebook",
            "Conversation Practice": "◉   Conversation Practice",
            "History": "◷   History"
        }[x],
        label_visibility="collapsed",
        key="gt_navigation"
    )

    st.markdown("""
    <div class="gt-sidebar-separator"></div>

    <div class="gt-discover-card">
        <div class="gt-discover-icon">✦</div>
        <div class="gt-discover-title">Break language barriers</div>
        <div class="gt-discover-description">
            Explore new languages, express yourself,
            and connect with the world.
        </div>
        <div class="gt-language-pill">
            🌍  20 Languages Supported
        </div>
    </div>

    <div class="gt-sidebar-bottom">
        <div class="gt-bottom-symbol">💜</div>
        <div class="gt-bottom-text">Made for meaningful connections</div>
        <div class="gt-bottom-subtext">POWERED BY GROQ AI</div>
    </div>
    """, unsafe_allow_html=True)

# Keep your existing PAGES dictionary below this section.

# --------------------------------------------------
# PAGE NAVIGATION
# --------------------------------------------------

PAGES = {
    "Dashboard": dashboard,
    "Translate": translate_page,
    "Grammar & Tone": grammar_page,
    "Context Translate": context_page,
    "Phrasebook": phrasebook_page,
    "Conversation Practice": practice_page,
    "History": history_page
}

# Display selected page

PAGES[page]()
