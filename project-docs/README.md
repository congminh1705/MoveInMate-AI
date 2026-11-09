# Hồ sơ dự án MoveInMate

> Bản public: đã bỏ `de_tai.png`, thay địa chỉ triển khai cũ bằng địa chỉ mẫu và che mã học viên trong PDF trình bày. Giữ tên tác giả. Các tài liệu là snapshot theo ngày; một số liên kết tới `docs/nghiep-vu` hoặc `deliverables` thuộc bộ hồ sơ gốc chưa được đưa vào repo này. Cấu hình và cách chạy bản public ở [README](../README.md).

**Rà soát: 19/10/2026.** Thư mục này giữ hồ sơ có mục đích riêng, không giữ
nhiều bản hướng dẫn luồng cũ. Muốn chạy/test ngay, mở [README](../README.md)
hoặc [mục lục tài liệu hiện hành](../docs/README.md).

## Hồ sơ cần giữ trong Git

| Nhóm | Tệp | Vai trò |
|---|---|---|
| Yêu cầu VHR-16 | [PROJECT_BRIEF](PROJECT_BRIEF.md), [ảnh đề tài](de_tai.png) | Bối cảnh và đầu vào gốc; không phải mô tả UI hiện tại |
| Phạm vi sản phẩm | [MoveInMate_Brief](MoveInMate_Brief.md), [BRD](MoveInMate_BRD.md), [PRD](MoveInMate_PRD.md) | Yêu cầu và tiêu chí thiết kế; các cập nhật được xác nhận có ưu tiên hơn baseline cũ |
| Kiến trúc thiết kế | [SAD v1.0](MoveInMate_SAD_v1.0.md), [deck đầu vào](MoveInMate_MVP_RAG_SAD_Deck_Final.pptx) | Hồ sơ thiết kế lịch sử, không dùng làm sơ đồ runtime; hiện trạng ở [kiến trúc](../docs/architecture_diagram.md) |
| Căn cứ nghiên cứu | [Problem Analysis](PROBLEM_ANALYSIS.md), [Pain Points](RESEARCH_PAIN_POINTS.md), [Competitive Analysis](COMPETITIVE_ANALYSIS.md) | Ba góc nhìn khác nhau: phương pháp, giả thuyết và đối chiếu sản phẩm; không phải ba bản luồng trùng nhau |
| Tài khoản và an toàn vận hành | [AUTH_SETUP](AUTH_SETUP.md) | Đăng nhập, cấp/cấp lại tài khoản, mật khẩu tạm và Reset |
| Triển khai | [AWS deployment](AWS_DEPLOYMENT_20261009.md) | Runbook có điều kiện áp dụng, backup và chi phí; không phải nhật ký triển khai |
| Trải nghiệm và dữ liệu test | [Investor Guide](INVESTOR_DEMO_GUIDE_AND_TEST_DATA.md) | Hướng dẫn hiện hành, dữ liệu tổng hợp và kết quả cần quan sát |
| Yêu cầu nộp | [MVP Submission](MVP_Submission_Requirements_20261004.md) | Giữ nguyên căn cứ về nội dung bộ nộp |
| Video và slide bàn giao | [Video mới nhất](DEMO/README.md), [slide PDF](PRESENTATION/README.md) | Giữ đúng một MP4 mới nhất và một PDF được chọn trong Git theo yêu cầu; không kèm thư mục dựng |

Brief, BRD, PRD và SAD có nội dung đề xuất/chưa được BQL độc lập phê duyệt.
Không xóa yêu cầu nguồn chỉ vì chức năng hiện tại chưa đáp ứng; các khác biệt
runtime được nêu trong [nghiệp vụ hiện hành](../docs/nghiep-vu/README.md).

## Đã hợp nhất và không đưa lên Git

- Ghi chú rời về agent BQL, popup mật khẩu, khôi phục tài khoản, thông báo,
  bổ sung ticket, màu trạng thái và giọng đọc: nội dung còn đúng đã đưa vào
  [luồng](../docs/nghiep-vu/03-quy-trinh-nghiep-vu.md),
  [API](../docs/nghiep-vu/06-api-va-giao-dien.md) và [AUTH_SETUP](AUTH_SETUP.md).
- Hai bộ sơ đồ cũ được thay bằng [một bộ hiện hành](../docs/nghiep-vu/so-do/README.md);
  prototype wireframe cũ không còn là hướng dẫn thao tác.
- Lời dẫn video, ghi chú thuyết trình, thư mục dựng slide/video, file xuất lặp
  và nhật ký triển khai/QA riêng không thuộc tài liệu cần push. MP4 mới nhất
  và PDF được chọn ở bảng trên là ngoại lệ bàn giao có chủ ý.
  Bằng chứng nộp đã có trong `deliverables/` vẫn giữ theo mốc lịch sử.

Không đưa tài khoản thật, API key, token, mật khẩu riêng cư dân hoặc dữ liệu
giấy tờ vào tài liệu. Bộ tài khoản demo được công bố riêng tại
[README](../README.md#đăng-nhập-để-test--đọc-mục-này-trước).
