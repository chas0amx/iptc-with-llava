import base64
import glob
import os
from iptcinfo3 import IPTCInfo
from langchain_community.llms import Ollama
from io import BytesIO
from PIL import Image
from pathlib import Path

OLLAMA_BASE_URL = "http://host.docker.internal:11434"
OLLAMA_MODEL = "llava-llama3"
OLLAMA_MODEL = "llava"


SOURCE_DIR = "img_source"
OUTPUT_DIR = "img_output"

def convert_to_base64(pil_image):
    buffered = BytesIO()
    rgb_im = pil_image.convert('RGB')
    rgb_im.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def main():
    # Connect to LlaVA 1.6 
    llava_model = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
    prompt = "Find very precise keywords and separate them with commas."

    # Iterate over all images in the source folder
    for img_filename in glob.glob(f"{SOURCE_DIR}/*.jpg"):  
        # Read the image...
        print(f"Image '{img_filename}' processing...")
        info = IPTCInfo(img_filename, force=True, inp_charset='utf8')
        pil_image = Image.open(img_filename)

        # Resize image to 672 pixels width
        base_width = 672
        wpercent = (base_width / float(pil_image.size[0]))
        hsize = int((float(pil_image.size[1]) * float(wpercent)))
        pil_image = pil_image.resize((base_width, hsize), Image.Resampling.LANCZOS)

        # Convert image to Base64 and pass it to the model along with the prompt
        image_b64 = convert_to_base64(pil_image)
        llm_with_image_context = llava_model.bind(images=[image_b64])
        response = llm_with_image_context.invoke(prompt)
		 
        # Process the model's response
        # response = response.replace(" ", "")
        keywords = response.split(',')
        print(response)
        
        # Create new image in the target folder
        output_filename = Path(os.path.basename(img_filename)).stem
        output_filename = f"{output_filename}_meta.jpg"
        output_file = os.path.join(OUTPUT_DIR, output_filename)

        # Fill in IPTC fields
        info['writer/editor'] = Path(__file__).name
        info['object name'] = output_filename
        info['keywords'] = keywords
        
        # Save the new image file
        print(f"save to '{output_file}'")
        info.save_as(output_file)

if __name__ == "__main__":
    main()
