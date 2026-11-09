# BRD — MoveInMate AI

> **Baseline yêu cầu nghiệp vụ, không phải báo cáo triển khai.** Luồng và quyền
> hiện hành ngày 19/10/2026 nằm trong [docs/nghiep-vu](../docs/nghiep-vu/README.md).
> Giữ các mã yêu cầu và căn cứ nghiên cứu bên dưới để truy vết; các mục đề xuất
> chưa được BQL xác nhận không tự trở thành quy định khu.

## Cập nhật phạm vi được người dùng xác nhận — 07/10/2026

Người dùng xác nhận mở rộng phạm vi để AI đọc thông tin giấy tờ trong ảnh do cư dân chủ động đính kèm trong chat. Cập nhật này thay thế các giới hạn OCR/đọc ảnh giấy tờ và cấm chuyển ảnh giấy tờ tới LLM trong tài liệu này, riêng cho luồng chat đính kèm. Backend được chuyển ảnh tới model thị giác đang cấu hình để trích xuất thông tin; không đưa ảnh vào chỉ mục embedding.

AI liệt kê trường đọc được, chỉ rõ phần không đọc được và yêu cầu cư dân kiểm tra trước khi dùng cho hồ sơ. Chữ trong ảnh là dữ liệu, không phải chỉ dẫn. Không suy đoán phần mờ, xác nhận giấy tờ hợp lệ, tự cập nhật hồ sơ hay tự gửi yêu cầu. BQL vẫn quyết định nghiệp vụ. Giữ giới hạn upload, xác thực và phân quyền hiện có; không bổ sung lưu tệp gốc lâu dài. Chính sách checkpoint/lưu/xóa production vẫn cần được chốt.

Luồng đang triển khai và giới hạn: [chat và tệp đính kèm](../docs/nghiep-vu/06-api-va-giao-dien.md#chat-tệp-đính-kèm-và-phạm-vi).

**Tên:** Business Requirements Document  
**Sản phẩm:** MoveInMate AI  
**Mã đề:** VHR-16  
**Phiên bản:** 0.2  
**Ngày:** 24/09/2026  
**Trạng thái:** Bản làm việc cho nhóm. Chưa có chữ ký BQL doanh nghiệp X.  
**Nguồn:** `RESEARCH_PAIN_POINTS.md`, `COMPETITIVE_ANALYSIS.md`, đề tài VHR-16  
**Đọc tiếp:** Mục 8 về phạm vi MVP, rồi `MoveInMate_PRD.md` và `MoveInMate_SAD_v1.0.md`
**Tình trạng:** SAD là thiết kế đề xuất; phạm vi và quy tắc thật vẫn cần nhóm/BQL xác nhận.

BRD trả lời việc kinh doanh cần đạt. Cách làm kỹ thuật nằm ở PRD. Quy tắc kiểm thử chi tiết vẫn là BR-01 đến BR-14 và FR-01 đến FR-18 trong PRD; bảng cuối tài liệu này nối mã hai bên.

## 1. Bối cảnh

Cư dân mới nhận nhà tại một khu của doanh nghiệp bất động sản phải tự lần từng thủ tục: thẻ cư dân, phương tiện, internet, nội quy, tiện ích. Đề bài mô tả tình trạng này là choáng và sót việc. Khảo sát app công khai ngày 24/09/2026 cho thấy các cổng cư dân đang phục vụ phí, tiện ích, thông báo và ticket hỗ trợ; chưa thấy sản phẩm nào lập checklist theo hồ sơ rồi dẫn từng bước bằng tài liệu đúng khu.

Doanh nghiệp X trong đề bài là bối cảnh thí điểm, chưa phải khách hàng đã ký và đã cung cấp số liệu vận hành.

## 2. Mục tiêu kinh doanh

| ID | Mục tiêu | Cách biết là đạt ở vòng thí điểm |
|---|---|---|
| BG-01 | Cư dân mới hết sót thủ tục bắt buộc của đúng tình huống, kể cả khi mô tả đầu vào tự nhiên chưa đủ hoặc mâu thuẫn | Cư dân xác nhận dữ kiện; checklist thử có đủ mục bắt buộc so với đáp án BQL hoặc đáp án giả lập đã khóa |
| BG-02 | Giảm vòng hồ sơ thiếu trên một thủ tục có duyệt | Đếm số lần BQL bấm “cần bổ sung” trên luồng thẻ và thời gian cư dân kiểm tra/sửa. Chưa đặt mức giảm phần trăm vì chưa có baseline |
| BG-03 | Cư dân khỏi hỏi “đang tới đâu” cho chính thủ tục đó | Màn hình cư dân phân biệt bản nháp, đã gửi, cần bổ sung, được duyệt, hoàn tất |
| BG-04 | BQL chỉ nhận việc đúng thẩm quyền | AI không có thao tác duyệt. Mọi quyết định có người, thời điểm, lý do |
| BG-05 | Hướng dẫn không dùng nhầm khu hoặc bản hết hạn | Ca không có nguồn phù hợp phải dừng và chuyển BQL |

Mục tiêu không gồm: cắt nhân sự BQL, cấp thẻ vật lý trong ngày, hay tự động hóa mọi bộ phận tòa nhà.

## 3. Giá trị cốt lõi

**Một danh sách việc đúng người, đúng khu, và một trạng thái đáng tin cho tới khi BQL xác nhận xong.**

Giá trị tăng thêm cần chứng minh của agent là giúp cư dân diễn đạt tình huống tự nhiên, hỏi làm rõ đúng điểm thiếu/mâu thuẫn, hiểu vì sao cần làm việc tiếp theo và chuẩn bị bản nháp thẻ cư dân ít thiếu sót hơn. So sánh với form + rules + tìm kiếm tài liệu trên cùng ca; việc dùng LLM, LangGraph hoặc RAG tự nó chưa chứng minh giá trị.

Người hưởng:

- Cư dân mới bớt mò và bớt nộp thiếu.
- BQL bớt trả lời câu đã có trong tài liệu và bớt nhận hồ sơ không đủ trường.
- Vận hành, ở giai đoạn sau, thấy bước nào tắc. Chưa nằm trong bản này.

## 4. Bên liên quan

| Bên | Quan tâm | Quyền với MVP |
|---|---|---|
| Cư dân mới | Xong thủ tục, biết đang chờ ai | Khai báo, xem việc của mình, gửi yêu cầu của mình |
| BQL tiếp nhận | Hồ sơ đủ, quyết định còn trong tay mình | Duyệt, yêu cầu bổ sung, từ chối có lý do |
| Chủ quy trình / người giữ tài liệu | Bản hướng dẫn nào đang hiệu lực | Gán nguồn cho từng thủ tục. Đổi bản là việc người, không phải việc model |
| Bộ phận chuyên trách (xe, tiện ích) | Nhận đúng loại việc | MVP chỉ một đầu mối cho một loại thủ tục |
| Quản lý vận hành | Tỷ lệ hoàn tất, chỗ tắc | Xem sau, khi trạng thái đã nhất quán |
| Nhóm đề tài | Đủ tiêu chí cơ bản của VHR-16 | Xây trong scope mục 8 |

## 5. Hiện trạng và trạng thái cần tới

### Hiện trạng, mức đã có căn cứ

1. Cư dân tự xác định việc cần làm từ tài liệu hoặc bằng cách hỏi.
2. App cư dân trên thị trường nhận yêu cầu hỗ trợ, thu phí, đặt tiện ích; không lập kế hoạch onboarding theo hồ sơ.
3. Thủ tục thẻ và ra vào đã xuất hiện như điểm nghẽn trong review công khai, dưới dạng chờ lâu hoặc không thấy phản hồi.
4. Quy trình nội bộ, SLA và hệ thống ticket của doanh nghiệp X chưa được cung cấp.

### Trạng thái cần tới của bản thí điểm

1. Cư dân đăng nhập đúng khu, đúng căn.
2. Kể tình huống hoặc điền hồ sơ; được hỏi rõ dữ kiện thiếu/mâu thuẫn và xác nhận trước khi lưu.
3. Nhận checklist do rules quyết định, có lý do và phụ thuộc từng mục.
4. Mở một mục, đọc hướng dẫn/việc nên làm tiếp theo có nguồn và người đang chờ; thiếu hoặc xung đột nguồn thì chuyển người phụ trách.
5. Với thủ tục thẻ, xem bản nháp được kiểm tra theo nguồn và schema, xác nhận gửi, theo dõi quyết định của BQL.
6. Checklist chỉ hoàn tất khi mọi mục bắt buộc đạt trạng thái đích.

## 6. Yêu cầu nghiệp vụ

Ưu tiên: **Bắt buộc** là điều MVP phải chứng minh. **Sau** là việc có giá trị nhưng phụ thuộc dữ liệu hoặc kênh chưa có.

| ID | Yêu cầu | Ưu tiên | Đo bằng |
|---|---|---|---|
| YC-01 | Mỗi cư dân thuộc một khu và một căn được cấp quyền, chỉ thấy hồ sơ của mình | Bắt buộc | Thử truy cập chéo bị từ chối |
| YC-02 | Cư dân có thể mô tả tự nhiên; agent đề xuất dữ kiện và hỏi rõ điểm thiếu/mâu thuẫn. Hồ sơ chính thức chỉ lưu sau xác nhận, gồm tư cách cư trú, số thành viên, phương tiện và nhu cầu internet | Bắt buộc | Thiếu/mâu thuẫn chưa rõ thì không ra checklist “đầy đủ”; không lưu suy đoán chưa xác nhận |
| YC-03 | Rules được chủ quy trình phê duyệt tạo checklist từ hồ sơ đã xác nhận; mỗi mục có bắt buộc/tùy chọn, lý do và phụ thuộc | Bắt buộc | Cùng hồ sơ/rules cho cùng kết quả; agent không thêm thủ tục bắt buộc |
| YC-04 | Đổi hồ sơ làm các mục phụ thuộc được tính lại, tiến độ cũ còn lịch sử | Bắt buộc | Đổi từ không xe sang có xe thì thêm mục và giải thích |
| YC-05 | Hướng dẫn và việc nên làm tiếp theo dựa trên hồ sơ, checklist, trạng thái chính thức và nguồn đúng khu còn hiệu lực; nêu đang chờ cư dân hay BQL | Bắt buộc | Thiếu/xung đột nguồn hoặc bản hết hạn thì không hướng dẫn chắc; chuyển người phụ trách xác nhận |
| YC-06 | Cư dân thấy tiến độ theo mục bắt buộc và không hiểu nhầm đã gửi là đã xong | Bắt buộc | Nhãn trạng thái trên checklist và trên yêu cầu |
| YC-07 | Một yêu cầu thẻ cư dân có mẫu, nháp và bước agent kiểm phần thiếu/chưa rõ theo nguồn; backend kiểm điều kiện bắt buộc, cư dân xác nhận mới gửi | Bắt buộc | Nháp thiếu bị chỉ rõ căn cứ; không có đường gửi ngầm |
| YC-08 | BQL trong phạm vi khu xử lý yêu cầu: duyệt, yêu cầu bổ sung hoặc từ chối có lý do; cư dân được hướng về đúng bản nháp để sửa | Bắt buộc | Cư dân/agent không duyệt; bổ sung giữ phiên bản và lịch sử |
| YC-09 | Quyết định của BQL cập nhật đúng mục checklist. Duyệt yêu cầu chưa đương nhiên là hoàn tất nếu còn bước phát thẻ | Bắt buộc | Ca “đã duyệt, thẻ chưa phát” vẫn chưa hoàn tất |
| YC-10 | Lưu tiến độ qua các lần đăng nhập và giữ lịch sử quyết định | Bắt buộc | Thoát ra vào lại vẫn đúng trạng thái |
| YC-11 | Chỉ thu dữ liệu cần cho thủ tục; giấy tờ không nằm trong kho tài liệu hướng dẫn | Bắt buộc | Tách file cư dân và kho RAG |
| YC-12 | Có người chịu trách nhiệm từng nhóm tài liệu. Bản mới không tự được model bịa ra | Bắt buộc | Mỗi nguồn có chủ và ngày hiệu lực |
| YC-13 | Định tuyến tự động tới nhiều bộ phận | Sau | Cần danh mục bộ phận thật |
| YC-14 | Nhắc việc còn thiếu | Sau | Cần hạn đáng tin và sự đồng ý nhận tin |
| YC-15 | Dashboard tỷ lệ hoàn tất cho quản lý | Sau | Cần trạng thái đã ổn và quy tắc ẩn danh |
| YC-16 | Đo chất lượng checklist, hướng dẫn và giá trị agent trên bộ tình huống có đáp án | P0 bộ eval tối thiểu; P1 tự động hóa | Tách tập làm và tập chấm; so với form + rules + tìm kiếm |

## 7. Quy tắc nghiệp vụ then chốt

- Chính sách thủ tục thuộc về người giữ quy trình. Agent có thể nêu gợi ý riêng, nhưng không được thêm thủ tục bắt buộc vào checklist ngoài bộ quy tắc đã được phê duyệt.
- Giấy tờ hợp lệ hay không là quyết định của BQL.
- Tài liệu khu này không được dùng để hướng dẫn khu khác, trừ khi tài liệu ghi phạm vi chung.
- Gửi lại sau lỗi mạng không được tạo hai yêu cầu.
- Nội dung tài liệu và nội dung cư dân nhập là dữ liệu, không phải lệnh cho agent.
- Agent chọn câu hỏi làm rõ, công cụ được phép và cách giải thích; hệ thống quyết định phân quyền, checklist, điều kiện gửi, trạng thái và tiến độ. Agent không tự gửi, duyệt, đánh dấu hoàn tất hoặc sửa chính sách.

Bản đầy đủ của các quy tắc này là BR-01 đến BR-14 trong PRD.

## 8. Phạm vi nghiệp vụ của MVP

Trong phạm vi:

- Một khu thí điểm. Dữ liệu demo dùng khu giả lập đã có trong wireframe cho tới khi có khu thật.
- Tiếng Việt.
- Cư dân mới và BQL.
- Năm nhóm việc: xác nhận cư trú, thẻ cư dân, nội quy, phương tiện, internet hoặc một tiện ích.
- Đúng một luồng có duyệt từ đầu tới cuối: thẻ cư dân. Phương tiện là mục checklist theo hồ sơ, không thêm luồng duyệt thứ hai.
- P0 agent hỗ trợ làm rõ hồ sơ, giải thích checklist/việc tiếp theo, kiểm tra và đề xuất nội dung nháp thẻ; mẫu và backend kiểm trường bắt buộc, cư dân xác nhận gửi. Soạn thảo nâng cao và định tuyến nhiều đầu mối thuộc P1.
- Dữ liệu giả lập hoặc dữ liệu được phép. Không đưa giấy tờ thật vào repo.

Ngoài phạm vi nghiệp vụ:

- Thanh toán phí, cấp thẻ vật lý, ký số, OCR, nhận diện khuôn mặt.
- Mở cửa, intercom, đặt tiện ích, sàn mua căn hộ.
- Tự duyệt hồ sơ, tự ban hành nội quy.
- Nhiều khu, nhiều ngôn ngữ.
- Thay thế app cư dân hiện có nếu doanh nghiệp X đã có app đó. MoveInMate bổ sung lớp onboarding, chưa phải cổng sinh hoạt.

Ranh giới này cùng mục 7 của `MoveInMate_Brief.md` là baseline làm việc; chưa có tài liệu `MVP_SCOPE.md` được nhóm phê duyệt.

## 9. Ràng buộc

| ID | Ràng buộc | Nguồn |
|---|---|---|
| RC-01 | Human-in-the-loop với thủ tục cần xác nhận hồ sơ hoặc giấy tờ | Đề VHR-16 |
| RC-02 | Bảo mật giấy tờ và thông tin cá nhân | Đề VHR-16 |
| RC-03 | Hướng dẫn chính xác theo từng khu | Đề VHR-16 |
| RC-04 | Cân chi phí và số bước của agent | Đề VHR-16 |
| RC-05 | Phần cơ bản của đề phải có app triển khai, đăng nhập, checklist, trích tài liệu, ghi nhớ tiến độ | Đề VHR-16 |
| RC-06 | Chưa có SLA, danh mục bộ phận và kho tài liệu thật | Hiện trạng nhóm |

RC-06 có nghĩa các tích hợp “gửi sang hệ thống có sẵn” để sau. MVP được phép mô phỏng kênh nhận, miễn là trạng thái và HITL là thật trong sản phẩm.

## 10. Chỉ số

| Chỉ số | Công thức | Mốc lúc này |
|---|---|---|
| Đủ việc bắt buộc | Mục bắt buộc đúng có trong checklist / mục bắt buộc của đáp án | Phải đủ trên bộ demo |
| Không thêm việc rác | Mục áp dụng đúng / tổng mục tạo ra | Theo dõi, ngưỡng kỹ thuật ở PRD |
| Đúng nguồn | Câu trả lời dùng nguồn còn hiệu lực của đúng khu / câu cần nguồn | Sai khu là lỗi chặn |
| Vòng bổ sung | Số lần “cần bổ sung” trên một yêu cầu thẻ | Đo, chưa cam kết mức giảm |
| Giá trị agent so với cách đơn giản | Độ đúng trích xuất, câu hỏi làm rõ phù hợp, phát hiện hồ sơ/nháp thiếu, hướng dẫn có nguồn đúng khu và thời gian gồm kiểm tra/sửa | So với form + rules + tìm kiếm trên cùng ca; chưa có số đo |
| Kiểm soát duyệt | Quyết định do đúng vai trò thực hiện / tổng quyết định | 100% trên ca thử |
| Hoàn tất đúng nghĩa | Hồ sơ đạt hoàn tất chỉ khi mọi mục bắt buộc xong | Không có ngoại lệ “gần xong” |

Công thức giờ công ở Product Brief vẫn dùng được sau khi có số phút hỗ trợ trước và sau. Chưa điền số.

## 11. Giả định còn mở

| ID | Giả định | Nếu sai thì |
|---|---|---|
| GA-01 | Một khu chuẩn hóa được năm nhóm thủ tục | Thu hẹp còn ba nhóm, vẫn giữ một luồng HITL |
| GA-02 | Có người duyệt bộ đáp án checklist | Nhóm tự gán nhãn và ghi rõ kết quả chỉ là kiểm thử kỹ thuật |
| GA-03 | Cư dân chấp nhận khai báo bốn nhóm trường | Cắt trường, chấp nhận checklist thô hơn |
| GA-04 | Doanh nghiệp X chưa có checklist đạt yêu cầu YC-03 và YC-05 | Nếu đã có, MVP chuyển thành lớp trạng thái và HITL trên checklist đó, không xây thêm agent cho phần đã xong |

## 12. Nối sang PRD

| Yêu cầu nghiệp vụ | Việc trong PRD |
|---|---|
| YC-01 | FR-01, NFR-01 |
| YC-02 | FR-02, FR-03 |
| YC-03 | FR-04, BR-01 |
| YC-04 | FR-03, BR-02 |
| YC-05 | FR-05, FR-06, FR-07, BR-05, BR-06, NFR-11 |
| YC-06 | FR-05, BR-04 |
| YC-07 | FR-09, FR-10, BR-08, BR-11 |
| YC-08 | FR-11, FR-12, FR-13, BR-07 |
| YC-09 | FR-13, FR-14, BR-03 |
| YC-10 | FR-08, FR-15, FR-16 |
| YC-11 | FR-18, NFR-02, NFR-03, NFR-09 |
| YC-12 | EX-05 khi làm P1; trước đó là quy trình người, ngoài phần mềm |
| YC-13 | EX-02 |
| YC-14 | EX-03 |
| YC-15 | EX-04 |
| YC-16 | PRD mục 3 cho eval P0 tối thiểu; EX-06 cho tự động hóa P1 |

## 13. Điều kiện để viết SAD

SAD được viết khi nhóm không đổi các mục sau:

- Pain point chính là PP-01, điều kiện PP-02, luồng mẫu là thẻ có HITL.
- YC-01 đến YC-12 là bắt buộc.
- YC-13 đến YC-15 ở sau MVP.
- YC-16 có bộ eval tối thiểu trong P0; tự động hóa ở P1.
- Một khu, năm nhóm thủ tục, một luồng duyệt.

Đổi một trong các mục đó thì sửa BRD và scope trước, rồi mới sửa kiến trúc.
