from openai import OpenAI
from executor import execute_drawing_code
import os
from dotenv import load_dotenv
import json

load_dotenv()


# ✅ OpenRouter client
def get_client():
    return OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url="https://openrouter.ai/api/v1"
    )


# =========================================================
# MAIN STORYBOARD FUNCTION
# =========================================================
def generate_storyboard(idea: str, num_scenes: int):
    client = get_client()

    scene_prompt = f"""
You are a professional film storyboard artist.

Break this idea into exactly {num_scenes} scenes:

"{idea}"

Return ONLY valid JSON.

Format:

{{
  "scenes": [
    {{
      "scene_number": 1,
      "camera_angle": "...",
      "elements": "...",
      "action": "...",
      "mood": "..."
    }}
  ]
}}
"""

    # ✅ DO NOT force json_object
    scene_response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": scene_prompt}]
    )

    raw_text = scene_response.choices[0].message.content.strip()

    # -------------------------------------------------
    # 🔥 SAFE JSON PARSING (handles messy outputs)
    # -------------------------------------------------
    try:
        scenes_data = json.loads(raw_text)
    except Exception:
        # Try extracting JSON substring if model added text
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        scenes_data = json.loads(raw_text[start:end])

    # -------------------------------------------------
    # 🔥 NORMALIZE TO LIST OF SCENES
    # -------------------------------------------------
    scenes = None

    # Case 1 — {"scenes": [...]}
    if isinstance(scenes_data, dict) and isinstance(scenes_data.get("scenes"), list):
        scenes = scenes_data["scenes"]

    # Case 2 — Already a list
    elif isinstance(scenes_data, list):
        scenes = scenes_data

    # Case 3 — Single scene object
    elif isinstance(scenes_data, dict) and "scene_number" in scenes_data:
        scenes = [scenes_data]

    # Case 4 — Find any list inside dict
    elif isinstance(scenes_data, dict):
        for v in scenes_data.values():
            if isinstance(v, list):
                scenes = v
                break

    if not scenes:
        raise ValueError(f"Model returned unexpected format: {scenes_data}")

    # -------------------------------------------------
    # 🔥 GENERATE IMAGES
    # -------------------------------------------------
    results = []

    for scene in scenes:
        code = generate_drawing_code(scene)
        execute_drawing_code(code, scene["scene_number"])

        results.append({
            "scene_number": scene["scene_number"],
            "description": scene,
            "image_url": f"/outputs/scene_{scene['scene_number']}.png"
        })

    return {"scenes": results}


# =========================================================
# GENERATE PIL DRAWING CODE
# =========================================================
def generate_drawing_code(scene: dict) -> str:
    client = get_client()

    code_prompt = f"""
Write Python Pillow (PIL) code to draw a simple storyboard panel.

Scene data:
{scene}

Rules:
- Size: 800x450
- Light background
- Stick figures + shapes
- Camera angle label on top
- Scene number top-left
- Caption at bottom
- Save to outputs/scene_{scene['scene_number']}.png
- Only Python code
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": code_prompt}]
    )

    return response.choices[0].message.content