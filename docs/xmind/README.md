# Bộ sơ đồ XMind — MoveInMate AI

Bộ này diễn giải nghiệp vụ và cấu trúc bản source hiện hành: **18 sheet**, gồm **12 luồng người dùng**, bản đồ sản phẩm, use case, cấu trúc màn hình, nguồn/RAG, vòng đời ticket và kiến trúc.

## Mở và chỉnh sửa

Tải tệp `.xmind` về và mở bằng XMind. Mỗi sheet giữ topic, vị trí, màu, relationship và ghi chú điều kiện/nguồn. Tệp master và các tệp nhóm dùng chung ID và nội dung sheet.

GitHub hiển thị ảnh SVG trong README, không tự chuyển tệp XMind thành sơ đồ. Sau khi chỉnh sửa XMind, cần cập nhật ảnh SVG tương ứng để hai bản tiếp tục thống nhất.

| Tệp XMind | Sheet | Nội dung |
| --- | --- | --- |
| [moveinmate-ai.xmind](moveinmate-ai.xmind) | 18 | Toàn bộ bộ sơ đồ |
| [01-product-and-use-cases.xmind](01-product-and-use-cases.xmind) | 3 | Sản phẩm, tác nhân/use case, cấu trúc màn hình |
| [02-user-flows.xmind](02-user-flows.xmind) | 12 | Hành trình cư dân/BQL, điều kiện và điểm xác nhận |
| [03-ticket-states.xmind](03-ticket-states.xmind) | 1 | Các trạng thái ticket và quan hệ xét duyệt |
| [04-ai-and-architecture.xmind](04-ai-and-architecture.xmind) | 2 | Nguồn/RAG và thành phần thực thi |

Ảnh SVG trong `previews/` dùng để hiển thị trên GitHub. Chúng được dựng từ cùng mô hình nội dung và topic ID với XMind, có bố cục tối ưu cho README; **không phải ảnh chụp hoặc bản export từ XMind Desktop**. XMind Desktop chưa được mở trong đợt tạo bộ tài liệu này. Các kiểm tra đã thực hiện gồm cấu trúc ZIP/JSON, ID, relationship endpoint, nguồn tham chiếu, tính đồng nhất master/nhóm và render SVG để rà soát.

## Mục lục ảnh

| Mã | Sơ đồ | Phạm vi |
| --- | --- | --- |
| 01 | [Bản đồ sản phẩm](previews/01-product-map.svg) | Cư dân, BQL, tri thức, dữ liệu và kiểm soát |
| 02 | [Use case theo tác nhân](previews/02-use-cases.svg) | Hai role người dùng; tư cách cư trú và công cụ AI |
| 03 | [Cấu trúc không gian làm việc](previews/03-information-architecture.svg) | Nhóm màn hình và tương tác |
| 04 | [Đăng nhập và xác nhận cư trú](previews/04-resident-onboarding.svg) | Luồng 01; thiết lập và dữ liệu được cấp |
| 05 | [Gửi thủ tục](previews/05-resident-request.svg) | Luồng 02; nháp, xác nhận và mã ticket |
| 06 | [Bổ sung cùng ticket](previews/06-correction-resubmit.svg) | Luồng 03; kiểm phiên bản và gửi lại |
| 07 | [BQL xét duyệt](previews/07-manager-review.svg) | Luồng 04; quyết định và kết quả thực tế |
| 08 | [Tài khoản phụ thuộc](previews/08-dependent-account.svg) | Luồng 05; điều kiện, giao dịch và bàn giao |
| 09 | [Phương tiện và giấy tờ](previews/09-vehicle-registration.svg) | Luồng 06; đọc tệp hỗ trợ, cư dân/BQL xác nhận |
| 10 | [Trợ lý BQL theo nhóm](previews/10-manager-agent.svg) | Luồng 07; tối đa 20 ticket và xác nhận snapshot |
| 11 | [Khôi phục truy cập](previews/11-password-recovery.svg) | Luồng 08; đối chiếu trước khi cấp lại |
| 12 | [Thông báo và ẩn danh sách](previews/12-notifications-and-hide.svg) | Luồng 09; trạng thái đọc và visibility riêng |
| 13 | [Người cùng ở và căn hộ](previews/13-household-management.svg) | Luồng 10; quyền thêm người và nguồn dữ liệu chung |
| 14 | [Tra cứu và xác nhận nguồn](previews/14-knowledge-rag.svg) | Phạm vi nguồn, BM25, trích dẫn, revision |
| 15 | [Vòng đời ticket](previews/15-ticket-states.svg) | Mốc xét duyệt, kết thúc và điều kiện hủy |
| 16 | [Kiến trúc thực thi](previews/16-system-architecture.svg) | Web, backend, agent, retrieval, provider và DB |
| 17 | [Cấp tài khoản trực tiếp](previews/17-direct-account-provisioning.svg) | Luồng 11; BQL cấp và bàn giao riêng |
| 18 | [Checklist và chưa có nhu cầu](previews/18-checklist-needs.svg) | Luồng 12; mục được phép và nhánh không tạo ticket |

## Cách đọc

- Xanh biển: cư dân/chủ sở hữu; tím: BQL; xanh ngọc: hệ thống; vàng: AI; hình thoi: điều kiện; đỏ: tình huống cần xử lý.
- Mũi tên trong sơ đồ luồng thể hiện đường đi và điều kiện. Nhánh trong bản đồ sản phẩm/use case thể hiện phân nhóm, không tự xác định thứ tự thực hiện hoặc cấp quyền.
- Dữ liệu chi tiết và đường dẫn source nằm trong notes của topic. Các nguồn chính là `src/security`, `src/services`, `src/repositories`, `src/rag`, `src/api`, kiểm thử liên quan và `project-docs/AUTH_SETUP.md`.
- SVG trạng thái ưu tiên nhánh thông thường để dễ đọc; ba cạnh API trực tiếp từ `submitted` được ghi ở chú thích. XMind giữ cả 10 relationship xét duyệt. Nhánh hủy dùng điều kiện riêng, được ghi cạnh trạng thái hủy và trong notes.
- Sơ đồ kiến trúc thể hiện các thành phần/đường gọi chính; không phải sequence diagram cho mọi endpoint. Sơ đồ IA gom nhóm không gian làm việc, không khẳng định số trang triển khai.

## Các quy tắc cần giữ khi chỉnh sửa

1. BQL cấp tài khoản; không có tự đăng ký BQL. Chủ sở hữu/người nhà/người thuê là tư cách cư trú, không phải role quản trị mới.
2. AI hỗ trợ đọc và chuẩn bị trong quyền người gọi; cư dân/BQL xác nhận qua luồng được phép. Model không có quyền tự duyệt, từ chối, đọc mật khẩu hay ghi SQL.
3. Nháp, đã gửi, đã duyệt và hoàn tất là các mốc khác nhau. Duyệt không tự chứng minh công việc ngoài đời đã xong.
4. Bổ sung giữ ID ticket và lịch sử; dữ liệu thay đổi sau preview cần được kiểm tra lại. Cấp tài khoản và retry phải tránh ghi trùng.
5. Ẩn danh sách không xóa ticket, tài khoản, giấy tờ hay lịch sử nghiệp vụ.
6. Các tệp này không chứa mật khẩu, khóa API, hồ sơ cư dân hoặc địa chỉ máy chủ đang vận hành. Nội dung tài liệu không thay thế kiểm tra quyền và quy tắc thực thi trong source.

[Về README dự án](../../README.md)
