# Yêu cầu bộ hồ sơ nộp chốt MVP — 04/10/2026

Nguồn: yêu cầu giảng viên được người dùng cung cấp trong cuộc trao đổi ngày
04/10/2026. Đây là yêu cầu về hồ sơ nộp, không mở rộng phạm vi nghiệp vụ
MoveInMate đã mô tả trong Brief/BRD/PRD.

## Nội dung cần nộp

1. **MVP Demo:** video 3 phút thể hiện user flow end-to-end.
2. **Architecture diagram:** sơ đồ components và data flow.
3. **Repository:** ít nhất 10 Pull Request đã merge.
4. **README.md:** setup instructions, environment variables, sample queries và thông tin cần để chạy/đối chiếu sản phẩm.
5. **Eval evidences:** ít nhất 5 test case manual có output thực tế.

## Cách trình bày được yêu cầu

Bộ `deliverables/` là hồ sơ sản phẩm để gửi giảng viên chốt MVP, không phải
hướng dẫn học cách mở PR, quay video hay lập kế hoạch đánh giá. Giữ phần
setup kỹ thuật trong README vì đây là mục cần nộp; các báo cáo còn lại trình
bày sản phẩm, đầu ra, bằng chứng, nhận xét và giới hạn đã quan sát.

Theo cập nhật ngày 05/10/2026, đây là đề tài nhóm. Hồ sơ trình bày theo
giọng nhóm, không có phần ghi công công cụ hỗ trợ.
Nhận xét dùng văn phong tự nhiên và dựa trên output thực tế. Phương pháp thu
thập bằng chứng phải đúng với lần thử; không gán tên người thử, chữ ký hoặc
xác nhận chưa có. Các thành phần mô hình của sản phẩm vẫn được mô tả đúng
trong kiến trúc.

Không đổi phép thử định tuyến tự động thành ca manual, không dựng đầu ra,
không thay số PR bằng số commit merge và không tạo PR rỗng để đủ chỉ tiêu.
Ngưỡng 10 PR là yêu cầu cần đạt, không phải số liệu mặc định của báo cáo;
số đã merge phải đối chiếu từ GitHub.

## Yêu cầu trình bày bổ sung

- Architecture phải hiện đầy đủ components và data flow ngay trong báo cáo.
- Eval đặt tiêu chí, output và ảnh thực tế trong từng ca, có nhận xét và giới hạn.
- README tại root cũng phải có setup instructions, env vars và sample queries;
  không chỉ trỏ tới một hướng dẫn khác.
- Phần PR dùng trạng thái đã đối chiếu, giữ riêng số PR và số merge commit.

## Công bố bộ nộp

Tạo repository GitHub mới tên `deliverables`, đặt public, giữ nguyên đầy đủ
thư mục `deliverables/` trong repo mới. Không công bố mã ứng dụng, `.env`,
dữ liệu DB, cấu hình riêng hoặc thay đổi quyền repo mã nguồn. Lịch sử PR
vẫn thuộc repository P-047; repo bộ nộp không kế thừa số PR đã merge.
