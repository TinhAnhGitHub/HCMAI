from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, List





class Position(BaseModel): 
    pos2d: str | None = Field(..., description="Vị trí tương quan 2D trong khung hình, ví dụ: 'ở góc dưới bên phải', 'giữa khung hình'.")
    pos3d: str | None = Field(..., description="Vị trí tương quan trong không gian 3D hoặc chiều sâu khung cảnh, ví dụ: 'xa phía sau', 'gần camera'.")


class Object(BaseModel):
    vis: str | None = Field(..., description="Ngoại hình vật thể như màu sắc, hình dạng, chất liệu, kích thước, ví dụ: 'màu đỏ, hình trụ', 'vỏ kim loại, cao khoảng 1m'.  Và một số đặc trưng nổi bật của vật thể")
    func: str | None = Field(..., description="Chức năng hoặc mục đích sử dụng của vật thể, ví dụ: 'ghế để ngồi', 'thiết bị ghi hình'. (dựa vào ngoại hình và đoạn ASR đi kèm) ")


class Human(BaseModel):
    clothing: str   | None = Field(..., description="Trang phục bên ngoài như áo, quần, mũ, phụ kiện, ví dụ: 'áo vest đen, đeo kính', 'mặc đồng phục học sinh'. Bạn có thể diễn tả gì đó nổi bật)")
    vis: str  | None = Field(..., description="Ngoại hình người bao gồm giới tính, độ tuổi, dáng người, trạng thái mặt, tư thế, ví dụ: 'nam, khoảng 30 tuổi, tóc ngắn', 'nữ U20, đang cười tươi'.")
    role: str  | None = Field(..., description="Vai trò của người đó trong bối cảnh, ví dụ: 'người thuyết trình', 'người tham gia biểu diễn'. (dựa vào ngoại hình và đoạn ASR đi kèm) ")


class HumanGroup(BaseModel):
    role: Optional[str] = Field(None, description="Vai trò chung của nhóm người, ví dụ: 'ban giám khảo', 'đội cổ vũ'.")
    clothing: Optional[str] = Field(None, description="Đặc điểm trang phục chung nếu có, ví dụ: 'đồng phục trắng', 'áo sơ mi xanh'.")
    vis: Optional[str] = Field(None, description="Ngoại hình chung của nhóm người, ví dụ: 'nhóm nữ', 'người cao tuổi'.")
    des: str  | None = Field(..., description="Mô tả nổi bật chung của nhóm người, ví dụ: 'ngồi hàng ghế đầu', 'đứng quanh bục phát biểu'.")
    amount: str  | None = Field(..., description="Số lượng ước tính của nhóm người, ví dụ: 'khoảng 5 người', 'hơn 10 người'.")


class ObjectGroup(BaseModel):
    vis: Optional[str] = Field(None, description="Ngoại hình chung của nhóm vật thể, ví dụ: 'màu đỏ, cùng kích thước nhỏ'.")
    func: Optional[str] = Field(None, description="Chức năng chung của nhóm vật thể, ví dụ: 'ghế ngồi', 'đèn chiếu sáng'.")
    des: str = Field(..., description="Đặc điểm chung của nhóm vật thể, ví dụ: 'xếp thành hàng', 'nằm gần sân khấu'.")
    amount: str = Field(..., description="Số lượng vật thể, ví dụ: '3 chiếc', 'hơn 10 cái'.")


class Iden(BaseModel):
    name: Optional[str] = Field(None, description="Tên riêng cụ thể, ví dụ: 'Nguyễn Văn A', 'Trần Tuấn Anh'. Nếu không có hãy bỏ qua")
    label: Optional[str] = Field(None, description="Tên gọi chung của vật/thể, ví dụ: 'người tham gia', 'máy ảnh'.")
    brand: Optional[str] = Field(None, description="Tên thương hiệu, ví dụ: 'Sony', 'Adidas'.")


Attribute = Union[Human, Object, HumanGroup, ObjectGroup]


class Entity(BaseModel): 
    id_: str = Field(..., description="ID duy nhất cho thực thể, ví dụ: 'E1', 'ent_01'.")
    iden: Optional[Iden] = Field(None, description="Thông tin định danh của thực thể (nếu có).")
    pos: Position | None = Field(..., description="Vị trí 2D và 3D của thực thể trong khung hình.")
    attr: Attribute  = Field(..., description="Thông tin thuộc tính, có thể là người, vật, nhóm người hoặc nhóm vật.")


class OCR(BaseModel):
    content: str = Field(..., description="Nội dung văn bản OCR được quét, ví dụ: 'Trường Đại học Bách Khoa'.")
    des: Optional[str] = Field(None, description="Mô tả nội dung của đoạn văn bản OCR, ví dụ: 'Tên tổ chức giáo dục'.")


class Rel(BaseModel):
    subj: str = Field(..., description="ID của chủ thể trong quan hệ, ví dụ: 'E1'.")
    obj: str = Field(..., description="ID của đối tượng bị tác động, ví dụ: 'E2'.")
    type_rel: str = Field(..., description="Loại quan hệ giữa các thực thể, ví dụ: 'hành động', 'vị trí'.")
    des: str = Field(..., description="Mô tả chi tiết của quan hệ, ví dụ: 'đứng cạnh', 'đang nói chuyện với'.")


# class Graph(BaseModel):
#     subj: str = Field(..., description="ID của chủ thể trong quan hệ, ví dụ: 'E1'.")
#     obj: str = Field(..., description="ID của đối tượng bị tác động, ví dụ: 'E2'.")
#     rel: Rel = Field(..., description="Thông tin về mối quan hệ giữa chủ thể và đối tượng.")


class Background(BaseModel):
    description: str = Field(..., description="Mô tả khung cảnh nền, ví dụ: 'phòng họp đông người', 'sân khấu ngoài trời vào buổi tối'.")


class SceneGraph(BaseModel):
    sce_id: str = Field(..., description="ID duy nhất của SceneGraph, ví dụ: 'scene_{keyframe number}'.")
    sce_des: str = Field(..., description="Mô tả tổng quan về khung cảnh, ví dụ: 'buổi lễ khai mạc diễn ra trong hội trường lớn'.")
    ents: List[Entity] = Field(..., description="Danh sách các thực thể trong cảnh.")
    rels: List[Rel] = Field(..., description="Danh sách các quan hệ giữa các thực thể.")
    ocr: Optional[List[OCR]] = Field(None, description="Danh sách các đoạn văn bản OCR (nếu có).")


class VisCap(BaseModel):
    caption: str = Field(...)
    keyframe_number: int = Field(...)


class VisSceneCap(BaseModel):
    vis_cap: List[VisCap] = Field(..., description="Danh sách caption mô tả theo từng keyframe.")




if __name__ == "__main__":

    print(VisSceneCap.model_json_schema())