import streamlit as st
import requests
import time
import tempfile
import os

st.set_page_config(page_title="Kling Motion Control", layout="centered")

st.title("🎬 Kling v2.6 Motion Control")
st.caption("Upload gambar + video motion, generate pakai Magnific API")

# ===== API KEY INPUT DI DEPAN =====
with st.container(border=True):
    st.subheader("🔑 API Key Magnific")
    api_key = st.text_input(
        "Masukkan API Key",
        type="password",
        placeholder="sk-magnific-xxx",
        help="API key tidak disimpan. Masukkan ulang tiap buka halaman."
    )
    st.warning("⚠️ API Key tidak disimpan. Wajib isi ulang setiap reload.", icon="⚠️")

if not api_key:
    st.stop()

st.divider()

# ===== UPLOAD FILE =====
col1, col2 = st.columns(2)

with col1:
    st.subheader("🖼️ Image Karakter")
    image_file = st.file_uploader(
        "Drag & drop atau pilih gambar",
        type=["png", "jpg", "jpeg", "webp"],
        key="image"
    )
    if image_file:
        st.image(image_file, caption="Preview", use_container_width=True)

with col2:
    st.subheader("🎥 Video Motion")
    video_file = st.file_uploader(
        "Drag & drop atau pilih video",
        type=["mp4", "mov"],
        key="video"
    )
    if video_file:
        st.video(video_file)

st.divider()

# ===== PROMPT & SETTINGS =====
prompt = st.text_area(
    "Prompt *",
    placeholder="karakter menari di pantai, cinematic lighting, 4k",
    height=100
)

col3, col4 = st.columns(2)
with col3:
    orientation = st.selectbox("Orientation", ["video", "image"])
with col4:
    cfg_scale = st.slider("CFG Scale", 0.0, 1.0, 0.5, 0.1)

webhook_url = st.text_input("Webhook URL (opsional)", placeholder="https://webhook.site/xxx")

st.divider()

# ===== UPLOAD KE TMPFILES.ORG =====
def upload_to_tmpfiles(file_data, filename):
    """Upload file ke tmpfiles.org biar dapet public URL"""
    try:
        files = {'file': (filename, file_data)}
        res = requests.post('https://tmpfiles.org/api/v1/upload', files=files, timeout=60)
        res.raise_for_status()
        data = res.json()
        if data['status'] == 'success':
            # Convert ke direct download link
            return data['data']['url'].replace('tmpfiles.org/', 'tmpfiles.org/dl/')
        return None
    except Exception as e:
        st.error(f"Upload error: {e}")
        return None

# ===== GENERATE =====
if st.button("🚀 Generate Video", type="primary", use_container_width=True):
    if not image_file or not video_file or not prompt:
        st.error("Upload gambar, video, dan isi prompt dulu!")
        st.stop()

    with st.status("Processing...", expanded=True) as status:
        st.write("📤 Uploading image ke server sementara...")
        image_url = upload_to_tmpfiles(image_file.getvalue(), image_file.name)
        
        if not image_url:
            st.error("Gagal upload image")
            st.stop()
        
        st.write("📤 Uploading video ke server sementara...")
        video_url = upload_to_tmpfiles(video_file.getvalue(), video_file.name)
        
        if not video_url:
            st.error("Gagal upload video")
            st.stop()
        
        st.write("🎯 Mengirim ke Magnific API...")
        
        payload = {
            "image_url": image_url,
            "video_url": video_url,
            "prompt": prompt,
            "character_orientation": orientation,
            "cfg_scale": cfg_scale
        }
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        try:
            res = requests.post(
                "https://api.magnific.com/v1/ai/video/kling-v2-6-motion-control-std",
                headers={
                    "x-magnific-api-key": api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            res.raise_for_status()
            data = res.json()
            job_id = data.get("job_id")
            
            if not job_id:
                st.error("Gagal dapat job_id")
                st.json(data)
                st.stop()
            
            st.write(f"✅ Job dibuat: `{job_id}`")
            st.write("⏳ Menunggu video selesai diproses...")
            
            # Polling status
            status_url = f"https://api.magnific.com/v1/ai/video/status/{job_id}"
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            for i in range(120):  # Max 10 menit
                time.sleep(5)
                status_res = requests.get(status_url, headers={"x-magnific-api-key": api_key})
                status_data = status_res.json()
                current_status = status_data.get("status")
                
                progress_bar.progress((i + 1) / 120)
                progress_text.text(f"Status: {current_status}")
                
                if current_status == "completed":
                    progress_bar.progress(1.0)
                    status.update(label="✅ Selesai!", state="complete")
                    st.success("Video berhasil dibuat!")
                    st.video(status_data["video_url"])
                    st.link_button("⬇️ Download Video", status_data["video_url"])
                    break
                elif current_status == "failed":
                    status.update(label="❌ Gagal", state="error")
                    st.error(f"Job gagal: {status_data.get('error', 'Unknown')}")
                    break
            else:
                status.update(label="⏱️ Timeout", state="error")
                st.warning("Timeout. Cek status manual pake job_id di atas.")
                
        except requests.exceptions.RequestException as e:
            status.update(label="❌ Error", state="error")
            st.error(f"Request error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                st.code(e.response.text)

# ===== REQUIREMENTS.TXT =====
st.divider()
with st.expander("📦 File requirements.txt untuk Streamlit Cloud"):
    st.code("streamlit\nrequests", language="text")
    st.caption("Buat file `requirements.txt` di repo kamu isi 2 baris di atas")
