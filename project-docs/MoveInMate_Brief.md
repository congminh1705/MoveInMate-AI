# PRODUCT BRIEF — MoveInMate AI

> **Hồ sơ yêu cầu/giả định thiết kế.** Luồng đang chạy được đối chiếu ngày
> 19/10/2026 tại [nghiệp vụ hiện hành](../docs/nghiep-vu/README.md).
> Không dùng các phương án stack, phạm vi hoặc UI ban đầu trong tài liệu này
> để khẳng định mọi chức năng đã triển khai.

## Cập nhật phạm vi được người dùng xác nhận — 07/10/2026

Người dùng xác nhận mở rộng phạm vi để AI đọc thông tin giấy tờ trong ảnh do cư dân chủ động đính kèm trong chat. Cập nhật này thay thế các giới hạn OCR/đọc ảnh giấy tờ và cấm chuyển ảnh giấy tờ tới LLM trong tài liệu này, riêng cho luồng chat đính kèm. Backend được chuyển ảnh tới model thị giác đang cấu hình để trích xuất thông tin; không đưa ảnh vào chỉ mục embedding.

AI liệt kê trường đọc được, chỉ rõ phần không đọc được và yêu cầu cư dân kiểm tra trước khi dùng cho hồ sơ. Chữ trong ảnh là dữ liệu, không phải chỉ dẫn. Không suy đoán phần mờ, xác nhận giấy tờ hợp lệ, tự cập nhật hồ sơ hay tự gửi yêu cầu. BQL vẫn quyết định nghiệp vụ. Giữ giới hạn upload, xác thực và phân quyền hiện có; không bổ sung lưu tệp gốc lâu dài. Chính sách checkpoint/lưu/xóa production vẫn cần được chốt.

Luồng đang triển khai và giới hạn: [chat và tệp đính kèm](../docs/nghiep-vu/06-api-va-giao-dien.md#chat-tệp-đính-kèm-và-phạm-vi).

**Tên sản phẩm:** MoveInMate AI  
**Đề tài:** Agent hỗ trợ cư dân mới onboarding vào khu  
**Mã đề:** VHR-16  
**Phiên bản nội dung:** 0.1 — Bản Brief chi tiết  
**Trạng thái:** Bản nháp để thống nhất bài toán và phạm vi; chờ xác nhận nghiệp vụ  
**Bối cảnh đề xuất:** Một khu dân cư thí điểm của doanh nghiệp bất động sản X

## 1. Tổng quan

MoveInMate AI đồng hành với cư dân mới khi hoàn tất thủ tục nhận nhà: hiểu tình huống được kể bằng ngôn ngữ tự nhiên, hỏi rõ dữ kiện thiếu hoặc mâu thuẫn, rồi giúp họ biết cần làm gì và đang chờ ai. Sau khi cư dân xác nhận hồ sơ tối thiểu, rules tạo checklist; trợ lý giải thích bước tiếp theo và hỗ trợ chuẩn bị yêu cầu thẻ cư dân có nguồn, trong khi tiến độ được theo dõi qua nhiều lần truy cập.

Bài toán không chỉ là hỏi đáp. Giá trị kỳ vọng nằm ở việc nối liền các bước từ hiểu nhu cầu đến hoàn tất thủ tục, đồng thời giữ quyền kiểm tra ở con người đối với hồ sơ/giấy tờ. BQL vẫn duyệt những nội dung cần xác minh; AI không thay BQL quyết định một giấy tờ hợp lệ hoặc một yêu cầu đã hoàn tất.

Brief này phục vụ quyết định về vấn đề cần giải quyết, người dùng ưu tiên, giá trị cần chứng minh và phạm vi thử nghiệm. Kiến trúc nêu trong yêu cầu đề tài được ghi nhận như phương án đề xuất, chưa phải hệ thống đã triển khai.

## 2. Căn cứ và mức độ chắc chắn

| Nội dung | Căn cứ | Cách sử dụng trong Brief |
|---|---|---|
| Cư dân mới phải tự mò thủ tục thẻ cư dân, thẻ xe, internet, nội quy và tiện ích | Yêu cầu đề tài | Bài toán gốc cần giải quyết |
| Agent lập checklist theo tình huống, hướng dẫn từng bước, tạo yêu cầu và theo dõi tiến độ | Yêu cầu đề tài | Năng lực sản phẩm đích |
| HITL khi BQL cần xác nhận giấy tờ; bảo mật thông tin; hướng dẫn phải đúng từng khu | Yêu cầu đề tài | Ràng buộc bắt buộc |
| App deploy, đăng nhập, checklist cá nhân hóa, trích tài liệu và memory | Yêu cầu đề tài | Phần cơ bản của đề tài |
| Định tuyến yêu cầu, nhắc việc, BQL duyệt, dashboard và eval | Yêu cầu đề tài | Đề bài xếp phần nâng cao; MVP đề xuất đưa một luồng BQL duyệt và eval tối thiểu vào P0, các phần còn lại ở P1 |
| GPT-4o-mini, LangGraph, Chroma, PostgreSQL, FastAPI, Next.js, Supabase, Railway và Vercel | Yêu cầu đề tài | Kiến trúc gợi ý; cần kiểm chứng khi triển khai |
| Một khu thí điểm, dữ liệu giả lập và bộ thủ tục giới hạn | Đề xuất của Brief | Giả định để thu hẹp phạm vi |

Chưa có phỏng vấn cư dân/BQL, bản đồ quy trình thật, SLA, số lượng hồ sơ, tài liệu thủ tục hay baseline thời gian. Vì vậy, mô tả quy trình và tác động bên dưới là giả thuyết cần kiểm chứng.

## 3. Bài toán và quy trình hiện tại

### 3.1. Phát biểu bài toán

Khi nhận nhà, cư dân phải hoàn tất nhiều thủ tục có điều kiện khác nhau. Ví dụ, người có ô tô cần đăng ký phương tiện khác người không có xe; người thuê có thể cần giấy tờ khác chủ sở hữu; gia đình nhiều thành viên có thể cần nhiều thẻ. Nếu thông tin phân tán trong nội quy, biểu mẫu, tin nhắn và nhiều đầu mối, cư dân khó biết danh sách đầy đủ và thứ tự hợp lý.

Việc gửi thiếu giấy tờ hoặc sai bộ phận có thể tạo nhiều vòng trao đổi. BQL cũng tốn công trả lời lại câu hỏi giống nhau, kiểm tra hồ sơ thiếu và cập nhật trạng thái thủ công. Chưa có số liệu chứng minh mức độ hoặc tần suất của các vấn đề này tại doanh nghiệp X.

**Bài toán đề xuất:** Làm thế nào để mỗi cư dân mới nhận được đúng checklist và hướng dẫn của khu mình, hoàn tất từng thủ tục với ít vòng hỏi lại, trong khi BQL vẫn kiểm soát các bước cần xác minh và dữ liệu cá nhân được bảo vệ?

### 3.2. Quy trình hiện tại giả định

| Bước | Công việc | Điểm cần kiểm chứng |
|---|---|---|
| 1. Nhận thông tin | Cư dân nhận tài liệu/bài đăng hoặc liên hệ BQL | Thông tin đang nằm ở đâu, có cùng phiên bản không? |
| 2. Tự xác định thủ tục | Cư dân tìm việc nào áp dụng cho tình huống của mình | Nhóm cư dân nào dễ thiếu bước nhất? |
| 3. Chuẩn bị hồ sơ | Điền biểu mẫu, chụp giấy tờ và hỏi lại yêu cầu | Loại giấy tờ nào thường thiếu/sai? |
| 4. Gửi yêu cầu | Gửi trực tiếp, qua email, ứng dụng hoặc quầy | Bộ phận nào tiếp nhận và có mã yêu cầu không? |
| 5. BQL xử lý | Kiểm tra, yêu cầu bổ sung, duyệt hoặc chuyển bộ phận | Trạng thái và SLA được ghi ở đâu? |
| 6. Cư dân theo dõi | Hỏi tiến độ, nhận kết quả và tiếp tục bước khác | Có bước nào phụ thuộc nhau hoặc thường bị quên? |

### 3.3. Nút thắt ưu tiên

Phạm vi thử nghiệm tập trung vào ba nút thắt:

1. Không biết đầy đủ thủ tục nào áp dụng cho tình huống cụ thể.
2. Không có hướng dẫn thống nhất, có nguồn và đúng phiên bản của từng khu.
3. Không thấy trạng thái xuyên suốt sau khi gửi yêu cầu.

Tự động tạo/định tuyến nhiều loại yêu cầu có thể tạo giá trị nhưng phụ thuộc hệ thống tiếp nhận thật. Vì vậy, bản đầu chỉ chứng minh một luồng thẻ cư dân với hàng đợi BQL trong ứng dụng; tích hợp ngoài và nhiều loại yêu cầu để giai đoạn sau khi có đầu mối rõ ràng.

## 4. Người dùng và nhu cầu

| Nhóm | Tình huống sử dụng | Nhu cầu | Giá trị kỳ vọng |
|---|---|---|---|
| Cư dân mới | Vừa nhận nhà, chưa biết quy trình của khu | Biết việc nào cần làm, giấy tờ gì và thứ tự hợp lý | Giảm choáng ngợp, sót việc và số lần hỏi lại |
| Cư dân thuê/thành viên | Quyền và giấy tờ có thể khác chủ hộ | Checklist phản ánh đúng tư cách cư trú | Không làm nhầm thủ tục hoặc chuẩn bị sai hồ sơ |
| Nhân viên BQL | Nhận nhiều yêu cầu với chất lượng hồ sơ khác nhau | Xem đủ thông tin, yêu cầu bổ sung và cập nhật trạng thái | Giảm trao đổi lặp lại, ưu tiên việc chờ xử lý |
| Quản lý vận hành | Theo dõi chất lượng onboarding | Thấy bước bị tắc, thời gian xử lý và tỷ lệ hoàn tất | Cải tiến tài liệu/quy trình dựa trên dữ liệu |
| Bộ phận chuyên trách | Xử lý internet, thẻ xe hoặc tiện ích | Nhận yêu cầu đúng loại và đủ trường bắt buộc | Giảm chuyển lại giữa các đầu mối |

Hai nhu cầu trọng tâm:

- **Cư dân:** Khi vừa nhận nhà, tôi muốn có một kế hoạch rõ ràng cho chính tình huống của mình để biết cần làm gì tiếp theo và không bỏ sót việc.
- **BQL:** Khi nhận một yêu cầu, tôi muốn biết checklist nào sinh ra yêu cầu đó, hồ sơ đã đủ chưa và cư dân đang chờ gì để xử lý nhất quán.

## 5. Mục tiêu và giá trị kỳ vọng

| Mục tiêu | Thay đổi kỳ vọng | Điều kiện để có giá trị |
|---|---|---|
| Giảm sót thủ tục | Cư dân thấy đủ mục bắt buộc áp dụng | Checklist được BQL xác nhận theo từng khu/tình huống |
| Giảm vòng hỏi lại | Hướng dẫn nêu đúng bước, hồ sơ và biểu mẫu | Nguồn đúng phiên bản; nội dung không mơ hồ |
| Tăng khả năng tự theo dõi | Cư dân biết mục nào đang làm/chờ BQL/đã xong | Trạng thái đồng bộ với hệ thống hoặc được BQL cập nhật |
| Giảm công trả lời lặp lại | BQL dùng cùng một nguồn và mẫu yêu cầu | Nội dung có người sở hữu và quy trình cập nhật |
| Định tuyến đúng | Yêu cầu tới đúng bộ phận từ lần đầu | Danh mục bộ phận/loại yêu cầu được xác nhận |
| Bảo vệ dữ liệu cá nhân | Chỉ thu thập và hiển thị dữ liệu cần thiết | Phân quyền, vòng đời dữ liệu và kiểm soát truy cập được triển khai |

Mục tiêu thử nghiệm là chứng minh giá trị ở một khu với một nhóm thủ tục hữu hạn. Chưa đặt mục tiêu tự động hóa toàn bộ BQL, thay thế nhân viên hoặc xử lý mọi tình huống cư trú.

Giá trị vận hành có thể ước tính sau khi có dữ liệu:

**Giờ công BQL tiết kiệm/tháng = Số cư dân phù hợp × (Phút hỗ trợ thủ công − Phút hỗ trợ khi có sản phẩm) ÷ 60.**

Phải tính cả thời gian BQL cập nhật tài liệu, sửa đề xuất AI, xử lý cảnh báo sai và vận hành hệ thống.

## 6. Trải nghiệm đề xuất và đầu ra

### 6.1. Hành trình sử dụng đích

| Giai đoạn | Người dùng làm gì? | Sản phẩm hỗ trợ gì? |
|---|---|---|
| Đăng nhập | Xác thực và chọn/nhận diện căn hộ được cấp quyền | Tách dữ liệu theo người dùng và khu |
| Tạo hồ sơ | Kể tình huống hoặc điền trường tối thiểu; kiểm tra và xác nhận dữ kiện | Agent hỏi rõ điểm thiếu/mâu thuẫn; chỉ lưu hồ sơ chính thức sau xác nhận |
| Nhận kế hoạch | Xem checklist và thứ tự đề xuất | Rules tạo mục bắt buộc/tùy chọn, lý do áp dụng và phụ thuộc; agent giải thích |
| Làm từng bước | Đọc hướng dẫn, mở biểu mẫu, chuẩn bị hồ sơ | Trả lời có nguồn; giữ phiên bản tài liệu; cảnh báo khi nguồn cũ/không phù hợp |
| Gửi yêu cầu | Kiểm tra nội dung, giấy tờ và nơi nhận trước khi gửi | Mẫu tạo nháp; agent chỉ ra phần thiếu/chưa rõ theo nguồn và đề xuất nội dung; backend kiểm trường bắt buộc, cư dân xác nhận gửi |
| BQL xử lý | Xem hồ sơ, duyệt hoặc yêu cầu bổ sung | HITL, lịch sử quyết định và lý do |
| Theo dõi | Xem trạng thái và bổ sung khi BQL yêu cầu | Trợ lý giải thích việc tiếp theo từ trạng thái chính thức và lý do bổ sung; nhắc việc tự động để P1 |

### 6.2. Các nhóm đầu ra chính

**Checklist cá nhân hóa:** Tên thủ tục, mức bắt buộc, lý do áp dụng, bước phụ thuộc, trạng thái và hành động tiếp theo. Checklist phải gắn với phiên bản hồ sơ cư dân và bộ quy tắc của đúng khu.

**Hướng dẫn có nguồn:** Các bước thực hiện, giấy tờ cần chuẩn bị, nơi/kênh tiếp nhận, thời gian dự kiến nếu có căn cứ, nguồn, ngày hiệu lực và phạm vi áp dụng. Nếu không có nguồn phù hợp, hệ thống chuyển BQL xác nhận thay vì tự trả lời chắc chắn.

**Yêu cầu có cấu trúc:** Loại yêu cầu, bộ phận đề xuất, thông tin cư dân đã được phép dùng, tài liệu đính kèm, nội dung xác nhận và mã theo dõi. Cư dân phải xem lại trước khi gửi.

**Tiến độ onboarding:** Tổng số mục bắt buộc/tùy chọn; trạng thái chưa bắt đầu, đang làm, chờ bổ sung, chờ BQL, được duyệt và hoàn tất; mục đang chặn các bước khác.

**Hàng đợi BQL:** Yêu cầu theo loại, tuổi yêu cầu, tình trạng hồ sơ, hành động duyệt/yêu cầu bổ sung/từ chối/chuyển đúng bộ phận và dấu vết xử lý.

**Dashboard vận hành — phần nâng cao:** Tỷ lệ hoàn tất, thời gian trung vị/p90, số vòng bổ sung, tỷ lệ định tuyến đúng và các bước hay bị tắc. Mọi số demo phải gắn nhãn giả lập.

### 6.3. Ví dụ minh họa đầu ra

Ví dụ hoàn toàn giả lập: cư dân là chủ hộ, có một ô tô, hai thành viên và cần internet.

- Checklist bắt buộc: xác nhận thông tin cư dân, đăng ký thẻ cư dân, đọc/xác nhận nội quy.
- Checklist theo tình huống: đăng ký ô tô và đăng ký internet.
- Một mục hướng dẫn: “Đăng ký thẻ cư dân — chuẩn bị giấy tờ định danh và thông tin căn hộ theo Quy trình thẻ cư dân Khu Mặt Trời, phiên bản 2.1, hiệu lực 01/08/2026.”
- Trạng thái: “Chờ BQL kiểm tra” sau khi gửi; chưa được tính là hoàn tất.
- Nếu thiếu mặt trước giấy tờ: BQL yêu cầu bổ sung và hệ thống chỉ hiển thị yêu cầu cụ thể, không kết luận giấy tờ không hợp lệ.

Tên khu, tài liệu, phiên bản và dữ liệu trong ví dụ là giả lập.

## 7. Phạm vi phiên bản đầu — MVP

### 7.1. Giới hạn làm việc đề xuất

- **Khu áp dụng:** Một khu thí điểm.
- **Người dùng trực tiếp:** Cư dân mới và BQL.
- **Ngôn ngữ:** Tiếng Việt.
- **Tình huống:** Chủ sở hữu/người thuê; có/không có phương tiện; có/không có nhu cầu internet; số thành viên giới hạn.
- **Nhóm thủ tục:** Xác nhận cư trú, thẻ cư dân, nội quy, phương tiện và internet. Tiện ích là phương án thay internet nếu nhóm/BQL chốt, không phải nhóm thứ sáu.
- **Dữ liệu:** Dữ liệu giả lập hoặc đã được phép sử dụng; không dùng giấy tờ thật trong repo/demo công khai.
- **Tích hợp:** Có thể mô phỏng gửi yêu cầu; tích hợp thật chỉ cho loại thủ tục có API/kênh được xác nhận.

### 7.2. Nội dung cơ bản

| Nội dung | Phạm vi cần đạt | Giới hạn |
|---|---|---|
| Đăng nhập/phân quyền | Cư dân và BQL chỉ thấy dữ liệu được cấp | Wireframe chỉ mô phỏng vai trò, không phải xác thực thật |
| Hồ sơ tình huống | Thu thập trường tối thiểu và cho phép cập nhật | Thay đổi ảnh hưởng checklist phải tạo phiên bản/tái đánh giá |
| Hỗ trợ agent có giới hạn | Hiểu lời kể, hỏi rõ dữ kiện, giải thích checklist/việc tiếp theo và kiểm tra nháp thẻ cư dân | Cư dân xác nhận dữ kiện và thao tác gửi; thiếu/xung đột nguồn thì chuyển người phụ trách |
| Checklist | Có mục áp dụng, lý do, phụ thuộc và trạng thái | Không suy diễn từ dữ liệu chưa khai báo |
| Hướng dẫn | Từng câu trả lời có nguồn phù hợp | Không dùng tài liệu sai khu/hết hiệu lực mà không cảnh báo |
| Tiến độ | Lưu trạng thái qua phiên làm việc | “Đã gửi” khác “đã duyệt/hoàn tất” |
| HITL | BQL duyệt hoặc yêu cầu bổ sung các bước cần xác minh | AI không tự duyệt giấy tờ |
| Lịch sử | Ghi thay đổi hồ sơ, checklist, yêu cầu và quyết định | Dữ liệu nhạy cảm không được đưa vào log dạng toàn văn |

### 7.3. Phần nâng cao

| Hướng mở rộng | Giá trị dự kiến | Điều kiện trước khi thực hiện |
|---|---|---|
| Soạn thảo nâng cao và định tuyến nhiều đầu mối | Giảm nhập lại và chuyển nhầm đầu mối | Đo lợi ích của gợi ý P0, có danh mục loại yêu cầu, trường bắt buộc và kênh nhận |
| Nhắc việc | Giảm mục bị quên | Có hạn/SLA đáng tin cậy, cài đặt đồng ý và kênh gửi |
| Dashboard | Nhận biết điểm tắc và đo onboarding | Trạng thái nhất quán, định nghĩa chỉ số và quyền xem |
| Eval tự động/hỗn hợp | Theo dõi chất lượng checklist và RAG | Bộ tình huống có đáp án, người rà soát và quy trình hồi quy |
| Nhiều khu | Mở rộng phạm vi sử dụng | Tách kho tài liệu/quy tắc, chủ sở hữu và phiên bản theo khu |

**Ngoài phạm vi MVP:** thanh toán phí; cấp thẻ vật lý; ký số; OCR giấy tờ tùy thân; nhận diện khuôn mặt; tự ra quyết định pháp lý/nghiệp vụ; gửi thông báo đại trà; tích hợp mọi hệ thống tòa nhà; hỗ trợ không giới hạn khu/ngôn ngữ.

## 8. Vai trò của AI và con người

| Phần việc | Cách xử lý đề xuất | Lý do |
|---|---|---|
| Kiểm tra quyền, trạng thái và trường bắt buộc | Quy tắc xác định trước | Cần nhất quán, kiểm thử được |
| Hiểu lời kể và hỏi làm rõ | Agent đề xuất dữ kiện/câu hỏi; cư dân xác nhận hồ sơ | Ngôn ngữ tự nhiên có thể thiếu hoặc mâu thuẫn; không lưu suy diễn như sự thật |
| Xây checklist từ hồ sơ | Rules engine từ hồ sơ đã xác nhận; BQL sở hữu quy tắc | Mục bắt buộc và phụ thuộc phải xác định, kiểm thử được |
| Tìm nguồn, giải thích và đề xuất việc tiếp theo | Agent dùng nguồn đúng khu, checklist và trạng thái chính thức | Có căn cứ; thiếu/xung đột nguồn thì chuyển người phụ trách |
| Chuẩn bị yêu cầu thẻ cư dân | Mẫu và backend kiểm bắt buộc; agent kiểm nháp, đề xuất nội dung; cư dân xác nhận gửi | Không tự gửi, không tự duyệt; soạn thảo nâng cao để P1 |
| Duyệt giấy tờ, xác nhận hoàn tất | BQL/bộ phận phụ trách | Cần quyền và trách nhiệm nghiệp vụ |
| Nhắc việc | Quy tắc dựa trên trạng thái và lựa chọn người dùng | Tránh nhắc quá mức hoặc sai thời điểm |
| Cập nhật tài liệu/quy trình | Người sở hữu nghiệp vụ | AI không tự đặt chính sách |

Agent được chọn câu hỏi làm rõ, công cụ được phép và bước hỗ trợ tiếp theo trong giới hạn; hệ thống giữ quyền, checklist theo rules, điều kiện gửi và trạng thái. Đề xuất phải dựa vào dữ liệu đã xác nhận và nguồn được phép. Chi tiết giới hạn bước, công cụ và checkpoint nằm trong SAD; tên framework/RAG không chứng minh giá trị nếu chưa so sánh được với form + rules + tìm kiếm tài liệu.

## 9. Giả định, dữ liệu và phụ thuộc

| Giả định/điều chưa biết | Vì sao quan trọng? | Cách kiểm chứng |
|---|---|---|
| Cư dân thường bỏ sót hoặc làm sai thứ tự | Xác định giá trị thật của checklist | Phỏng vấn 5–8 cư dân mới và xem ca hỗ trợ gần đây |
| Có thể chuẩn hóa thủ tục của một khu | Quyết định khả năng xây quy tắc/đáp án | Workshop với BQL và lập ma trận tình huống–thủ tục |
| Tài liệu hiện hành có người sở hữu | RAG chỉ tốt khi nguồn đáng tin | Kiểm kê tài liệu, ngày hiệu lực và quy trình cập nhật |
| Trạng thái yêu cầu có thể đồng bộ | Cần để theo dõi tiến độ thật | Xác minh API hoặc thao tác cập nhật của BQL |
| Có người duyệt dữ liệu eval | Cần phân biệt checklist/hướng dẫn đúng sai | Phân công BQL hoặc chủ quy trình |
| Cư dân chấp nhận khai báo dữ liệu tối thiểu | Ảnh hưởng hoàn thành hồ sơ và quyền riêng tư | Usability test và rà soát consent |

Dữ liệu tối thiểu cần chuẩn bị:

| Nhóm dữ liệu | Nội dung | Vai trò |
|---|---|---|
| Danh mục thủ tục | Mã, tên, khu, điều kiện áp dụng, phụ thuộc, bộ phận, SLA | Sinh checklist và theo dõi |
| Tài liệu hướng dẫn | Nguồn, phiên bản, ngày hiệu lực, phạm vi khu, bước và biểu mẫu | RAG và trích dẫn |
| Ma trận hồ sơ | Tư cách cư trú, phương tiện, thành viên, nhu cầu → thủ tục | Đáp án tham chiếu checklist |
| Loại yêu cầu | Trường bắt buộc, tệp cho phép, bộ phận và trạng thái | Tạo/định tuyến yêu cầu |
| Bộ tình huống eval | Ca bình thường, thiếu dữ liệu, nguồn cũ, mâu thuẫn và quyền truy cập | Đo chất lượng/hồi quy |

Không đưa bản sao giấy tờ thật vào kho vector nếu không có quyết định rõ về mục đích, mã hóa, vị trí lưu, thời hạn xóa và quyền truy cập. RAG tài liệu thủ tục và lưu hồ sơ cư dân là hai miền dữ liệu khác nhau.

## 10. Cách đo thành công

| Khía cạnh | Cách đo | Lưu ý |
|---|---|---|
| Độ đúng checklist | Precision/recall theo mục áp dụng so với đáp án BQL | Báo theo từng nhóm tình huống; không gộp để che lỗi |
| Tỷ lệ hoàn tất | Cư dân hoàn tất tất cả mục bắt buộc / cư dân bắt đầu | Cần định nghĩa thời hạn theo cohort |
| Thời gian hoàn tất | Trung vị và p90 từ tạo checklist đến mục bắt buộc cuối cùng hoàn tất | Tách thời gian chờ BQL và thời gian cư dân |
| Chất lượng hướng dẫn | Đúng khu/phiên bản/bước/giấy tờ và có nguồn hỗ trợ | Lỗi sai tài liệu khu là lỗi nghiêm trọng |
| Giá trị riêng của agent | Độ đúng trích xuất; câu hỏi làm rõ phù hợp; phát hiện hồ sơ/nháp thiếu; việc tiếp theo có nguồn đúng khu | So với form + rules + tìm kiếm trên cùng tình huống; chưa có kết quả đo |
| Định tuyến | Yêu cầu đúng bộ phận ngay lần đầu / tổng yêu cầu | Ghi số lần chuyển lại |
| Vòng bổ sung | Số lần BQL yêu cầu thêm hồ sơ trên mỗi yêu cầu | Phân biệt thiếu do hướng dẫn và do cư dân |
| Công sức | Thời gian thao tác, kiểm tra/sửa và số lượt trao đổi trước/sau | Tính cả công sửa AI và duy trì tài liệu |
| An toàn/quyền riêng tư | Sự cố truy cập trái quyền, log lộ dữ liệu, yêu cầu xóa được xử lý | Mục tiêu lỗi quyền nghiêm trọng là 0 |

Ưu tiên chất lượng: checklist không bỏ sót mục bắt buộc, hướng dẫn không dùng sai khu/phiên bản, trích dẫn đúng nguồn và không có đường vượt quyền duyệt. Các ngưỡng định lượng cần chốt sau baseline; không suy ra hiệu quả từ dữ liệu demo nhỏ.

Cách đo thử: chia bộ tình huống độc lập thành tập phát triển và tập đánh giá; không để các biến thể gần giống của cùng một hồ sơ nằm ở hai tập. So sánh quy trình hiện tại với prototype trên nhiệm vụ tương đương; ghi rõ cỡ mẫu, người tham gia và giới hạn.

## 11. Rủi ro và nguyên tắc xử lý

| Rủi ro | Tác động | Nguyên tắc xử lý |
|---|---|---|
| Checklist thiếu mục bắt buộc | Cư dân bỏ sót thủ tục | Chủ quy trình duyệt rules; eval recall; BQL sửa quy tắc, agent không tự thêm mục bắt buộc |
| Hướng dẫn sai khu/hết hạn | Chuẩn bị sai hoặc gửi sai hồ sơ | Lọc metadata bắt buộc; gắn phiên bản/ngày hiệu lực; chặn khi không đủ nguồn |
| AI bịa bước/SLA | Tạo kỳ vọng sai | Chỉ trả lời từ nguồn; nêu chưa biết; chuyển BQL |
| Lộ giấy tờ/thông tin cá nhân | Tác động nghiêm trọng đến cư dân | Tối thiểu hóa dữ liệu, mã hóa, phân quyền, log an toàn và thời hạn xóa |
| Gửi yêu cầu ngoài ý muốn | Ảnh hưởng vận hành và niềm tin | Hiển thị bản nháp, nơi nhận và dữ liệu; yêu cầu xác nhận trước gửi |
| Nhắc việc quá mức | Làm phiền, giảm sử dụng | Cho cấu hình kênh/tần suất và dừng khi trạng thái đổi |
| Sai trạng thái | Cư dân tưởng việc đã xong | Tách rõ nháp/đã gửi/chờ duyệt/đã duyệt/hoàn tất; nguồn trạng thái xác định |
| Prompt injection trong tài liệu | Agent bỏ qua quy tắc hoặc lộ dữ liệu | Coi tài liệu là dữ liệu, giới hạn công cụ và kiểm tra đầu ra |
| Phụ thuộc model/vendor | Chi phí hoặc hành vi thay đổi | Ghi phiên bản, đo chi phí/chất lượng và giữ lớp trừu tượng phù hợp |

## 12. Việc cần làm để chốt Brief

### 12.1. Xác minh với người dùng

- Phỏng vấn cư dân mới về 3 ca gần nhất, không chỉ hỏi ý kiến chung.
- Quan sát nhân viên BQL xử lý một yêu cầu thiếu hồ sơ và một yêu cầu hoàn chỉnh.
- Lập bản đồ kênh nhận, bộ phận, trạng thái và SLA hiện có.
- Thử prototype với ít nhất một chủ hộ có xe và một người thuê không xe.
- Kiểm tra người dùng có hiểu khác biệt giữa “đã gửi” và “đã hoàn tất” hay không.
- Kiểm tra nội dung consent và khả năng xóa dữ liệu/tệp.

### 12.2. Quyết định còn mở

- Khu thí điểm và danh sách thủ tục P0.
- Trường hồ sơ cư dân tối thiểu.
- Bộ phận nào cập nhật trạng thái và qua kênh nào.
- Dữ liệu/tệp nào được phép lưu; thời hạn và nơi lưu.
- Người sở hữu tài liệu và quy trình xuất bản phiên bản mới.
- Model, chi phí, hạ tầng và tiêu chí môn học/đồ án.
- Xác nhận với BQL ranh giới agent đã đề xuất: được chọn câu hỏi/công cụ hỗ trợ nào, điểm dừng cư dân/BQL và nguồn/rules nào được phê duyệt.

## Tài liệu tham chiếu

- `mẫu/README.md`, `mẫu/Brief.md`, `mẫu/AI_Agent_PRD.md`, `mẫu/Wireframe_UI_Flow.html` — cấu trúc tham khảo; nội dung mẫu thuộc đề tài khác.
