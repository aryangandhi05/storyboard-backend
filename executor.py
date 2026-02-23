import os
import traceback

def execute_drawing_code(code: str, scene_number: int) -> str:
    os.makedirs("outputs", exist_ok=True)
    
    # Clean code if GPT adds backticks
    code = code.strip()
    if code.startswith("```"):
        code = code.split("\n", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]
    
    try:
        exec(code, {"__builtins__": __builtins__})
        return f"outputs/scene_{scene_number}.png"
    except Exception as e:
        print(f"Error executing scene {scene_number}: {traceback.format_exc()}")
        # Generate fallback blank panel
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (800, 450), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), f"Scene {scene_number}", fill="black")
        draw.text((20, 200), "Sketch generation failed", fill="red")
        img.save(f"outputs/scene_{scene_number}.png")
        return f"outputs/scene_{scene_number}.png"