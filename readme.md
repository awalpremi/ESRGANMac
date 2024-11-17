## Usage

To enhance a video, follow these steps:

1. **Set Up Your Environment**

    Ensure your environment is set up by running the `install.ipynb` notebook or manually following the setup steps above. Use the replacement files to replace the appropriate files in the newly downloaded directory

2. **Run the Enhancement Script**

    Use the following command to enhance your video:

    ```sh
    python mps.py /path/to/your/video.mp4
    ```

    This script will:
    - Extract frames from the video
    - Enhance the frames using Real-ESRGAN
    - Reconstruct the video with the enhanced frames and original audio

## Script Details

### [mps.py](http://_vscodecontentref_/1)

This script performs the following steps:

1. **Extract Frames**

    Extracts frames from the input video using FFmpeg.

    ```python
    def extract_frames(video_path, frames_dir):
        ...
    ```

2. **Enhance Frames**

    Enhances the extracted frames using Real-ESRGAN.

    ```python
    def enhance_frames(frames_dir, output_dir, model_name="realesr-general-x4v3", outscale=2, face_enhance=True):
        ...
    ```

3. **Reconstruct Video**

    Reconstructs the video from the enhanced frames and original audio using FFmpeg.

    ```python
    def reconstruct_video(frames_dir, audio_path, output_video, fps):
        ...
    ```

4. **Extract Audio**

    Extracts audio from the input video using FFmpeg.

    ```python
    def extract_audio(video_path, audio_path):
        ...
    ```

5. **Get Video FPS**

    Retrieves the frames per second (FPS) of the input video using ffprobe.

    ```python
    def get_video_fps(video_path):
        ...
    ```

6. **Main Function**

    The main function orchestrates the entire process.

    ```python
    def main():
        ...
    ```

## System Specifications

This setup is optimized for the following system specifications:
- **Processor:** Apple M2 Ultra
- **Memory:** 192 GB RAM

## Conclusion

This project provides a robust solution for enhancing video quality on macOS using Real-ESRGAN. Follow the setup and usage instructions to get started with enhancing your videos.

For any issues or contributions, please refer to the [GitHub repository](https://github.com/xinntao/Real-ESRGAN).