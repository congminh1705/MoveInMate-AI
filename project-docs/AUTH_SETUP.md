# Đăng nhập, cấp tài khoản và Reset demo

**Đối chiếu source local: 19/10/2026.** Hướng dẫn sử dụng tài khoản thật cần
người vận hành quản lý secret; bảng [đăng nhập demo](../README.md#đăng-nhập-để-test--đọc-mục-này-trước)
chỉ dành cho bản thử nghiệm công khai.

## 1. Tài khoản và cấu hình

Bộ mặc định gồm `admin`, `user`, `demo001`–`demo010`. Hiện một BQL được
cấp sẵn; không có form tự đăng ký BQL. Cư dân nhận tài khoản từ BQL, không chọn
role lúc đăng nhập. `vuongtq` không phải tài khoản bắt buộc.

| Biến cấu hình | Ý nghĩa |
|---|---|
| `AUTH_MODE`, `AUTH_PROVIDER` | `required`, `local`; không cần Supabase |
| `AUTH_JWT_SECRET` | Khóa riêng đủ mạnh; không dùng giá trị demo khi có dữ liệu thật |
| `LOCAL_AUTH_ADMIN_USERNAME/PASSWORD` | Tài khoản BQL cấu hình sẵn |
| `LOCAL_AUTH_USER_USERNAME/PASSWORD` | Tài khoản cư dân cấu hình sẵn |
| `LOCAL_AUTH_SITE_ID`, `LOCAL_AUTH_USER_RESIDENT_ID` | Khu/hồ sơ gắn tài khoản cư dân, phải tồn tại đúng |
| `LOCAL_AUTH_ADMIN_SITE_IDS` | Các khu bổ sung BQL được quản lý; danh mục không tự cấp quyền |
| `SETTINGS_ENCRYPTION_KEY` | Khóa mã hóa ngoài DB, cần cho cấu hình và mật khẩu bàn giao |
| `SHOW_LOCAL_LOGIN_CREDENTIALS` | Mặc định false; chỉ development/test mới được hiện gợi ý |
| `LOGIN_RESET_ENABLED`, `LOGIN_RESET_CODE` | Bật Reset có BQL, mã và xác nhận; mặc định tắt |
| `LOGIN_RESET_PRESERVED_USERNAMES` | Giữ thêm tài khoản ngoài bộ mặc định nếu được cấu hình rõ |

Biến có dấu `/PASSWORD` ở bảng là cách viết gọn hai biến riêng, không phải một
tên biến có dấu gạch chéo. Xem tên đầy đủ trong `.env.example`.

Tên đăng nhập không phân biệt hoa/thường, chữ/số và `_.@-`, tối đa 80 ký tự.
Mật khẩu phân biệt hoa/thường, không tự bỏ khoảng trắng. Tài khoản cấu hình
local/test có trần riêng; triển khai công khai phải dùng mật khẩu mạnh.
Không công bố toàn bộ `.env`, API key, JWT secret, khóa mã hóa hoặc mật khẩu riêng.

Sau khi sửa cấu hình riêng, nạp lại bằng `docker compose up -d --no-deps --wait backend`,
không dùng `restart` để kỳ vọng nhận biến môi trường mới.
Khởi động bình thường không đặt lại mật khẩu riêng hoặc tự mở khóa membership.

## 2. Cấp tài khoản cư dân trực tiếp

1. Đăng nhập BQL, mở **Đăng ký cư dân → Tạo tài khoản cư dân**.
2. Nhập người, tư cách và chọn khu/tòa/căn hộ thuộc quyền quản lý.
3. Dùng gợi ý **TK/MK ngẫu nhiên** hoặc nhập đúng hợp đồng form. Đây chỉ là điền
   gợi ý, chưa tạo tài khoản và chưa thay mật khẩu người nào.
4. Xem lại thông tin, tích xác nhận và tạo. Server kiểm tên duy nhất, quyền khu
   và điều kiện chủ sở hữu/căn hộ trước khi lưu.
5. Sao chép và bàn giao riêng. Không mặc định có gửi email/tin nhắn.
6. **Quản lý tài khoản** là phần riêng, tìm/lọc theo tên/khu và xem trạng thái.

Mật khẩu riêng được lưu hash/salt, không phải bản rõ. Mật khẩu tạm bàn giao có
bản mã được kiểm quyền; không ghi vào notification/ticket/log/RAG.

## 3. Đặt tên và mật khẩu lần đầu

- Cư dân mới đăng nhập bằng thông tin BQL cấp. Popup bắt buộc yêu cầu tên đăng
  nhập mới khác tên cấp, mật khẩu riêng và nhập lại; chưa được dùng nghiệp vụ
  cho tới khi thiết lập thành công.
- `POST /api/v1/auth/password/first-login` xác định hồ sơ từ token. Tên mới và
  hash cập nhật cùng transaction; mật khẩu riêng 8–256 ký tự, khác mật khẩu tạm.
- ID cư dân, căn hộ, tư cách và lịch sử không đổi. Tên gốc là định danh nội bộ,
  không được tái cấp cho người khác. Tên chỉ tự đổi trong bước thiết lập đầu.
- Thành công làm token cũ hết hiệu lực, xóa bản mật khẩu bàn giao/challenge liên
  quan. BQL chỉ thấy tên và trạng thái **Cư dân đã đổi mật khẩu**.
- Hai tài khoản cấu hình sẵn không bị tự sửa. Tài khoản cũ chỉ có hash không
  được tự reset hoặc suy ngược mật khẩu.
- Form/hộp xác nhận/xem mật khẩu phải chờ người dùng đóng; không tự biến mất
  theo thời gian cảnh báo 1,5 giây.

## 4. Tài khoản phụ thuộc và xem bàn giao

Chủ sở hữu đăng ký người nhà/người thuê đã được BQL duyệt cư trú và chưa có
tài khoản. BQL xem ticket → **Cấp tài khoản ngẫu nhiên** → thông tin chỉ đọc →
**Xác nhận duyệt và cấp tài khoản**. Server tạo đúng người/căn, liên kết ticket
và chỉ hoàn tất sau khi tạo thành công; retry không tạo thêm.

Đọc bàn giao từ ticket/thông báo chỉ cho chủ sở hữu gửi yêu cầu và BQL đúng
khu. BQL cũng có đường xem/sao chép theo tài khoản trong quản lý tài khoản.
Danh sách chỉ có cờ khả dụng, không tải sẵn mật khẩu.

Sau khi cư dân đặt mật khẩu riêng, mọi đường đọc ngừng trả mật khẩu tạm.
Tài khoản cũ không có bản mã hiện **Không còn mật khẩu bàn giao**; cần thì đi
quy trình cấp lại, không tự đổi chỉ để có mật khẩu cho BQL xem.

Chi tiết [luồng phụ thuộc](../docs/nghiep-vu/03-quy-trinh-nghiep-vu.md#4-người-cư-trú-và-tài-khoản-phụ-thuộc).

## 5. Đổi mật khẩu và hỗ trợ khi quên

- Cư dân đổi mật khẩu trong popup riêng, có mật khẩu hiện tại; không trộn với
  màn hình BQL quản lý danh sách tài khoản.
- Màn hình đăng nhập có hỗ trợ quên mật khẩu. Trợ lý tiếp nhận thông tin/yêu
  cầu hỗ trợ, không xem giấy tờ rồi tự quyết định người yêu cầu có quyền.
- Yêu cầu chuyển BQL đúng phạm vi; BQL đối chiếu hồ sơ trước khi cấp lại hoặc
  từ chối. Không đưa giấy tờ, tài khoản hay mật khẩu vào câu trả lời model/log.
- BQL xem tài khoản đúng khu → đặt lại/cấp mật khẩu tạm → xác nhận → bàn giao.
  Cư dân dùng mật khẩu tạm và đặt mật khẩu riêng mới, giữ tên đã chọn; không
  mở lại quyền đổi tên lần hai chỉ vì cấp lại mật khẩu.
- API email có trong mã nguồn nhưng chỉ hoạt động khi cấu hình SMTP và xác
  minh email đầy đủ. Không yêu cầu cư dân nhập email trong xác nhận cư trú
  hoặc nói OTP đang hoạt động nếu cấu hình chưa bật.

## 6. Danh mục khu và xác nhận cư trú

- Danh mục nguồn ở `scripts/residential_sites.json`. Nhập bằng
  `python -m scripts.import_residential_sites` trong môi trường đúng; không cần
  Reset/seed cư dân để cập nhật danh mục.
- Bộ căn mẫu dùng tòa A/B/C/D, 20 tầng, 10 phòng/tầng. Quyền BQL theo cấu hình
  và membership, không tự có vì tên khu xuất hiện trong danh mục.
- Text người dùng nhập không được tự thêm vào gợi ý khu/tòa/căn.
- Mọi cư dân xem và xác nhận thông tin BQL cấp, không tự đổi họ tên/tư cách/căn.
  Chưa xác nhận thì không dùng các nghiệp vụ; sai dữ liệu phải báo BQL.
- Xác nhận không tạo ticket chờ BQL duyệt lại. Household hiển thị chung theo
  khu/tòa/căn đã xác nhận, không nối chéo khu vì cùng số phòng.

## Reset trạng thái để test demo

> **Không dùng Reset để thử tài liệu hoặc chuẩn bị demo trên DB đang dùng.**
> Chỉ thử chức năng phá hủy dữ liệu trên PostgreSQL QA riêng đã được cho phép.

Nút Reset màu đỏ ở góc trái cuối trang, ngoài các tính năng; chỉ BQL đã đăng
nhập có capability mới thấy. Cần bật cấu hình, nhập đúng mã và xác nhận.
Endpoint thực hiện: `POST /api/v1/management/reset`.
Hai endpoint công khai cũ `/auth/reset` và `/demo/reset` trả `410`.

| Giữ lại | Xóa/đặt lại |
|---|---|
| Tài khoản cấu hình sẵn `user/admin` và secret cấu hình không đổi | Ticket, lịch sử xử lý và dữ liệu nghiệp vụ demo phát sinh |
| 10 tài khoản mẫu, kể cả đã đổi tên được nhận diện bằng creation key | Đưa tài khoản mẫu về `demo001`–`demo010`, mật khẩu tạm ban đầu và bước thiết lập lần đầu |
| Tài khoản được cấu hình giữ thêm rõ ràng | Tài khoản tạo thêm ngoài danh sách giữ, dữ liệu người/xe/dịch vụ phát sinh |
| Danh mục khu/căn, nguồn tri thức và cấu hình riêng | Xác nhận cư trú, xác nhận nội quy, tiến độ và context/hội thoại theo quy tắc Reset |
| Audit an ninh và log do cơ chế riêng quản lý | Trạng thái ẩn/đã đọc và dữ liệu phiên giao dịch liên quan |

Mật khẩu mẫu ban đầu xem [README](../README.md). `vuongtq` không được giữ mặc
định nếu không nằm trong cấu hình giữ thêm. Reset không phải backup hoặc cách
khôi phục mật khẩu riêng. Khởi động/seed thông thường không được tự reset.

Hủy, sai mã, hết phiên hoặc lỗi mạng không được coi là Reset thành công.
Backend có giới hạn thử mã/thời gian, transaction và generation chặn request
cũ ghi lại dữ liệu. Các tab khác có thể cần tải lại sau Reset.
