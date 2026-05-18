import streamlit as st
import requests
import time

# =========================
# CONFIG
# =========================
API_URL = "https://api.magnific.com/v1/ai/video/kling-v2-6-motion-control-std"

st.set_page_config(
    page_title="Kling Motion Control",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Kling Motion Control Generator")
st.caption("Generate AI motion control video using Magnific API")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ API Settings")

api_key = st.sidebar.text_input(
    "Magnific API Key",
    type="password"
)

webhook_url = st.sidebar.text_input(
    "Webhook URL (Optional)",
    placeholder="https://your-webhook-url.com"
)

# =========================
# MAIN FORM
# =========================
with st.form("motion_control_form"):

    image_url = st.text_input(
        "Image URL",
        placeholder="https://example.com/image.jpg"
    )

    video_url = st.text_input(
        "Reference Video URL",
        placeholder="https://example.com/video.mp4"
    )

    prompt = st.text_area(
        "Prompt",
        placeholder="A cinematic camera movement with realistic motion..."
    )

    character_orientation = st.selectbox(
        "Character Orientation",
        ["video", "horizontal", "vertical"]
    )

    cfg_scale = st.slider(
        "CFG Scale",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )

    submit = st.form_submit_button("🚀 Generate Video")

# =========================
# GENERATE
# =========================
if submit:

    if not api_key:
        st.error("Please input Magnific API Key")
        st.stop()

    if not image_url:
        st.error("Please input Image URL")
        st.stop()

    if not video_url:
        st.error("Please input Video URL")
        st.stop()

    payload = {
        "image_url": image_url,
        "video_url": video_url,
        "webhook_url": webhook_url,
        "prompt": prompt,
        "character_orientation": character_orientation,
        "cfg_scale": cfg_scale
    }

    headers = {
        "x-magnific-api-key": api_key,
        "Content-Type": "application/json"
    }

    with st.spinner("Generating video..."):

        try:
            response = requests.post(
                API_URL,
                json=payload,
                headers=headers,
                timeout=120
            )

            result = response.json()

            st.success("Request sent successfully!")

            st.subheader("📦 API Response")
            st.json(result)

            # Optional output
            if "id" in result:
                st.info(f"Generation ID: {result['id']}")

            if "status" in result:
                st.info(f"Status: {result['status']}")

            # If API directly returns video URL
            if "video_url" in result:
                st.video(result["video_url"])

        except Exception as e:
            st.error(f"Error: {e}")
