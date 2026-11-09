# PROJECT BRIEF — MoveInMate AI

Tài liệu đầu vào giai đoạn thiết kế được giữ để truy vết yêu cầu VHR-16.
Luồng cập nhật ngày 19/10/2026 ở [nghiệp vụ hiện hành](../docs/nghiep-vu/README.md);
cách chạy ở [README](../README.md); yêu cầu nộp xem [MVP Submission](MVP_Submission_Requirements_20261004.md).

**Tên đề tài:** MoveInMate – AI Agent hỗ trợ cư dân mới onboarding vào khu dân cư  
**Mã đề:** VHR-16  
**Nguồn yêu cầu chính:** Nội dung đề tài VHR-16 được cung cấp cho nhóm  
**Phiên bản:** 0.1  
**Trạng thái:** Phân tích ban đầu; chưa được nhóm/BQL xác nhận

## 1. Bối cảnh

Theo đề bài, cư dân mới nhận nhà tại doanh nghiệp bất động sản X phải tự tìm nhiều thủ tục như đăng ký thẻ cư dân, phương tiện, internet, nội quy và kích hoạt tiện ích. Việc này có thể gây quá tải thông tin và sót việc.

Đây là mô tả trong đề bài, chưa phải kết quả khảo sát của nhóm. Tên doanh nghiệp, khu, căn hộ, cư dân và tài liệu hiển thị trong prototype đều là dữ liệu giả lập.

## 2. Problem statement

Làm thế nào để một cư dân mới biết đúng những thủ tục áp dụng cho tình huống của mình, nhận hướng dẫn có căn cứ và theo dõi được tiến độ đến khi hoàn tất, trong khi BQL vẫn kiểm soát các bước cần xác minh và dữ liệu cá nhân được bảo vệ?

## 3. Target users

### Người dùng chính

- **Cư dân mới:** tạo hồ sơ tình huống, nhận checklist, xem hướng dẫn, gửi yêu cầu và theo dõi tiến độ.
- **Ban quản lý:** kiểm tra hồ sơ/giấy tờ, yêu cầu bổ sung, duyệt và cập nhật trạng thái.

### Bên liên quan

- Bộ phận chuyên trách nhận yêu cầu: lễ tân/chăm sóc cư dân, an ninh/bãi xe, tiện ích hoặc đối tác dịch vụ. Danh sách thật chưa được xác nhận.
- Quản lý vận hành: theo dõi chất lượng onboarding và điểm tắc; thuộc phạm vi nâng cao.

## 4. Mục tiêu đề tài

Tạo một AI Agent hỗ trợ cư dân mới trong quy trình onboarding bằng cách:

1. Thu thập thông tin tình huống cần thiết.
2. Làm rõ lời kể thiếu/mâu thuẫn và để cư dân xác nhận hồ sơ trước khi lưu; rules quyết định checklist cá nhân hóa.
3. Hướng dẫn từng bước và đề xuất việc tiếp theo từ trạng thái chính thức, có trích tài liệu đúng khu.
4. Hỗ trợ kiểm tra bản nháp yêu cầu thẻ cư dân; cư dân xác nhận gửi, BQL quyết định.
5. Theo dõi tiến độ qua nhiều bước/lần truy cập.
6. Dừng ở BQL đối với thủ tục cần kiểm tra hồ sơ hoặc giấy tờ.

## 5. Yêu cầu bắt buộc xác định từ đề bài

### Phần cơ bản

- Có ứng dụng được triển khai và đăng nhập.
- Agent tạo checklist onboarding cá nhân hóa.
- Agent hướng dẫn từng bước có trích tài liệu.
- Theo dõi tiến độ, có memory.

Trong MVP, cụm “agent tạo checklist” của đề bài được thực hiện bằng agent hỗ trợ thu thập/làm rõ và giải thích; rules đã được chủ quy trình xác nhận mới quyết định mục bắt buộc, tùy chọn và phụ thuộc.

### Ràng buộc

- Human-in-the-loop cho thủ tục cần BQL xác nhận hồ sơ/giấy tờ.
- Bảo mật giấy tờ và thông tin cá nhân của cư dân mới.
- Hướng dẫn phải chính xác theo từng khu.
- Cân đối chi phí và trải nghiệm của workflow nhiều bước.

### Phần nâng cao

- Agent tạo và định tuyến yêu cầu tới bộ phận phù hợp.
- Nhắc việc còn thiếu.
- BQL duyệt hồ sơ trong luồng HITL.
- Dashboard tiến độ onboarding.
- Đánh giá tỷ lệ hoàn tất thủ tục.

## 6. Công nghệ nêu trong đề bài

| Lớp | Công nghệ |
|---|---|
| LLM | GPT-4o-mini |
| Agent | LangGraph: `profile → build_checklist → guide → create_requests → track` |
| Knowledge | RAG tài liệu thủ tục; Chroma |
| Database | PostgreSQL |
| Backend | FastAPI |
| Frontend | Next.js |
| Auth | Supabase Auth, vai trò Cư dân mới/BQL |
| Deploy | Railway + Vercel |

Đây là cấu hình được nêu trong yêu cầu đề tài. Tính khả dụng, phiên bản, chi phí, chính sách dữ liệu và mức phù hợp production phải được xác nhận tại thời điểm triển khai.

## 7. Tiêu chí đánh giá đã xác định và còn thiếu

### Đã xác định từ đề bài

- Có app deploy và đăng nhập.
- Checklist được cá nhân hóa.
- Hướng dẫn từng bước có trích tài liệu.
- Tiến độ được ghi nhớ.
- Có HITL BQL ở bước cần xác minh.
- Phần nâng cao có dashboard và đánh giá tỷ lệ hoàn tất.

### Chưa được cung cấp

- Thang điểm chi tiết của chương trình.
- Ngưỡng chính xác/tỷ lệ hoàn tất bắt buộc.
- Số lượng tình huống test và cách chấm.
- Yêu cầu bắt buộc về source code, video, slide hoặc báo cáo cuối.
- Hạn nộp, lịch demo và số thành viên.

Không tự coi các ngưỡng đề xuất trong PRD là tiêu chí chính thức của chương trình.

## 8. Phạm vi MVP đề xuất

Ưu tiên một luồng cốt lõi hoạt động tốt tại một khu giả lập:

1. Đăng nhập hai vai trò Cư dân/BQL.
2. Hồ sơ tình huống tối thiểu: tư cách cư trú, số thành viên, phương tiện, nhu cầu internet; agent hỏi rõ đầu vào tự nhiên nhưng cư dân xác nhận trước khi lưu.
3. Checklist cho 5 nhóm: xác nhận cư trú, thẻ cư dân, nội quy, phương tiện và internet/tiện ích.
4. Hướng dẫn bằng RAG có nguồn, khu, phiên bản và ngày hiệu lực.
5. Một loại yêu cầu thẻ cư dân cần BQL duyệt từ đầu đến cuối: mẫu/backend kiểm trường bắt buộc, agent giải thích và chỉ ra phần thiếu theo nguồn, cư dân xác nhận gửi.
6. Trạng thái và lịch sử không nhập nhằng: bản nháp, đã gửi, cần bổ sung, đã duyệt, hoàn tất.
7. Bộ eval nhỏ nhưng tách tập phát triển/đánh giá và có đáp án được rà soát.

### Ngoài MVP đề xuất

- OCR/nhận diện giấy tờ, khuôn mặt, thanh toán, cấp thẻ vật lý.
- Tích hợp mọi hệ thống tòa nhà hoặc mọi loại yêu cầu.
- Hỗ trợ không giới hạn khu/ngôn ngữ.
- Tự động duyệt giấy tờ hoặc tự quyết định quy định.
- Soạn thảo nâng cao, tự gửi, định tuyến nhiều bộ phận và nhắc việc tự động; cân nhắc ở P1 sau khi đo lợi ích P0.

Phạm vi trên là đề xuất để nhóm thảo luận, chưa phải quyết định cuối cùng.

## 9. Deliverables

### Đã tạo trong workspace

- `PROJECT_BRIEF.md` — bản tóm tắt yêu cầu chính thức/đề xuất.
- `PROBLEM_ANALYSIS.md` — phân tích pain point và kế hoạch kiểm chứng.
- `MoveInMate_Brief.md` — Product Brief chi tiết.
- `MoveInMate_PRD.md` — PRD, yêu cầu, kiến trúc và kế hoạch test.
- Prototype wireframe ban đầu đã được bỏ khỏi tài liệu hiện hành; dùng luồng trong `docs/nghiep-vu/` để test.
- `README.md` — hướng dẫn và trạng thái dự án.

### Cần làm ở giai đoạn phát triển

- Source code frontend/backend/agent.
- Knowledge base và bộ dữ liệu eval được phép sử dụng.
- App deploy có auth.
- Bằng chứng kiểm thử thực tế trong [hồ sơ eval](../deliverables/05-eval-evidence.md).
- Demo script/video nếu chương trình yêu cầu.
- Báo cáo/slide cuối nếu chương trình yêu cầu.

## 10. Thời hạn

Chưa có hạn nộp chính thức trong tài liệu đã nhận. PRD chỉ đưa lộ trình sáu tuần tham khảo; không xem đó là cam kết.

## 11. Những vấn đề cần làm rõ

1. Khu thí điểm và bộ thủ tục thật là gì?
2. Nhóm có được sử dụng tài liệu/quy trình thực tế hay chỉ dữ liệu mô phỏng?
3. Ai là người sở hữu và xác nhận tài liệu, checklist, route và trạng thái?
4. Tiêu chí chấm, deadline và deliverables bắt buộc của chương trình là gì?
5. Phần “app deploy” cần mức hoàn thiện nào và môi trường nào được phép dùng?
6. Tích hợp gửi yêu cầu thật có bắt buộc hay chỉ cần mô phỏng có giải thích?
7. Chính sách lưu/xóa giấy tờ, nơi lưu và phạm vi dữ liệu cho model là gì?
8. Nhóm thống nhất MVP nào trước khi viết production code?

## 12. Quyết định tạm để tiếp tục

- Dùng một khu giả lập tên **Khu Mặt Trời** chỉ trong prototype.
- Dùng dữ liệu cư dân/tài liệu giả lập và ghi nhãn rõ.
- Wireframe không đọc tệp, không gọi AI và không gửi yêu cầu thật.
- Chưa bắt đầu backend/AI production cho đến khi nhóm chốt MVP, dữ liệu và tiêu chí chương trình.
