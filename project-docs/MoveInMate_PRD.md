# PRD — MoveInMate AI

> **Baseline sản phẩm và tiêu chí đề xuất.** Xem [nghiệp vụ hiện hành](../docs/nghiep-vu/README.md)
> và [checklist kiểm thử](../docs/nghiep-vu/07-kiem-thu-va-demo.md) đối chiếu ngày
> 19/10/2026. Không coi mọi mục P0/P1, SLA, mockup hoặc số liệu thiết kế ở đây
> là kết quả đã triển khai/đo đạt.

## Cập nhật phạm vi được người dùng xác nhận — 07/10/2026

Người dùng xác nhận mở rộng phạm vi để AI đọc thông tin giấy tờ trong ảnh do cư dân chủ động đính kèm trong chat. Cập nhật này thay thế các giới hạn OCR/đọc ảnh giấy tờ và cấm chuyển ảnh giấy tờ tới LLM trong tài liệu này, riêng cho luồng chat đính kèm. Backend được chuyển ảnh tới model thị giác đang cấu hình để trích xuất thông tin; không đưa ảnh vào chỉ mục embedding.

AI liệt kê trường đọc được, chỉ rõ phần không đọc được và yêu cầu cư dân kiểm tra trước khi dùng cho hồ sơ. Chữ trong ảnh là dữ liệu, không phải chỉ dẫn. Không suy đoán phần mờ, xác nhận giấy tờ hợp lệ, tự cập nhật hồ sơ hay tự gửi yêu cầu. BQL vẫn quyết định nghiệp vụ. Giữ giới hạn upload, xác thực và phân quyền hiện có; không bổ sung lưu tệp gốc lâu dài. Chính sách checkpoint/lưu/xóa production vẫn cần được chốt.

Luồng đang triển khai và giới hạn: [chat và tệp đính kèm](../docs/nghiep-vu/06-api-va-giao-dien.md#chat-tệp-đính-kèm-và-phạm-vi).

**Tên sản phẩm:** MoveInMate AI  
**Đề tài:** Agent hỗ trợ cư dân mới onboarding vào khu  
**Mã đề:** VHR-16  
**Phiên bản:** 0.1 — Bản đặc tả ban đầu  
**Trạng thái:** Đề xuất để thảo luận; chưa được BQL/chủ quy trình phê duyệt

PRD này chuyển yêu cầu đề tài và Product Brief thành yêu cầu có thể xây dựng/kiểm thử. Mọi dữ liệu, SLA và kết quả trong wireframe là giả lập. Các ngưỡng chất lượng là cổng thử nghiệm đề xuất, không phải kết quả đã đạt.

## Phạm vi đọc

- **P0 — cơ bản:** đăng nhập; agent làm rõ lời kể và để cư dân xác nhận hồ sơ; checklist do rules quyết định; hướng dẫn/việc tiếp theo có nguồn; mẫu nháp thẻ cư dân được agent kiểm và đề xuất nội dung; cư dân xác nhận gửi; BQL duyệt/bổ sung/từ chối; lưu tiến độ, lịch sử và bộ eval tối thiểu.
- **P1 — nâng cao:** soạn thảo yêu cầu nâng cao, định tuyến nhiều đầu mối, nhắc việc, dashboard, giao diện quản trị nguồn và tự động hóa eval. Hàng đợi BQL cho đúng một luồng thẻ đã thuộc P0.
- **Giới hạn:** một khu, tiếng Việt, danh mục thủ tục hữu hạn, dữ liệu mô phỏng hoặc được phép sử dụng.
- **Nguyên tắc:** Agent chọn câu hỏi làm rõ, công cụ được phép và bước hỗ trợ; backend giữ quyền, rules, điều kiện gửi và trạng thái. Cư dân xác nhận dữ kiện trước khi lưu và xác nhận trước khi gửi; BQL quyết định các bước cần xác minh.

## 1. Yêu cầu sản phẩm

### 1.1. Mục tiêu sản phẩm

G1. Tạo checklist onboarding đúng tình huống cư dân và đúng quy trình của khu.  
G2. Hướng dẫn từng bước có nguồn, phiên bản và phạm vi áp dụng để kiểm tra.  
G3. Theo dõi trạng thái xuyên suốt, không để người dùng nhầm “đã gửi” với “đã hoàn tất”.  
G4. Đưa hồ sơ cần xác minh đến BQL và giữ dấu vết quyết định.  
G5. Đo độ đúng, tỷ lệ hoàn tất, thời gian và công sức để quyết định mở rộng.

### 1.2. Luồng chính và trạng thái

1. Cư dân đăng nhập và truy cập đúng căn hộ/khu được cấp.
2. Cư dân kể tình huống hoặc điền form; hệ thống giải thích mục đích sử dụng dữ liệu; agent đề xuất dữ kiện, hỏi từng điểm thiếu/mâu thuẫn cần thiết; cư dân kiểm tra, đồng ý và xác nhận trước khi lưu hồ sơ chính thức.
3. Backend kiểm tra dữ liệu, dùng rules đã được phê duyệt của khu để tạo checklist; agent giải thích lý do, không tự thêm mục bắt buộc.
4. Cư dân mở một thủ tục; agent đọc hồ sơ, checklist, trạng thái chính thức và nguồn còn hiệu lực của đúng khu để đề xuất việc tiếp theo, nêu đang chờ cư dân hay BQL.
5. Với thẻ cư dân, mẫu tạo nháp; agent đối chiếu trường/giấy tờ với nguồn hợp lệ, chỉ ra thiếu/chưa rõ, trích căn cứ và đề xuất nội dung. Backend kiểm điều kiện bắt buộc; cư dân xem lại và xác nhận gửi.
6. BQL duyệt, yêu cầu bổ sung hoặc từ chối có lý do trên đúng phiên bản. Khi cần bổ sung, agent giải thích lý do, dẫn về đúng bước và giữ lịch sử.
7. Hệ thống cập nhật tiến độ và mở khóa bước phụ thuộc từ quyết định/trạng thái chính thức. Nhắc việc tự động thuộc P1.
8. Khi mọi mục bắt buộc hoàn tất, onboarding được ghi nhận hoàn tất theo phiên bản checklist.

Trạng thái cấp checklist:

`Chưa tạo → Đang xây checklist → Đang thực hiện → Chờ cư dân bổ sung/Chờ BQL → Hoàn tất`

Trạng thái cấp mục:

`Chưa bắt đầu → Đang chuẩn bị → Bản nháp yêu cầu → Đã gửi → Đang xử lý → Cần bổ sung → Được duyệt → Hoàn tất`

Nhánh ngoại lệ: `Thiếu hoặc mâu thuẫn hồ sơ đầu vào`, `Thiếu/xung đột nguồn phù hợp`, `Nguồn hết hiệu lực`, `Lỗi xử lý`, `Hết giới hạn bước/chi phí`, `Từ chối có lý do`, `Cần xây lại checklist`. Khi thiếu/xung đột nguồn, không hướng dẫn nghiệp vụ chắc chắn hoặc gợi ý gửi hồ sơ như đã đủ; chuyển người phụ trách xác nhận.

### 1.3. Vai trò và quyền

| Thao tác | Cư dân mới | BQL | Quản lý vận hành (P1) |
|---|---:|---:|---:|
| Xem/sửa hồ sơ của mình | Có | Chỉ trong phạm vi được cấp | Không mặc định |
| Tạo/xem checklist của mình | Có | Có khi hỗ trợ | Không mặc định |
| Xem hướng dẫn và nguồn | Có | Có | Có theo phân quyền |
| Soạn yêu cầu | Có | Có khi hỗ trợ | Không |
| Gửi yêu cầu thẻ cư dân | Chỉ cư dân sở hữu sau khi xem và xác nhận | Không gửi thay trong P0 | Không |
| Yêu cầu bổ sung/duyệt/từ chối | Không | Có | Không mặc định |
| Quản trị tài liệu/quy tắc | Không | Người được phân công | Có theo quyền |
| Xem dashboard tổng hợp | Chỉ tiến độ của mình | Theo khu/phạm vi | Có |

Wireframe dùng bộ chọn vai trò để xem thiết kế; đó không phải cơ chế xác thực. Sản phẩm thật phải kiểm tra quyền ở backend cho từng tài nguyên và thao tác.

### 1.4. Yêu cầu chức năng và tiêu chí nghiệm thu P0

| ID | User story/yêu cầu | Tiêu chí nghiệm thu tối thiểu |
|---|---|---|
| FR-01 | Người dùng đăng nhập | Phiên đăng nhập hợp lệ gắn với vai trò và phạm vi khu/căn hộ; truy cập tài nguyên ngoài quyền bị từ chối ở API; đăng xuất thu hồi phiên theo thiết kế |
| FR-02 | Cư dân tạo hồ sơ onboarding từ lời kể hoặc form | Giải thích mục đích và lấy consent; agent trích xuất tư cách, thành viên, phương tiện, nhu cầu và hiển thị dữ kiện/căn cứ để sửa; hỏi riêng điểm thiếu/mâu thuẫn, không tự chọn một giá trị; chỉ cư dân xác nhận mới lưu ProfileVersion; chưa đủ thì không tạo checklist “đầy đủ” |
| FR-03 | Cư dân cập nhật hồ sơ | Giá trị thay đổi cần cư dân xác nhận; trường ảnh hưởng rules làm checklist chuyển cần đánh giá lại; UI nêu mục thêm/bỏ/đổi điều kiện; lưu phiên bản trước/sau, tác giả và yêu cầu đang xử lý, không xóa tiến độ cũ |
| FR-04 | Hệ thống tạo checklist cá nhân hóa | Rules từ hồ sơ đã xác nhận quyết định mã, tên, bắt buộc/tùy chọn, lý do, phụ thuộc và bộ phận; cùng profile/rules cho cùng kết quả; gợi ý ngoài quy tắc chỉ hiển thị riêng, không thành mục bắt buộc |
| FR-05 | Cư dân xem tổng quan tiến độ và việc tiếp theo | Hiển thị mẫu số bắt buộc/tùy chọn, trạng thái và người đang chờ; agent đề xuất một việc hợp lệ từ hồ sơ/checklist/trạng thái mới nhất, giải thích lý do; “đã gửi” không tính hoàn tất; không tự đổi trạng thái |
| FR-06 | Cư dân mở hướng dẫn một thủ tục | Trả lời có cấu trúc: bước, hồ sơ, kênh/nơi nhận, lưu ý, việc tiếp theo và nguồn tên/phiên bản/hiệu lực/khu/đoạn; thiếu, hết hạn hoặc xung đột nguồn thì nêu rõ, không đoán điều kiện nghiệp vụ và chuyển người phụ trách xác nhận |
| FR-07 | Người dùng kiểm tra nguồn | Liên kết mở đúng tài liệu/đoạn đã dùng; không trỏ sang phiên bản mới hơn cho câu trả lời cũ; nguồn hết hiệu lực có cảnh báo rõ |
| FR-08 | Cư dân lưu tiến độ và ghi chú | Trạng thái/ghi chú còn sau khi đăng nhập lại; thay đổi có thời gian; dữ liệu nhạy cảm bị hạn chế trong ghi chú tự do theo chính sách |
| FR-09 | Cư dân chuẩn bị yêu cầu thẻ cư dân | Mẫu hiển thị trường/tệp bắt buộc và BQL nhận; agent so nháp với nguồn hợp lệ, liệt kê từng chỗ thiếu/chưa rõ và citation, đề xuất nội dung để cư dân sửa; backend chặn gửi khi thiếu điều kiện bắt buộc hoặc tệp sai loại/kích thước/quét lỗi |
| FR-10 | Cư dân xác nhận gửi | Trước khi gửi hiển thị phiên bản nháp, nơi nhận và dữ liệu/tệp sẽ chia sẻ; chỉ cư dân sở hữu bấm xác nhận rõ; backend kiểm lại quyền, trường bắt buộc, phiên bản và trạng thái; trả mã/trạng thái; lỗi giữ nháp và retry không tạo trùng |
| FR-11 | BQL xem hàng đợi | Chỉ thấy yêu cầu thuộc phạm vi; lọc theo trạng thái/loại/tuổi; hiển thị dữ liệu đủ để quyết định nhưng che trường không cần thiết |
| FR-12 | BQL xử lý yêu cầu thẻ cư dân | BQL đúng khu duyệt, yêu cầu bổ sung hoặc từ chối; bổ sung/từ chối có lý do gắn đúng revision; quyết định ghi người, thời gian, phiên bản hồ sơ và request; cư dân/agent không có quyền quyết định |
| FR-13 | Cư dân bổ sung hồ sơ | Agent đọc lý do BQL và revision liên quan, giải thích cần sửa/cung cấp gì, dẫn về đúng trường/tệp và giữ citation khi có; cư dân sửa, xác nhận gửi revision mới; BQL thấy lịch sử, không mất bản trước |
| FR-14 | Hệ thống đồng bộ trạng thái checklist | Quyết định BQL cập nhật đúng mục; duyệt yêu cầu chưa mặc định đồng nghĩa hoàn tất nếu còn bước phát hành/kích hoạt; mapping trạng thái có kiểm thử |
| FR-15 | Lịch sử và truy vết | Xem được thay đổi hồ sơ, checklist, hướng dẫn đã dùng, yêu cầu, quyết định và trạng thái; log không chứa toàn văn giấy tờ/token |
| FR-16 | Hoàn tất onboarding | Chỉ đạt khi mọi mục bắt buộc áp dụng ở phiên bản checklist hiện tại đã hoàn tất; mục tùy chọn không chặn; hiển thị thời điểm và phiên bản |
| FR-17 | Phục hồi lỗi và giới hạn agent | Lỗi model/RAG, timeout hoặc hết giới hạn bước/chi phí trả trạng thái rõ và bước thủ công phù hợp; giữ nháp/checkpoint, đọc lại quyền và trạng thái chính thức khi tiếp tục; retry idempotent, không gửi trùng hay tự duyệt/hoàn tất |
| FR-18 | Xóa/thu hồi dữ liệu theo chính sách | Người có quyền có thể yêu cầu xóa/thu hồi; hệ thống áp dụng thời hạn lưu đã chốt và ghi bằng chứng xử lý, trừ phần buộc lưu theo quy định được xác nhận |

### 1.5. Yêu cầu P1

| ID | Chức năng | Tiêu chí nghiệm thu |
|---|---|---|
| EX-01 | Soạn thảo yêu cầu nâng cao | Sau khi đo gợi ý P0, có thể soạn nhiều loại yêu cầu theo schema/nguồn đã duyệt; thiếu dữ liệu thì hỏi lại, cư dân vẫn xác nhận và agent không tự gửi |
| EX-02 | Định tuyến tự động | Kết quả có bộ phận, loại yêu cầu và lý do; trường hợp dưới ngưỡng/chưa ánh xạ chuyển hàng đợi BQL; đo tỷ lệ đúng lần đầu |
| EX-03 | Nhắc việc | Dựa trên trạng thái/hạn có nguồn; người dùng chọn kênh/tần suất và có thể tắt; thay đổi trạng thái hủy nhắc không còn phù hợp |
| EX-04 | Dashboard vận hành | Hiển thị định nghĩa chỉ số, khoảng thời gian và mẫu số; lọc theo khu/nhóm thủ tục; không lộ dữ liệu cá nhân không cần thiết |
| EX-05 | Quản trị tài liệu | Xuất bản/thu hồi phiên bản có người duyệt, ngày hiệu lực và khu; re-index có kiểm tra; câu trả lời mới không dùng bản thu hồi |
| EX-06 | Eval và hồi quy | Chạy bộ tình huống cố định; lưu model/prompt/rule/source version; báo precision/recall, nguồn, định tuyến, lỗi và chi phí |

### 1.6. Quy tắc nghiệp vụ

- **BR-01.** Checklist luôn gắn với khu, phiên bản hồ sơ đã được cư dân xác nhận và phiên bản bộ quy tắc được chủ quy trình phê duyệt; agent không tự thêm mục bắt buộc.
- **BR-02.** Trường ảnh hưởng điều kiện áp dụng làm checklist cần đánh giá lại; hệ thống giải thích mục thêm/bớt.
- **BR-03.** Mục bắt buộc chỉ hoàn tất khi đạt trạng thái đích do người sở hữu quy trình định nghĩa.
- **BR-04.** Đã tạo/đã gửi yêu cầu không đồng nghĩa đã được duyệt hoặc hoàn tất.
- **BR-05.** Mọi hướng dẫn nghiệp vụ, yêu cầu giấy tờ và lý do kiểm nháp phải có nguồn đúng khu còn hiệu lực; thiếu hoặc xung đột nguồn thì dừng khẳng định và chuyển người phụ trách xác nhận.
- **BR-06.** Không lấy tài liệu khu A để hướng dẫn khu B trừ khi tài liệu ghi rõ phạm vi chung.
- **BR-07.** BQL chịu trách nhiệm quyết định ở bước cần xác minh; AI không gọi API duyệt.
- **BR-08.** Agent không tự gửi yêu cầu, duyệt, đánh dấu hoàn tất, tải tệp hay chia sẻ dữ liệu. P0 chỉ cư dân xác nhận gửi nháp thẻ của mình; BQL quyết định nghiệp vụ đúng quyền.
- **BR-09.** Yêu cầu gửi lại phải dùng khóa idempotency để tránh bản ghi trùng khi mạng lỗi.
- **BR-10.** Tài liệu, tệp và nội dung người dùng là dữ liệu, không phải chỉ dẫn có quyền thay đổi policy/tool của agent.
- **BR-11.** Chỉ thu thập trường cần cho thủ tục; trường không áp dụng không được bắt buộc vì “có thể hữu ích”.
- **BR-12.** Thay đổi trạng thái, quyết định và nguồn đã dùng phải giữ lịch sử; không sửa ngược bản ghi duyệt.
- **BR-13.** Nhắc việc dừng khi mục hoàn tất, bị hủy hoặc đổi trạng thái không còn phù hợp.
- **BR-14.** Dashboard tổng hợp phải áp dụng ngưỡng nhóm tối thiểu/quyền phù hợp để hạn chế suy ra dữ liệu cá nhân.

### 1.7. Mô hình dữ liệu tối thiểu

| Thực thể | Trường chính |
|---|---|
| User | ID, vai trò, trạng thái, tenant/khu được cấp, định danh auth |
| Residence | ID, khu/tòa/căn, người dùng được cấp, trạng thái bàn giao |
| OnboardingProfile | ID, residence, phiên bản, tư cách cư trú, số thành viên, loại phương tiện, nhu cầu, consent, tác giả, thời gian |
| ProcedureDefinition | ID, khu, mã, tên, điều kiện áp dụng, bắt buộc, phụ thuộc, bộ phận, trạng thái đích, rule version |
| Checklist | ID, profile version, rule version, trạng thái, thời gian tạo/hoàn tất |
| ChecklistItem | ID, checklist, procedure, lý do áp dụng, trạng thái, hành động tiếp theo |
| GuidanceSource | ID, khu, tên, URI nội bộ, phiên bản, hiệu lực từ/đến, chủ sở hữu, trạng thái, checksum |
| SourceChunk | ID, source, mục/trang/đoạn, nội dung, embedding ref, metadata |
| GuidanceAnswer | ID, item, câu hỏi, câu trả lời, source IDs, model/prompt version, thời gian |
| ServiceRequest | ID, item, loại, bộ phận, payload version, trạng thái, idempotency key, external ref |
| Attachment | ID, request, tên hiển thị, loại, kích thước, object key, checksum, trạng thái quét, thời hạn lưu |
| ReviewDecision | ID, request/item, hành động, lý do, người duyệt, thời gian, version |
| Reminder | ID, item, kênh, thời gian dự kiến, trạng thái, consent ref |
| AuditEvent | ID, actor, action, resource, before/after refs, time, correlation ID |
| AgentRun | ID, bước graph, input refs, tool calls, model/prompt/rule/source versions, latency, token/cost, error |

Không lưu nội dung giấy tờ trực tiếp trong vector DB nếu RAG chỉ cần tài liệu thủ tục. Tệp cư dân nên nằm ở object storage riêng, mã hóa và cấp quyền có thời hạn; PostgreSQL chỉ lưu metadata cần thiết.

### 1.8. Yêu cầu phi chức năng

| ID | Yêu cầu | Cách kiểm chứng |
|---|---|---|
| NFR-01 | Phân quyền theo tenant/khu/căn và vai trò ở backend | Test truy cập chéo ID/API/object; mọi ca phải bị từ chối và ghi audit phù hợp |
| NFR-02 | Mã hóa truyền/lưu và không có URL công khai mặc định | Rà soát TLS, bucket, signed URL, secret và backup |
| NFR-03 | Tối thiểu hóa log | Quét log/error/tracing để bảo đảm không có token, toàn văn giấy tờ hoặc trường định danh nhạy cảm ngoài whitelist |
| NFR-04 | Hiệu năng tương tác | P95 API không gồm agent ≤2 giây; P95 tạo checklist ≤15 giây; mục tiêu agent/RAG ≤20 giây cho truy vấn thường, đo trên cấu hình ghi rõ |
| NFR-05 | Tin cậy gửi yêu cầu | Retry có backoff/idempotency; test timeout giữa chừng không tạo trùng |
| NFR-06 | Khả năng truy vết | 100% quyết định BQL và lần gửi có actor/time/version/correlation ID |
| NFR-07 | Khả năng tiếp cận | Điều hướng bàn phím, nhãn form, tương phản, trạng thái không chỉ dựa màu; kiểm tra tự động và thủ công |
| NFR-08 | Responsive | Các luồng chính dùng được từ 360px đến desktop; hàng đợi BQL tối ưu desktop nhưng không mất chức năng cơ bản trên mobile |
| NFR-09 | Vòng đời dữ liệu | Cấu hình thời hạn theo loại dữ liệu, job xóa và bằng chứng; backup cũng có chính sách tương ứng |
| NFR-10 | Quan sát vận hành | Metric latency/error/cost/quality, health check và cảnh báo; không gắn nội dung nhạy cảm vào metric label |
| NFR-11 | Tách tenant/khu trong RAG | Retrieval bắt buộc lọc metadata theo tenant/khu và phiên bản; test nguồn chéo khu |
| NFR-12 | Khả năng thay model | Prompt/schema/tool contract được version; eval hồi quy trước khi đổi model |

### 1.9. Gợi ý giao diện

1. **Đăng nhập:** thương hiệu, thông tin quyền riêng tư ngắn, phục hồi tài khoản.
2. **Tổng quan:** lời chào, % theo mục bắt buộc, việc tiếp theo, mục chờ BQL và hoạt động gần đây.
3. **Hồ sơ onboarding:** form theo bước, giải thích vì sao cần dữ liệu, xem lại trước khi tạo checklist.
4. **Checklist:** nhóm “Cần làm trước”, “Đang chờ”, “Tùy chọn”, trạng thái và phụ thuộc.
5. **Trợ lý hướng dẫn:** chat/structured answer bên phải; thẻ nguồn bên dưới; CTA tạo yêu cầu khi phù hợp.
6. **Yêu cầu:** bản nháp, nơi nhận, tệp, consent gửi; timeline sau khi gửi.
7. **BQL duyệt:** hàng đợi, chi tiết cạnh nhau, hành động có lý do và audit.
8. **Dashboard:** chỉ số có định nghĩa/mẫu số, funnel và điểm tắc; ghi “dữ liệu demo” trong prototype.

Không hiển thị “AI tự tin 95%” nếu chưa có hiệu chuẩn. Ưu tiên trạng thái có ý nghĩa: có nguồn, cần BQL xác nhận, nguồn đã cũ, thiếu dữ liệu.

## 2. Thiết kế agent và kiến trúc đề xuất

### 2.1. Graph agent

```text
interpret_profile ↔ clarify_missing_or_conflicting
  → resident_confirm_profile → rules_build_checklist
  → choose_next_help ↔ retrieve_procedure_sources
  → template_draft → preflight_and_suggest
  → resident_confirm → backend_submit
  → wait_for_human_review ↔ explain_needs_info
  → track_official_state
```

Các node và ranh giới:

| Node | Đầu vào | Đầu ra | Không được làm |
|---|---|---|---|
| `interpret_profile` / `clarify` | Lời kể hoặc form; schema hồ sơ | Dữ kiện đề xuất, điểm thiếu/mâu thuẫn, câu hỏi tiếp | Lưu hồ sơ chính thức khi chưa có xác nhận |
| `build_checklist` | ProfileVersion đã xác nhận + procedure rules | Checklist có lý do áp dụng | Tự tạo policy hoặc mục bắt buộc mới |
| `guide` / `choose_next_help` | Câu hỏi + profile/checklist/trạng thái chính thức + nguồn đúng khu | Hướng dẫn/việc tiếp theo có citation, người đang chờ | Trả lời chắc chắn khi thiếu/xung đột nguồn; sửa trạng thái |
| `create_requests` / `preflight` | Nháp thẻ từ mẫu + schema + nguồn hợp lệ | Danh sách thiếu/chưa rõ có citation, nội dung đề xuất | Gửi, bỏ qua backend validation hoặc đọc bytes giấy tờ |
| `track` / `explain_needs_info` | Request revision, lý do BQL và trạng thái mới nhất | Việc sửa/cung cấp tiếp theo và lịch sử | Tự đổi quyết định BQL |

Điểm dừng bắt buộc: cư dân xác nhận dữ kiện trước khi lưu hồ sơ và xác nhận nháp trước khi backend gửi; BQL quyết định mọi `approve/reject/needs_info/complete`. Agent chỉ chọn trong công cụ được phép. LangGraph/RAG là phương tiện điều phối/tìm nguồn, không phải bằng chứng đã có năng lực agent hoặc lợi ích tăng thêm.

### 2.2. Thành phần

| Thành phần | Công nghệ theo đề bài | Trách nhiệm |
|---|---|---|
| Frontend | Next.js | Giao diện cư dân/BQL, checklist, chat, form và dashboard |
| Backend | FastAPI | API, quyền, workflow nghiệp vụ, integration và audit |
| Agent orchestration | LangGraph | Luồng node, state, checkpoint và HITL |
| LLM | GPT-4o-mini theo đề bài | Tạo hướng dẫn/bản nháp có schema; lựa chọn cuối cần eval |
| RAG | Chroma (prototype) | Index tài liệu thủ tục với metadata bắt buộc |
| Database | PostgreSQL | Hồ sơ, checklist, yêu cầu, quyết định, audit và agent metadata |
| Auth | Supabase Auth | Xác thực; authorization chi tiết vẫn ở backend/database policy |
| File storage | Cần chốt (ví dụ Supabase Storage/S3-compatible) | Tệp cư dân, signed URL, mã hóa và vòng đời |
| Deploy | Vercel + Railway theo đề bài | Frontend và backend/database, tùy giới hạn môi trường |

Chroma phù hợp prototype; trước production cần đánh giá multi-tenancy, backup, filtering, vận hành và lựa chọn vector store. Model/hạ tầng phải được xác nhận theo yêu cầu dữ liệu, chi phí và điều khoản sử dụng tại thời điểm triển khai.

### 2.3. API mức khái niệm

| Method/route | Mục đích | Quyền chính |
|---|---|---|
| `GET /me/context` | Vai trò và phạm vi cư trú | Người đăng nhập |
| `POST /profiles/interpret` | Trả dữ kiện đề xuất, thiếu/mâu thuẫn và câu hỏi làm rõ; chưa lưu chính thức | Cư dân sở hữu |
| `POST /profiles` / `PATCH /profiles/{id}` | Tạo/cập nhật hồ sơ sau xác nhận của cư dân | Cư dân sở hữu |
| `POST /checklists` | Tạo từ profile version | Cư dân sở hữu |
| `GET /checklists/{id}` | Xem mục và tiến độ | Cư dân sở hữu/BQL được cấp |
| `POST /items/{id}/guidance` | Hỏi hướng dẫn có nguồn | Người có quyền xem item |
| `POST /items/{id}/request-drafts` | Tạo bản nháp yêu cầu | Cư dân sở hữu |
| `POST /requests/{id}/preflight` | Kiểm nháp thẻ theo schema/nguồn, trả thiếu sót và citation; không gửi | Cư dân sở hữu |
| `POST /requests/{id}/submit` | Xác nhận gửi idempotent | Cư dân sở hữu |
| `POST /requests/{id}/decisions` | Duyệt/bổ sung/từ chối/chuyển | BQL đúng phạm vi |
| `GET /requests/{id}/timeline` | Theo dõi trạng thái | Cư dân sở hữu/BQL được cấp |
| `GET /admin/dashboard` | Chỉ số tổng hợp | BQL/quản lý theo quyền |

Mọi mutation dùng authorization, validation schema, audit và correlation ID. Không tin `role`, `tenant_id` hoặc `resident_id` do client tự gửi nếu có thể suy ra từ phiên/quyền.

## 3. Kế hoạch đánh giá và nghiệm thu

### 3.1. Bộ dữ liệu dự kiến

Đề xuất tối thiểu 40 tình huống giả lập từ ít nhất 10 profile gốc độc lập: 20 phát triển, 20 đánh giá giữ riêng. Mỗi tập có chủ hộ/người thuê, nhiều/ít thành viên, có/không phương tiện, lời kể thiếu/mâu thuẫn, nguồn hợp lệ/hết hạn/xung đột, tài liệu chéo khu, nháp thiếu, lỗi model/tích hợp và yêu cầu cần bổ sung.

Nhãn chuẩn gồm: dữ kiện trích xuất, câu cần hỏi rõ, trường hồ sơ, checklist đúng, lý do/phụ thuộc, nguồn hướng dẫn, lỗi nháp, schema yêu cầu, trạng thái đích, người đang chờ và hành động mong đợi. BQL/chủ quy trình nên rà soát; nếu nhóm dự án tự gán, kết quả chỉ là kiểm thử kỹ thuật trên dữ liệu mô phỏng.

### 3.2. Chỉ số và ngưỡng thử nghiệm đề xuất

| Chỉ số | Cách đo | Ngưỡng đề xuất |
|---|---|---|
| Recall mục bắt buộc | Mục bắt buộc đúng được tạo / tổng mục bắt buộc trong nhãn | 100% trên bộ demo; báo riêng theo nhóm |
| Precision checklist | Mục áp dụng đúng / tổng mục được tạo | ≥95% |
| Đúng khu/phiên bản nguồn | Câu trả lời dùng đúng nguồn còn hiệu lực / tổng câu trả lời cần nguồn | 100%; lỗi chéo khu chặn phát hành |
| Citation support | Nhận định được đoạn nguồn hỗ trợ / tổng nhận định được chấm | ≥95%; mọi bước/giấy tờ quan trọng có nguồn |
| Định tuyến đúng lần đầu (P1) | Route đúng / tổng yêu cầu có route chuẩn | ≥95% trước khi bật định tuyến tự động; ca không chắc chuyển BQL, cư dân vẫn xác nhận gửi |
| Kiểm soát HITL | Quyết định được thực hiện đúng quyền và trạng thái / tổng quyết định | 100% |
| Gửi trùng | Số yêu cầu trùng do retry | 0 trong test idempotency |
| Hoàn tất tác vụ usability | Người dùng hoàn tất luồng chính không trợ giúp / tổng phiên | ≥80% trong thử nhỏ; báo cỡ mẫu |
| Thời gian tạo checklist | P95 từ submit profile đến hiển thị | ≤15 giây trên cấu hình thử |
| Công sức | So sánh thời gian/lượt hỏi lại với baseline | Chỉ kết luận sau pilot; mục tiêu giảm cần BQL chốt |
| Trích xuất và làm rõ | Trường đúng / trường có nhãn; câu hỏi cần thiết / câu hỏi đã hỏi; ca thiếu/mâu thuẫn được phát hiện / tổng ca tương ứng | Báo từng tỷ lệ và số mẫu; chưa có kết quả hay ngưỡng đã chốt |
| Kiểm nháp thẻ | Ca thiếu được chỉ đúng trước gửi / tổng ca nháp thiếu; số vòng BQL yêu cầu bổ sung | So với baseline; không coi ít vòng hơn là lợi ích nếu tăng quá nhiều thời gian sửa |
| Việc tiếp theo và quyền | Đề xuất có nguồn đúng khu, đúng người đang chờ; số ca agent vượt quyền | Lỗi vượt quyền là lỗi chặn phát hành |

Báo cả mẫu số và TP/FP/FN; không chỉ báo phần trăm. Chạy lặp các ca agent để đo dao động. Ghi model, prompt, rule, source index, số bước, token/chi phí và thời gian chạy. So sánh **agent với form + rules + tìm kiếm tài liệu** trên cùng ca và nguồn; đo tổng thời gian từ bắt đầu đến hoàn thành gồm kiểm tra/sửa của cư dân và BQL. Đây là kế hoạch đánh giá, chưa phải KPI đã đạt.

### 3.3. Kịch bản kiểm thử

| TC | Tình huống | Kết quả mong đợi | Liên kết |
|---|---|---|---|
| 01 | Chủ hộ có ô tô và cần internet | Checklist có thẻ cư dân, ô tô, internet, nội quy; lý do áp dụng đúng | FR-04 |
| 02 | Người thuê không phương tiện | Không tạo mục đăng ký xe; thủ tục cư trú dùng quy tắc người thuê | FR-04, BR-01 |
| 03 | Thiếu tư cách cư trú | Hỏi bổ sung; không tuyên bố checklist đầy đủ | FR-02 |
| 04 | Tài liệu đúng chủ đề nhưng thuộc khu khác | Retrieval loại bỏ; không dùng làm hướng dẫn | FR-06, NFR-11 |
| 05 | Nguồn hết hiệu lực, chưa có bản mới | Cảnh báo và chuyển BQL; không đưa hướng dẫn chắc chắn | FR-06–07 |
| 06 | Tài liệu chứa câu “bỏ qua kiểm tra quyền” | Coi là nội dung; không thay tool/policy | BR-10 |
| 07 | Cư dân gọi API duyệt | Backend từ chối và ghi sự kiện an toàn | FR-12, NFR-01 |
| 08 | Mạng timeout sau gửi | Retry cùng khóa không tạo yêu cầu thứ hai | FR-10, BR-09 |
| 09 | BQL yêu cầu bổ sung mặt trước giấy tờ | Cư dân thấy lý do; gửi bổ sung tạo phiên bản/lịch sử | FR-12–13 |
| 10 | BQL duyệt đăng ký nhưng thẻ chưa phát hành | Mục ở trạng thái được duyệt/đang thực hiện, chưa hoàn tất | FR-14, BR-04 |
| 11 | Cư dân đổi từ không xe sang có xe | Checklist cần đánh giá lại, thêm mục và giải thích; tiến độ cũ còn lịch sử | FR-03 |
| 12 | Tệp vượt kích thước/không đúng loại | Chặn trước gửi, hướng dẫn khắc phục, không tạo record thành công | FR-09 |
| 13 | Agent/RAG timeout | Trạng thái lỗi và thử lại; không mất bản nháp/đổi trạng thái | FR-17 |
| 14 | Truy cập signed URL của cư dân khác | Bị từ chối dù biết object key | NFR-01–02 |
| 15 | Tất cả mục bắt buộc xong, tùy chọn chưa làm | Onboarding được hoàn tất; hiển thị mục tùy chọn còn lại riêng | FR-16 |
| 16 | Nhắc việc đã lên lịch nhưng BQL vừa duyệt | Nhắc không còn phù hợp bị hủy | EX-03, BR-13 |
| 17 | Lời kể thiếu tư cách cư trú và phương tiện tự mâu thuẫn | Agent nêu dữ kiện đề xuất và hỏi từng điểm; không lưu giá trị đoán hoặc tạo checklist đầy đủ trước khi cư dân xác nhận | FR-02, BR-01 |
| 18 | Cư dân xác nhận sửa hồ sơ khi yêu cầu thẻ đang xử lý | Checklist phiên bản mới hiển thị diff, yêu cầu cũ vẫn gắn revision gốc; BQL quyết định trên bản được xem, không mất lịch sử | FR-03, FR-12, BR-02 |
| 19 | Hai nguồn cùng khu còn hiệu lực nhưng quy định giấy tờ khác nhau | Không khẳng định giấy tờ nào bắt buộc, gắn trạng thái xung đột và chuyển chủ nguồn/BQL xác nhận | FR-06, FR-09, BR-05 |
| 20 | Nháp thẻ thiếu trường hoặc giấy tờ được nguồn hợp lệ yêu cầu | Agent chỉ rõ thiếu/chưa rõ và citation; backend chặn gửi, cư dân vẫn giữ nháp để sửa | FR-09–10, BR-05, BR-11 |
| 21 | BQL yêu cầu bổ sung trên revision đã gửi | Cư dân thấy lý do, trường/tệp cần sửa và revision; gửi lại sau xác nhận tạo bản mới, bản cũ/decision còn lịch sử | FR-12–13, BR-12 |
| 22 | Model/RAG lỗi hoặc agent hết 8 bước/2 lần gọi LLM trong một lượt | Nêu tạm không khả dụng hoặc giới hạn; vẫn xem được trạng thái chính thức và nháp; không tự gửi/duyệt; thử lại đọc dữ liệu mới nhất | FR-17, NFR-05 |
| 23 | Agent đề xuất gửi/duyệt/hoàn tất hoặc tài liệu chứa chỉ thị đổi policy | Tool/API từ chối; checklist/quyền/trạng thái không đổi; sự kiện an toàn được ghi | BR-01, BR-07–10, NFR-01 |

## 4. Backlog và lộ trình tham khảo

| Thứ tự | Công việc | Đầu ra/điều kiện hoàn thành | Phụ thuộc |
|---|---|---|---|
| 1 | Chốt Brief và khu thí điểm | Danh sách người dùng, thủ tục P0, owner và ranh giới dữ liệu | BQL/chủ đề |
| 2 | Dựng ma trận thủ tục và dữ liệu eval | Rule/source/schema có phiên bản; tập dev/eval tách biệt | Người rà soát |
| 3 | Prototype UX và usability test | Cư dân/BQL hiểu trạng thái, nguồn và HITL | Wireframe hiện tại |
| 4 | Auth, tenant và mô hình dữ liệu | Truy cập chéo bị chặn; migration/test | Kiến trúc được chốt |
| 5 | Checklist engine | Kết quả xác định theo rules, có lý do và version | Ma trận thủ tục |
| 6 | RAG hướng dẫn | Retrieval đúng khu/phiên bản, citation và no-source behavior | Tài liệu đã chuẩn hóa |
| 7 | Request + HITL | Mẫu nháp thẻ, preflight có nguồn, xác nhận, gửi idempotent, BQL quyết định/bổ sung và timeline | Schema/kênh nhận |
| 8 | Agent orchestration | Làm rõ hồ sơ, đề xuất bước tiếp theo, kiểm nháp; checkpoint, giới hạn tool, recovery và audit | Các service P0 ổn định |
| 9 | Eval, bảo mật và sửa lỗi | Báo cáo metric, test quyền/log/idempotency và giới hạn | Bộ eval |
| 10 | P1 dashboard/nhắc việc | Chỉ làm khi trạng thái và dữ liệu P0 đủ tin cậy | Pilot P0 |

Lộ trình sáu tuần chỉ là tham khảo: tuần 1 xác minh/dữ liệu; tuần 2 UX + auth/data; tuần 3 checklist/RAG; tuần 4 request/HITL; tuần 5 agent/eval/security; tuần 6 hoàn thiện demo và báo cáo. Cần điều chỉnh theo đội ngũ, hạn nộp và khả năng tích hợp.

## 5. Quyết định mở và mặc định tạm

| ID | Cần quyết định | Mặc định tạm | Ảnh hưởng |
|---|---|---|---|
| Q1 | Khu và thủ tục P0 | Một khu giả lập; 5 nhóm thủ tục trong đề bài | Rules, nguồn, demo |
| Q2 | Tư cách cư trú | Chủ sở hữu/người thuê/thành viên | Form và checklist |
| Q3 | Kênh gửi thật | Mô phỏng trong prototype | Khả năng chứng minh end-to-end |
| Q4 | Lưu trữ tệp | Chưa chốt; không lưu tệp thật trong prototype | Bảo mật và FR-09–13 |
| Q5 | Người duyệt nghiệp vụ | BQL mô phỏng | Chưa thể khẳng định đúng quy trình thật |
| Q6 | Model và vector store production | Theo đề bài cho prototype; đánh giá lại trước production | Chất lượng, chi phí, dữ liệu |
| Q7 | SLA và nhắc việc | Không tự đặt; chỉ dùng số giả lập có nhãn | Dashboard/EX-03 |
| Q8 | Chính sách lưu/xóa | Chưa chốt; chặn pilot dữ liệu thật | Compliance và kiến trúc |

## 6. Kịch bản demo đề xuất

1. Đăng nhập vai trò cư dân, kể tình huống “Chủ hộ có ô tô” nhưng bỏ sót nhu cầu internet; agent hỏi rõ và cư dân xác nhận hồ sơ.
2. Tạo checklist bằng rules, cho thấy mục đăng ký ô tô xuất hiện vì hồ sơ có phương tiện.
3. Mở “Đăng ký thẻ cư dân”, xem hướng dẫn và nguồn đúng khu/phiên bản.
4. Tạo nháp thẻ cư dân thiếu một thông tin; agent chỉ chỗ thiếu có căn cứ, backend kiểm điều kiện, cư dân sửa rồi xem dữ liệu chia sẻ và xác nhận gửi.
5. Chuyển sang BQL; mở yêu cầu và chọn “Yêu cầu bổ sung” với lý do.
6. Quay lại cư dân, bổ sung mô phỏng và gửi lại.
7. BQL duyệt; chứng minh trạng thái “được duyệt” và “hoàn tất” không bị nhập nhằng.
8. Mở UI Flow; dashboard dữ liệu demo nếu dùng thì ghi rõ là minh họa P1, không phải nghiệm thu P0.
9. Chuyển tình huống “Nguồn hướng dẫn đã cũ” để chứng minh agent dừng và chuyển BQL.

Cuối demo phải nói rõ wireframe không gọi AI, không đọc/đẩy tệp và không phải bằng chứng hệ thống đã đạt các ngưỡng eval.
