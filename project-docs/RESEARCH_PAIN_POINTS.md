# NGHIÊN CỨU PAIN POINT — MoveInMate AI

**Mã đề:** VHR-16  
**Phiên bản:** 0.2  
**Ngày:** 24/09/2026  
**Loại bằng chứng:** Nghiên cứu thứ cấp và khảo sát nguồn công khai. Chưa phỏng vấn cư dân hay BQL của doanh nghiệp X.  
**Đọc tiếp:** `COMPETITIVE_ANALYSIS.md` → `MoveInMate_BRD.md` mục 8 → `MoveInMate_PRD.md`

Tài liệu này chọn pain point để làm BRD. Mọi nhận định đều gắn loại bằng chứng. Không có mẫu sơ cấp nên không có tỷ lệ phần trăm người dùng.

## 1. Câu hỏi nghiên cứu

Cư dân mới nhận nhà đang vướng ở đâu đủ lớn để một agent onboarding giải quyết được trong một khu, một bộ thủ tục, và vẫn để BQL duyệt hồ sơ?

## 2. Nguồn và cách dùng

| Nguồn | Ngày xem | Dùng để |
|---|---|---|
| Đề tài VHR-16 | Tài liệu nhóm | Bài toán gốc, ràng buộc HITL, đúng khu, bảo mật |
| Vinhomes Resident, Google Play `com.vinhomes.resident` | 24/09/2026 | App cư dân đang vận hành: tiện ích, hóa đơn, yêu cầu hỗ trợ, intercom. 4,7 sao; hơn 100 nghìn lượt tải; mô tả cập nhật 02/09/2026 |
| Masterise Homes, Google Play `com.masterisehomes.customer` | 24/09/2026 | App theo hành trình mua nhà tới lúc nhận nhà. 4,2 sao; 83 bài đánh giá; mô tả cập nhật 13/08/2026 |
| Bcons Service, Google Play `vn.com.bconsliving` | 24/09/2026 | App chung cư: thông báo, thanh toán, tiện ích, yêu cầu hỗ trợ, đăng ký ra vào. 2,6 sao; 44 bài đánh giá; mô tả cập nhật 19/08/2026 |
| HomeID Cư dân, Google Play `asia.homeid` | 24/09/2026 | App cư dân thiên về phí, thông báo, mua sắm. 4,0 sao; 21 bài đánh giá; cập nhật 06/03/2024 |
| `PROBLEM_ANALYSIS.md` | Nội bộ | Giả thuyết H1–H7 và cách bác bỏ. Tài liệu này kết luận giả thuyết nào được giữ |

Một bài đánh giá công khai là ví dụ, không phải tần suất. Điểm sao là của cả ứng dụng, không đo riêng khâu onboarding.

## 3. Việc app cư dân đang làm

Bốn ứng dụng công khai phủ cuộc sống sau khi đã ở hoặc hành trình mua nhà. Không ứng dụng nào, trong phần mô tả nhà phát triển, nêu checklist thủ tục theo tư cách cư trú, số thành viên và phương tiện, kèm trích nguồn đúng khu.

| Việc cư dân cần lúc mới đến | Vinhomes Resident | Masterise Homes | Bcons Service | HomeID Cư dân |
|---|---|---|---|---|
| Biết việc nào áp dụng cho đúng tình huống | Không nêu | Theo dõi trạng thái mua, ký, đặt cọc | Không nêu | Không nêu |
| Hướng dẫn có phiên bản tài liệu của từng khu | Không nêu | Không nêu | Thông báo từ BQL | Thông báo tới cư dân |
| Gửi yêu cầu cho BQL | Yêu cầu hỗ trợ dịch vụ tòa nhà | Liên hệ tư vấn bán hàng | Đăng ký yêu cầu, hỗ trợ | Phản hồi góp ý |
| Đăng ký ra vào / xe | Intercom, đăng ký khách, phân tầng thang | Không nêu | Đăng ký ra vào | Thanh toán phí xe |
| Biết hồ sơ đang chờ ai trong cả chuỗi onboarding | Không nêu | Trạng thái mua nhà | Không nêu | Không nêu |
| Thanh toán, tiện ích, đời sống hàng ngày | Có | Không phải trọng tâm app này | Có | Có |

Khoảng trống lặp lại: cổng dịch vụ và cổng mua nhà đã có; lớp “việc cần làm lúc mới nhận nhà, đúng hồ sơ của tôi, đúng tài liệu của khu” thì không thấy trong mô tả sản phẩm.

## 4. Pain point

| ID | Pain point | Bằng chứng | Độ chắc | Quyết định |
|---|---|---|---|---|
| PP-01 | Cư dân không có danh sách thủ tục đúng tình huống của mình | Đề VHR-16. Bốn app đối chiếu không mô tả checklist theo tư cách cư trú, thành viên, xe | Đủ để làm việc, vì vừa là yêu cầu đề vừa là lỗ hổng sản phẩm công khai | Chọn làm pain point chính |
| PP-02 | Hướng dẫn không gắn khu, phiên bản và nguồn | Đề VHR-16 bắt buộc hướng dẫn đúng từng khu. App hiện đưa thông báo hoặc tài liệu chung, không thấy trích nguồn theo thủ tục | Đủ để thành ràng buộc sản phẩm | Giữ, đi cùng PP-01 |
| PP-03 | Thủ tục thẻ ra vào hoặc thẻ xe dễ thành vòng chờ | Vinhomes Resident có review công khai: đồng bộ app khoảng một tuần, chưa làm được thẻ ra vào và thẻ gửi xe, phát sinh phí gửi xe theo đêm. Bcons có mục đăng ký ra vào nhưng review nói BQL hẹn lịch rồi không đến, phản ánh cả ngày chưa thấy trả lời | Yếu về tần suất, đủ để chọn làm luồng đại diện | Một luồng HITL của MVP, không suy ra tỷ lệ thị trường |
| PP-04 | Cư dân hỏi lại vì không thấy trạng thái | Suy ra từ PP-01 và các review về không phản hồi. Chưa có log ticket của doanh nghiệp X | Chưa đủ để tuyên bố độ lớn | Thiết kế để đo. Chưa đưa vào cam kết lợi ích |
| PP-05 | App chủ đầu tư dừng ở mua và đặt cọc | Mô tả Masterise Homes: ảnh, tour 3D, bộ lọc, thông báo đổi trạng thái mua, ký, ra ngân hàng đặt cọc, một chạm gọi tư vấn | Đủ để định vị | Dùng để nói MoveInMate bắt đầu sau khi nhận nhà |

Giả thuyết H1, H2, H4, H5 trong `PROBLEM_ANALYSIS.md` gộp vào PP-01 và PP-02. H6 và H7 giữ ở dạng cần đo (PP-03, PP-04). H3 chưa có log nên không nâng thành sự thật.

## 5. Pain point được chọn

**PP-01, với PP-02 là điều kiện để checklist đáng tin.** Luồng làm mẫu ưu tiên đăng ký thẻ cư dân (PP-03): cư dân chuẩn bị đủ hồ sơ, gửi có xác nhận, BQL duyệt hoặc yêu cầu bổ sung, cư dân thấy trạng thái khác với “đã gửi”. Thẻ xe chỉ là mục checklist theo hồ sơ trong MVP, không mở luồng duyệt thứ hai.

Pain point này chọn được vì bốn lý do:

1. Đề bài đặt nó làm bài toán.
2. App cư dân lớn đang giải quyết tiện ích, phí và yêu cầu hỗ trợ, chưa giải quyết checklist theo hồ sơ.
3. Có một thủ tục cụ thể để demo hết vòng HITL.
4. Nằm trong phạm vi một khu và một bộ quy tắc, không cần tích hợp toàn bộ tòa nhà.

Không chọn “thay BQL trả lời mọi câu” và không chọn “rút ngắn thời gian cấp thẻ vật lý”. Thời gian cấp thẻ phụ thuộc vận hành hiện trường. Sản phẩm chỉ kiểm soát chất lượng đầu vào và độ rõ của trạng thái.

## 6. Người dùng ưu tiên

| Nhóm | Vì sao ưu tiên | Việc họ cần trong MVP |
|---|---|---|
| Cư dân mới, chủ hộ hoặc người thuê, trong một khu | Người chịu pain point chính | Khai báo ngắn, xem checklist, làm một thủ tục, theo dõi |
| Nhân viên BQL tiếp nhận | Người đóng HITL và sở hữu quy tắc | Hàng đợi, lý do bổ sung hoặc duyệt, không để AI duyệt hộ |
| Quản lý vận hành | Cần số liệu sau khi trạng thái đã đáng tin | Để sau MVP |

Bộ phận xe, internet, tiện ích là đầu mối nhận yêu cầu. MVP chỉ cần một đầu mối cho một loại thủ tục.

## 7. Giá trị cốt lõi rút ra

Cư dân mới biết việc nào là của mình, làm theo tài liệu còn hiệu lực của đúng khu, và thấy hồ sơ đang chờ ai. BQL nhận yêu cầu đủ trường và vẫn là người quyết định hồ sơ hợp lệ.

Giá trị này đứng được khi checklist có lý do áp dụng, câu hướng dẫn có nguồn hoặc nói rõ là chưa có nguồn, và trạng thái “đã gửi” không bị tính là “đã xong”.

**Giả thuyết giá trị riêng của agent, chưa được khảo sát xác nhận:** khi cư dân mô tả tự nhiên, bỏ sót dữ kiện hoặc đưa thông tin mâu thuẫn, trợ lý có thể hiểu phần đã biết, hỏi đúng điều còn thiếu và giải thích việc tiếp theo có căn cứ. Cần thử giả thuyết này trên cùng tình huống với form + rules + tìm kiếm tài liệu; nếu phương án đơn giản cho kết quả tương đương sau khi tính thời gian kiểm tra/sửa, không có bằng chứng để tăng độ phức tạp bằng agent.

## 8. Hệ quả cho yêu cầu nghiệp vụ

| Từ pain point | Yêu cầu nghiệp vụ sẽ ghi trong BRD |
|---|---|
| PP-01 | Checklist theo khu và hồ sơ tối thiểu; có mục bắt buộc, lý do, phụ thuộc |
| Giả thuyết tương tác từ PP-01 | Nhận mô tả tự nhiên, hỏi làm rõ dữ kiện thiếu/mâu thuẫn và để cư dân xác nhận trước khi lưu hồ sơ; rules vẫn quyết định checklist |
| PP-02 | Mỗi hướng dẫn có nguồn, phiên bản, ngày hiệu lực, khu; thiếu nguồn thì chuyển BQL |
| PP-03 | Một luồng thẻ cư dân: bản nháp, cư dân xác nhận gửi, BQL bổ sung hoặc duyệt; thẻ xe chỉ là mục checklist theo hồ sơ |
| PP-04 | Timeline trạng thái; chưa có baseline nên KPI này là chỉ số theo dõi, chưa phải cam kết giảm bao nhiêu phần trăm |
| Ràng buộc đề bài | AI không duyệt giấy tờ; tách dữ liệu theo khu và theo người; thu thập tối thiểu |

## 9. Khảo sát sơ cấp còn để ngỏ

Chưa có quyền tiếp cận cư dân hoặc BQL của doanh nghiệp X, nên vòng này không bịa phiếu trả lời. Nếu nhóm phát được khảo sát, dùng đúng các câu dưới đây. Kết quả sơ cấp chỉ thay pain point đã chọn khi nó bác bỏ PP-01: hầu hết cư dân đã có checklist đủ và không sót việc.

### Cư dân mới, 5–8 người, việc thật trong 1–3 tháng gần đây

- Thủ tục gần nhất anh/chị phải làm khi chuyển đến là gì?
- Anh/chị biết việc đó từ đâu?
- Hồ sơ gửi lần đầu đã đủ chưa? Thiếu mục nào?
- Liên hệ mấy lần, qua kênh nào?
- Lúc nào anh/chị không biết bước tiếp theo hoặc đang chờ ai?
- Với thủ tục thẻ hoặc xe, anh/chị cần thấy trạng thái nào thì khỏi phải hỏi lại?

### BQL, 3–5 người

- Một hồ sơ đủ và một hồ sơ thiếu khác nhau ở những trường nào?
- Việc nào cư dân hỏi lại nhiều nhất trong tuần nhận nhà?
- Trạng thái đang ghi ở đâu, ai được sửa?
- Tài liệu nào là bản đang hiệu lực của khu, ai duyệt bản mới?

Không hỏi “anh/chị có muốn dùng AI không” trước khi nghe xong việc họ vừa làm.

## 10. Điều nghiên cứu này chưa chứng minh

- Tần suất sót việc, số vòng bổ sung, thời gian BQL tại doanh nghiệp X.
- Quy trình thật của từng khu và tên bộ phận tiếp nhận.
- Cư dân có chịu khai báo hồ sơ tối thiểu hay không.
- Độ chính xác trích xuất từ lời kể, câu hỏi làm rõ có phù hợp không và thời gian kiểm tra/sửa so với form + rules + tìm kiếm tài liệu.

BRD và scope MVP phía sau dùng các mục đã chọn ở trên. Chỉ số lợi ích để ở dạng “đo được”, chưa điền mục tiêu phần trăm.
