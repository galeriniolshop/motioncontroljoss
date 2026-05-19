import streamlit as st
import requests

# ==================================================
# CONFIG
# ==================================================
API_URL = "https://api.magnific.com/v1/ai/video/kling-v2-6-motion-control-std"

st.set_page_config(
    page_title="Kling Motion Control",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Kling Motion Control")
st.caption("Upload image & video from computer")

# ==================================================
# API KEY
# ==================================================
api_key = st.text_input(
    "Magnific API Key",
    type="password"
)

# ==================================================
# UPLOAD IMAGE
# ==================================================
uploaded_image = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png", "webp"]
)

# ==================================================
# UPLOAD VIDEO
# ==================================================
uploaded_video = st.file_uploader(
    "Upload Video",
    type=["mp4", "mov", "webm"]
)

# ==================================================
# PROMPT OPTIONAL
# ==================================================
prompt = st.text_area(
    "Prompt (Optional)",
    placeholder="A cinematic camera movement..."
)

# ==================================================
# OPTIONS
# ==================================================
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

# ==================================================
# PREVIEW
# ==================================================
if uploaded_image:
    st.image(uploaded_image)

if uploaded_video:
    st.video(uploaded_video)

# ==================================================
# UPLOAD TO CATBOX
# ==================================================
def upload_catbox(file):

    response = requests.post(
        "https://catbox.moe/user/api.php",
        data={
            "reqtype": "fileupload"
        },
        files={
            "fileToUpload": (
                file.name,
                file,
                file.type
            )
        }
    )

    return response.text.strip()

# ==================================================
# GENERATE BUTTON
# ==================================================
if st.button("🚀 Generate Video"):

    # VALIDATION
    if not api_key:
        st.error("Please input API Key")
        st.stop()

    if not uploaded_image:
        st.error("Please upload image")
        st.stop()

    if not uploaded_video:
        st.error("Please upload video")
        st.stop()

    try:

        # ==========================================
        # UPLOAD FILES
        # ==========================================
        with st.spinner("Uploading files..."):

            image_url = upload_catbox(uploaded_image)
            video_url = upload_catbox(uploaded_video)

        st.success("Files uploaded successfully!")

        st.write("Image URL:")
        st.code(image_url)

        st.write("Video URL:")
        st.code(video_url)

        # ==========================================
        # PAYLOAD
        # ==========================================
        payload = {
            "image_url": image_url,
            "video_url": video_url,
            "character_orientation": character_orientation,
            "cfg_scale": cfg_scale
        }

        # prompt optional
        if prompt.strip():
            payload["prompt"] = prompt

        # ==========================================
        # HEADERS
        # ==========================================
        headers = {
            "x-magnific-api-key": api_key,
            "Content-Type": "application/json"
        }

        # ==========================================
        # SEND REQUEST
        # ==========================================
        with st.spinner("Generating video..."):

            response = requests.post(
                API_URL,
                json=payload,
                headers=headers,
                timeout=300
            )

        # ==========================================
        # RESPONSE
        # ==========================================
        st.subheader("API Response")

        try:
            result = response.json()
            st.json(result)

            # tampilkan video jika ada
            if "video_url" in result:
                st.success("Video generated successfully!")
                st.video(result["video_url"])

        except:
            st.text(response.text)

    except Exception as e:
        st.error(f"Error: {e}")
