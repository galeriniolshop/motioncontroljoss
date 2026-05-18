import streamlit as st
import requests
import time
import uuid

st.set_page_config(page_title="Kling Motion Control", layout="centered")

st.title("🎬 Kling v2.6 Motion Control")
st.caption("Max Image 200MB | Deploy di Streamlit Cloud")

# ===== API KEY INPUT DI DEPAN =====
with st.container(border=True):
    st.subheader("🔑 API Key Magnific")
    api_key = st.text_input(
        "Masukkan API Key",
        type="password",
        placeholder="sk-magnific-xxx",
        help="Tidak disimpan sama sekali",
        autocomplete="off"
    )
    st.caption("⚠️ API key gak disimpan. Isi ulang tiap refresh halaman.")

if not api_key:
    st.stop()

st.divider()

# ===== UPLOAD FILE =====
col1, col2 = st.columns(2)

with col1:
    st.subheader("🖼️ Image Karakter")
    image_file = st.file_uploader(
        "PNG, JPG, WEBP - Max 200MB",
        type=["png", "jpg", "jpeg", "webp"],
        key="image"
    )
    if image_file:
        st.image(image_file, use_container_width=True)
        size_mb = image_file.size / 1024 / 1024
        if size_mb > 200:
            st.error(f"Size: {size_mb:.2f} MB - Melebihi 200MB")
        else:
            st.caption(f"Size: {size_mb:.2f} MB")

with col2:
    st.subheader("🎥 Video Motion")
    video_file = st.file_uploader(
        "MP4, MOV - Max 200MB",
        type=["mp4", "mov"],
        key="video"
    )
    if video_file:
        st.video(video_file)
        size_mb = video_file.size / 1024 / 1024
        if size_mb > 200:
            st.error(f"Size: {size_mb:.2f} MB - Melebihi 200MB")
        else:
            st.caption(f"Size: {size_mb:.2f} MB")

st.divider()

# ===== PROMPT & SETTINGS =====
prompt = st.text_area("Prompt *", placeholder="karakter menari di pantai, cinematic lighting, 4k", height=100)

col3, col4 = st.columns(2)
with col3:
    orientation = st.selectbox("Orientation", ["video", "image"])
with col4:
    cfg_scale = st.slider("CFG Scale", 0.0, 1.0, 0.5, 0.1)

webhook_url = st.text_input("Webhook URL (opsional)", placeholder="https://webhook.site/xxx")

st.divider()

# ===== UPLOAD KE TRANSFER.SH - SUPPORT 200MB+ =====
def upload_to_transfersh(file_data, filename):
    """Upload ke transfer.sh, support sampe 10GB, expired 14 hari"""
    try:
        # Generate unique filename biar gak bentrok
        unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
        url = f"https://transfer.sh/{unique_name}"
        
        res = requests.put(
            url,
            data=file_data,
            headers={'Max-Days': '1'},  # Auto delete 1 hari
            timeout=300  # 5 menit timeout buat file gede
        )
        res.raise_for_status()
        return res.text.strip()
    except Exception as e:
        st.error(f"Upload error: {e}")
        return None

# ===== GENERATE =====
if st.button("🚀 Generate Video", type="primary", use_container_width=True):
    if not image_file or not video_file or not prompt:
        st.error("Upload gambar, video, dan isi prompt dulu!")
        st.stop()
    
    # Validasi size 200MB
    if image_file.size > 200 * 1024:
        st.error(f"Gambar kegedean: {image_file.size / 1024:.2f}MB. Max 200MB")
        st.stop()
    
    if video_file.size > 200 * 1024:
        st.error(f"Video kegedean: {video_file.size / 1024:.2f}MB. Max 200MB")
        st.stop()

    with st.status("Processing...", expanded=True) as status:
        st.write(f"📤 Uploading image {image_file.size / 1024:.1f}MB ke transfer.sh...")
        image_url = upload_to_transfersh(image_file.getvalue(), image_file.name)
        
        if not image_url:
            st.error("Gagal upload image")
            st.stop()
        st.write(f"✅ Image uploaded")
        
        st.write(f"📤 Uploading video {video_file.size / 1024:.1f}MB ke transfer.sh...")
        video_url = upload_to_transfersh(video_file.getvalue(), video_file.name)
        
        if not video_url:
            st.error("Gagal upload video")
            st.stop()
        st.write(f"✅ Video uploaded")
        
        st.write("🎯 Kirim ke Magnific API...")
        
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
                headers={"x-magnific-api-key": api_key, "Content-Type": "application/json"},
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
            
            st.write(f"✅ Job ID: `{job_id}`")
            st.write("⏳ Tunggu proses render...")
            
            status_url = f"https://api.magnific.com/v1/ai/video/status/{job_id}"
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            for i in range(180):  # 15 menit timeout buat file gede
                time.sleep(5)
                status_res = requests.get(status_url, headers={"x-magnific-api-key": api_key})
                status_data = status_res.json()
                current_status = status_data.get("status")
                
                progress_bar.progress((i + 1) / 180)
                progress_text.text(f"Status: {current_status}")
                
                if current_status == "completed":
                    progress_bar.progress(1.0)
                    status.update(label="✅ Selesai!", state="complete")
                    st.success("Video berhasil dibuat!")
                    st.video(status_data["video_url"])
                    st.link_button("⬇️ Download Video", status_data["video_url"])
                    st.info("💡 File di transfer.sh auto hapus 1 hari. Download segera.")
                    break
                elif current_status == "failed":
                    status.update(label="❌ Gagal", state="error")
                    st.error(f"Error: {status_data.get('error', 'Unknown')}")
                    break
            else:
                status.update(label="⏱️ Timeout", state="error")
                st.warning(f"Timeout. Cek manual: job_id `{job_id}`")
                
        except requests.exceptions.RequestException as e:
            status.update(label="❌ Error", state="error")
            st.error(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                st.code(e.response.text)

st.divider()
with st.expander("📦 requirements.txt"):
    st.code("streamlit\nrequests", language="text")
