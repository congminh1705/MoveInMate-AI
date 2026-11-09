# Đưa MoveInMate lên AWS, bao gồm PostgreSQL

Ngày đối chiếu tài liệu AWS: **09/10/2026**. Đây là hướng dẫn triển khai, không phải
xác nhận đã tạo máy chủ hoặc đã kiểm thử tải trên AWS. Làm theo các bước tạo tài
nguyên sẽ tiêu credit/tiền trong tài khoản của bạn.

**Thông tin bạn đã xác nhận:** Free plan có 100 USD credit, chưa có tên miền,
dùng trải nghiệm AWS mới và dự án tại **Sydney (`ap-southeast-2`)**.
Lộ trình phù hợp: EC2 `t3.small` + DB Docker + subdomain miễn phí + HTTPS.
Lần triển khai thực tế dùng `sslip.io` với Elastic IP; không cần đăng ký DuckDNS.
Thông tin máy chủ, nhật ký triển khai và nghiệm thu được giữ riêng ngoài Git.
Không cần mua domain hoặc nâng cấp Paid plan để làm theo lộ trình này.

### Địa chỉ công khai — cập nhật 16/10/2026

Địa chỉ chính: <https://moveinmate.example.com/>.
`sslip.io` là DNS miễn phí của bên thứ ba, không phải tên miền riêng của nhóm.
Tên `c4.app.t047.moveinmateai` là phần đầu của địa chỉ đầy đủ này.

Hai địa chỉ cũ `moveinmate.example.com` và
`moveinmate.example.com` chuyển hướng vĩnh viễn bằng HTTP 308
đến HTTPS của địa chỉ chính, giữ nguyên đường dẫn, tham số và phương thức HTTP.
Nginx trên EC2 xử lý chuyển hướng; không chuyển hướng `localhost:8000`.
HTTPS và chứng chỉ tự gia hạn được giữ cho cả ba địa chỉ để link cũ không
báo lỗi chứng chỉ trước khi chuyển hướng. Đường dẫn ACME vẫn được phục vụ
trên HTTP cho việc gia hạn; không thay chúng bằng chuyển hướng toàn bộ server.

Đổi địa chỉ không di chuyển hoặc reset PostgreSQL, không thay tài khoản cư dân/BQL.
Do đổi origin trình duyệt, người dùng cần đăng nhập lại ở địa chỉ mới.
Không chép đè Nginx mẫu trong repo lên cấu hình HTTPS đang vận hành.

### Tự cập nhật từ máy Windows

`deploy/aws/configure_windows_relay.ps1 -Action Enable` bật bộ theo dõi `main`
trong phiên đăng nhập Windows hiện tại và tạo shortcut khởi động cùng phiên đăng
nhập sau. Bộ theo dõi kiểm tra GitHub mỗi 15 giây, không phải webhook tức thời;
thời gian build, kiểm thử và triển khai được tính riêng. Máy Windows cần bật,
có mạng và quyền đọc repo từ Git Credential Manager.

Security Group chỉ cho phép SSH từ từng IP máy triển khai bằng CIDR `/32`;
có thể giữ nhiều IP đã được phép, không mở cổng 22 cho toàn Internet. Nếu đổi
sang mạng chưa được phép, phải cập nhật rule SSH bằng phiên AWS hợp lệ.
Lỗi kết nối SSH tạm thời được thử lại sau 30, 60, 120, 240 giây, sau đó tối đa
mỗi 300 giây. Lỗi xác thực, host key, build hoặc kiểm thử không tự chạy lại liên
tục; giữ bản web đang hoạt động và chờ sửa lỗi hoặc yêu cầu thử lại.

Ứng dụng chỉ được thay sau khi kiểm thử đạt, backup DB được kiểm tra và migration
thành công. Nếu backend mới không healthy thì khôi phục image trước, không tự
reset dữ liệu hoặc hạ schema. Tự cập nhật hoàn toàn trên AWS cần deploy key chỉ
đọc được quản trị viên GitHub cấp quyền; bật relay Windows không tự cấp quyền đó.

Mọi tài nguyên theo vùng, gồm EC2, EBS, VPC và bucket backup, phải ở
`ap-southeast-2`. Không chuyển sang Singapore theo ví dụ cũ. Agent Toolkit dùng
endpoint dịch vụ `us-east-1` để thiết lập công cụ; đây không phải vùng triển khai
web hoặc PostgreSQL của dự án.

## 1. Phương án nên dùng với credit 100 USD

**Một EC2 Ubuntu chạy Nginx, backend và PostgreSQL bằng Docker.**

```text
Cư dân / BQL trên điện thoại, máy tính
                  |
           HTTPS, tên miền
                  |
      EC2 Ubuntu tại Sydney
      ├── Nginx + chứng chỉ TLS
      │        |
      │   127.0.0.1:8000
      ├── Docker: FastAPI + giao diện web + agent
      │        ├── Docker: PostgreSQL 17, không mở cổng ra Internet
      │        ├── Volume Chroma/runtime
      │        └── HTTPS tới nhà cung cấp LLM
      └── EBS gp3: hệ điều hành + Docker volumes
                  |
           Backup riêng ngoài EC2
           (máy cá nhân hoặc S3 private)
```

Ứng dụng hiện phục vụ luôn HTML/CSS/JavaScript từ FastAPI; không cần thêm Vercel,
Supabase hoặc một server frontend. Model chạy qua API, **không cần GPU**.

| Thành phần | Lựa chọn khởi đầu |
|---|---|
| Region | Asia Pacific (Sydney), `ap-southeast-2` |
| EC2 | `t3.small`, 2 vCPU, 2 GiB RAM, kiến trúc x86_64 |
| Hệ điều hành | Ubuntu Server 24.04 LTS, AMI chính thức Canonical, không chọn bản Marketplace trả phí |
| CPU credits | Standard để tránh phí surplus của Unlimited; hết CPU credits thì CPU bị giới hạn |
| Ổ đĩa | 30 GiB gp3, mã hóa bằng khóa AWS mặc định, IOPS/throughput mặc định |
| Swap | 2 GiB để giảm nguy cơ hết RAM khi build; không thay thế RAM thật |
| Database | PostgreSQL 17 trong Docker, volume riêng |
| Web | Nginx ở cổng 80/443; backend chỉ bind loopback 8000 |
| HTTPS | Tên miền/subdomain của bạn + Let's Encrypt |

Đây là cấu hình cho **MVP/pilot nhóm người dùng nhỏ**, không có dự phòng máy chủ
hay cam kết uptime. Quan sát idle ở máy local trước đó: backend khoảng 282 MiB,
PostgreSQL khoảng 102 MiB; không dùng các số này để cam kết số người dùng đồng
thời. Upload, xử lý PDF, tạo tài khoản và nhiều phiên chat có thể tăng RAM/CPU rõ rệt.

### Hiểu đúng “free 100 đô”

- Với tài khoản mới từ 15/07/2025, AWS cấp 100 USD credit ban đầu và có hoạt động
  giúp nhận thêm tối đa 100 USD; không mặc định bạn đã có đủ 200 USD.
- **Free plan:** kết thúc sau 6 tháng hoặc hết credit, tùy điều kiện đến trước;
  không bị tính tiền khi vẫn ở Free plan, nhưng tài khoản đóng và mất quyền truy cập
  khi hết hạn. Sao lưu ra ngoài trước đó; đừng dựa vào thời gian AWS lưu giữ dữ liệu.
- **Paid plan có credit:** vẫn có thể phát sinh tiền thật nếu vượt credit hoặc dùng
  dịch vụ không được credit chi trả. Chỉ nâng cấp khi chủ động chấp nhận thanh toán.
- Đây không phải một máy chủ miễn phí vĩnh viễn, cũng không mặc định là chương trình
  cũ “750 giờ mỗi tháng trong 12 tháng”.

Nguồn: [AWS account plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html),
[EC2 Free Tier](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html).

### Giá nền đã đối chiếu tại Sydney

Bảng dưới tra qua AWS Price List API ngày 09/10/2026, `regionCode=ap-southeast-2`,
Linux On-Demand, Shared tenancy. Tổng được tính bằng script Decimal với 730 giờ.

| Khoản | Giá và chi phí nền mỗi tháng tại Sydney |
|---|---:|
| EC2 `t3.small` Linux On-Demand | 0,0264 USD/giờ; 19,272 USD/730 giờ |
| EBS gp3 30 GiB | 0,096 USD/GiB-tháng; 2,88 USD |
| Một public IPv4 | 0,005 USD/giờ; 3,65 USD/730 giờ |
| Tổng hạ tầng nền | **25,802 USD, làm tròn 25,80 USD/tháng** |
| Chưa gồm | API model bên ngoài AWS, lưu lượng Internet tính phí, backup bổ sung và thuế |

Không cam kết thời gian chạy bằng 100 USD: chi phí biến động và Free plan có hạn.
Kiểm tra giá
trên [AWS Pricing Calculator](https://calculator.aws/) và màn hình xác nhận của
Console trước khi tạo; chưa chốt báo giá riêng cho tài khoản của bạn.
Public IPv4 có giá công bố 0,005 USD/giờ, kể cả Elastic IP.

**Chưa tính:** domain, thuế áp dụng, tải Internet lớn, CPU surplus nếu bật Unlimited,
dịch vụ phát sinh, phí LLM/STT/TTS. API model/relay đang cấu hình trong dự án là
dịch vụ bên ngoài; AWS credit không thanh toán hóa đơn của nhà cung cấp đó.

Tránh tạo NAT Gateway, ALB, EKS, Multi-AZ hoặc máy GPU cho cấu hình khởi đầu này.
`t3.medium` không nằm trong danh sách EC2 Free-plan eligible được AWS công bố ở
thời điểm đối chiếu; không tự chuyển sang Paid plan chỉ để chọn nó. Nếu Console
không cho tạo cấu hình đã chọn, kiểm tra plan/region/quota trước.

Nguồn giá: [EC2](https://aws.amazon.com/ec2/pricing/on-demand/),
[EBS](https://aws.amazon.com/ebs/pricing/), [IPv4](https://aws.amazon.com/vpc/pricing/).

## 2. Chuẩn bị và phân biệt nơi gõ lệnh

Cần có tài khoản AWS được phép dùng EC2/EBS, Docker Desktop đang chạy ở máy local,
SSH/SCP trên Windows và khóa API model. Nếu chưa có domain, đăng ký subdomain miễn
phí ở bước 11; không phải mua tên miền trước khi bắt đầu.

- **Windows:** PowerShell tại `D:\Python\P-047`.
- **EC2:** terminal Ubuntu sau khi kết nối SSH, không phải PowerShell local.
- **AWS Console:** trình duyệt đăng nhập tài khoản AWS.
- **DNS:** trang quản lý domain hiện tại; không bắt buộc chuyển sang Route 53.

Trong ví dụ, thay `EC2_PUBLIC_IP`, đường dẫn khóa `.pem`, email và
`moveinmate.example.com` bằng giá trị của bạn. Domain ví dụ không dùng được thật.

Nếu chưa muốn dùng dịch vụ DNS, kiểm tra riêng bằng SSH tunnel ở bước 12; chưa đưa
người dùng đăng nhập qua HTTP công khai. Domain trả phí không được mặc định được
credit thanh toán. Không gửi khóa `.pem`, API key, `.env.aws` cho người khác.

## 3. Kiểm tra plan và cảnh báo chi phí trước tiên

**AWS Console:**

1. Với trải nghiệm AWS mới, vào **AWS Settings**, chọn đúng dự án và kiểm tra
   plan, credit, hạn dùng cùng vùng trong **Overview → Additional Info → Region**.
   Nếu giao diện có liên kết Billing/Free Tier, đối chiếu số dư và hạn ở đó.
2. Bảo vệ tài khoản dùng để đăng nhập AWS và bật MFA theo tùy chọn được hỗ trợ;
   không tạo access key của root để đưa vào EC2.
3. Đăng nhập CLI bằng `aws login --region ap-southeast-2 --profile moveinmate-deploy`
   và chọn đúng dự án trên trình duyệt. Không cần tạo IAM user hay access key cho
   người vận hành. Không bật Organizations/Control Tower hoặc nâng Paid plan chỉ
   để vượt giới hạn của Free plan.
4. Nếu dự án hỗ trợ Budgets và bạn có quyền, tạo **Cost budget**, email cảnh báo ở
   50%, 80%, 100%, với ngưỡng đã tính lại theo giá Sydney. Theo dõi cả credit còn lại
   trên AWS Settings; không coi thiếu Budgets là lý do nâng Paid plan.
5. Để nhìn thấy mức tiêu tài nguyên dù hóa đơn được credit bù, chọn cách tính
   **không trừ credits/refunds** nếu giao diện Budgets cho phép tùy chỉnh này.
6. Đặt nhắc lịch kiểm tra hàng tuần và trước ngày hết hạn; số liệu billing có độ trễ.

Budget gửi cảnh báo, **không phải khóa cứng chi tiêu**. Paid plan không tự ngừng máy
ở ngưỡng cảnh báo. Không đăng ký gói AWS Support trả phí nếu không cần.

Nguồn cho trải nghiệm mới và giới hạn vùng:
[AWS starter rules](https://github.com/aws/agent-toolkit-for-aws/blob/main/rules/aws-starter-rules.md).

Nguồn: [Budgets best practices](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html),
[độ trễ và giới hạn cảnh báo](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html).

## 4. Tạo EC2

**AWS Console → giữ Sydney (`ap-southeast-2`) → EC2 → Instances → Launch instances:**

1. Name: `moveinmate-web`.
2. AMI: **Ubuntu Server 24.04 LTS**, x86_64, publisher Canonical.
3. Instance type: **t3.small**. Kiểm tra lựa chọn được account Free plan cho phép.
4. Key pair: **Create new key pair**, tên `moveinmate-aws`, RSA, định dạng `.pem`.
   Tải về và giữ riêng, ví dụ `C:\Users\<ban>\.ssh\moveinmate-aws.pem`.
5. Network: dùng default VPC và một **public subnet** có route tới Internet Gateway;
   bật **Auto-assign public IP**. Không chọn private subnet rồi tạo NAT Gateway.
6. Security group mới: `moveinmate-web-sg`, cấu hình inbound:

   | Type | Port | Source |
   |---|---:|---|
   | SSH | 22 | **My IP**, `/32`, không mở toàn Internet |
   | HTTP | 80 | `0.0.0.0/0` |
   | HTTPS | 443 | `0.0.0.0/0` |

   **Không thêm 5432 hay 8000.** Hướng dẫn này dùng IPv4, không cần rule IPv6.
   Outbound mặc định cho phép tải package và gọi API model; không cần rule inbound
   dành riêng cho chatbot.
7. Storage: **30 GiB gp3**, mã hóa, không tăng IOPS/throughput có phí.
8. Advanced details: bật IMDSv2/Metadata version **V2 only**; giữ detailed monitoring
   tắt nếu chưa cần; CPU credit specification **Standard**. Không cần IAM role nếu
   chưa dùng backup S3.
9. Số lượng: **1 instance**. Kiểm tra toàn bộ lựa chọn/giá trước **Launch instance**.
10. Đợi `Running` và status checks đạt. Ghi **Public IPv4 address**, instance ID,
    security group, EBS volume ID.

Không dùng Spot cho bản pilot cần DB bền vững và ít gián đoạn.

### Giữ IP ổn định

IP tự cấp có thể đổi sau stop/start. Để domain không phải cập nhật liên tục:
**EC2 → Elastic IPs → Allocate Elastic IP → Associate** với instance vừa tạo.
Nếu Console/plan không hỗ trợ, dùng IP tự cấp và nhớ cập nhật DNS khi IP đổi.
Một Elastic IP vẫn tính phí IPv4; không cấp dư, IP giữ sau khi stop vẫn có phí.

## 5. SSH từ Windows

**PowerShell Windows:**

```powershell
$AwsKey = "$HOME\.ssh\moveinmate-aws.pem"
$AwsIp = "EC2_PUBLIC_IP"
ssh -i $AwsKey "ubuntu@$AwsIp"
```

Kiểm tra IP/hostname ở Console và xác nhận host key lần đầu. Không dùng tùy chọn
tắt kiểm tra host key. Username của Ubuntu AMI là `ubuntu`, không phải `root`.

Nếu SSH báo private key có quyền quá rộng: trong **Properties → Security → Advanced**
của file `.pem`, tắt inheritance và giới hạn quyền đọc cho tài khoản Windows của
bạn. Không sửa bằng cách làm file public. Timeout thường do IP trong rule SSH
không khớp IP mạng hiện tại, instance chưa ready hoặc subnet không có Internet.

## 6. Cài Docker, Nginx và công cụ HTTPS

**Trong Ubuntu EC2:**

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git openssl nginx certbot python3-certbot-nginx
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker nginx
sudo usermod -aG docker ubuntu
exit
```

SSH lại từ Windows, rồi trong EC2 kiểm tra:

```bash
docker --version
docker compose version
docker info > /dev/null
```

Nếu `docker info` báo permission denied, thoát SSH và đăng nhập lại để nhận group.
Quyền trong group `docker` gần tương đương root; chỉ cấp cho tài khoản vận hành tin cậy.

Nguồn cài Docker: [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

### Swap cho máy 2 GiB RAM

```bash
free -h
swapon --show
```

**Chỉ khi chưa có swap**, thực hiện một lần:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
printf '/swapfile none swap sw 0 0\n' | sudo tee -a /etc/fstab
free -h
```

Không chạy lại nguyên đoạn tạo swap nếu `/swapfile` đã tồn tại/đang dùng.

## 7. Lấy code lên EC2

**EC2:**

```bash
cd /home/ubuntu
git clone --depth 1 --single-branch --branch main https://github.com/congminh1705/MoveInMate-AI.git moveinmate
cd /home/ubuntu/moveinmate
git rev-parse --short HEAD
mkdir -p deploy
```

Clone `vuong` không chỉnh sửa `main`, không push gì lên GitHub. Nếu repo private,
không đặt PAT trong URL hoặc lưu token trong shell history. Có thể tạo một SSH
deploy key riêng trên EC2, thêm **public key** vào GitHub repo → Settings → Deploy
keys với quyền **read-only**, rồi dùng URL SSH:
`git@github.com:congminh1705/MoveInMate-AI.git`.

**Quan trọng:** bộ cấu hình AWS của hướng dẫn này mới được thêm ở workspace local,
chưa mặc định có trên GitHub. Sau khi clone, chuyển thư mục này từ Windows:

```powershell
Set-Location D:\Python\P-047
scp -i $AwsKey -r .\deploy\aws "ubuntu@${AwsIp}:/home/ubuntu/moveinmate/deploy/"
```

Sau này nếu bộ cấu hình đã được commit/push thì clone có thể lấy trực tiếp; không
cần chép lại. Không đồng bộ nguyên workspace chứa `.env`, `.runtime`, DB hoặc khóa.
Dockerfile AWS chỉ copy mã runtime, không copy video/deliverables hoặc file `.env`.

## 8. Tạo cấu hình cloud riêng

**EC2, tại `/home/ubuntu/moveinmate`:**

Nếu vừa chép file từ Windows, chuẩn hóa xuống dòng của hai script:

```bash
sed -i 's/\r$//' deploy/aws/compose.sh deploy/aws/backup.sh
```

```bash
umask 077
cp deploy/aws/env.example .env.aws
for env_key in POSTGRES_PASSWORD AUTH_JWT_SECRET LOCAL_AUTH_ADMIN_PASSWORD LOCAL_AUTH_USER_PASSWORD; do
    env_value=$(openssl rand -hex 32)
    sed -i "s/^${env_key}=.*/${env_key}=${env_value}/" .env.aws
done
chmod 600 .env.aws
nano .env.aws
```

Chỉ dùng đoạn tạo file lần đầu; **không chạy lại để ghi đè cấu hình đang vận hành**.
Các mật khẩu được sinh là chuỗi hex riêng, tránh ký tự làm sai URL PostgreSQL và
Compose interpolation. Lưu mật khẩu đăng nhập trong password manager của nhóm.

Điền/sửa:

| Biến | Cách đặt |
|---|---|
| `ALLOWED_ORIGINS` | `https://<domain-cua-ban>`, không có dấu `/` cuối, không dùng `*` |
| `LLM_PROVIDER` | `custom` nếu tiếp tục dùng endpoint tương thích OpenAI hiện tại |
| `LLM_MODEL` | `gpt-5.6-luna`, đúng alias đã được provider của bạn cấp quyền |
| `LLM_BASE_URL`, `LLM_API_KEY` | Tự copy riêng từ cấu hình đang chạy; không gửi khóa vào chat/Git |
| `LOCAL_AUTH_ADMIN_USERNAME` | Tên đăng nhập BQL, có thể đổi `admin` thành tên riêng |
| `LOCAL_AUTH_ADMIN_PASSWORD` | Mật khẩu mạnh vừa sinh, không dùng `admin123` |
| `LOCAL_AUTH_USER_PASSWORD` | Mật khẩu mạnh vừa sinh, không dùng `user123` |
| `LOCAL_AUTH_SITE_ID` | Nếu chuyển DB hiện tại: giữ `sunrise-residence` để khớp R001 |
| `LOCAL_AUTH_ADMIN_SITE_IDS` | Chỉ các khu BQL được phép quản lý trong ứng dụng |
| `GEMINI_TTS_API_KEY`, `OMICX_API_KEY` | Chỉ điền nếu muốn bật giọng nói; có thể phát sinh phí riêng |

`gpt-5.6-luna` ở đây là alias provider đang cấu hình, không phải xác nhận danh tính
hay giá của một model chính thức OpenAI. Với `LLM_PROVIDER=custom`, đổi riêng
`OPENAI_MODEL` không làm model hiện tại đổi.

**Cấu hình bắt buộc đã được Compose AWS khóa:** `APP_ENV=production`, đăng nhập
local bắt buộc, tắt demo auth/reset, tắt hiện mật khẩu và nội quy mẫu. Không bật
LangSmith tracing mặc định để tránh chuyển dữ liệu cư dân sang dịch vụ khác.
Đây không sửa hoặc vô hiệu hóa các Git hook/log học tập của repo.

Đăng nhập cấu hình sẵn ở production yêu cầu password ít nhất 8 ký tự; `admin123`
và `user123` chỉ có 7, sẽ làm cấu hình auth không hợp lệ. Với tài khoản BQL tạo
trong DB, vẫn yêu cầu quy trình cấp mật khẩu mạnh 16+ ký tự; không mặc định rằng
code hiện đã cưỡng chế cùng tiêu chuẩn đó cho mọi tài khoản.

Kiểm tra cú pháp, không in toàn bộ cấu hình đã chứa mật khẩu:

```bash
bash deploy/aws/compose.sh config --quiet
```

Không dùng `source .env.aws` hoặc đăng output `docker inspect`/`compose config`
đầy đủ lên Internet. `.env.aws` đã được quy tắc Git/Docker hiện có loại khỏi bản lưu.

## 9. Build và chọn cách khởi tạo database

**EC2:**

```bash
cd /home/ubuntu/moveinmate
bash deploy/aws/compose.sh build backend
bash deploy/aws/compose.sh up -d --wait db
bash deploy/aws/compose.sh ps
```

Build đầu tiên có thể lâu vì Chroma và các thư viện Python. Nếu lỗi hết RAM,
kiểm tra swap/nhật ký; không giải quyết bằng cách mở thêm cổng mạng.

Chọn **một** đường đi dưới đây. Không chạy khởi tạo schema mới trước khi restore
full dump của đường B, vì dump đã chứa schema.

### A. Database mới cho người dùng thật — khuyến nghị

Không mang hồ sơ/ticket tổng hợp từ demo vào vận hành:

1. Trong `.env.aws`, đặt `LOCAL_AUTH_SITE_ID` đúng khu thí điểm được quản lý,
   ví dụ `vinhomes-ocean-park` nếu đó là phạm vi bạn được phép vận hành.
2. Chạy migration và nạp danh mục tên khu:

   ```bash
   bash deploy/aws/compose.sh run --rm --no-deps backend python -m scripts.migrate_database
   bash deploy/aws/compose.sh run --rm --no-deps backend python -m scripts.import_residential_sites
   ```

3. Sau khi bật HTTPS, BQL đăng nhập và tạo tài khoản cư dân với thông tin được
   kiểm tra; không chạy seed/reset để có người dùng giả.

Database mới chưa có R001, nên tài khoản `user` cấu hình sẵn không đăng nhập được;
đây là dự kiến, không phải DB mất dữ liệu. BQL vẫn đăng nhập và tạo cư dân mới.
Danh mục tên khu có nguồn không có nghĩa đã có danh sách căn hộ/nội quy được khu
đó xác minh. Chỉ trao quyền BQL và cấp tài khoản khi được chủ dữ liệu đồng ý.

### B. Chuyển bản sao DB local hiện có để chạy pilot

DB trên máy tính **không tự lên AWS chỉ vì clone repo**. Cần dump/restore.
Dữ liệu hiện có chứa hồ sơ/ticket tổng hợp; rà soát trước khi đưa cho người dùng
thật. Dump có dữ liệu cá nhân và hash tài khoản, không đưa vào Git/deliverables.

**Windows PowerShell, tại project:**

```powershell
docker compose up -d --wait db
New-Item -ItemType Directory -Force .runtime\aws-transfer | Out-Null
docker compose exec -T db sh -eu -c 'umask 077; pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl --file=/tmp/moveinmate-aws-transfer.dump'
docker compose cp db:/tmp/moveinmate-aws-transfer.dump .runtime/aws-transfer/moveinmate.dump
Get-FileHash .runtime\aws-transfer\moveinmate.dump -Algorithm SHA256
ssh -i $AwsKey "ubuntu@$AwsIp" "mkdir -p /home/ubuntu/moveinmate/.runtime/aws-transfer && chmod 700 /home/ubuntu/moveinmate/.runtime/aws-transfer"
scp -i $AwsKey .runtime\aws-transfer\moveinmate.dump "ubuntu@${AwsIp}:/home/ubuntu/moveinmate/.runtime/aws-transfer/"
docker compose exec -T db rm -f /tmp/moveinmate-aws-transfer.dump
```

Ở repo hiện tại, service là **`db`**, không phải `postgres`. Lệnh dump lấy đúng
`POSTGRES_DB` đang cấu hình local; kiểm tra bạn không trỏ nhầm DB test trước khi xuất.
Không dùng PowerShell `pg_dump > file.dump` với dữ liệu binary.
`pg_dump` nhất quán ở thời điểm chụp; nếu local tiếp tục có ghi, các ghi sau đó
không tự đồng bộ lên AWS. Khi cutover chính thức, ngừng thao tác ghi rồi chụp bản cuối.

**EC2:**

```bash
cd /home/ubuntu/moveinmate
chmod 600 .runtime/aws-transfer/moveinmate.dump
sha256sum .runtime/aws-transfer/moveinmate.dump
bash deploy/aws/compose.sh exec -T db sh -eu -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT count(*) FROM pg_tables WHERE schemaname = current_schema();"'
```

So hash với Windows. Lệnh SQL phải trả **0** trước khi restore vào DB mới.
Nếu không phải 0: dừng lại, xác định dữ liệu đã có; không dùng `--clean`, không xóa
volume để cố làm lệnh tiếp theo chạy được.

```bash
bash deploy/aws/compose.sh cp .runtime/aws-transfer/moveinmate.dump db:/tmp/moveinmate-transfer.dump
bash deploy/aws/compose.sh exec -T db sh -eu -c 'pg_restore --exit-on-error --single-transaction --no-owner --no-acl -U "$POSTGRES_USER" -d "$POSTGRES_DB" /tmp/moveinmate-transfer.dump'
bash deploy/aws/compose.sh exec -T db rm -f /tmp/moveinmate-transfer.dump
bash deploy/aws/compose.sh run --rm --no-deps backend python -m scripts.migrate_database
bash deploy/aws/compose.sh run --rm --no-deps backend python -m scripts.import_residential_sites
```

Migration hiện có tới `20261009_0006`; dùng `alembic current` ở bước 10 để đối chiếu.
Mật khẩu/JWT secret cloud phải khác local. Đổi password trong `.env.aws` chỉ đổi
tài khoản cấu hình sẵn, **không tự đổi các tài khoản đã có trong `local_credentials`**.
Nếu không kiểm soát được tài khoản/mật khẩu cũ, chọn đường A trước khi mở công khai.

## 10. Chạy backend và kiểm tra riêng trên EC2

```bash
cd /home/ubuntu/moveinmate
bash deploy/aws/compose.sh up -d --wait backend
bash deploy/aws/compose.sh ps
bash deploy/aws/compose.sh exec -T backend alembic current
curl --fail http://127.0.0.1:8000/api/v1/health
curl --fail http://127.0.0.1:8000/api/v1/auth/config
```

Kỳ vọng: cả hai service healthy, health `ready`, auth mode `required`, provider
`local`, `enabled=true`. Health ready chưa chứng minh model hoặc password hoạt động;
vẫn phải đăng nhập và gửi chat sau khi HTTPS sẵn sàng.

Chroma được khởi tạo lại từ knowledge chunks trong PostgreSQL khi backend bắt đầu;
đường B không cần copy nguyên Docker volume Chroma từ Windows. Volume runtime mới
giữ chỉ mục trên cloud. Không mặc định mọi memory/phiên hội thoại của agent đều bền
vững trong PostgreSQL; một phần trạng thái runtime hiện có thể mất khi restart.

## 11. Domain và HTTPS

### Bạn chưa có domain: dùng subdomain DuckDNS miễn phí

1. Mở [duckdns.org](https://www.duckdns.org/), đăng nhập bằng một phương thức được
   trang hỗ trợ. Tự thực hiện đăng nhập; không chia sẻ token tài khoản DuckDNS.
2. Chọn tên còn trống, ví dụ `moveinmate-nhom-ban`; sau khi thêm, địa chỉ sẽ dạng
   `moveinmate-nhom-ban.duckdns.org`. Tên ví dụ không được bảo đảm còn trống.
3. Ở ô IP của subdomain, nhập **Public IPv4/Elastic IP EC2**, bấm cập nhật. Địa chỉ
   tự điền lúc đăng ký có thể là IP mạng nhà bạn; phải đổi sang IP của EC2.
4. Trong PowerShell kiểm tra:

   ```powershell
   Resolve-DnsName moveinmate-nhom-ban.duckdns.org -Type A
   ```

5. Khi kết quả khớp EC2, dùng chính subdomain này thay mọi domain ví dụ bên dưới:
   `ALLOWED_ORIGINS`, hai vị trí trong Nginx và tham số `certbot -d`.
6. Nếu IP EC2 đổi sau stop/start, cập nhật lại DuckDNS. Dùng Elastic IP thì thường
   không cần script DDNS/token trên server. Không bật wildcard hoặc DNS challenge
   phức tạp khi HTTP challenge cho một subdomain đã đủ.

Subdomain miễn phí phù hợp pilot và truy cập từ điện thoại; không phải domain bạn
sở hữu độc lập, không có cam kết uptime của hệ thống này. Khi vận hành lâu dài,
có thể mua domain riêng và đổi DNS/chứng chỉ/origins. Nếu dịch vụ đăng ký/DNS gặp
vấn đề, dùng SSH tunnel tạm thời, không bỏ HTTPS để phát tài khoản.

Nguồn: [DuckDNS](https://www.duckdns.org/),
[cập nhật IP và chứng minh quyền kiểm soát DNS](https://www.duckdns.org/spec.jsp).

### DNS

Nếu dùng DuckDNS, bạn đã làm phần DNS ở trên, chuyển sang Nginx. Nếu dùng domain
riêng, ở nhà cung cấp domain tạo record **A**:

| Trường | Ví dụ |
|---|---|
| Name/Host | `app`, nếu muốn `app.tenmiencuaban.vn` |
| Type | `A` |
| Value | Public IPv4/Elastic IP của EC2 |
| TTL | 300 giây hoặc mặc định |

Không trỏ record tới IP private của EC2 hoặc `127.0.0.1`. Nếu đang dùng Cloudflare,
để **DNS only** trong lần cấp chứng chỉ đầu. Xóa/sửa record AAAA cũ nếu chưa có IPv6
đúng; DNS IPv6 sai có thể làm HTTPS/cấp chứng chỉ lỗi. Không cần tạo Route 53 zone
có phí nếu domain đã có dịch vụ DNS.

**Windows kiểm tra:**

```powershell
Resolve-DnsName app.tenmiencuaban.vn -Type A
```

### Nginx

**EC2:** sửa domain trong bản cấu hình **đã copy sang `/etc`**, không chỉnh code local:

```bash
sudo cp deploy/aws/nginx.conf /etc/nginx/sites-available/moveinmate
sudo nano /etc/nginx/sites-available/moveinmate
```

Thay **cả hai chỗ** `moveinmate.example.com`: dòng `server_name` và điều kiện `$host`.
Phải khớp `ALLOWED_ORIGINS` trong `.env.aws`. Trên máy EC2 mới chưa phục vụ web khác:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/moveinmate /etc/nginx/sites-enabled/moveinmate
sudo nginx -t
sudo systemctl reload nginx
```

Nếu symlink đã tồn tại, bỏ qua lệnh `ln -s`, không tạo cấu hình trùng. File mẫu nằm
trong `sites-enabled` nên các zone được đặt trong ngữ cảnh `http` hợp lệ của Ubuntu.

### Chứng chỉ HTTPS

Chỉ làm khi DNS đã trỏ đúng EC2, inbound 80/443 đã mở:

```bash
sudo certbot --nginx -d app.tenmiencuaban.vn --redirect
sudo nginx -t
sudo systemctl reload nginx
sudo certbot renew --dry-run
systemctl list-timers --all | grep certbot
```

Nhập email nhận cảnh báo và chấp nhận điều khoản khi Certbot hỏi. Kiểm tra timer
gia hạn được bật; không chỉ cấp chứng chỉ một lần rồi quên.
Mở `https://app.tenmiencuaban.vn`, không dùng HTTP để thử mật khẩu trước bước này.
Mẫu Nginx ban đầu là HTTP để Certbot cấu hình; chưa được dùng bàn giao tài khoản.

Nginx tắt buffering cho chat streaming, cho phép request tối đa 28 MiB để đủ
multipart/voice; backend vẫn kiểm soát loại/kích thước tệp riêng. Nó giới hạn login
10 request/phút/IP, chat/voice 20 request/phút/IP và 8 kết nối đang xử lý/IP, có burst.
Nhiều người dùng cùng Wi-Fi có thể chạm cùng giới hạn; điều chỉnh sau khi đo thực tế.
Đây **không phải** giới hạn chi phí LLM hay bảo vệ DDoS hoàn chỉnh. Đặt thêm quota/
hard spending cap tại nhà cung cấp model nếu có, không chỉ bật cảnh báo email.

Nginx ghi đè forwarded headers. Uvicorn chỉ được tin proxy trong mô hình này vì
cổng host 8000 chỉ bind loopback và Docker network chỉ có các container tin cậy;
không đổi thành `0.0.0.0:8000` hoặc mở 8000 trên security group.
Nếu thêm CDN/proxy khác, cần cấu hình trusted real-IP đúng trước khi dùng rate limit.

Nguồn: [Nginx proxy](https://nginx.org/en/docs/http/ngx_http_proxy_module.html),
[Nginx rate limit](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html),
[Certbot Ubuntu](https://manpages.ubuntu.com/manpages/noble/man1/certbot.1.html).

## 12. Nếu chưa có domain

Nếu chưa đăng ký subdomain ở bước 11 hoặc DNS chưa sẵn sàng, chỉ thử riêng qua
SSH tunnel; không cần mở security group port 8000.

**PowerShell Windows, giữ cửa sổ này đang chạy:**

```powershell
ssh -i $AwsKey -L 8002:127.0.0.1:8000 "ubuntu@$AwsIp"
```

Truy cập `http://localhost:8002` trên chính máy Windows. Tunnel mã hóa đoạn qua
Internet; không phải link công khai cho cư dân. Thêm tạm `http://localhost:8002`
vào `ALLOWED_ORIGINS` nếu cần thử qua origin này rồi recreate backend. Khi có
HTTPS thật, bỏ origin thử. Không phải cấp chứng chỉ miễn phí bằng cách nhập tùy
ý domain của người khác.

## 13. Kiểm tra trước khi gửi link cho người dùng

Ghi kết quả thực tế, không chỉ đánh dấu dự kiến:

| Kiểm tra | Kết quả cần có |
|---|---|
| Mở từ điện thoại dùng 4G | Domain HTTPS hợp lệ, không phụ thuộc máy tính/Docker Desktop local |
| Không đăng nhập | Không đọc được hồ sơ, danh sách yêu cầu, dữ liệu BQL |
| BQL đăng nhập | Dùng mật khẩu cloud mới; không hiện tài khoản/mật khẩu trên trang |
| BQL tạo cư dân | Đúng khu/tòa/căn hộ → xem lại → xác nhận → tạo; giao mật khẩu riêng |
| Cư dân mới đăng nhập | Chỉ xem hồ sơ/phạm vi được cấp, không vào danh sách BQL |
| Chat | Có câu trả lời/nguồn hoặc từ chối đúng phạm vi, stream không bị dồn đến cuối |
| Gửi yêu cầu | Cư dân xác nhận → có mã ticket → BQL thấy → BQL xử lý → cư dân xem tiến độ |
| Đọc nội quy | Xác nhận được lưu; không đánh dấu thay người dùng |
| Persistence | Tạo một dữ liệu kiểm tra được phép, restart backend rồi đọc lại hồ sơ/ticket |
| Cổng mạng | Từ ngoài không truy cập được 5432/8000; chỉ 80/443 và SSH từ IP được cấp |
| Backup/restore | Khôi phục thành công sang DB riêng và đối chiếu; không chỉ nhìn thấy file dump |

Chỉ restart backend ở cửa sổ bảo trì; phiên streaming đang chạy sẽ ngắt:

```bash
bash deploy/aws/compose.sh restart backend
bash deploy/aws/compose.sh ps
```

Trước dùng với cư dân thật, chốt quyền xử lý dữ liệu, nội quy/biểu mẫu được BQL xác
minh, người có quyền duyệt, quota model, chính sách ảnh giấy tờ và thời gian lưu/xóa.
Đây không phải lời bảo đảm hệ thống đã đủ tuân thủ pháp lý hoặc đủ tải production.

## 14. DB nằm ở đâu, có còn cần mở máy tính không?

- PostgreSQL nằm trong container `db` **trên EC2**, không phải Docker Desktop local.
- Dữ liệu vật lý ở Docker named volume `moveinmate-aws_postgres_data`, thường dưới
  Docker data root trên EBS. Xem đường dẫn chính xác bằng:

  ```bash
  docker volume inspect moveinmate-aws_postgres_data --format '{{ .Mountpoint }}'
  ```

- Không sửa/copy thủ công các file trong PGDATA khi PostgreSQL đang chạy; dùng dump.
- Tắt máy tính cá nhân hoặc Docker Desktop local: web cloud vẫn chạy nếu EC2 còn chạy.
- Restart/recreate container không tự xóa named volume. **`down -v` xóa volume**;
  tuyệt đối không dùng cho dịch vụ đang có dữ liệu cần giữ.
- EC2 bị terminate có thể làm mất EBS nếu bật Delete on termination. Volume không
  thay cho backup; giữ bản khôi phục ở ngoài EC2.
- Cloud và local là hai bản DB độc lập sau restore, không tự đồng bộ hai chiều.

Để xem bảng/SQL trên cloud:

```bash
bash deploy/aws/compose.sh exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Trong `psql`: `\dt` xem bảng, `SELECT version_num FROM alembic_version;` xem migration,
`SELECT count(*) FROM residents;` đếm cư dân, `\q` thoát. Không cần mở 5432 công khai.

## 15. Backup thường xuyên và giữ một bản ngoài EC2

**EC2:**

```bash
cd /home/ubuntu/moveinmate
bash deploy/aws/backup.sh
```

Script dùng `pg_dump` custom format cho toàn DB, lưu `.runtime/aws-backups/`, quyền
600, kèm SHA-256; không chứa DB password trong tên file. Kiểm tra `pg_restore --list`
chỉ xác nhận đọc được archive, **chưa phải kiểm thử restore**. Bản backup trên cùng
EBS sẽ mất cùng máy/ổ, nên phải tiếp tục chuyển ra ngoài.

**Windows kéo một bản về, thay tên file đúng output ở EC2:**

```powershell
New-Item -ItemType Directory -Force .runtime\aws-downloads | Out-Null
scp -i $AwsKey "ubuntu@${AwsIp}:/home/ubuntu/moveinmate/.runtime/aws-backups/moveinmate-TEN-FILE.dump*" .runtime/aws-downloads/
```

Giữ thêm bản trên ổ/thiết bị riêng có mã hóa, kiểm tra checksum và có lịch backup.
Không upload dump vào repository public. Có thể lập lịch backup local trên EC2
bằng `crontab -e` của user `ubuntu`, sau khi lệnh chạy tay thành công:

```cron
0 19 * * * /bin/bash /home/ubuntu/moveinmate/deploy/aws/backup.sh >> /home/ubuntu/moveinmate/.runtime/aws-backup.log 2>&1
```

EC2 Ubuntu thường dùng UTC: 19:00 UTC là 02:00 Việt Nam hôm sau. Thư mục `.runtime`
được lần backup tay tạo trước cron. Dòng cron này **chỉ tạo backup trên EC2**, chưa
chuyển ra ngoài; theo dõi lỗi và không để file tăng vô hạn làm đầy 30 GiB.
Đề xuất giữ 7 bản ngày và 4 bản tuần ở nơi ngoài EC2; xác nhận bản ngoài đã đọc được
trước khi dọn bản cũ. Cron không bảo đảm RPO 0 hay không mất một ngày dữ liệu.

### Tùy chọn S3 cho backup tự động ngoài máy

1. Tạo bucket cùng region Sydney (`ap-southeast-2`), tên toàn cục duy nhất, **Block all public access**
   bật, Object Ownership bucket-owner-enforced, mã hóa SSE-S3 mặc định.
2. Tạo IAM role cho EC2, chỉ cho `s3:PutObject` vào prefix backup của bucket đó; gắn
   role vào EC2. Không cấp `AmazonS3FullAccess`, không lưu AWS root/access key vào env.
3. Cài AWS CLI v2 theo [hướng dẫn chính thức](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
   CLI dùng instance role, không cần chạy `aws configure` với khóa lâu dài.
4. Sau khi có file backup, upload cụ thể:

   ```bash
   aws s3 cp .runtime/aws-backups/TEN-FILE.dump s3://TEN-BUCKET/moveinmate-backups/TEN-FILE.dump --sse AES256
   aws s3 cp .runtime/aws-backups/TEN-FILE.dump.sha256 s3://TEN-BUCKET/moveinmate-backups/TEN-FILE.dump.sha256 --sse AES256
   ```

5. Kiểm tra upload thành công trước khi bổ sung vào tác vụ hàng ngày. Quyền đọc/
   restore cấp riêng cho người vận hành; không cần cho app quyền xóa backup.
6. Thiết lập lifecycle/retention phù hợp và tính phí request/storage; nếu bật
   versioning, cần tính cả phiên bản cũ. Không chuyển Glacier nếu cần restore nhanh.

Backup dữ liệu nhạy cảm cần giới hạn người đọc và mã hóa. Không xóa bucket/role hoặc
backup cuối cùng khi dừng máy nếu vẫn còn nghĩa vụ giữ dữ liệu.

### Thử restore mà không chạm DB đang phục vụ

Dùng PostgreSQL 17 trong container/instance **riêng**, DB mới trống, không mở cổng
Internet. Khôi phục archive theo đường B, trỏ một môi trường kiểm tra riêng tới
DB đó và đối chiếu số dòng/hồ sơ/ticket/biên nhận. Chỉ ghi “đã kiểm thử restore”
sau khi thực sự làm xong. Không chạy script test hoặc `pg_restore --clean` vào
`moveinmate_prod` để kiểm tra backup.

## 16. Vận hành, cập nhật và xử lý lỗi

**EC2, tại thư mục project:**

```bash
bash deploy/aws/compose.sh ps
bash deploy/aws/compose.sh logs --tail=100 backend
bash deploy/aws/compose.sh logs --tail=100 db
free -h
df -h
docker stats --no-stream
sudo journalctl -u nginx --since '15 minutes ago'
```

Logs có thể chứa thông tin định danh; không đăng nguyên log công khai.

| Hiện tượng | Kiểm tra trước |
|---|---|
| `service "postgres" is not running` | Service repo là `db`; ở cloud dùng wrapper `bash deploy/aws/compose.sh ...` |
| `no configuration file` / file env thiếu | Đang ở `/home/ubuntu/moveinmate` chưa, đã chuyển `deploy/aws` và tạo `.env.aws` chưa |
| Nginx 502 | Backend healthy chưa; `curl 127.0.0.1:8000/api/v1/health`; kiểm tra log/migration |
| `authentication_not_configured` | Secret đủ 32 byte, cả hai password cấu hình sẵn đủ dài, username khác nhau |
| User cấu hình sẵn không login | Đã có hồ sơ đúng resident/site chưa; fresh DB dùng tài khoản BQL tạo, không tự seed |
| Chat lỗi nhưng login được | API key/base URL/model/quota của provider, kết nối HTTPS outbound |
| 429 | Rate limit Nginx hoặc quota provider; xem nguồn lỗi trước khi tăng giới hạn |
| Chat hiện nguyên đoạn cuối | Proxy/CDN có buffering; giữ cấu hình streaming và timeout |
| Upload 413 | Giới hạn Nginx hoặc backend; không bỏ giới hạn để xử lý |
| Certbot thất bại | DNS A/AAAA, cổng 80, đúng domain, record proxy và server_name |
| Máy chậm/exit 137 | RAM/swap/OOM, CPU credits, ổ đầy; không cam kết t3.small chịu mọi tải |
| Đổi password PostgreSQL trong env rồi mất kết nối | Volume đã có DB: POSTGRES_PASSWORD không tự đổi password trong DB; cần kế hoạch ALTER ROLE và cập nhật backend đồng bộ |

### Cập nhật code về sau

Chỉ thực hiện lúc bảo trì và khi thay đổi đã được kiểm tra:

```bash
cd /home/ubuntu/moveinmate
bash deploy/aws/backup.sh
git status --short
git pull --ff-only origin vuong
bash deploy/aws/compose.sh build backend
bash deploy/aws/compose.sh stop backend
bash deploy/aws/compose.sh run --rm --no-deps backend python -m scripts.migrate_database
bash deploy/aws/compose.sh up -d --wait backend
```

Backup phải được sao chép ra ngoài trước cập nhật quan trọng. Nếu `git pull` báo
conflict hoặc file local trùng, dừng đối chiếu; không `reset --hard` để xóa cấu hình.
`.env.aws` không nằm trong Git. File AWS copy thủ công ở bước 7 cần được quản lý
nhất quán khi về sau repo bắt đầu track chúng. Không copy lại Nginx HTTP mẫu đè lên
file `/etc/nginx` đã được Certbot cấu hình HTTPS. Migration có thể không đảo ngược
được bằng cách chạy image cũ; giữ backup và kế hoạch rollback dữ liệu trước khi đổi.

## 17. Khi nào nâng lên RDS / máy lớn hơn?

Nếu muốn AWS quản lý backup/maintenance DB thay vì tự vận hành PostgreSQL Docker,
chọn **EC2 backend + Amazon RDS PostgreSQL**. Không bắt buộc dùng RDS chỉ để có DB
trên AWS. RDS và EC2 đều tiêu credit; dự trù lại bằng Calculator, không cộng vào
phương án 27–35 USD như thể miễn phí.

Khởi đầu RDS: PostgreSQL 17 nếu available, Single-AZ `db.t4g.micro` hoặc
`db.t3.micro` được account cho phép, storage tối thiểu phù hợp, mã hóa, backup
retention, không bật Public access. Dùng DB subnet group trong cùng VPC, RDS security
group cho 5432 **từ security group EC2**, không từ `0.0.0.0/0`. Cấu hình DB riêng
theo least privilege, kết nối TLS với CA AWS và `sslmode=verify-full`; giữ endpoint
và mật khẩu ở server, không trong JavaScript.

**Bộ Compose kèm theo dùng DB Docker, chưa phải cấu hình RDS.** Khi đổi phải bỏ DB
container/dependency, thay DATABASE_URL và DB_HOST_OVERRIDE, mount CA đúng đường
dẫn, restore/migrate qua endpoint RDS, kiểm tra phiên bản/quyền extension. Không
chỉ thêm endpoint vào `.env.aws` vì Compose đang cố định host `db`.

Nguồn: [RDS Free Tier](https://aws.amazon.com/rds/free/),
[RDS SSL/TLS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Concepts.General.SSL.html).

Chỉ tăng RAM/CPU khi đo thấy cần. Với Paid plan có credit, máy 4 GiB có thể phù hợp
hơn nhưng credit hết nhanh hơn. Với Free plan, chỉ chọn instance được Console cho
phép và đối chiếu giá; nhãn eligible không có nghĩa máy mạnh được dùng vô hạn.
Muốn mở rộng nhiều backend phải giải quyết memory/checkpoint agent dùng chung,
chỉ mục và kết nối DB trước; không tăng `--workers` tùy ý.

## 18. Ngừng sử dụng mà không mất dữ liệu hoặc sót phí

1. Tạo backup mới, copy ra ngoài, kiểm tra checksum và khôi phục thử.
2. Thông báo người dùng và dừng tiếp nhận ghi trước khi chụp bản cuối.
3. Nếu tạm dừng, **stop EC2**: phí compute dừng, EBS và Elastic IP vẫn có thể tính phí.
4. Nếu xóa hẳn, kiểm tra Delete on termination của EBS; chỉ terminate khi đã có
   bản backup ngoài máy. Kiểm tra EBS/snapshot/Elastic IP còn sót ở đúng region.
5. Release Elastic IP không dùng, dọn tài nguyên không cần sau khi xác nhận backup;
   S3/snapshot còn giữ vẫn có phí. RDS nếu tạo thêm phải quản lý riêng; stop RDS
   không phải cách dừng miễn phí vĩnh viễn.
6. Rà Billing tất cả region, đặt lịch theo dõi cho tới khi không còn tài nguyên có phí.
7. Trước hết credit hoặc hết hạn Free plan, xuất dữ liệu chủ động. Không đợi tài
   khoản đóng rồi mới tìm cách lấy hồ sơ.

## 19. Bộ file đi kèm

| File | Vai trò |
|---|---|
| `deploy/aws/docker-compose.aws.yml` | Stack cloud riêng, không publish DB, backend chỉ loopback, log rotation |
| `deploy/aws/Dockerfile` | Image runtime không copy video/deliverables/secret local |
| `deploy/aws/env.example` | Mẫu cấu hình trống secret; copy thành `.env.aws` trên EC2 |
| `deploy/aws/compose.sh` | Chọn đúng Compose/env AWS, tránh thao tác nhầm stack local |
| `deploy/aws/nginx.conf` | Mẫu trước Certbot, proxy streaming và rate limits cơ bản |
| `deploy/aws/backup.sh` | Tạo dump/checksum; chưa tự chuyển S3 hoặc chứng nhận restore |

Các file này không tạo tài nguyên AWS, không đọc hoặc thay đổi `.env` local và
không push code. Chỉ khi bạn chạy bước tạo EC2 trên Console mới bắt đầu tiêu credit.

## 20. Kiểm tra bộ cấu hình trước khi bàn giao

Đã kiểm tra local bằng giá trị bí mật giả, không dùng tài khoản AWS:

- Compose parse thành công; không publish port DB, backend chỉ bind `127.0.0.1`;
  production auth/reset đúng cấu hình dự kiến. Bước này kiểm tra cấu trúc, không
  xác nhận bạn đã điền `.env.aws` thật hợp lệ.
- Hai script đạt kiểm tra cú pháp Bash.
- Dockerfile AWS build thành công; image import được app, kiểm tra cấu hình auth
  production hợp lệ với secret giả, không chứa `.env`, `.env.aws` hoặc deliverables.
- Nginx mẫu đạt `nginx -t` trong container kiểm tra; chưa phải kiểm tra chứng chỉ
  hoặc DNS thật của bạn.
- PostgreSQL 17 custom-format dump khôi phục thành công bằng transaction vào DB
  riêng dùng tmpfs, đối chiếu một dòng kiểm tra. Không dump/restore vào DB local
  đang dùng, không coi đây là kiểm thử khôi phục dữ liệu vận hành của bạn.

Các kiểm tra trên ghi nhận bước chuẩn bị local trước khi tạo tài nguyên. Tình trạng
triển khai AWS thực tế, HTTPS, sao lưu và nghiệm thu được quản lý riêng ngoài Git;
không dùng mục chuẩn bị này để suy ra chưa có máy chủ.
