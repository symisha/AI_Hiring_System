from deepface import DeepFace

result = DeepFace.verify(
    img1_path="C:\\Users\\NCS\\Desktop\\AI_Hiring_System\\backend\\app\\services\\A1.jpeg",
    img2_path="C:\\Users\\NCS\\Desktop\\AI_Hiring_System\\backend\\app\\services\\A4.jpeg",
    model_name="ArcFace",
    detector_backend="opencv",  # most accurate detector
    enforce_detection=True
)

print(result["verified"])       # True / False
print(result["distance"])       # cosine distance (lower = more similar)