import os
import cv2
import subprocess
import shutil
import sys

def extract_frames(video_path, frames_dir):
    """Extract frames from the video using FFmpeg."""
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir, ignore_errors=True)
    os.makedirs(frames_dir)
    frame_pattern = os.path.join(frames_dir, 'frame_%08d.jpg')
    command = [
        'ffmpeg', '-i', video_path, '-vsync', '0',
        '-q:v', '2',  # Adjust quality: 2 is high quality, 31 is lowest
        frame_pattern
    ]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error extracting frames: {result.stderr}")
        sys.exit(1)
    else:
        print(f"Frames extracted to: {frames_dir}")

def enhance_frames(frames_dir, output_dir, model_name="realesr-general-x4v3", outscale=2, face_enhance=True):
    """Enhance frames using Real-ESRGAN via inference_realesrgan.py."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)

    # Change to the Real-ESRGAN directory
    real_esrgan_dir = os.path.join(os.getcwd(), 'Real-ESRGAN')  # Update this path if needed
    if not os.path.exists(real_esrgan_dir):
        print(f"Real-ESRGAN directory not found at {real_esrgan_dir}")
        sys.exit(1)
    original_dir = os.getcwd()
    os.chdir(real_esrgan_dir)

    command = [
        'python', 'inference_realesrgan.py',
        '-i', frames_dir,
        '-o', output_dir,
        '-n', model_name,
        '--outscale', str(outscale),
        '--tile', '0',    # Process entire image at once
        '--fp32',         # Ensure full precision for MPS backend
        '--suffix', ''    # Keep filenames the same
    ]
    if face_enhance:
        command.append('--face_enhance')

    print("Running Real-ESRGAN for frame enhancement...")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.chdir(original_dir)  # Change back to the original directory
    if result.returncode != 0:
        print(f"Error enhancing frames: {result.stderr}")
        sys.exit(1)
    else:
        print(f"Enhanced frames saved to: {output_dir}")

def reconstruct_video(frames_dir, audio_path, output_video, fps):
    """Reconstruct video from enhanced frames and original audio using FFmpeg."""
    frame_pattern = 'frame_%08d.jpg'

    command = [
        'ffmpeg', '-y', '-framerate', str(fps),
        '-i', os.path.join(frames_dir, frame_pattern),
        '-i', audio_path,
        '-c:v', 'h264_videotoolbox', '-b:v', '5000k',  # Adjust bitrate to reduce file size
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-movflags', '+faststart',  # Optimize for web playback
        output_video
    ]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error reconstructing video: {result.stderr}")
        sys.exit(1)
    else:
        print(f"Reconstructed video saved to: {output_video}")

def extract_audio(video_path, audio_path):
    """Extract audio from the video using FFmpeg."""
    command = [
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'copy', audio_path
    ]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error extracting audio: {result.stderr}")
        sys.exit(1)
    else:
        print(f"Audio extracted to: {audio_path}")

def get_video_fps(video_path):
    """Get the frames per second of the video using ffprobe."""
    command = [
        'ffprobe', '-v', '0', '-of', 'csv=p=0',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=r_frame_rate',
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error getting fps: {result.stderr}")
        return None
    else:
        fps_str = result.stdout.strip()
        try:
            num, denom = fps_str.split('/')
            fps = float(num) / float(denom)
            return fps
        except ValueError:
            print(f"Unexpected fps format: {fps_str}")
            try:
                fps = float(fps_str)
                return fps
            except ValueError:
                return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python mps.py /path/to/video.mp4")
        sys.exit(1)
    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        sys.exit(1)
    video_folder = os.path.dirname(video_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    enhanced_folder = os.path.join(video_folder, "enhanced")

    # Paths for processing
    frames_dir = os.path.join(enhanced_folder, "frames")
    enhanced_frames_dir = os.path.join(enhanced_folder, "enhanced_frames")
    audio_path = os.path.join(enhanced_folder, "audio.aac")
    output_video = os.path.join(enhanced_folder, f"{video_name}_enhanced.mp4")

    # Ensure the enhanced folder exists
    if not os.path.exists(enhanced_folder):
        os.makedirs(enhanced_folder)

    # Step 1: Extract frames from the video
    print("Extracting frames...")
    extract_frames(video_path, frames_dir)

    # Step 2: Extract audio from the video
    print("Extracting audio...")
    extract_audio(video_path, audio_path)

    # Step 3: Enhance the extracted frames
    print("Enhancing frames...")
    enhance_frames(frames_dir, enhanced_frames_dir)

    # Step 4: Get the video FPS
    fps = get_video_fps(video_path)
    if fps is None:
        print("Could not determine FPS, defaulting to 30")
        fps = 30

    # Step 5: Reconstruct the enhanced video
    print("Reconstructing enhanced video...")
    reconstruct_video(enhanced_frames_dir, audio_path, output_video, fps)

    print("Video enhancement complete!")

if __name__ == "__main__":
    main()
