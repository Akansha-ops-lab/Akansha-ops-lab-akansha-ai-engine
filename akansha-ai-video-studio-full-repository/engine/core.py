"""Template script generation and slideshow MP4 rendering."""
from pathlib import Path
import re
import textwrap

ENGINE_VERSION = "1.0.0"

def _clean(text):
    return re.sub(r"\s+", " ", (text or "").strip())

def generate_script(
    topic,
    audience="General audience",
    presenter="Akansha",
    style="Educational",
    tone="Simple and conversational",
    duration=2,
    extra_context="",
    include_example=True,
    include_cta=True,
):
    topic = _clean(topic)
    if not topic:
        raise ValueError("Please enter a video topic.")

    audience_note = {
        "General audience": "Keep the language accessible and connect ideas to everyday life.",
        "School student": "Use simple words, short sentences, and familiar examples.",
        "College student": "Explain concepts clearly and connect them to practical applications.",
        "Fresher / job seeker": "Focus on career relevance, practical skills, and workplace situations.",
        "Working professional": "Focus on workplace application, decisions, and useful takeaways.",
        "Professor / trainer": "Use a clear teaching structure with definitions, examples, and a recap.",
    }.get(audience, "Keep the explanation clear and practical.")
    style_note = {
        "Educational": "Teach the topic step by step.",
        "Storytelling": "Use a relatable situation to introduce and explain the topic.",
        "Motivational": "Use encouraging language and focus on achievable progress.",
        "Conversational": "Speak naturally, as if talking directly to one viewer.",
        "Professional": "Use a polished and informative presentation style.",
    }.get(style, "Explain the topic step by step.")
    tone_note = {
        "Simple and conversational": "Use natural spoken language and explain any difficult term.",
        "Friendly and energetic": "Keep the delivery warm, upbeat, and encouraging.",
        "Formal and informative": "Keep the delivery professional, precise, and structured.",
    }.get(tone, "Use clear spoken language.")

    sections = [
        ("Opening hook", f"Have you ever wanted to understand {topic}, but weren't sure where to begin? In this video, we'll break it into clear, manageable ideas."),
        ("Introduction", f"Hello everyone! Welcome to this video. I'm {presenter or 'your presenter'}, and today we're exploring {topic}. {audience_note} {style_note} {tone_note} By the end, you'll have a useful starting framework."),
        ("Key idea 1: Understand the basics", f"First, let's clarify what {topic} means. Identify its purpose, the problem it helps solve, and the key terms associated with it. Start with the fundamentals before moving to advanced details."),
        ("Key idea 2: Break it into steps", f"Next, divide {topic} into smaller parts. Focus on one part at a time, understand how it works, and then connect the pieces. This makes a broad topic easier to manage."),
        ("Key idea 3: Apply what you learn", f"Understanding a concept is only the beginning. Choose one small task related to {topic}, set a clear goal, and try it yourself. Review what worked, identify what needs improvement, and try again."),
        ("Common mistakes", f"When learning {topic}, avoid rushing through the basics, attempting everything at once, or expecting instant results. Practise consistently, ask questions, and use feedback to improve."),
    ]
    if include_example:
        sections.append((
            "Practical example",
            f"Imagine you are exploring {topic} for the first time. Start with one specific question. Find a reliable explanation, note the main steps, and try them in a small practice activity. Finally, explain what you learned in your own words. This helps turn passive learning into active practice."
        ))
    if extra_context:
        sections.append(("Your requested focus", f"Keep these user-provided requirements in mind: {extra_context}. Address them directly in the explanation and use them to shape the examples and recommendations."))
    sections.append((
        "Quick recap",
        f"Let's recap the main points: understand the fundamentals of {topic}, break the process into manageable steps, practise with a relevant example, and review your progress."
    ))
    if include_cta:
        sections.append((
            "Closing and call to action",
            f"Your next step is simple: choose one small action related to {topic} and try it today. Thank you for watching! Share your questions and suggest what you'd like to learn about next."
        ))
    else:
        sections.append(("Closing", "Thank you for watching. Take a moment to review the key ideas and decide which one you will apply first."))

    header = (
        f"# Video Script: {topic}\n\n"
        f"**Audience:** {audience}  \n**Presenter:** {presenter}  \n"
        f"**Style:** {style}  \n**Target duration:** {duration} minute(s)  \n**Tone:** {tone}\n"
    )
    body = "\n\n".join(
        f"## {index}. {heading}\n\n{content}"
        for index, (heading, content) in enumerate(sections, start=1)
    )
    if int(duration) >= 3:
        body += (
            f"\n\n## Extended discussion\n\n"
            f"To explore {topic} more deeply, compare different approaches. Think about where each approach works well, where it has limitations, and what makes one option suitable for a particular situation. Create a checklist of what you understand, what you have practised, and what you still need to learn. Review your work and improve it based on what you discover."
        )
    if int(duration) >= 5:
        body += (
            f"\n\n## Viewer reflection\n\n"
            f"Pause and think about how {topic} connects to your own goals. What is one challenge you want to solve? What information or practice would help you take the next step? Write down one action you can complete today and one question you want to investigate."
        )
    return header + "\n\n" + body

def split_script_into_scenes(script, max_chars=440):
    """Split script into readable scene cards, ignoring markdown heading markers."""
    paragraphs = []
    for raw in (script or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        if line.startswith(("Audience:", "Presenter:", "Style:", "Target duration:", "Tone:")):
            continue
        if len(line) <= max_chars:
            paragraphs.append(line)
        else:
            sentences = re.split(r"(?<=[.!?])\s+", line)
            current = ""
            for sentence in sentences:
                if current and len(current) + len(sentence) + 1 > max_chars:
                    paragraphs.append(current)
                    current = sentence
                else:
                    current = (current + " " + sentence).strip()
            if current:
                paragraphs.append(current)
    return paragraphs or ["Welcome to this video."]

def generate_narration(script, output_path=None, language="en"):
    """Create MP3 narration via gTTS; requires internet. Raises an informative error if unavailable."""
    try:
        from gtts import gTTS
    except ImportError as exc:
        raise RuntimeError("gTTS is not installed. Check requirements.txt.") from exc
    clean_script = re.sub(r"^#{1,6}\s*", "", script or "", flags=re.MULTILINE)
    clean_script = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_script)
    clean_script = re.sub(r"\n{2,}", "\n", clean_script)
    if not clean_script.strip():
        raise ValueError("Cannot create narration from an empty script.")
    if output_path is None:
        import tempfile
        fd, name = tempfile.mkstemp(suffix=".mp3")
        import os
        os.close(fd)
        output_path = name
    gTTS(text=clean_script[:4500], lang=language, slow=False).save(str(output_path))
    return str(output_path)

def render_video(
    scenes,
    output_path,
    topic="Video",
    presenter="Akansha",
    style="Educational",
    duration_minutes=2,
    narration_path=None,
    width=1280,
    height=720,
    fps=12,
):
    """Render simple branded scene cards to MP4 using Pillow + imageio-ffmpeg."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError("Video dependencies are missing. Re-deploy after installing requirements.txt.") from exc
    import subprocess

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenes = list(scenes or ["Welcome to this video."])
    # Keep rendering manageable on free hosting: 3 seconds per card, with a cap.
    scene_duration = max(2, min(5, int((max(1, int(duration_minutes)) * 60) / max(1, len(scenes)))))
    total_frames = min(len(scenes) * scene_duration * fps, 900)
    scene_frames = max(1, total_frames // len(scenes))

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
        font_body = ImageFont.truetype("DejaVuSans.ttf", 32)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 22)
    except OSError:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    temp_video = output_path.with_name(output_path.stem + "_silent.mp4")
    command = [
        ffmpeg_exe, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgb24", "-r", str(fps),
        "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(temp_video)
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for index, scene in enumerate(scenes):
            image = Image.new("RGB", (width, height), (12, 31, 67))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((55, 45, width-55, height-45), radius=28, outline=(70, 145, 220), width=3)
            draw.text((90, 78), "AKANSHA AI VIDEO STUDIO", font=font_small, fill=(125, 195, 255))
            title = topic[:70]
            draw.text((90, 135), title, font=font_title, fill=(255, 255, 255))
            body = textwrap.fill(str(scene), width=54)
            # Draw body lines, limit the visible amount to fit.
            y = 245
            for line in body.splitlines()[:8]:
                draw.text((95, y), line, font=font_body, fill=(235, 241, 250))
                y += 48
            draw.text((90, height-100), f"{presenter}  •  {style}  •  Scene {index+1}/{len(scenes)}", font=font_small, fill=(160, 190, 225))
            frame = image.tobytes()
            for _ in range(scene_frames):
                process.stdin.write(frame)
        process.stdin.close()
        stderr = process.stderr.read()
        return_code = process.wait()
        if return_code != 0:
            raise RuntimeError(stderr.decode("utf-8", errors="ignore")[-1500:])
    except Exception:
        try:
            process.kill()
        except Exception:
            pass
        raise

    if narration_path and Path(narration_path).exists():
        audio_video = output_path.with_name(output_path.stem + "_with_audio.mp4")
        audio_cmd = [
            ffmpeg_exe, "-y", "-i", str(temp_video), "-i", str(narration_path),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-movflags", "+faststart", str(audio_video)
        ]
        result = subprocess.run(audio_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and audio_video.exists():
            audio_video.replace(output_path)
        else:
            temp_video.replace(output_path)
    else:
        temp_video.replace(output_path)
    return str(output_path)
