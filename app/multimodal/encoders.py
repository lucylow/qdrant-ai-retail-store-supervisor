"""
Multimodal encoders for products: text (bge-m3 / fallback), CLIP image, audio placeholder, video (keyframe pool).

Hackathon: use sentence-transformers for text/image; stub or small models for audio/video to avoid heavy deps.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.multimodal.schema import TEXT_DIM, IMAGE_DIM, AUDIO_DIM, VIDEO_DIM

logger = logging.getLogger(__name__)

# Optional heavy deps
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import cv2
except ImportError:
    cv2 = None


def _pad_or_truncate(vec: np.ndarray, target_dim: int) -> np.ndarray:
    out = np.zeros(target_dim, dtype=np.float32)
    n = min(len(vec), target_dim)
    out[:n] = vec[:n]
    norm = np.linalg.norm(out)
    if norm > 1e-9:
        out = out / norm
    return out


class MultimodalProductEncoders:
    """Encode text, image, audio, and video to the 4 named-vector dimensions."""

    def __init__(
        self,
        text_model_name: str = "sentence-transformers/all-mpnet-base-v2",
        image_model_name: str = "clip-ViT-B-32",
    ):
        self.text_model_name = text_model_name
        self.image_model_name = image_model_name
        self._text_model: Any = None
        self._image_model: Any = None

    def _get_text_model(self) -> Any:
        if self._text_model is None and SentenceTransformer is not None:
            self._text_model = SentenceTransformer(self.text_model_name)
        return self._text_model

    def _get_image_model(self) -> Any:
        if self._image_model is None and SentenceTransformer is not None:
            try:
                self._image_model = SentenceTransformer(self.image_model_name)
            except Exception as e:
                logger.warning("Image model %s failed: %s", self.image_model_name, e)
        return self._image_model

    def encode_text(self, text: str) -> List[float]:
        """Encode title+desc to textvector (padded to TEXT_DIM)."""
        model = self._get_text_model()
        if model is None:
            return [0.0] * TEXT_DIM
        vec = model.encode([text], normalize_embeddings=True)[0]
        if not isinstance(vec, np.ndarray):
            vec = np.array(vec, dtype=np.float32)
        return _pad_or_truncate(vec, TEXT_DIM).tolist()

    def encode_image(self, image_path: str) -> Optional[List[float]]:
        """Encode product image to imagevector (IMAGE_DIM)."""
        model = self._get_image_model()
        if model is None:
            return None
        try:
            vec = model.encode([image_path], convert_to_numpy=True)[0]
            if not isinstance(vec, np.ndarray):
                vec = np.array(vec, dtype=np.float32)
            return _pad_or_truncate(vec, IMAGE_DIM).tolist()
        except Exception as e:
            logger.warning("Image encode failed for %s: %s", image_path, e)
            return None

    def encode_image_bytes(self, image_bytes: bytes) -> Optional[List[float]]:
        """Encode in-memory image (e.g. from upload). Uses temp file or PIL if available."""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(image_bytes)
                path = f.name
            try:
                return self.encode_image(path)
            finally:
                Path(path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning("encode_image_bytes failed: %s", e)
            return None

    def encode_audio(self, audio_path: Optional[str] = None, audio_bytes: Optional[bytes] = None) -> List[float]:
        """Encode 30s demo audio to audiovector (AUDIO_DIM). Stub: zeros or small random for hackathon."""
        # NVmix-8B would go here; for hackathon use deterministic placeholder from path/bytes hash
        if audio_path:
            seed = hash(audio_path) % (2**32)
        elif audio_bytes:
            seed = hash(audio_bytes[:1024]) % (2**32) if len(audio_bytes) >= 1024 else hash(audio_bytes) % (2**32)
        else:
            seed = 0
        rng = np.random.default_rng(int(seed))
        vec = rng.standard_normal(AUDIO_DIM).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        return vec.tolist()

    def encode_video_frames(self, frame_vectors: List[np.ndarray]) -> List[float]:
        """Average-pool frame embeddings to single videovector (VIDEO_DIM). CLIP frames are 512 → pad/project to 768."""
        if not frame_vectors:
            return [0.0] * VIDEO_DIM
        stacked = np.array(frame_vectors, dtype=np.float32)
        if stacked.ndim == 1:
            stacked = stacked.reshape(1, -1)
        pooled = np.mean(stacked, axis=0)
        return _pad_or_truncate(pooled, VIDEO_DIM).tolist()

    def encode_video_file(self, video_path: str, every_nth_frame: int = 5) -> List[float]:
        """Extract keyframes from video, encode with CLIP, average-pool to videovector."""
        if cv2 is None:
            logger.warning("opencv-python not installed; videovector will be zeros")
            return [0.0] * VIDEO_DIM
        model = self._get_image_model()
        if model is None:
            return [0.0] * VIDEO_DIM
        frames = _extract_keyframes(video_path, every_nth=every_nth_frame)
        if not frames:
            return [0.0] * VIDEO_DIM
        # Encode each frame (path list not supported by all ST; use temp files or single-frame decode)
        vectors = []
        for i, frame in enumerate(frames):
            try:
                # CLIP expects image path; write frame to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                    cv2.imwrite(f.name, frame)
                    path = f.name
                try:
                    v = model.encode([path], convert_to_numpy=True)[0]
                    vectors.append(np.array(v, dtype=np.float32))
                finally:
                    Path(path).unlink(missing_ok=True)
            except Exception as e:
                logger.debug("Frame %s encode failed: %s", i, e)
        return self.encode_video_frames(vectors)


def _extract_keyframes(video_path: str, every_nth: int = 5) -> List[Any]:
    """Extract every_nth frame (e.g. 10fps from 50fps). Returns list of BGR arrays."""
    if cv2 is None:
        return []
    cap = cv2.VideoCapture(video_path)
    frames = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % every_nth == 0:
            frames.append(frame)
        idx += 1
    cap.release()
    return frames


def extract_audio_from_video(video_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """Extract audio track to WAV. Returns path to temp WAV if output_path not given. Requires ffmpeg."""
    try:
        import subprocess
        import tempfile
        out = output_path or tempfile.mktemp(suffix=".wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", out],
            check=True,
            capture_output=True,
        )
        return out
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logger.warning("extract_audio_from_video failed: %s", e)
        return None
