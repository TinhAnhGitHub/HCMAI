import os
import json 
import asyncio 
from pathlib import Path
from typing import  Union, Annotated, cast

from dotenv import load_dotenv

from llama_index.core.llms import ChatMessage, TextBlock, ImageBlock
from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import (
    Workflow,
    Context,
    step
)
from llama_index.core.workflow.resource import Resource
from llama_index.llms.google_genai import GoogleGenAI
from schema import VisSceneCap, SceneGraph

from keyframe_analysis_prompt import visual_caption_prompt, scene_graph_generation_prompt
from event import AnalysisStartEvent, CaptionAndImageEvent, DebugIntermediate, DebugEndEvent, AllCaptionsDispatchedEvent, IntermediateResultEvent




load_dotenv()


def get_flash_lite_llm() -> GoogleGenAI:

    return GoogleGenAI(
        model="models/gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_GENAI_API_KEY"),
        max_output_tokens=65536,
        min_output_tokens=6000,
        temperature=1,
        top_p=0.95, 
    )

def get_prompt(prompt_str: str):
    return lambda: PromptTemplate(template=prompt_str)



    



class SceneAnalysisWorkflow(Workflow):
    """
    Workflow of ingestion

    1. First, with keyframes and prompt, we generate visual caption for each keyframe
    2. For each keyframe + visual caption, we generate a scene graph.
    3. In the mean time, with all visual captions and ASR, we can generate a event caption
    4. After we have the event caption, we can generate a event graph based on the visual caption + prompt + event caption

    5. Finally, when we have everything, we will have a big complete knowledge graph
    """


    @step
    async def generate_visual_captions(
        self,
        ctx: Context,
        ev: AnalysisStartEvent,
        llm: Annotated[GoogleGenAI, Resource(get_flash_lite_llm)],
        prompt : Annotated[PromptTemplate, Resource(get_prompt(visual_caption_prompt))]     
    ) -> CaptionAndImageEvent |AllCaptionsDispatchedEvent:
        print("--- Running Step 1: Generating Visual Captions (Fork Point) ---")

        image_map = {str(int(os.path.basename(p).split('.')[0])): p for p in ev.image_paths}
        keyframe_numbers = sorted(image_map.keys(), key=int)

        formatted_prompt = prompt.format(
            keyframe_list=keyframe_numbers,
            asr=ev.asr_text
        )

        messages = [
            ChatMessage(
                role='user',
                blocks=[
                    *[
                        ImageBlock(
                            path=Path(image_map[kf]),
                            detail=f"Keyframe number {kf}"
                        )
                        for kf in keyframe_numbers
                    ],
                    TextBlock(text=formatted_prompt)
                ]
            )
        ]
        print("--- Print before running ---")
        responses = await llm.as_structured_llm(VisSceneCap).achat(messages)
        print("--- Print after running ---")
        output_obj: VisSceneCap = cast(VisSceneCap, responses.raw)

        for caption_obj in output_obj.vis_cap:
            
            keyframe_number = str(caption_obj.keyframe_number)
            if keyframe_number in image_map:

                event = CaptionAndImageEvent(
                        keyframe_number=keyframe_number,
                        visual_caption=caption_obj.caption,
                        image_path=image_map[keyframe_number],
                        asr_text=ev.asr_text
                    )
                ctx.send_event(event)
            
        
        await ctx.store.set("all_captions_event", AllCaptionsDispatchedEvent(
            caption_count=len(output_obj.vis_cap)
        ))
        

        return AllCaptionsDispatchedEvent(
            caption_count=len(output_obj.vis_cap)
        )
    

    


    @step(num_workers=2)
    async def generate_scene_graph(
        self,
        ev: CaptionAndImageEvent,
        llm: Annotated[GoogleGenAI, Resource(get_flash_lite_llm)],
        prompt: Annotated[PromptTemplate, Resource(get_prompt(scene_graph_generation_prompt))]   
    ) -> IntermediateResultEvent:
        
        print(f"--- Running Step 2: Generating SceneGraph for keyframe {ev.keyframe_number} ---")

        formatted_scene_graph_prompt = prompt.format(
            asr = ev.asr_text,
            keyframe_number = ev.keyframe_number,
            visual_caption=ev.visual_caption
        )

        messages = [ChatMessage(role='user', blocks=[ImageBlock(path=Path(ev.image_path)), TextBlock(text=formatted_scene_graph_prompt)])]

        

        generated_scene_graph = await llm.as_structured_llm(SceneGraph).achat(messages)

        print("--- RAW Gemini Output ---")
        print(generated_scene_graph.raw)


        scene_graph_obj = cast(SceneGraph, generated_scene_graph.raw)


        
        debug_data = DebugIntermediate(
            caption_image_event=ev,
            scene_graph=scene_graph_obj
        )

        return IntermediateResultEvent(result=debug_data)


    @step
    async def step3_collection(
        self,
        ctx: Context,
        ev: Union[AllCaptionsDispatchedEvent, IntermediateResultEvent]
    ) -> DebugEndEvent | None:
        if isinstance(ev, AllCaptionsDispatchedEvent):
            print(f"--- Running Step 3: Collector is now waiting for {ev.caption_count} results ---")
        
        start_event = await ctx.store.get("all_captions_event")
        

        if not start_event:
            print("should not be here")
            return None #

        events = ctx.collect_events(
            ev,
            [IntermediateResultEvent] * start_event.caption_count
        )
        print("after collect events")
        if events is None  :
            return None
        
        print("--- Collector has all results. Stopping workflow. ---")

        final_results = [e.result for e in events]

        return DebugEndEvent(end_result=final_results)


async def main():


    event_0_folder = "../sample/event_0"
    list_of_images = [os.path.join(event_0_folder, file) for file in os.listdir(event_0_folder)]
    with open('../chunked_events_enhanced.json', 'r', encoding='utf-8') as f:
        asr = json.load(f)['events'][0]['cnt']

    

    workflow = SceneAnalysisWorkflow(verbose=True, timeout=3600.0)
    start_event = AnalysisStartEvent(image_paths=list_of_images, asr_text=asr)
    print("hi")
    result_event = await workflow.run(start_event=start_event)

    if isinstance(result_event, DebugEndEvent):
        print(f"Debug Success")
        final_output = [
            res.model_dump() for res in result_event.end_result
        ]

        output_path = '../sample/response/debug_workflow1.json'

        Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                final_output, f, ensure_ascii=False
            )

        print("Saved ")

    else:
        print(f"Workflow error: {type(result_event)}")
    
if __name__ == "__main__":
    asyncio.run(main())





