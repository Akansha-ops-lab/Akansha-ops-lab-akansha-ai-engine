import streamlit as st
from pathlib import Path
import tempfile

from engine.core import (
    generate_script,
    split_script_into_scenes,
    render_video,
    generate_narration,
    ENGINE_VERSION,
)

st.set_page_config(page_title="Akansha AI Video Studio", page_icon="🎬", layout="wide")
st.title("🎬 Akansha AI Video Studio")
st.caption(f"Script-to-video workspace · Engine {ENGINE_VERSION}")

with st.sidebar:
    st.header("Video settings")
    audience = st.selectbox("Audience", [
        "General audience", "School student", "College student",
        "Fresher / job seeker", "Working professional", "Professor / trainer"
    ])
    presenter = st.selectbox("Presenter character", [
        "Akansha", "Friendly Mentor", "Professional Presenter", "Student Guide"
    ])
    style = st.selectbox("Video style", [
        "Educational", "Storytelling", "Motivational", "Conversational", "Professional"
    ])
    tone = st.selectbox("Voice and tone", [
        "Simple and conversational", "Friendly and energetic", "Formal and informative"
    ])
    duration = st.selectbox("Target duration", [1, 2, 3, 5], index=1, format_func=lambda n: f"{n} minute(s)")
    include_example = st.checkbox("Include a practical example", value=True)
    include_cta = st.checkbox("Include a closing call to action", value=True)

st.subheader("1. Create your script")
topic = st.text_input("Video idea or topic", placeholder="Example: Data analytics for beginners")
extra_context = st.text_area(
    "Additional instructions (optional)",
    placeholder="Mention key points, examples, facts, or things to avoid.",
    height=90,
)

if "script_editor" not in st.session_state:
    st.session_state.script_editor = ""
if "final_script" not in st.session_state:
    st.session_state.final_script = ""

col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("✨ Generate Script", type="primary", use_container_width=True):
        if not topic.strip():
            st.error("Please enter a topic first.")
        else:
            try:
                st.session_state.script_editor = generate_script(
                    topic=topic.strip(),
                    audience=audience,
                    presenter=presenter,
                    style=style,
                    tone=tone,
                    duration=duration,
                    extra_context=extra_context.strip(),
                    include_example=include_example,
                    include_cta=include_cta,
                )
                st.session_state.final_script = ""
                st.success("Script draft created. Review and edit it below.")
            except Exception as exc:
                st.error(f"Script generation error: {exc}")
with col_b:
    if st.button("Clear script", use_container_width=True):
        st.session_state.script_editor = ""
        st.session_state.final_script = ""
        st.rerun()

st.subheader("2. Edit and finalise")
st.caption("The built-in generator works without an API key. It creates a structured draft from your topic and instructions; it is not an LLM.")
st.text_area("Editable script", key="script_editor", height=400, placeholder="Your generated script will appear here.")

if st.button("✅ Finalise this script", use_container_width=True):
    if st.session_state.script_editor.strip():
        st.session_state.final_script = st.session_state.script_editor.strip()
        st.success("Script finalised. You can now create a video.")
    else:
        st.warning("Generate or enter a script before finalising it.")

script_to_render = st.session_state.final_script
if script_to_render:
    st.subheader("3. Generate a video")
    st.info("The renderer creates a narrated slideshow-style MP4 with text scenes. It does not create a photorealistic moving avatar or lip-sync.")
    add_narration = st.checkbox("Add online text-to-speech narration (requires internet)", value=True)
    if st.button("🎬 Generate MP4", type="primary", use_container_width=True):
        try:
            with st.spinner("Preparing scenes and rendering video..."):
                scenes = split_script_into_scenes(script_to_render)
                narration_path = None
                if add_narration:
                    try:
                        narration_path = generate_narration(script_to_render)
                    except Exception as tts_exc:
                        st.warning(f"Narration unavailable; rendering video without audio. Details: {tts_exc}")
                output_dir = Path(tempfile.mkdtemp(prefix="akansha_studio_"))
                video_path = output_dir / "akansha_video.mp4"
                render_video(
                    scenes=scenes,
                    output_path=video_path,
                    topic=topic or "Video",
                    presenter=presenter,
                    style=style,
                    duration_minutes=duration,
                    narration_path=narration_path,
                )
                st.session_state.video_path = str(video_path)
            st.success("Video rendered.")
        except Exception as exc:
            st.error(f"Video rendering failed: {exc}")
            st.caption("Open Manage app → Logs in Streamlit Community Cloud to inspect deployment errors.")

if st.session_state.get("video_path") and Path(st.session_state.video_path).exists():
    vp = Path(st.session_state.video_path)
    st.subheader("4. Preview and download")
    st.video(str(vp))
    st.download_button(
        "⬇️ Download MP4",
        data=vp.read_bytes(),
        file_name="akansha_ai_video.mp4",
        mime="video/mp4",
        use_container_width=True,
    )

with st.expander("Deployment and capability notes"):
    st.markdown("""
- No Groq key or paid API key is required.
- Script generation is template-based and runs on the app server.
- Text-to-speech uses gTTS when enabled; it requires an internet connection and its availability is not guaranteed.
- The MP4 renderer needs Pillow and imageio-ffmpeg.
- Streamlit Community Cloud has limited resources. Long videos may take time or hit resource limits.
- This project does not include genuine LLM reasoning, photorealistic human animation, or lip-sync.
""")
