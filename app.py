import streamlit as st
import requests
import tempfile
import os

# ==================================
# CONFIG
# ==================================
API_URL = "https://api.magnific.com/v1/ai/video/kling-v2-6-motion-control-std"

st.set_page_config(
    page_title="Kling Motion Control",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Kling Motion Control")
st.caption("Upload image & video from your computer")

# ==================================
# API KEY
# ==================================
api_key = st.text_input(
    "Magnific API Key",
    type="password"
)

# ==================================
# UPLOAD FILE
# ==================================
uploaded_image = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png", "webp"]
)

uploaded_video = st.file_uploader(
    "Upload Reference Video",
    type=["mp4", "mov", "webm"]
)

# ==================================
# OPTIONS
# ==================================
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
    0.0,
    1.0,
    0.5,
    0.1
)

# ==================================
# PREVIEW
# ==================================
if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image")

if uploaded_video:
    st.video(uploaded_video)

# ==================================
# GENERATE BUTTON
# ==================================
if st.button("🚀 Generate Video"):

    if not api_key:
        st.error("Please input API Key")
        st.stop()

    if not uploaded_image:
        st.error("Please upload image")
        st.stop()

    if not uploaded_video:
        st.error("Please upload video")
        st.stop()

    # ==================================
    # SAVE TEMP FILES
    # ==================================
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
        img_tmp.write(uploaded_image.read())
        image_path = img_tmp.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as vid_tmp:
        vid_tmp.write(uploaded_video.read())
        video_path = vid_tmp.name

    # ==================================
    # REQUEST
    # ==================================
    headers = {
        "x-magnific-api-key": api_key
    }

    files = {
        "image": open(image_path, "rb"),
        "video": open(video_path, "rb")
    }

    data = {
        "prompt": prompt,
        "character_orientation": character_orientation,
        "cfg_scale": cfg_scale
    }

    with st.spinner("Generating video..."):

        try:

            response = requests.post(
                API_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=300
            )

            result = response.json()

            st.success("Video generation started!")

            st.subheader("API Response")
            st.json(result)

            # ==================================
            # SHOW RESULT VIDEO
            # ==================================
            if "video_url" in result:
                st.video(result["video_url"])

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            # cleanup
            files["image"].close()
            files["video"].close()

            if os.path.exists(image_path):
                os.remove(image_path)

            if os.path.exists(video_path):
                os.remove(video_path)
