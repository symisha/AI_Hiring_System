import tempfile
from pathlib import Path


def extract_cnic_embedding(file_bytes: bytes, file_ext: str) -> list[float]:
    if not file_bytes:
        raise ValueError("Empty CNIC image")

    suffix = f".{file_ext}" if file_ext else ".jpg"
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = Path(tmp.name)

        # Import here to avoid heavy import cost for non-CNIC routes.
        from deepface import DeepFace

        reps = DeepFace.represent(
            img_path=str(tmp_path),
            model_name="ArcFace",
            detector_backend="opencv",
            enforce_detection=True,
        )
        if not reps:
            raise ValueError("No face detected in CNIC photo")

        embedding = reps[0].get("embedding") if isinstance(reps, list) else reps.get("embedding")
        if not embedding:
            raise ValueError("No face detected in CNIC photo")

        return list(embedding)
    finally:
        if tmp_path:
            tmp_path.unlink(missing_ok=True)