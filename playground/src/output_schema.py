from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, List
from llama_index.core.workflow import Event, StartEvent, StopEvent



class Position2D(BaseModel):
    relative_description: str = Field(
        ...,
        description="Mô tả vị trí tương đối 2D trong khung hình. Ví dụ: 'góc trái trên', 'chính giữa', 'phía trước'."
    )
    


class Position3D(BaseModel):
    relative_description: str = Field(
        ...,
        description=(
           "Mô tả vị trí tương đối của đối tượng trong không gian 3D bằng ngôn ngữ tự nhiên"
        )
    )
    

class ObjectVisual(BaseModel):
    """
    Dùng để miêu tả các đặc trưng nhận dạng trực quan của vật thể (object).
    Cho phép sử dụng mô tả tự nhiên, gần gũi với cách con người quan sát và nhận biết.
    """
    color: Optional[list[str]] = Field(
        None,
        description=(
            "Màu sắc chính và phụ của vật thể. "
            "Có thể diễn đạt theo cách tự nhiên"
        )
    )
    shape: Optional[str] = Field(
        None,
        description=(
            "Hình dạng tổng thể của vật thể. "
            
        )
    )
    material: Optional[str] = Field(
        None,
        description=(
            "Chất liệu hoặc cảm giác bề mặt của vật thể khi nhìn hoặc chạm vào. "
            ""
        )
    )
    texture: Optional[str] = Field(
        None,
        description=(
            "Kết cấu bề mặt hoặc cảm nhận khi nhìn thấy bề mặt. "
            
        )
    )
    size_estimation: Optional[str] = Field(
        None,
        description=(
            "Ước lượng kích thước tổng thể của vật thể. "
        )
    )
    details: str = Field(
        ...,
        description=(
            "Mô tả thêm về các đặc điểm chi tiết khác của vật thể nếu có. "
        )
    )

    functionality: str = Field(
        ..., description=(
            "Chức năng hoặc mục đích sử dụng của vật thể. "
        ))

    



class TextContent(BaseModel):
    content: str = Field(..., description="Nội dung OCR có trên khung hình/vật thể/...")
    description: str = Field(..., description="ý nghĩa của nội dung OCR.")
    
    


class ClothingAttributes(BaseModel):
    top: ObjectVisual | None= Field(..., description="Mô tả chi tiết phần thân trên")
    bottom: ObjectVisual | None = Field(..., description="Mô tả chi tiết phần thân dưới")
    headwear: Union[ObjectVisual, Optional[TextContent]] | None = Field(None, description="Mô tả chi tiết phần mũ nếu có")
    accessories: list[Union[ObjectVisual, Optional[TextContent]]] | None = Field(None, description="Mô tả chi tiết các phụ kiện nếu có")

    




class HumanVisual(BaseModel):
    gender: str = Field(..., description="Giới tính (nam, nữ)")
    age_estimation: str = Field(..., description="Độ tuổi ước tính")
    ethnicity: Optional[str] = Field(None, description="Dân tộc")
    body_type: Optional[str] = Field(None, description="Kiểu dáng cơ thể")
    hair_style: Optional[str] = Field(None, description="Kiểu tóc")
    skin_color: Optional[str] = Field(None, description="Màu da")
    posture: Optional[str] = Field(None, description="Tư thế")
    action: str = Field(..., description="Hành động đang thực hiện")
    facial_expression: Optional[str] = Field(None, description="Biểu cảm")
    role: str = Field(..., description="Vai trò")

    clothing: ClothingAttributes = Field(
        ...,
        description=(
            "Thông tin về trang phục của người"
        )
    )  
    



class GroupHumanMember(BaseModel):
    member_id: Optional[str] = Field(None, description="UUID duy nhất cho thành viên nhóm")
    description: str = Field(..., description="Mô tả ngắn gọn về thành viên này")
    human_specific: Optional[HumanVisual] = Field(None, description="Thuộc tính con người của thành viên")
    

class GroupObjectMember(BaseModel):
    member_id: Optional[str] = Field(None, description="UUID duy nhất cho vật thể trong nhóm")
    description: str = Field(..., description="Mô tả ngắn gọn về vật thể này")
    visual: Optional[ObjectVisual] = Field(None, description="Thuộc tính hình ảnh của vật thể")
    functionality: Optional[str] = Field(None, description="Chức năng cơ bản của vật thể")
    

class GroupObjectEntities(BaseModel):
    """
    Miêu tả một nhóm vật thể trong bối cảnh, dựa trên những tính chất tương đồng của các vật thể đó.
    """
    group_name: str = Field(
        ...,
        description=(
            "Tên gọi của nhóm vật thể. "
        )
    )
    group_description: str = Field(
        ...,
        description=(
            "Mô tả ngắn gọn về nhóm vật thể, bao gồm các đặc điểm chung hoặc chức năng của nhóm. "
        )
    )
    objects: List[GroupObjectMember] = Field(
        ...,
        description="Danh sách các vật thể trong nhóm, mỗi vật thể được mô tả chi tiết."
    )
    quantity: Optional[int] = Field(None, description="Số lượng ước tính các vật thể trong nhóm")

    



class GroupHumanEntities(BaseModel):
    """
    Miêu tả một nhóm con người trong bối cảnh, dựa trên những tính chất tương đồng của họ.
    """
    group_name: str = Field(
        ...,
        description=(
            "Tên gọi của nhóm người, có thể là tên chung hoặc tên riêng. "
        )
    )
    group_description: str = Field(
        ...,
        description=(
            "Mô tả ngắn gọn về nhóm người "
        )
    )
    members: List[GroupHumanMember] = Field(
        ...,
        description="Danh sách các thành viên trong nhóm, mỗi thành viên được mô tả chi tiết."
    )
    quantity: Optional[int] = Field(None, description="Số lượng ước tính các thành viên trong nhóm")
    common_attributes: Optional[HumanVisual] = Field(None, description="Các thuộc tính chung cho toàn bộ nhóm")
    

class EntityIsObject(BaseModel):
    type_discriminator: Literal["object"] = "object"
    object_details: ObjectVisual = Field(..., description="Chi tiết trực quan và chức năng của vật thể.")
    

class EntityIsHuman(BaseModel):
    type_discriminator: Literal["human"] = "human"
    human_details: HumanVisual = Field(..., description="Chi tiết trực quan và hành vi của con người.")
    


class EntityIsGroup(BaseModel):
    type_discriminator: Literal["group"] = "group"
    group_info: Union[GroupObjectEntities, GroupHumanEntities] = Field(
        ..., description="Chi tiết nhóm vật thể hoặc nhóm người."
    )
    

class EntityIsOCR(BaseModel):
    type_discriminator: Literal["ocr"] = "ocr"
    text_content: TextContent = Field(..., description="Nội dung văn bản được nhận dạng từ hình ảnh hoặc video.")
    


SpecificEntityTypeAttributes = Union[EntityIsObject, EntityIsHuman, EntityIsGroup, EntityIsOCR]


class IdentityInfo(BaseModel):
    name: Optional[str] = Field(None, description="Tên định danh của thực thể.")
    label: Optional[str] = Field(None, description="Nhãn hoặc phân loại của thực thể.")
    brand: Optional[str] = Field(None, description="Thương hiệu liên quan đến thực thể.")



class EntityAttributes(BaseModel):
    identity: Optional[IdentityInfo] = Field(None, description="Thông tin định danh  của thực thể, có thể lấy từ ảnh, ASR, ....")
    position: Optional[Union[Position2D, Position3D]] = Field(None  , description="Vị trí thực thể")
    specific_attributes: Optional[SpecificEntityTypeAttributes] = Field(
        None, description="Các thuộc tính chi tiết tùy thuộc vào loại thực thể ."
    )

    

class Entity(BaseModel):
    entity_id: str = Field(
        ...,
        description=(
            "UUID duy nhất cho thực thể "
        )
    )
    represent: Optional[str] = Field(None, description="tóm tắt trạng thái của vật thể một cách ngắn gọn nhưng sinh động nhất")
    attributes: Optional[EntityAttributes] = Field(None, description="Các thuộc tính chi tiết của thực thể")
    


class RelationAttributes(BaseModel):
    details: Optional[str] = Field(None, description="Mô tả chi tiết hơn về mối quan hệ")
    location: Optional[str] = Field(None, description="Vị trí cụ thể của mối quan hệ")
    


class Relation(BaseModel):
    relation_id: str = Field(
        ...,
        description=(
            "UUID duy nhất cho mối quan hệ. "
        )
    )
    subject_entity_id: str = Field(..., description="UUID của thực thể chủ thể")
    predicate_type: str = Field(..., description="Loại quan hệ (mặc , cằm nắm, cạnh bên, hành động, etc.)")
    object_entity_id: str  = Field(..., description="ID của thực thể đối tượng")
    relation_attributes: Optional[RelationAttributes] = Field(None, description="Thuộc tính chi tiết về mối quan hệ")
    


class BackgroundElement(BaseModel):
    description: str = Field(..., description="Mô tả chi tiết phông nền")
    colors: Optional[List[str]] = Field(None, description="Màu sắc của phông nền")
    



class EnvironmentDetails(BaseModel):
    lighting: str = Field(..., description="Chi tiết về ánh sáng")
    time_of_day: Optional[str] = Field(None, description="Thời điểm trong ngày")
    color_palette: Optional[List[str]] = Field(None, description="Màu sắc môi trường")
    event_context: Optional[str] = Field(None, description="Ngữ cảnh sự kiện")
    background_elements: Optional[List[BackgroundElement]] = Field(None, description="Các yếu tố khung hình nền")
    



class SceneDescription(BaseModel):
    type: str = Field(..., description="Loại không gian (studio truyền hình/sân khấu/phòng họp/ngoài trời/...)")
    environment_details: Optional[EnvironmentDetails] = Field(None, description="Chi tiết môi trường")
    context_mood: Optional[str] = Field(None, description="Không khí chung của khung hình")
    


class SceneGraph(BaseModel):
    scene_id: str = Field(
        ...,
        description=(
            "UUID duy nhất cho scene graph"
        )
    )
    entities: List[Entity] = Field(..., description="Danh sách các thực thể trong scene")
    relations: List[Relation] = Field(..., description="Danh sách các mối quan hệ giữa các thực thể")
    



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
    ast_text: str


class CaptionAndImageEvent(Event):
    keyframe_number: int
    visual_caption: str
    image_path: str


class AllCaptionGeneratedEvent(Event):
    """An event to signal that all captions have been generated and sent."""
    caption_count: int


class SceneGraphGeneratedEvent(Event):
    """Event carrying a fully generated SceneGraph."""
    scene_graph: SceneGraph

class AnalysisCompleteEvent(StopEvent):
    """Final event holding all the generated scene graphs."""
    scene_graphs: List[SceneGraph]









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
    


