from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, List
from llama_index.core.workflow import Event, StartEvent, StopEvent
from typing import Annotated


class Position2D(BaseModel):
    relative_description: str = Field(
        ...,
        alias="rel_des"
        # description="Mô tả vị trí tương đối 2D trong khung hình. Ví dụ: 'góc trái trên', 'chính giữa', 'phía trước'."
    )
    


class Position3D(BaseModel):
    relative_description: str = Field(
        ...,
        alias="rel_des"
        # description=(
        #    "Mô tả vị trí tương đối của đối tượng trong không gian 3D bằng ngôn ngữ tự nhiên"
        # )
    )
    

class ObjectVisual(BaseModel):
    """
    Dùng để miêu tả các đặc trưng nhận dạng trực quan của vật thể (object).
    Cho phép sử dụng mô tả tự nhiên, gần gũi với cách con người quan sát và nhận biết.
    """
    color: Optional[list[str]] = Field(
        None,
        # description=(
        #     "Màu sắc chính và phụ của vật thể. "
        #     "Có thể diễn đạt theo cách tự nhiên"
        # )
    )
    shape: Optional[str] = Field(
        None,
        # description=(
        #     "Hình dạng tổng thể của vật thể. "
            
        # )
    )
    material: Optional[str] = Field(
        None,
        # description=(
        #     "Chất liệu hoặc cảm giác bề mặt của vật thể khi nhìn hoặc chạm vào. "
        # )
    )
    texture: Optional[str] = Field(
        None,
        # description=(
        #     "Kết cấu bề mặt hoặc cảm nhận khi nhìn thấy bề mặt. "
        # )
    )
    size_estimation: Optional[str] = Field(
        None,
        alias='size_est'
        # description=(
        #     "Ước lượng kích thước tổng thể của vật thể. "
        # )
    )
    details: str = Field(
        ...,
        # description=(
        #     "Mô tả thêm về các đặc điểm chi tiết khác của vật thể nếu có. "
        # )
    )

    functionality: str = Field(
        ..., 
        alias='func'
        # description=(
        #     "Chức năng hoặc mục đích sử dụng của vật thể. "
        # )
    )



class TextContent(BaseModel):
    content: str | None = Field(..., 
        # description="Nội dung OCR có trên khung hình/vật thể/..."
    )
    description: str | None = Field(..., alias='desc'
                                #    description="ý nghĩa của nội dung OCR."
                                )
    
    


class ClothingAttributes(BaseModel):
    top: ObjectVisual | None = Field(...,
        # description="Mô tả chi tiết phần thân trên"
    )
    bottom: ObjectVisual | None = Field(...,
        # description="Mô tả chi tiết phần thân dưới"
    )
    headwear: ObjectVisual | None = Field(None,
        # description="Mô tả chi tiết phần mũ nếu có"
    )
    accessories: list[ObjectVisual] | None = Field(None,
        # description="Mô tả chi tiết các phụ kiện nếu có"
    )

    



class HumanVisual(BaseModel):
    gender: str = Field(...,
        # description="Giới tính (nam, nữ)"
    )
    age_estimation: str = Field(...,
        alias='age'
        # description="Độ tuổi ước tính"
    )
    ethnicity: Optional[str] = Field(None,
        # description="Dân tộc"
    )
    body_type: Optional[str] = Field(None,
        # description="Kiểu dáng cơ thể"
    )
    hair_style: Optional[str] = Field(None,
        # description="Kiểu tóc"
    )
    skin_color: Optional[str] = Field(None,
        # description="Màu da"
    )
    posture: Optional[str] = Field(None,
        # description="Tư thế"
    )
    action: str = Field(...,
        # description="Hành động đang thực hiện"
    )
    facial_expression: Optional[str] = Field(None,
        alias='face_expr'
        # description="Biểu cảm"
    )
    role: str = Field(...,
        # description="Vai trò"
    )
    clothing: ClothingAttributes = Field(...,
        # description="Thông tin về trang phục của người"
    )
    


class GroupMember(BaseModel):
    member_id: Optional[str] = Field(None,
        alias="mem_id"
        # description="UUID duy nhất cho thành viên trong nhóm"
    )
    description: str = Field(...,
        alias='des'
        # description="Mô tả ngắn gọn về thành viên"
    )
    object_visual: Optional[ObjectVisual] = Field(None,
        alias='obj_vis'
        # description="Thuộc tính vật thể nếu là vật thể"
    )
    human_visual: Optional[HumanVisual] = Field(None,
        alias='hum_vis'
        # description="Thuộc tính con người nếu là người"
    )


class GroupEntities(BaseModel):
    group_name: str = Field(...,
        alias='gr_name'
        # description="Tên gọi của nhóm"
    )
    group_description: str = Field(...,
        alias='gr_des'
        # description="Mô tả ngắn gọn về nhóm"
    )
    members: List[GroupMember] = Field(...,
        # description="Danh sách các thành viên trong nhóm"
    )
    quantity: Optional[int] = Field(None,
        # description="Số lượng ước tính các thành viên"
    )
    common_human_attributes: Optional[HumanVisual] = Field(None,
        alias='comHu_attr'
        # description="Thuộc tính chung nếu nhóm là người"
    )
    common_object_attributes: Optional[ObjectVisual] = Field(None,
        alias='comObj_attr'
        # description="Thuộc tính chung nếu nhóm là vật thể"
    )
    


class IdentityInfo(BaseModel):
    name: Optional[str] = Field(None,
        # description="Tên định danh của thực thể."
    )
    label: Optional[str] = Field(None,
        # description="Nhãn hoặc phân loại của thực thể."
    )
    brand: Optional[str] = Field(None,
        # description="Thương hiệu liên quan đến thực thể."
    )


class ObjectAttrs(BaseModel):
    type: Literal["object"]
    object_attributes: ObjectVisual

class HumanAttrs(BaseModel):
    type: Literal["human"]
    human_attributes: HumanVisual

class GroupAttrs(BaseModel):
    type: Literal["group"]
    group_attributes: GroupEntities

class OCRAttrs(BaseModel):
    type: Literal["ocr"]
    ocr_attributes: TextContent


EntityContent = Union[ObjectAttrs, HumanAttrs, GroupAttrs, OCRAttrs]


# class EntityAttributes(BaseModel):
#     identity: Optional[IdentityInfo] = Field(None, description="Thông tin định danh  của thực thể, có thể lấy từ ảnh, ASR, ....")
#     position: Optional[Union[Position2D, Position3D]] = Field(None  , description="Vị trí thực thể")

#     # object_attributes: Optional[ObjectVisual] = Field(None, description="Thuộc tính chi tiết của vật thể, nếu như là vật thể. Bỏ qua nếu không phải vật thể")
#     # human_attributes: Optional[HumanVisual] = Field(None, description="Thuộc tính chi tiết của con người, nếu như là con người. Bỏ qua nếu không phải là con người")
#     # group_attributes: Optional[GroupEntities] = Field(None, description="Thuộc tính chi tiết của một nhóm, nếu như là một nhóm. Bỏ qua nếu không phải là một nhóm")
#     #ocr_attibutes: Optional[TextContent] = Field(None, description="Thuộc tính chi tiết của một dòng nội dung OCR, nếu như là một dòng nội dung OCR. Bỏ qua nếu không phải là một dòng nội dung OCR")
#     content: EntityContent



class EntityAttributes(BaseModel):
    identity: Optional[IdentityInfo] = Field(None,
        # description="Thông tin định danh của thực thể, có thể lấy từ ảnh, ASR, ...."
    )
    # position: Optional[Union[Position2D, Position3D]] = Field(None,
    #     # description="Vị trí thực thể"
    # )
    position_2d: Optional[Position2D] = None
    position_3d: Optional[Position3D] = None
    content: EntityContent


    
class Entity(BaseModel):
    entity_id: str = Field(...,
        # description="UUID duy nhất cho thực thể"
    )
    represent: Optional[str] = Field(None,
        # description="Tóm tắt trạng thái của vật thể một cách ngắn gọn nhưng sinh động nhất"
    )
    attributes: Optional[EntityAttributes] = Field(None,
        alias='attrs'
        # description="Các thuộc tính chi tiết của thực thể"
    )
    

class RelationAttributes(BaseModel):
    details: Optional[str] = Field(None,
        # description="Mô tả chi tiết hơn về mối quan hệ"
    )
    location: Optional[str] = Field(None,
        # description="Vị trí cụ thể của mối quan hệ"
    )


class Relation(BaseModel):
    relation_id: str = Field(...,
        # description="UUID duy nhất cho mối quan hệ."
    )
    subject_entity_id: str = Field(...,
        # description="UUID của thực thể chủ thể"
    )
    predicate_type: str = Field(...,
        # description="Loại quan hệ (mặc, cầm nắm, cạnh bên, hành động, etc.)"
    )
    object_entity_id: str = Field(...,
        # description="ID của thực thể đối tượng"
    )
    relation_attributes: Optional[RelationAttributes] = Field(None,
        alias='rel_attr'
        # description="Thuộc tính chi tiết về mối quan hệ"
    )

    


class BackgroundElement(BaseModel):
    description: str = Field(...,
        # description="Mô tả chi tiết phông nền"
    )
    colors: Optional[List[str]] = Field(None,
        # description="Màu sắc của phông nền"
    )

    



class EnvironmentDetails(BaseModel):
    lighting: str = Field(...,

        # description="Chi tiết về ánh sáng"
    )
    time_of_day: Optional[str] = Field(None,
        alias='tod'
        # description="Thời điểm trong ngày"
    )
    color_palette: Optional[List[str]] = Field(None,
        # description="Màu sắc môi trường"
    )
    event_context: Optional[str] = Field(None,
        alias='eve_ctx'
        # description="Ngữ cảnh sự kiện"
    )
    background_elements: Optional[List[BackgroundElement]] = Field(None,
        alias='bg_eles'
        # description="Các yếu tố khung hình nền"
    )

    




class SceneDescription(BaseModel):
    type: str = Field(...,
        # description="Loại không gian (studio truyền hình/sân khấu/phòng họp/ngoài trời/...)"
    )
    environment_details: Optional[EnvironmentDetails] = Field(None,
        alias='env_detail'
        # description="Chi tiết môi trường"
    )
    context_mood: Optional[str] = Field(None,
        alias='ctx_mood'
        # description="Không khí chung của khung hình"
    )

class SceneGraph(BaseModel):
    scene_id: str = Field(...,
        # description="UUID duy nhất cho scene graph"
    )
    scene_desription: SceneDescription = Field(...,
        alias='scene_des'
        # description="Thông tin về cảnh quan ảnh"
    )
    entities: list[Entity] = Field(...,
        # description="Danh sách các thực thể trong scene"
    )
    relations: list[Relation] = Field(...,
        # description="Danh sách các mối quan hệ giữa các thực thể"
    )
    



class VisualCaption(BaseModel):
    caption: str = Field(..., description="Nội dung mô tả hình ảnh sinh động chi tiết")
    keyframe_number: int = Field(
        ...,
        description="Số thứ tự của khung hình (keyframe) trong video"
    )


class OutputVisualCaption(BaseModel):
    visual_caption: list[VisualCaption] = Field(
        ...,
        description="Nội dung mô tả hình ảnh sinh động chi tiết, bao gồm các đối tượng, hành động và bối cảnh trong khung hình."
    )


    


class AnalysisStartEvent(StartEvent):
    image_paths: list[str]
    asr_text: str


class CaptionAndImageEvent(Event):
    keyframe_number: str
    visual_caption: str
    image_path: str
    asr_text: str


class AllCaptionGeneratedEvent(Event):
    """An event to signal that all captions have been generated and sent."""
    caption_count: int


class SceneGraphGeneratedEvent(Event):
    """Event carrying a fully generated SceneGraph."""
    scene_graph: SceneGraph

class AnalysisCompleteEvent(StopEvent):
    """Final event holding all the generated scene graphs."""
    scene_graphs: List[SceneGraph]





class DebugIntermediate(Event):
    caption_image_event: CaptionAndImageEvent
    scene_graph: SceneGraph

class IntermediateResultEvent(Event):
    result: DebugIntermediate
class DebugEndEvent(StopEvent):
    end_result : list[DebugIntermediate]

class AllCaptionsDispatchedEvent(Event):
    caption_count: int





if __name__ == "__main__":
    
    print(EntityAttributes.model_json_schema())



# class KeyframeAnalysis(BaseModel):
#     """
#     Bước đầu ra 1: Building a visual caption and scene graph from keyframe
#     """

#     keyframe_number: int = Field(
#         ...,
#         description="Số thứ tự của khung hình (keyframe) trong video"
#     )

#     visual_caption: VisualCaption = Field(
#         ...,
#         description="Nội dung mô tả hình ảnh sinh động chi tiết, bao gồm các đối tượng, hành động và bối cảnh trong khung hình."
#     )

#     scene_graph: SceneGraph = Field(..., description="Scene Graph của khung hình")
    


# class OutputStep1(BaseModel):
#     """
#     Bước đầu ra 1: Building a visual caption and scene graph from keyframe
#     """
#     keyframe_analysis: list[KeyframeAnalysis] = Field(
#         ...,
#         description="Phân tích khung hình để tạo mô tả hình ảnh và scene graph"
#     )
    


