import streamlit as st
import yt_dlp
import os

# --- Ask the user where they want to save the videos ---
default_download_dir = os.path.join(os.path.expanduser("~"), "Desktop", "YouTube Downloads")
user_download_dir = st.text_input(
    "Enter folder path where you want to save downloaded videos:",
    value=default_download_dir
)
download_dir = user_download_dir.strip()  # remove any accidental whitespace
os.makedirs(download_dir, exist_ok=True)

# --- Attempt to get the ffmpeg executable using imageio-ffmpeg ---
try:
    import imageio_ffmpeg as iff
    ffmpeg_exe = iff.get_ffmpeg_exe()
    merging_possible = True
except Exception as e:
    ffmpeg_exe = None
    merging_possible = False

# --- Custom HTTP Headers to avoid 403 errors ---
custom_headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.122 Safari/537.36"
    )
}

# --- Display information to the user ---
st.title("YouTube Playlist Downloader (Up to 1080p Quality)")
st.markdown(f"**Download Folder:** {download_dir}")

if merging_possible:
    st.info(f"ffmpeg detected at: {ffmpeg_exe}\nUsing merging mode for highest quality downloads.")
else:
    st.warning("ffmpeg not detected! Falling back to progressive streams which may be lower quality. "
               "To download merged high-quality videos (up to 1080p), ensure ffmpeg is installed. "
               "See: [ffmpeg.org](https://ffmpeg.org/download.html)")

st.markdown("""
**Note:**  
- This app uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading videos.
- A custom HTTP header is added to mimic a browser, which helps prevent 403 errors.
- The downloaded videos will be saved to the folder you specified.
""")

# --- Get the YouTube Playlist URL from the user ---
playlist_url = st.text_input("Enter YouTube Playlist URL:")

if playlist_url:
    try:
        # --- Extract playlist information using yt-dlp in flat mode ---
        ydl_opts_info = {
            'extract_flat': True,   # Only extract minimal info (IDs and titles)
            'skip_download': True,
            'quiet': True,
            'http_headers': custom_headers,
        }
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
        
        # For playlists, videos are stored in the "entries" key.
        videos = playlist_info.get("entries", [playlist_info])
        
        if not videos:
            st.error("No videos found in the playlist.")
        else:
            st.success(f"Found {len(videos)} videos in the playlist!")
            
            # --- Global Download All Videos Button ---
            if st.button("Download All Videos"):
                st.write("Starting global downloads...")
                for i, video in enumerate(videos):
                    video_id = video.get("id")
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Choose options based on whether merging (with ffmpeg) is available.
                    if merging_possible:
                        ydl_opts_download = {
                            "format": "bestvideo[height<=1080]+bestaudio/best",
                            "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
                            "ffmpeg_location": ffmpeg_exe,
                            "http_headers": custom_headers,
                        }
                    else:
                        ydl_opts_download = {
                            "format": "best[ext=mp4][height<=1080]",
                            "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
                            "http_headers": custom_headers,
                        }
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                            ydl.download([video_url])
                        st.write(f"Downloaded: {video_url}")
                    except Exception as e:
                        st.error(f"Error downloading {video_url}: {e}")
                st.success("Global download completed!")
            
            st.write("### Individual Video Downloads")
            # --- Display individual download buttons for each video ---
            for i, video in enumerate(videos):
                video_id = video.get("id")
                title = video.get("title", f"Video {i+1}")
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(title)
                with col2:
                    if st.button("Download", key=f"download_{video_id}_{i}"):
                        if merging_possible:
                            ydl_opts_download = {
                                "format": "bestvideo[height<=1080]+bestaudio/best",
                                "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
                                "ffmpeg_location": ffmpeg_exe,
                                "http_headers": custom_headers,
                            }
                        else:
                            ydl_opts_download = {
                                "format": "best[ext=mp4][height<=1080]",
                                "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
                                "http_headers": custom_headers,
                            }
                        try:
                            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                                ydl.download([video_url])
                            st.write(f"Downloaded: {title}")
                        except Exception as e:
                            st.error(f"Error downloading {title}: {e}")
    except Exception as e:
        st.error(f"Error processing playlist: {e}")
