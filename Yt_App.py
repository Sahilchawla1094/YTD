import streamlit as st
import yt_dlp
import os

# --- Determine the path to the Desktop and create "YouTube Downloads" folder ---
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
download_dir = os.path.join(desktop_path, "YouTube Downloads")
os.makedirs(download_dir, exist_ok=True)

# --- Attempt to get the ffmpeg executable using imageio-ffmpeg ---
try:
    import imageio_ffmpeg as iff
    ffmpeg_exe = iff.get_ffmpeg_exe()
    merging_possible = True
except Exception as e:
    ffmpeg_exe = None
    merging_possible = False

# --- Display information to the user ---
st.title("YouTube Playlist Downloader (Up to 1080p Quality)")

if merging_possible:
    st.info(f"ffmpeg detected at: {ffmpeg_exe}\nUsing merging mode for highest quality downloads.")
else:
    st.warning("ffmpeg not detected! Falling back to progressive streams which may be lower quality. "
               "To download merged high-quality videos (up to 1080p), ensure ffmpeg is installed. "
               "See: https://ffmpeg.org/download.html")

st.markdown("""
**Note:**  
- This app uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading videos.  
- If merging separate video and audio streams is required (for higher quality), ffmpeg must be available.  
- The downloaded videos will be saved to your Desktop under **YouTube Downloads**.
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
                    
                    # Choose options based on whether ffmpeg (merging) is available.
                    if merging_possible:
                        ydl_opts_download = {
                            "format": "bestvideo[height<=1080]+bestaudio/best",
                            "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
                            "ffmpeg_location": ffmpeg_exe,
                        }
                    else:
                        ydl_opts_download = {
                            "format": "best[ext=mp4][height<=1080]",
                            "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
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
                            }
                        else:
                            ydl_opts_download = {
                                "format": "best[ext=mp4][height<=1080]",
                                "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
                            }
                        try:
                            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                                ydl.download([video_url])
                            st.write(f"Downloaded: {title}")
                        except Exception as e:
                            st.error(f"Error downloading {title}: {e}")
    except Exception as e:
        st.error(f"Error processing playlist: {e}")
