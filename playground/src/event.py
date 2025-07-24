from llama_index.core.workflow import Event, StartEvent, StopEvent

from schema import SceneGraph

class AnalysisStartEvent(StartEvent):
    image_paths: list[str]
    asr_text: str

class CaptionAndImageEvent(Event):
    keyframe_number: str
    visual_caption: str
    image_path: str
    asr_text: str

class DebugIntermediate(Event):
    caption_image_event: CaptionAndImageEvent
    scene_graph: SceneGraph


class IntermediateResultEvent(Event):
    result: DebugIntermediate

class DebugEndEvent(StopEvent):
    end_result : list[DebugIntermediate]

class AllCaptionsDispatchedEvent(Event):
    caption_count: int


