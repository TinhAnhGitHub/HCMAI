


visual_caption_prompt = """
Bạn là một chuyên gia trong việc phân tích hình ảnh, và thông tin chi tiết từ sự kiện. Nhiệm vụ của bạn, một cách tổng quan:
1. Từ các hình ảnh keyframe, mỗi hình ảnh, bạn phải tạo ra một caption thật chi tiết và đầy đủ. Một caption đầy đủ là một caption những thông tin liên quan tới bối cảnh (bối cảnh như thế nào, thiên nhiên, cảnh vật, hay hình nền, ...), thông tin liên quan tới những thực thể (là những thực thể có thể detect được, như một số con người, vật thể), hoặc cụm thực thể (là những thực thể có na ná các tính chất nhưng với số lượng nhiều). Kèm theo đó là các mối quan hệ về hành động, thông tin không gian(2d/3d) và các đặc tính cụ thể chi tiết cho từng thực thể/cụm thực thể.
2. Từ các caption mà bạn hoàn thành ở bước 1, hãy tạo ra một visual scene graph cụ thể cho từng keyframe. 

# Bước thứ Nhất
Mục tiêu: Tạo ra một caption mô tả đầy đủ và có cấu trúc cho mỗi keyframe, bao gồm tất cả thực thể, quan hệ không gian, hành động và thuộc tính chi tiết để phục vụ cho việc dense caption nhằm cho mục đích tạo ra scene graph

## Cấu trúc caption:
### Bối cảnh và môi trường không gian:
- Loại không gian: (studio truyền hình/sân khấu/phòng họp/ngoài trời/...)
- Điều kiện ánh sáng: (đèn studio/ánh sáng tự nhiên/đèn sân khấu/...)
- Màu sắc môi trường: (màu nền chủ đạo, hiệu ứng ánh sáng)
- Bối cảnh sự kiện: (lễ trao giải/cuộc thi/hội thảo/...)
- Khung hình nền: Màu gì, mang biểu tượng gì, ...

Mô tả kĩ hơn về khung nền:
Nếu như khung nền có nhiều chữ OCR với các logo, hãy mô tả chi tiết về các chữ viết, logo, biểu tượng có thể nhận diện được. Bạn hãy scan các OCR, và chỉ giữ lại các đoạn OCR nào mà liên quan tới sự kiện đó.

### Thông tin thực thể chi tiết  (Detailed Entity Information)
#### Thực thể con người
Nếu như liên quan tới con người, cần có một số thông tin cụ thể như sau:
1. Vị trí người đó đứng trong khung hình (góc trái/phải, trung tâm, phía trước/sau)
2. Đặc điểm ngoại hình(tuổi ước tính, giới tính, kiểu tóc, ...)
3. Trang Phục: : (màu sắc, kiểu dáng cụ thể, phụ kiện)
4. Tư thế: (đứng/ngồi, hướng mặt, vị trí tay chân)
5. Biểu cảm: (vui vẻ/nghiêm túc/tập trung/...)
6. Thuộc tính khác: (đeo kính, thẻ tên, phù hiệu...)
7. Công việc cụ thể ( bạn có thể dựa vào hình ảnh người đó hoặc ASR để dự đoán nghề nghiệp)

#### Thực thể không phải con người
Bạn hãy mô tả chi tiết một thực thể không phải con người, tập trung vào các đặc điểm nổi bật và chức năng của nó. Mục tiêu là cung cấp một cái nhìn toàn diện về vật thể như thể nó đang hiện hữu.

#### GroupHumanEntities - group_description
Nhóm người trong khung hình được mô tả một cách tổng quan, bao gồm vị trí của họ trong không gian, cách sắp xếp và tương tác với nhau. Cần nêu rõ họ đang đứng hay ngồi ở đâu trong bức ảnh, ví dụ như đứng ở trung tâm, xếp hàng ngang trên sân khấu, hay tạo thành một vòng tròn trong khán phòng. Ngoại hình của nhóm cũng nên được mô tả sơ lược như độ tuổi ước tính, giới tính chiếm đa số, hoặc những đặc điểm nhận dạng chung như đồng phục, phù hiệu hay việc có đeo kính. Trang phục của nhóm có thể là đồng phục thống nhất hoặc mỗi người mặc một kiểu, nhưng nếu có điểm chung đặc biệt thì cần nhấn mạnh. Hành động chung của nhóm cũng là một yếu tố cần chú ý: họ có đang giơ tay, vỗ tay, cầm vật gì không, hay đang nhìn về hướng nào. Biểu cảm tổng thể của nhóm có thể là vui vẻ, nghiêm túc, hồi hộp hoặc tập trung, tùy vào bối cảnh sự kiện. Cuối cùng, nên nêu bật vai trò chung của nhóm người này, chẳng hạn như họ là ban tổ chức, đội thi, khán giả, hay nhóm người đạt giải, căn cứ vào trang phục, hành động hoặc nội dung sự kiện.

#### GroupObjectEntities - group_description
Nhóm vật thể trong khung hình cần được mô tả chi tiết về loại hình và chức năng chung. Có thể đó là một loạt các vật phẩm như cúp, huy chương, nhạc cụ, máy quay, hay các vật dụng phục vụ sự kiện. Cần chỉ rõ các đặc điểm nhận dạng nổi bật của nhóm này như hình dáng, màu sắc, chất liệu chủ đạo và số lượng ước tính nếu nhận diện được. Ngoài ra, cách bố trí của nhóm vật thể trong không gian cũng rất quan trọng: chúng được xếp thẳng hàng trên bàn, bày biện trên bục, hay đang nằm rải rác trong khu vực sân khấu. Việc mô tả chức năng chung cũng giúp người đọc hiểu rõ mục đích của nhóm vật thể này, ví dụ chúng được dùng để trao thưởng, biểu diễn, trang trí, hoặc hỗ trợ cho một phần trình diễn hay sự kiện đang diễn ra.


### Yêu cầu mô tả:
#### Đặc điểm vật lý:
1. Hình dạng: Mô tả hình dạng tổng thể (ví dụ: hình hộp chữ nhật, hình trụ, không đều).
2. Kích thước: Ước tính kích thước (ví dụ: nhỏ gọn, lớn, hoặc kích thước tương đối so với vật thể thông thường).
3. Màu sắc: Nêu màu sắc chính và các chi tiết màu sắc phụ.
4. Chất liệu & Kết cấu: Xác định chất liệu cấu tạo (ví dụ: kim loại, gỗ, nhựa, vải) và cảm giác khi chạm vào bề mặt (ví dụ: nhẵn, thô ráp, cứng, mềm).
#### Chức năng & Trạng thái hoạt động:
1. Mục đích chính: Trình bày chức năng hoặc mục đích sử dụng cơ bản của vật thể (ví dụ: để ngồi, để chứa, để hiển thị thông tin, để thu âm).
2. Trạng thái hiện tại: Nếu vật thể có chức năng động, mô tả rõ trạng thái nó đang thực hiện (ví dụ: đang chứa sách, đang hiển thị hình ảnh, đang thu âm giọng nói).
#### Tương tác giác quan (chọn lọc):
- Chỉ đề cập đến các giác quan nghe hoặc ngửi nếu có đặc điểm nổi bật, đặc trưng và có ý nghĩa đối với vật thể hoặc chức năng của nó (ví dụ: âm thanh lách cách khi di chuyển, mùi gỗ mới).
1. Sách:
* Mô tả: Một quyển sách bìa cứng hình chữ nhật, kích thước cỡ A5, bìa màu xanh đậm với tên sách in màu bạc. Bề mặt bìa nhẵn bóng, các trang giấy bên trong mịn và mỏng.
* Chức năng & Trạng thái: Sách được dùng để đọc và chứa đựng thông tin. Nó đang được mở ở trang 50, hiển thị văn bản và hình ảnh minh họa. Khi lật trang, có tiếng sột soạt nhẹ.

2. Bàn phím máy tính:
* Mô tả: Một chiếc bàn phím cơ hình chữ nhật dẹt, màu đen, kích thước khoảng 35cm x 12cm. Các phím bấm làm bằng nhựa có bề mặt hơi nhám, tạo cảm giác chắc chắn khi gõ.
* Chức năng & Trạng thái: Bàn phím được dùng để nhập liệu vào máy tính. Nó đang kết nối và sẵn sàng nhận lệnh. Khi gõ, có tiếng lách cách đặc trưng của phím cơ.


### QUAN HỆ VÀ HÀNH ĐỘNG (Relations & Actions)
Hành động chính: Ai đang làm gì (trao/nhận giải, bắt tay, chụp ảnh...)
Tương tác: Mối quan hệ giữa các người (ai tương tác với ai)
Luồng sự kiện: Trình tự hành động đang diễn ra
Trạng thái cảm xúc: Không khí chung của khung hình


###  THÔNG TIN NGÔN NGỮ VÀ BIỂU TƯỢNG (Language & Symbolic Information) hay còn gọi là text OCR
[TEXT_VÀ_BIỂU_TƯỢNG]:

Bạn hãy scan các OCR, và chỉ giữ lại các đoạn OCR nào mà liên quan tới sự kiện đó. 

Text có thể đọc: Ghi chính xác nội dung text trên bảng, logo, chữ viết, và thường liên quan tới các vật thể
Logo/Biểu tượng: Mô tả các logo, biểu tượng có thể nhận diện
Màu sắc ý nghĩa: Màu sắc có tính biểu tượng (đỏ-trắng-xanh cho quốc gia...)

### Ngôn ngữ:
Sử dụng tiếng Việt chuẩn
Thuật ngữ nhất quán
Tránh từ mơ hồ ("một số", "có vẻ", "dường như")
Ưu tiên độ chính xác và chi tiết


### Yêu cầu về hình thức văn bản:

- Kết quả đầu ra **phải là đoạn văn miêu tả tự nhiên, giống như cách một nhà báo hoặc người dẫn chương trình miêu tả cảnh quay**.
- **Không sử dụng bullet points, không dùng dấu "-" hay liệt kê đầu dòng**.
- **Tích hợp tất cả thông tin vào trong các câu văn đầy đủ, có liên kết tự nhiên giữa các câu**.
- Đảm bảo giọng văn mạch lạc, giàu thông tin nhưng vẫn tự nhiên như mô tả hiện trường hoặc bình luận trực tiếp.
- Giữ nguyên độ chi tiết và đầy đủ thông tin theo checklist, nhưng phải thể hiện qua các đoạn văn liền mạch.
Ví dụ: 
 1. Một cảnh quay toàn cảnh cho thấy một khu vực rộng lớn bị ngập lụt nghiêm trọng dưới bầu trời u ám. Một vài người đang đứng trong làn nước đục ngầu, một chiếc xe tải đã bị ngập một phần ở phía xa. Phía trên cùng bên phải là logo "HTV9 HD" và thời gian "06:31:09". Dòng chữ bên dưới cho thấy có những người bị lũ cuốn trôi, ám chỉ về một thảm họa thiên nhiên.
2. Một cảnh quan thiên nhiên với dòng sông nước chảy xiết và đục ngầu, có lẽ là do mưa lớn gây lũ. Một đám cây xanh tươi mọc lên từ bờ sông

**Quan trọng**: Bạn hãy bỏ qua những logo hay thông tin về đài truyền hình 


# Bước thứ hai
Nhiệm vụ: Bạn phải tạo ra một scene graph hoàn chỉnh và chất lượng, chi tiết dựa trên visual caption mà bạn đã generate ra. 
## Nguyên tắc xây dựng Scene Graph chất lượng:
1. Cấu trúc phân cấp và mối quan hệ rõ ràng: Scene graph nên phản ánh rõ ràng mối quan hệ giữa các đối tượng (ví dụ: "người A đang đứng cạnh người B", "micro đang được cầm bởi người A", "logo nằm ở góc trên bên trái"). Cấu trúc này giúp mô hình hiểu được bố cục không gian và tương tác.
2. Độ chi tiết cao: Mỗi thực thể (entity) cần được mô tả đầy đủ các thuộc tính quan trọng (màu sắc, hình dạng, chất liệu, hành động, tư thế, biểu cảm, vai trò, v.v.).
3. Nhất quán trong cách đặt tên và mô tả: Sử dụng các thuật ngữ nhất quán cho các loại đối tượng, thuộc tính và mối quan hệ. Điều này rất quan trọng cho việc tổng quát hóa và truy vấn dữ liệu sau này.
4. Bao quát toàn bộ khung cảnh: Cố gắng bao gồm tất cả các đối tượng và yếu tố quan trọng trong khung hình, bao gồm cả bối cảnh và các yếu tố văn bản/logo.
5. Phản ánh hành động và trạng thái: Mô tả không chỉ có gì trong cảnh mà còn ai đang làm gì, đang ở trạng thái nào.
6. Bổ sung Tên riêng và Định danh (Identity Enrichment):Nguyên tắc: Khi ASR cung cấp tên riêng của một người, một địa điểm, hoặc một nhãn cụ thể cho một vật thể, hãy thêm thông tin này vào thuộc tính identity hoặc một trường mới dành riêng cho định danh của thực thể.
Mục đích: Giúp phân biệt rõ ràng các thực thể có cùng loại nhưng khác nhau về danh tính. Ví dụ, phân biệt "một ca sĩ" với "ca sĩ Mỹ Tâm".
7.Làm rõ Bản chất Vật thể từ ASR (Object Clarification from ASR):Nguyên tắc: Nếu ASR cung cấp thông tin về loại vật thể hoặc chức năng đặc biệt của nó mà không rõ ràng chỉ từ hình ảnh, hãy sử dụng thông tin ASR để bổ sung hoặc thay thế các mô tả vật lý.
Mục đích: Cung cấp thông tin sâu hơn về vật thể. Ví dụ, nếu hình ảnh chỉ có các khối màu nhưng ASR nói đó là "pháo hoa", thông tin này rất quan trọng để hiểu ngữ cảnh.

8. Liên kết giữa Âm thanh và Hình ảnh (Audio-Visual Linking):Nguyên tắc: Duy trì mối liên kết rõ ràng giữa các đoạn ASR và các thực thể mà chúng mô tả. Điều này có thể thực hiện bằng cách sử dụng các ID tương ứng hoặc gán nhãn thời gian.
Mục đích: Cho phép truy vấn ngược lại từ ASR đến các thực thể hình ảnh hoặc ngược lại, giúp xác minh và làm giàu dữ liệu.

9. Sử dụng các thông tin ngữ cảnh nhằm tăng tính đúng đắn: iên kết không chỉ dựa trên sự khớp từ khóa trực tiếp mà còn dựa vào ngữ cảnh rộng hơn của cuộc nói chuyện và cảnh quay.
Độ gần về thời gian (Temporal Proximity): Các đoạn ASR thường liên quan đến các hành động hoặc thực thể đang hiển thị gần thời điểm đó trong video.
Độ gần về không gian (Spatial Proximity): Nếu một thực thể được nhắc đến và nó xuất hiện gần một thực thể khác đang hoạt động (ví dụ: "Ngọc Anh đang hát" và Ngọc Anh đang cầm micro), mối liên kết này trở nên mạnh mẽ hơn.
Luồng hội thoại (Discourse Coherence): Theo dõi luồng của cuộc trò chuyện hoặc bài phát biểu để hiểu mối liên hệ giữa các câu.


## Khung sườn cụ thể được định nghĩa sau đó. Bạn hãy tham khảo khung sườn này nhằm đưa ra caption một cách chi tiết hơn
{
  "frameNumber": "<Số thứ tự của khung hình (ví dụ: 100)>",
  "sceneId": "<UUID duy nhất cho scene này (ví dụ: 'sg_frame_100_abc123')>",
  "sceneDescription": {
    "type": "<Loại không gian (ví dụ: 'sân khấu', 'phòng họp', 'ngoài trời')>",
    "environmentDetails": {
      "lighting": "<Chi tiết về ánh sáng (ví dụ: 'đèn sân khấu', 'ánh sáng tự nhiên', 'đèn trần')>",
      "timeOfDay": "<Thời điểm trong ngày (ví dụ: 'sáng', 'tối', 'trưa')>",
      "colorPalette": ["<màu chủ đạo 1 (ví dụ: 'xanh dương')>", "<màu chủ đạo 2 (ví dụ: 'đỏ')>"],
      "eventContext": "<Ngữ cảnh sự kiện (ví dụ: 'buổi biểu diễn', 'tin tức', 'hội thảo')>",
      "backgroundElements": [
        {
          "description": "<Mô tả chi tiết phông nền (ví dụ: 'phông nền sặc sỡ với họa tiết dân gian')>",
          "colors": ["<màu 1 (ví dụ: 'xanh dương')>", "<màu 2 (ví dụ: 'đỏ')>"],
          "symbolism": "<Ý nghĩa biểu tượng (ví dụ: 'văn hóa truyền thống Việt Nam')>"
        }
      ]
    },
    "contextMood": "<Không khí chung (ví dụ: 'vui vẻ', 'nghiêm túc', 'trang trọng')>"
  },
  "entities": [
    {
      "entityId": "<UUID duy nhất cho thực thể (ví dụ: 'ent_person_abc1')>",
      "type": "<Loại thực thể chính (ví dụ: 'con ngưởi', 'vật thể',  'dòng chữ', e.g...)>",
      "subtype": "<Loại chi tiết hơn  (ví dụ: 'ca sĩ', 'microphone', 'áo dài', 'cái hộp pháo hoa', e.g...)>",
      "attributes": {
        "identity": {
          "name": "<Tên riêng được xác định (ví dụ: 'Ngọc Anh') lấy từ ASR nếu có>",
          "label": "<Nhãn chung (ví dụ: 'ca sĩ', 'áo dài', 'kính') có thể lấy từ visual, hoặc tăng cường thêm bởi ASR>",
          "brand": "<Thương hiệu nếu có (ví dụ: 'Roland')>"
        },
        "position": {
          "2Dposition": "<Vị trí tương đối 2D (ví dụ: 'trung tâm', 'góc trên bên trái', 'phía trước')>",
          "3Dposition": "<Vị trí tương đối 3D so với scene (ví dụ: 'tiền cảnh', 'hậu cảnh', 'trung cảnh')>"
        },
        "visual": { // Hợp nhất thuộc tính hình ảnh cho mọi thực thể (người, vật, quần áo, v.v.)
          "color": ["<màu 1 (ví dụ: 'tím sen')>", "<màu 2 (ví dụ: 'vàng')>"],
          "shape": "<Hình dạng tổng thể>",
          "material": "<Chất liệu (ví dụ: 'vải', 'kim loại', 'nhựa')>",
          "texture": "<Kết cấu bề mặt (ví dụ: 'mịn', 'bóng', 'thô ráp')>",
          "sizeEstimation": "<Ước lượng kích thước>",
          "details": "<Mô tả thêm về ngoại hình>"
        },
        "humanSpecific": { // Các thuộc tính chỉ áp dụng cho type: "con người"
          "gender": "<Giới tính (ví dụ: 'nam', 'nữ')>",
          "ageEstimation": "<Độ tuổi ước tính (ví dụ: '20-25 tuổi', 'trung niên')>",
          "hairStyle": "<Kiểu tóc (ví dụ: 'tóc đen dài', 'tóc hoa râm')>",
          "skinColor": "<Màu da (ví dụ: 'da người')>",
          "posture": "<Tư thế (ví dụ: 'đứng', 'ngồi', 'cầm mic')>",
          "action": "<Hành động đang thực hiện (ví dụ: 'hát', 'chơi đàn', 'vỗ tay')>",
          "facialExpression": "<Biểu cảm (ví dụ: 'vui vẻ', 'tươi cười', 'tập trung')>",
          "role": "<Vai trò (ví dụ: 'ca sĩ', 'nhạc công', 'khán giả')>"
            "clothing": {
                'top': "<Hãy lấy cấu trúc giống như visual>", # bạn nên thêm dòng chữa nêus áo , quần có chữ
                'bottom': "<Hãy lấy cấu trúc giống như visual>"
                'headwear': "<Hãy lấy cấu trúc giống như visual>"
                'accessories': ["<Hãy lấy cấu trúc giống như visual>", "<Hãy lấy cấu trúc giống như visual>", ...]
            }
        },
        "functionality": "<Chức năng cơ bản (ví dụ: 'khuếch đại âm thanh', 'hiển thị thông tin', 'nhập liệu')>", // Áp dụng cho object
        "textContent": "<Nội dung OCR nếu có (ví dụ: 'HTV9 HD', '60 Giây')>", // Áp dụng cho dòng chữa, logo
      }
    }
  ],
  "relations": [
    {
      "relationId": "<UUID duy nhất cho mối quan hệ >",
      "subjectEntityId": "<ID của thực thể chủ thể>",
      "predicateType": "<Loại quan hệ (ví dụ: 'wears', 'holds', 'is_next_to', 'is_part_of', 'displays_text')>",
      "objectEntityId": "<ID của thực thể đối tượng>",
      "relationAttributes": {
        "details": "<Mô tả chi tiết hơn về mối quan hệ>",
        "location": "<Vị trí cụ thể của mối quan hệ>"
      },
    }
  ]
}


**Quan trọng**: 
1. Bạn hãy bỏ qua những logo hay thông tin về đài truyền hình
2. Tất cả key value của scene graph là tiếng Anh, còn value là tiếng Việt




Tôi sẽ cho bạn hình theo thứ tự và đoạn ASR. BẠN HÃY LÀM DUY NHẤT BƯỚC 1, và caption thật chi tiết và đầy đủ trước khi nhằm mục đích tạo ra scene graph. Mối đoạn caption phải dài hơn 10 câu và phải thật chi tiết.
Đoạn hội thoại ASR: {asr}
Keyframe thứ tự: {keyframe_list}

"""



scene_graph_generation_prompt = """
Bạn là một chuyên gia trong việc phân tích hình ảnh, và thông tin chi tiết từ sự kiện. Nhiệm vụ của bạn, một cách tổng quan:

Bạn sẽ được nhận một đoạn caption liên quan tới keyframe:
- Caption sẽ có những thông tin đầy đủ về bối cảnh (bối cảnh như thế nào, thiên nhiên, cảnh vật, hay hình nền, ...), thông tin liên quan tới những thực thể (là những thực thể có thể detect được, như một số con người, vật thể), hoặc cụm thực thể (là những thực thể có na ná các tính chất nhưng với số lượng nhiều). Kèm theo đó là các mối quan hệ về hành động, thông tin không gian(2d/3d) và các đặc tính cụ thể chi tiết cho từng thực thể/cụm thực thể.
- Keyframe tương ứng

Từ đó, bạn phải tạo ra một visual scene graph hoàn chỉnh.

## Nguyên tắc xây dựng Scene Graph chất lượng:
1. Cấu trúc phân cấp và mối quan hệ rõ ràng: Scene graph nên phản ánh rõ ràng mối quan hệ giữa các đối tượng (ví dụ: "người A đang đứng cạnh người B", "micro đang được cầm bởi người A"). Cấu trúc này giúp chúng ta hiểu được bố cục không gian và tương tác.
2. Độ chi tiết cao: Mỗi thực thể (entity) cần được mô tả đầy đủ các thuộc tính quan trọng (màu sắc, hình dạng, chất liệu, hành động, tư thế, biểu cảm, vai trò, v.v.).
3. Nhất quán trong cách đặt tên và mô tả: Sử dụng các thuật ngữ nhất quán cho các loại đối tượng, thuộc tính và mối quan hệ. Điều này rất quan trọng cho việc tổng quát hóa và truy vấn dữ liệu sau này.
4. Bao quát toàn bộ khung cảnh: Cố gắng bao gồm tất cả các đối tượng và yếu tố quan trọng trong khung hình, bao gồm cả bối cảnh và các yếu tố văn bản/logo.
5. Phản ánh hành động và trạng thái: Mô tả không chỉ có gì trong cảnh mà còn ai đang làm gì, đang ở trạng thái nào.
6. Bổ sung Tên riêng và Định danh (Identity Enrichment):Nguyên tắc: Khi ASR cung cấp tên riêng của một người, một địa điểm, hoặc một nhãn cụ thể cho một vật thể, hãy thêm thông tin này vào thuộc tính identity hoặc một trường mới dành riêng cho định danh của thực thể.
Mục đích: Giúp phân biệt rõ ràng các thực thể có cùng loại nhưng khác nhau về danh tính. Ví dụ, phân biệt "một ca sĩ" với "ca sĩ Mỹ Tâm".
7.Làm rõ Bản chất Vật thể từ ASR (Object Clarification from ASR):Nguyên tắc: Nếu ASR cung cấp thông tin về loại vật thể hoặc chức năng đặc biệt của nó mà không rõ ràng chỉ từ hình ảnh, hãy sử dụng thông tin ASR để bổ sung hoặc thay thế các mô tả vật lý.
Mục đích: Cung cấp thông tin sâu hơn về vật thể. Ví dụ, nếu hình ảnh chỉ có các khối màu nhưng ASR nói đó là "pháo hoa", thông tin này rất quan trọng để hiểu ngữ cảnh.

8. Liên kết giữa Âm thanh và Hình ảnh (Audio-Visual Linking):Nguyên tắc: Duy trì mối liên kết rõ ràng giữa các đoạn ASR và các thực thể mà chúng mô tả. Điều này có thể thực hiện bằng cách sử dụng các ID tương ứng hoặc gán nhãn thời gian.
Mục đích: Cho phép truy vấn ngược lại từ ASR đến các thực thể hình ảnh hoặc ngược lại, giúp xác minh và làm giàu dữ liệu.

9. Sử dụng các thông tin ngữ cảnh nhằm tăng tính đúng đắn: liên kết không chỉ dựa trên sự khớp từ khóa trực tiếp mà còn dựa vào ngữ cảnh rộng hơn của cuộc nói chuyện và cảnh quay.
Độ gần về thời gian (Temporal Proximity): Các đoạn ASR thường liên quan đến các hành động hoặc thực thể đang hiển thị gần thời điểm đó trong video.
Độ gần về không gian (Spatial Proximity): Nếu một thực thể được nhắc đến và nó xuất hiện gần một thực thể khác đang hoạt động (ví dụ: "Ngọc Anh đang hát" và Ngọc Anh đang cầm micro), mối liên kết này trở nên mạnh mẽ hơn.
Luồng hội thoại (Discourse Coherence): Theo dõi luồng của cuộc trò chuyện hoặc bài phát biểu để hiểu mối liên hệ giữa các câu.



**Quan trọng**: 
1. Bạn hãy bỏ qua những logo hay thông tin về đài truyền hình
2. Tất cả key value của scene graph là tiếng Anh, còn value là tiếng Việt

Tôi sẽ cho bạn một hình keyframe, một đoạn ASR và visual caption. Bạn phải làm thật tốt phần scene graph generation đó

Đoạn hội thoại asr: {asr}
Keyframe number: {keyframe_number}
Visual Caption: {visual_caption}
"""

