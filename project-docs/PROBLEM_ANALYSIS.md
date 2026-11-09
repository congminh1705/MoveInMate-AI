# PROBLEM ANALYSIS — MoveInMate AI

**Phiên bản:** 0.1  
**Trạng thái bằng chứng:** Chưa có nghiên cứu người dùng thực tế; nội dung pain point hiện là giả thuyết từ yêu cầu đề tài và cần kiểm chứng.

## 1. Mục tiêu nghiên cứu

Xác định cư dân mới thực sự gặp khó khăn ở đâu trong quá trình chuyển đến, bước nào tạo nhiều công sức cho BQL, thông tin nào có thể chuẩn hóa và phần nào phù hợp để AI hỗ trợ.

Nghiên cứu phải giúp nhóm chọn một pain point và một luồng MVP có thể triển khai, kiểm thử và chứng minh giá trị trong thời gian chương trình.

## 2. Target users

### Cư dân mới

- Chủ sở hữu nhận bàn giao.
- Người thuê chuyển đến.
- Thành viên gia đình được đăng ký bổ sung.
- Cư dân có/không có phương tiện; có nhu cầu chuyển đồ, internet hoặc tiện ích khác nhau.

### Ban quản lý

- Nhân viên tiếp nhận và hỗ trợ cư dân.
- Nhân viên kiểm tra hồ sơ/thẻ/phương tiện.
- Người quản trị tài liệu và quy trình.
- Quản lý vận hành theo dõi chất lượng onboarding.

## 3. Proto-personas cần kiểm chứng

### Persona A — Cư dân chủ hộ bận rộn

- Vừa nhận nhà, muốn hoàn tất thủ tục trong ít lần liên hệ.
- Có thể cần đăng ký nhiều thành viên và phương tiện.
- Nhu cầu giả định: một danh sách rõ, giấy tờ cần chuẩn bị và trạng thái đang chờ ai.
- Rủi ro nghiên cứu: có thể người dùng đã được sales/BQL hỗ trợ đủ, nên pain point không lớn như giả thuyết.

### Persona B — Người thuê lần đầu chuyển đến

- Không chắc quyền/thủ tục của mình khác chủ sở hữu thế nào.
- Có thể thiếu giấy ủy quyền hoặc thông tin chủ nhà.
- Nhu cầu giả định: chỉ dẫn theo tư cách cư trú, không phải tài liệu chung cho mọi người.
- Rủi ro nghiên cứu: quy trình thuê có thể do chủ nhà hoặc môi giới xử lý, không phải cư dân trực tiếp.

### Persona C — Nhân viên BQL tiếp nhận

- Nhận câu hỏi và hồ sơ qua nhiều kênh.
- Có thể phải lặp lại hướng dẫn hoặc yêu cầu bổ sung.
- Nhu cầu giả định: yêu cầu có cấu trúc, đúng bộ phận và đủ trường tối thiểu.
- Rủi ro nghiên cứu: nút thắt thật có thể nằm ở hệ thống nội bộ/SLA, không phải chất lượng đầu vào.

## 4. Giả thuyết pain point

| ID | Giả thuyết | Bằng chứng hiện có | Dữ liệu cần thu |
|---|---|---|---|
| H1 | Cư dân khó tìm thông tin và quy định | Mô tả trong đề bài | Tần suất tìm kiếm, kênh đang dùng, ví dụ thông tin không tìm thấy |
| H2 | Cư dân không biết đủ thủ tục cần làm | Mô tả trong đề bài | Tỷ lệ/số ca sót việc, mục thường sót, tác động |
| H3 | Cư dân phải hỏi BQL nhiều lần về nội dung cơ bản | Chưa có số liệu | Log/FAQ/ticket hoặc nhật ký phỏng vấn; số lượt hỏi trên một cư dân |
| H4 | Hướng dẫn chưa được tổ chức thành quy trình dễ theo dõi | Suy luận từ thông tin phân tán | Kiểm kê tài liệu/kênh và quan sát hành trình thực tế |
| H5 | Hướng dẫn cá nhân hóa tốt hơn tài liệu chung | Đề bài yêu cầu checklist theo tình huống | So sánh nhiệm vụ với tài liệu chung và checklist theo profile |
| H6 | Gửi sai bộ phận hoặc thiếu hồ sơ tạo vòng xử lý lại | Tính năng định tuyến/HITL trong đề bài gợi ý | Tỷ lệ chuyển tuyến, tỷ lệ cần bổ sung, lý do |
| H7 | Trạng thái không rõ làm cư dân phải hỏi tiến độ | Yêu cầu track/memory trong đề bài | Số câu hỏi tiến độ, trạng thái hiện được ghi ở đâu |

Không trình bày H1–H7 như sự thật trong báo cáo cho đến khi có dữ liệu.

## 5. Pain points theo hành trình giả định

| Giai đoạn | Cư dân có thể gặp | BQL có thể gặp | Cơ hội cần kiểm chứng |
|---|---|---|---|
| Trước chuyển đến | Không biết thứ tự, mốc thời gian, điều kiện | Trả lời câu hỏi chung | Checklist theo thời điểm/tình huống |
| Khai báo cư trú | Không biết giấy tờ nào áp dụng | Hồ sơ thiếu/không đúng vai trò | Form có điều kiện và kiểm tra trước gửi |
| Thẻ/phương tiện | Không biết route, biểu mẫu hoặc quy định | Chuyển sai đầu mối, bổ sung nhiều vòng | Hướng dẫn có nguồn + request schema |
| Chuyển đồ | Không biết giờ/đặt lịch/quy tắc thang máy | Xung đột lịch hoặc thiếu xác nhận | Tra cứu quy định và đặt lịch nếu có tích hợp |
| Tiện ích/dịch vụ | Thông tin nằm ở nhiều nơi | Câu hỏi lặp lại | RAG tài liệu đã xác thực |
| Theo dõi | Không biết đang chờ ai hoặc đã xong chưa | Bị hỏi trạng thái qua nhiều kênh | Timeline và nguồn trạng thái |

## 6. User journey mục tiêu đề xuất

1. Cư dân đăng nhập vào đúng khu/căn được cấp.
2. Trả lời một số câu hỏi tối thiểu về tình huống.
3. Nhận checklist có lý do áp dụng và thứ tự.
4. Mở từng mục để xem hướng dẫn có nguồn.
5. Chuẩn bị và xem lại yêu cầu trước khi gửi.
6. BQL kiểm tra, yêu cầu bổ sung hoặc duyệt.
7. Cư dân theo dõi trạng thái, bổ sung nếu cần.
8. Hệ thống ghi nhận hoàn tất khi đạt trạng thái đích thật.

Hành trình này là giải pháp giả định; cần usability test trước khi chốt.

## 7. Kế hoạch thu thập bằng chứng

### 7.1. Phỏng vấn cư dân mới

Mẫu đề xuất: 5–8 người đã chuyển đến trong 1–3 tháng gần đây, gồm chủ sở hữu và người thuê nếu có.

Câu hỏi dựa trên sự kiện thật:

- Lần gần nhất bạn phải làm một thủ tục khi chuyển đến là gì?
- Bạn biết cần làm việc đó từ đâu?
- Bạn đã chuẩn bị/gửi những gì? Có phải bổ sung không?
- Bạn liên hệ bao nhiêu lần và qua kênh nào?
- Lúc nào bạn không biết bước tiếp theo hoặc trạng thái?
- Nếu có checklist, thông tin nào bắt buộc phải có để bạn tin và dùng?

Không hỏi dẫn dắt như “Bạn có thấy AI Agent hữu ích không?” trước khi hiểu hành vi hiện tại.

### 7.2. Phỏng vấn/quan sát BQL

Mẫu đề xuất: 3–5 người thuộc tiếp nhận cư dân, thẻ/phương tiện và quản lý vận hành.

- Đi theo một ca hoàn chỉnh và một ca thiếu hồ sơ.
- Ghi thời gian xử lý thực, thời gian chờ và số vòng trao đổi.
- Xin danh sách trạng thái, route, trường bắt buộc và lý do chuyển/từ chối.
- Xác định người sở hữu tài liệu và cách cập nhật phiên bản.

### 7.3. Dữ liệu vận hành nếu được phép

- FAQ hoặc nhóm câu hỏi đã ẩn danh.
- Ticket/yêu cầu đã ẩn danh và trạng thái.
- Tỷ lệ cần bổ sung, chuyển tuyến và thời gian xử lý.
- Danh mục tài liệu, biểu mẫu, phiên bản và phạm vi áp dụng.

Không đưa dữ liệu cá nhân thô vào repo nghiên cứu.

## 8. Evidence matrix dự kiến

| Pain point | Bằng chứng đủ để tiếp tục | Dấu hiệu bác bỏ/giảm ưu tiên |
|---|---|---|
| Sót thủ tục | Nhiều ca độc lập cho thấy mục bị quên, có tác động hoặc BQL xác nhận lặp lại | Hầu hết cư dân đã có checklist đầy đủ và không gặp sót |
| Thiếu/sai hồ sơ | Log hoặc quan sát cho thấy bổ sung nhiều vòng vì hướng dẫn không rõ | Bổ sung chủ yếu do lý do ngoài khả năng hướng dẫn |
| Hỏi thông tin lặp lại | FAQ/ticket và thời gian BQL cho thấy khối lượng đáng kể | Câu hỏi ít, biến thể cao hoặc đã có kênh tự phục vụ hiệu quả |
| Không rõ trạng thái | Cư dân hỏi tiến độ; BQL cập nhật thủ công nhiều kênh | Hệ thống hiện tại đã hiển thị trạng thái đáng tin cậy |
| Định tuyến sai | Có số ca chuyển lại giữa bộ phận | Mọi yêu cầu đi qua một đầu mối duy nhất và route không phải vấn đề |

## 9. Existing solutions cần khảo sát

Chưa có dữ liệu về hệ thống hiện tại của doanh nghiệp X. Cần kiểm tra:

- Ứng dụng cư dân đang có và các module onboarding/ticket.
- Bộ tài liệu bàn giao, email/Zalo/thông báo, website hoặc FAQ.
- Form đăng ký thẻ/phương tiện và hệ thống quản lý yêu cầu.
- Kênh liên hệ BQL và cách theo dõi SLA.
- Công cụ tìm kiếm hoặc chatbot đã tồn tại.

Baseline tối thiểu để so sánh là **form + rules tạo checklist + tìm kiếm tài liệu** trên cùng nguồn, không chỉ quy trình hoàn toàn thủ công. Nếu phương án đơn giản đã giải quyết tốt, không nên thêm agent phức tạp.

## 10. AI opportunities

| Cơ hội | Vì sao có thể phù hợp AI | Điều kiện/rủi ro |
|---|---|---|
| Hỏi đáp có RAG | Ngôn ngữ câu hỏi đa dạng; tài liệu có thể dài | Nguồn phải đúng khu/phiên bản; cần no-answer behavior |
| Tóm tắt hướng dẫn | Giúp cư dân nắm bước và giấy tờ | Không được bỏ điều kiện/ngoại lệ |
| Cá nhân hóa checklist | Hồ sơ có nhiều tổ hợp điều kiện | Nên kết hợp rules; không để LLM tự đặt policy |
| Soạn yêu cầu | Giảm nhập lại và chuẩn hóa nội dung | Cư dân xem lại; tối thiểu hóa dữ liệu |
| Phân loại/định tuyến | Nhiều cách mô tả cùng một nhu cầu | Cần taxonomy/nhãn; fallback BQL |
| Đề xuất bước tiếp theo | Hữu ích khi workflow nhiều trạng thái | Trạng thái phải đáng tin; không tự vượt HITL |

Giả thuyết cần thử riêng cho agent là khả năng xử lý lời kể tự nhiên chưa đủ hoặc tự mâu thuẫn: trích xuất dữ kiện, chọn câu hỏi làm rõ cần thiết, rồi giải thích bước tiếp theo từ hồ sơ đã xác nhận, trạng thái chính thức và nguồn đúng khu. Checklist bắt buộc vẫn do rules quyết định. Đây là cơ hội nghiên cứu, chưa phải kết quả đo hay bằng chứng rằng dùng LangGraph/RAG sẽ tạo giá trị.

### Khi không cần AI

- Kiểm tra quyền, trường bắt buộc, trạng thái và điều kiện cứng nên dùng code/rules.
- Mục menu, link biểu mẫu cố định hoặc trạng thái ticket không cần LLM.
- Nếu dữ liệu chỉ có vài FAQ ổn định, tìm kiếm/decision tree có thể đủ cho MVP.

## 11. MVP hypothesis

**Giả thuyết:** Với một khu và một bộ thủ tục giới hạn, checklist dựa trên rules kết hợp trợ lý làm rõ đầu vào, hướng dẫn có nguồn và hỗ trợ kiểm tra bản nháp sẽ giúp cư dân hoàn tất một luồng cần BQL duyệt với ít lỗi đầu vào và ít lượt hỏi lại hơn baseline **form + rules + tìm kiếm tài liệu**.

### Tính năng cốt lõi đề xuất

- Hồ sơ tình huống tối thiểu.
- Checklist xác định bằng rules và giải thích lý do.
- Hướng dẫn RAG có nguồn đúng khu/phiên bản.
- Một luồng yêu cầu thẻ cư dân có BQL duyệt; phương tiện là mục checklist theo hồ sơ, chưa là luồng duyệt thứ hai.
- Timeline và trạng thái lưu bền.
- Cư dân xác nhận dữ kiện trích xuất trước khi lưu; agent chỉ đề xuất nội dung và chỉ ra thiếu sót của bản nháp thẻ cư dân, không gửi hay duyệt thay người.

### Cách bác bỏ hoặc tiếp tục

- Bác bỏ/đổi hướng nếu nghiên cứu cho thấy pain point không đáng kể hoặc nguồn không thể chuẩn hóa.
- Tiếp tục nếu người dùng hoàn thành nhiệm vụ tốt hơn baseline và BQL xác nhận đầu vào/route hữu ích.
- So sánh cùng ca và cùng nguồn: độ đúng trích xuất, số câu hỏi làm rõ phù hợp, tỷ lệ phát hiện hồ sơ thiếu, nguồn đúng khu, vòng BQL yêu cầu bổ sung, thời gian hoàn thành gồm kiểm tra/sửa và lỗi vượt quyền. Chưa có số đo hoặc ngưỡng lợi ích được BQL xác nhận.
- Không mở rộng nhiều khu trước khi nguồn, rules, quyền và eval của khu đầu tiên ổn định.

## 12. Đầu ra nghiên cứu còn thiếu

- Biên bản phỏng vấn/quan sát đã ẩn danh.
- Bản đồ quy trình hiện tại được BQL xác nhận.
- Danh mục tài liệu/quy trình và người sở hữu.
- Baseline định lượng.
- Quyết định MVP chính thức của nhóm.

Cho đến khi có các đầu ra này, báo cáo phải dùng cụm “giả thuyết”, “đề xuất” hoặc “dữ liệu mô phỏng” tương ứng.
