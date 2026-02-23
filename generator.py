from openai import OpenAI
from executor import execute_drawing_code
import os
from dotenv import load_dotenv

load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def get_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def generate_storyboard(idea: str, num_scenes: int):
    client = get_client()
    # Call 1: Expand idea into scene descriptions
    scene_prompt = f"""
    You are a professional film storyboard artist.
    Break this idea into exactly {num_scenes} scenes for a storyboard:
    "{idea}"
    
    For each scene describe:
    - Scene number
    - Camera angle (close-up, wide shot, over-the-shoulder, etc.)
    - What is in the frame (characters, objects, background)
    - Action happening
    - Mood/lighting
    
    Be specific and visual. Output as JSON array with keys:
    scene_number, camera_angle, elements, action, mood
    Only output valid JSON, nothing else.
    """
    
    scene_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": scene_prompt}],
        response_format={"type": "json_object"}
    )
    
    import json
    scenes_data = json.loads(scene_response.choices[0].message.content)
    scenes = scenes_data.get("scenes", list(scenes_data.values())[0])
    
    # Call 2: Convert each scene into Pillow drawing code
    results = []
    for scene in scenes:
        code = generate_drawing_code(scene)
        image_path = execute_drawing_code(code, scene["scene_number"])
        results.append({
            "scene_number": scene["scene_number"],
            "description": scene,
            "image_url": f"/outputs/scene_{scene['scene_number']}.png"
        })
    
    return {"scenes": results}


def generate_drawing_code(scene: dict) -> str:
    client = get_client()
    code_prompt = f"""
    You are a Python developer. Write Pillow (PIL) code to draw a simple 2D storyboard sketch panel for this scene:
    
    {scene}
    
    Rules:
    - Image size: 800x450 pixels (16:9)
    - White/light gray background
    - Use simple geometric shapes, lines, stick figures to represent characters
    - Draw the camera angle as a label at top
    - Add scene number at top left
    - Draw basic shapes for objects mentioned (rectangle for can, circle for head, lines for body)
    - Add a caption bar at the bottom with the action text
    - Use black/dark lines, sketch style
    - Save the image to: outputs/scene_{scene['scene_number']}.png
    - Do NOT use any external images or fonts that may not exist
    - Use ImageDraw and basic shapes only
    - End with image.save(...)
    
    Output ONLY the Python code, no explanation, no markdown, no backticks.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": code_prompt}]
    )
    
    return response.choices[0].message.content