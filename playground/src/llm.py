from dotenv import load_dotenv
load_dotenv()
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.llms import ChatMessage, TextBlock, ImageBlock
from llama_index.core.prompts import PromptTemplate
from keyframe_analysis_prompt import instruction_prompt
from output_schema import OutputVisualCaption
import os
from pathlib import Path
import json

LLM = GoogleGenAI(
    model="models/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_GENAI_API_KEY"),
    max_output_tokens=65536,
    min_output_tokens=6000,
    temperature=1,
    top_p=0.95, 
)

def generate_prompt_template(list_images: list[str], asr: str):

    sorted_lambda = lambda x: os.path.basename(x).split('.')[0]

    list_images = sorted(list_images, key=sorted_lambda)
    list_images = [os.path.basename(image).split('.')[0] for image in list_images]
    print(list_images)
    print(asr)
    template =  PromptTemplate(
        template=instruction_prompt,
    )
    return template.format(
        keyframe_list=list_images,
        asr=asr
    )



if __name__ == "__main__":

    event_0_folder = "../sample/event_0"
    list_of_images = [
        os.path.join(event_0_folder, file) for file in os.listdir(event_0_folder)
    ]

    with open('../chunked_events_enhanced.json', 'r', encoding='utf-8') as f:
        chunked_event_enhanced = json.load(f)

    asr = chunked_event_enhanced['events'][0]['cnt']
    prompt_template = generate_prompt_template(list_of_images, asr)

    messages = [
        ChatMessage(
            role='user',
            blocks= [ImageBlock(path=Path(image), detail=f"Keyframe number: {os.path.basename(image).split('.')[0]}") for image in list_of_images] + [TextBlock(text=prompt_template)] 
        )
    ]

    response_obj = LLM.as_structured_llm(OutputVisualCaption).chat(messages)
    response_str = response_obj.model_dump()
    
    with open("../sample/response/visual_caption_output.json", "w", encoding="utf-8") as f:
        json.dump(response_str,f,indent=4, ensure_ascii=False)
    print("Done")
        