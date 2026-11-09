# KHẢO SÁT CẠNH TRANH — MoveInMate AI

**Mã đề:** VHR-16  
**Phiên bản:** 0.2  
**Ngày rà:** 24/09/2026  
**Phạm vi:** Sản phẩm công khai mà cư dân mới thực sự đụng: app cư dân, app mua nhà, và kênh thủ công. Không chấm sản phẩm nào là “kém” ngoài những gì mô tả cửa hàng và review công khai cho thấy.  
**Đọc trước:** `RESEARCH_PAIN_POINTS.md`  
**Đọc tiếp:** `MoveInMate_BRD.md`

## 1. Cách so

Mỗi năng lực chấm một trong ba mức:

- **Có:** nhà phát triển nêu trong mô tả ứng dụng.
- **Một phần:** có việc gần, nhưng không phải checklist onboarding theo hồ sơ.
- **Không thấy:** mô tả không nêu. Vắng mặt trên mô tả không chứng minh tính năng không tồn tại trong app.

Kênh thủ công (nhóm Zalo, file PDF, quầy, hotline) là mô hình phổ biến cần kiểm chứng tại doanh nghiệp X, không phải kết quả đi khảo sát một khu cụ thể.

## 2. Từng nhóm giải pháp

### 2.1. Kênh thủ công

Cư dân nhận file nội quy, hỏi nhóm chat hoặc ra quầy. BQL trả lời lặp và nhận hồ sơ tự do.

Phù hợp khi số cư dân mới ít và quy trình ngắn. Yếu khi cùng một câu hỏi được trả bằng nhiều phiên bản, và khi không ai chỉ ra việc nào áp dụng cho người thuê khác chủ hộ.

### 2.2. Vinhomes Resident

Package `com.vinhomes.resident`, Vingroup. Mô tả trên Google Play, cập nhật 02/09/2026: đặt tiện ích, thanh toán hóa đơn, gửi yêu cầu hỗ trợ, liên hệ BQL, thông tin PCCC, intercom, chỉ số môi trường, đăng ký khách và phân tầng thang máy. 4,7 sao, hơn 100 nghìn lượt tải.

Đây là app vận hành khu đô thị cho người đã ở. Yêu cầu hỗ trợ là ticket chung, không phải checklist theo tình huống nhận nhà. Một review công khai nói việc đồng bộ app kéo dài, chưa làm được thẻ ra vào và thẻ gửi xe. Đó là một trải nghiệm, không phải thống kê.

### 2.3. Masterise Homes

Package `com.masterisehomes.customer`. Mô tả cập nhật 13/08/2026: tìm căn, tour 3D, lọc dự án, thông báo khi trạng thái mua đổi, nhắc ký và ra ngân hàng đặt cọc, gọi tư vấn một chạm. 4,2 sao, 83 bài đánh giá.

App này giải quyết đoạn mua tới trước khi vào ở. MoveInMate không cạnh tranh listing hay trạng thái hợp đồng mua.

### 2.4. Bcons Service

Package `vn.com.bconsliving`, NeoTech / neoHome. Mô tả cập nhật 19/08/2026: nhận thông báo BQL, lịch sử giao dịch, thanh toán hóa đơn, đăng ký tiện ích, đăng ký yêu cầu hỗ trợ, đăng ký ra vào. 2,6 sao, 44 bài đánh giá.

Gần bài toán hơn vì có đăng ký ra vào và yêu cầu hỗ trợ. Mô tả không có checklist theo hồ sơ, không có trích nguồn theo khu, không có chuỗi trạng thái onboarding. Review công khai nói về hẹn lịch không tới và phản ánh không được trả lời: vấn đề nằm ở độ rõ của việc đang chờ ai.

### 2.5. HomeID Cư dân

Package `asia.homeid`. Mô tả: thông báo, phản hồi BQL, thanh toán điện nước và phí, đăng ký dịch vụ trong mục “Nhà của bạn”, kèm mua sắm và voucher. Cập nhật 06/03/2024. 4,0 sao, 21 bài đánh giá.

Một review nói sau khi vào app chủ yếu thấy đặt hàng và quảng cáo, không thấy phần quản lý cư dân. Dùng làm ví dụ về app cư dân bị kéo sang thương mại, không dùng làm kết luận cả thị trường.

### 2.6. Nhóm quản lý nhà trọ

LOZIDO, các app quản lý trọ, MISA tài sản: phục vụ chủ trọ thu phí và quản phòng. Khác người dùng, khác thủ tục thẻ cư dân và nội quy khu. Không đưa vào bảng chấm.

## 3. Bảng năng lực

Cột MoveInMate MVP là **thiết kế dự kiến**, chưa phải tính năng đã triển khai hoặc kết quả đo. Đối chiếu các app khác chỉ dựa trên mô tả công khai trong phạm vi nghiên cứu này.

| Năng lực cần cho onboarding | Kênh thủ công | Vinhomes Resident | Masterise Homes | Bcons Service | HomeID Cư dân | MoveInMate MVP |
|---|---|---|---|---|---|---|
| Checklist theo tư cách cư trú, thành viên, xe | Không thấy | Không thấy | Không thấy | Không thấy | Không thấy | Có |
| Hướng dẫn gắn khu, phiên bản, nguồn | PDF tĩnh, dễ lệch bản | Không thấy | Không thấy | Thông báo BQL | Thông báo | Có; thiếu nguồn thì dừng |
| Một thủ tục gửi được và BQL duyệt | Quầy, tin nhắn | Yêu cầu hỗ trợ | Không phải việc này | Đăng ký yêu cầu, đăng ký ra vào | Góp ý, đăng ký dịch vụ | Có, một loại thủ tục |
| Cư dân xác nhận trước khi gửi | Tùy kênh | Không thấy trong mô tả | Không áp dụng | Không thấy | Không thấy | Có |
| “Đã gửi” khác “đã xong” trên cả checklist | Không | Trạng thái từng yêu cầu, nếu có | Trạng thái mua nhà | Không thấy chuỗi onboarding | Không thấy | Có |
| Trợ lý làm rõ lời kể và đề xuất bước tiếp theo, người duyệt giấy tờ | Không | Không thấy trong mô tả | Không thấy trong mô tả | Không thấy trong mô tả | Không thấy trong mô tả | Thiết kế MVP; cần eval so với form + rules + tìm kiếm |
| Thanh toán phí, đặt tiện ích, intercom | Ngoài kênh | Có | Không | Có | Có | Ngoài MVP |
| Tìm căn, theo dõi hợp đồng mua | Không | Không | Có | Không | Không | Ngoài phạm vi |

## 4. Khoảng trống đáng làm

Thị trường đã có cổng cư dân cho phí, tiện ích và ticket, và đã có app cho đoạn mua nhà. Chỗ còn trống, trên chính mô tả sản phẩm, là lớp onboarding có điều kiện:

- Danh sách việc thay đổi theo hồ sơ, không phải menu cố định cho mọi căn.
- Câu hướng dẫn truy được về tài liệu còn hiệu lực của đúng khu.
- Một hồ sơ đi từ bản nháp tới quyết định của BQL, và checklist chỉ hoàn tất khi tới trạng thái đích.

MoveInMate chiếm khoảng trống đó. Không làm lại thanh toán, đặt tiện ích, mở cửa, intercom hay sàn mua căn hộ.

## 5. Việc cạnh tranh buộc MVP phải có

| Quan sát | Hệ quả cho tính năng |
|---|---|
| App cư dân đã nhận “yêu cầu hỗ trợ” dạng ticket tự do | MVP phải gửi yêu cầu có trường bắt buộc và loại thủ tục, không thêm một hộp chat trống |
| Review kêu không biết việc tới đâu | MVP phải có timeline và tách đã gửi / cần bổ sung / được duyệt / hoàn tất |
| Nội quy và thông báo đã tồn tại nhưng không cá nhân hóa | RAG chỉ bổ sung cho checklist. Checklist sai thì câu trả lời hay vẫn không hết sót việc |
| App đời sống làm nhiều việc và review phàn nàn lệch trọng tâm | MVP một khu, năm nhóm thủ tục, một luồng duyệt. Dashboard và nhắc việc để P1 |
| BQL vẫn là nơi hẹn lịch và xử lý hồ sơ | P0 agent làm rõ, giải thích và đề xuất nội dung bản nháp; mẫu/backend kiểm tra trường bắt buộc, cư dân xác nhận gửi, BQL duyệt. Soạn thảo nâng cao để P1 |

## 6. Định vị một câu

MoveInMate là trợ lý onboarding sau bàn giao cho một khu: việc nào phải làm, làm theo tài liệu nào, hồ sơ đang chờ ai. App cư dân hiện tại là cổng sinh hoạt; app chủ đầu tư là cổng mua nhà.

## 7. Giới hạn của vòng khảo sát này

- Chưa cài app để bấm từng màn. “Không thấy” nghĩa là không có trong mô tả cửa hàng.
- Chưa có bảng giá, thị phần, hay hợp đồng của doanh nghiệp X với nhà cung cấp app.
- Review trích lại là ví dụ công khai, không phải mẫu đại diện.
- Nếu doanh nghiệp X đã có app cư dân riêng, nhóm phải thêm một cột vào bảng mục 3 trước khi viết SAD, vì điểm tích hợp sẽ đổi. Phạm vi nghiệp vụ của MVP không đổi: vẫn là checklist, nguồn và một luồng HITL.
