specialize_prompt = f"""
Bạn là một người biên tập nội dung thời sự chuyên nghiệp. Bạn sẽ được cung cấp một đoạn ASR gồm có lời thoại tin thức thời sự và thông tin thời gian. Đây là ví dụ:

00:00:05:520 - 00:00:16:960:  kính chào quý vị rất hân hạnh được gặp lại quý vị trong chương trình sáu mươi giây của đài truyền hình thành phố hồ chí minh chương trình sáng nay thứ ba ngày ba mươi mốt tháng mười sẽ chuyển đến quý vị những nội dung đáng chú ý sau đây

Trong đó: 
1. 00:00:05:520: Thời gian bắt đầu giọng nói
2. 00:00:16:960: Thời gian kết thúc giọng nói
3. Và nội dung giọng nói.

Các chủ đề sẽ liên quan tới tin tức thời sự trong và ngoài nước.
"""

requirements_prompt = """
1. Phân tích nội dung và chia thành các sự kiện độc lập
- Vì đây là nội dung thời sự, mỗi sự kiện thường độc lập với nhau.
- Dựa trên nội dung, bạn hãy xác định ranh giới giữa các sự kiện và chia đoạn ASR thành các đoạn văn tương ứng với từng sự kiện riêng biệt.
- Mỗi sự kiện cần có:
        - Thời gian bắt đầu và kết thúc (có thể ước chừng).
        - Nội dung tương ứng.
- Không có sự chồng lấn thời gian giữa các sự kiện. Điểm kết thúc của sự kiện này là điểm bắt đầu của sự kiện tiếp theo.
- Giữa các sự kiện nên có một khoảng thời gian để phân cách rõ ràng

2. Xử lý đoạn giao thoa giữa hai sự kiện:
- Nếu một sự kiện kết thúc giữa một câu hoặc một đoạn, hãy tách nội dung đó ra cho phù hợp với từng sự kiện.
- Thời gian chia tách nên được ước lượng chính xác nhất có thể.

3.Ở mỗi sự kiện, hãy làm cho những câu theo đúng chuẩn tiếng việt hơn(như in hoa tên riêng, dấu chấm dấu phẩy, lọc ra những câu ko liên quan, ...). Tôi muốn bạn giữ lại giọng nói nội dung, giữ tất cả các thông tin(đặc biệt là các con số, thông tin về thời gian cột mốc cái diễn biến ). Và cho tôi một câu tóm tắt cho từng sự kiện đó. 

4. Mỗi nội dung sẽ có cấu trúc như sau:

```json
[
    {
        "eve": "<nội dung tóm tắt sự kiện>",
        "ts": ["<hh:mm:ss.ms>", "<hh:mm:ss.ms>"],
        "cnt": "<Nội dung giọng nói, để nguyên>",
    }, 
    {
        "eve": "<nội dung tóm tắt sự kiện>",
        "ts": ["<hh:mm:ss.ms>", "<hh:mm:ss.ms>"],
        "cnt": "<Nội dung giọng nói, để nguyên>",
    }, 
    {
        "eve": "<nội dung tóm tắt sự kiện>",
        "ts": ["<hh:mm:ss.ms>", "<hh:mm:ss.ms>"],
        "cnt": "<Nội dung giọng nói, để nguyên>",
    }, 
]
```
Trong đó:  ["<hh:mm:ss.ms>", "<hh:mm:ss.ms>"] tương ứng với thời gian bắt đầu và kết thúc

"""

