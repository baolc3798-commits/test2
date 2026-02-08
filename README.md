# CEH v13 Quiz Application

Đây là ứng dụng web trắc nghiệm CEH v13 được xây dựng bằng Django (Python).

## Tính năng chính

*   **Quản lý người dùng:** Đăng ký, Đăng nhập (với thông tin mở rộng: SĐT, Đơn vị).
*   **Quản lý bài thi (Admin):**
    *   Thêm/Sửa/Xóa Module, Câu hỏi (Trắc nghiệm 1 chọn, nhiều chọn, Tự luận).
    *   Cấu hình bài thi: Thời gian làm bài, Chế độ hiển thị kết quả (Ngay lập tức/Sau khi nộp/Ẩn), Trộn câu hỏi.
*   **Làm bài thi (Học viên):**
    *   Giao diện làm bài trực quan.
    *   Đếm ngược thời gian.
    *   Lưu trạng thái làm bài.
    *   Xem kết quả chi tiết (nếu được phép).
*   **Dashboard:** Thống kê kết quả học tập.

## Yêu cầu hệ thống

*   Python 3.10+
*   Git
*   SQLite (mặc định) hoặc PostgreSQL/MySQL (tùy chọn).
*   Linux Server (Ubuntu/CentOS) cho môi trường production.

## Hướng dẫn cài đặt và chạy (Development)

### 1. Cài đặt Git và Python (Nếu chưa có)

Nếu bạn dùng Ubuntu/Debian:
```bash
sudo apt update
sudo apt install git python3 python3-pip python3-venv
```

Nếu bạn dùng Windows, hãy tải và cài đặt [Git Bash](https://git-scm.com/downloads) và [Python](https://www.python.org/downloads/).

### 2. Clone Repository

Mở terminal (hoặc Git Bash) và chạy lệnh:

```bash
git clone <repository_url>
cd ceh_quiz
```

*(Thay `<repository_url>` bằng link git của bạn)*

### 3. Tạo môi trường ảo (Virtual Environment)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
# python -m venv venv
# venv\Scripts\activate

# Windows (Git Bash)
# python -m venv venv
# source venv/Scripts/activate
```

### 4. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 5. Cấu hình môi trường

Copy file cấu hình mẫu thành file chính thức:

```bash
cp .env.example .env
```
*(Bạn có thể mở file `.env` để sửa `SECRET_KEY` hoặc `DEBUG` nếu cần)*

### 6. Cấu hình Database

Khởi tạo cơ sở dữ liệu:

```bash
python manage.py migrate
```

Tạo tài khoản Admin (Quản trị viên):

```bash
python manage.py createsuperuser
```
*(Làm theo hướng dẫn nhập username, email, password)*

### 7. Chạy Server

```bash
python manage.py runserver
```

Truy cập trình duyệt tại địa chỉ: `http://127.0.0.1:8000`

*   **Trang chủ:** `http://127.0.0.1:8000`
*   **Trang quản trị:** `http://127.0.0.1:8000/admin` (Đăng nhập bằng tài khoản superuser vừa tạo).

### 8. Truy cập từ bên ngoài (External Access)

Nếu bạn không thể truy cập từ máy khác (hoặc từ IP Public):

1.  **Cập nhật cấu hình `.env`:**
    Mở file `.env` và thêm `*` hoặc địa chỉ IP Public của server vào `ALLOWED_HOSTS`:
    ```ini
    ALLOWED_HOSTS=*
    # Hoặc: ALLOWED_HOSTS=127.0.0.1,localhost,your.server.ip
    ```

2.  **Chạy server với địa chỉ 0.0.0.0:**
    Thay vì chỉ chạy `python manage.py runserver`, hãy chạy:
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

3.  **Kiểm tra Firewall (Tường lửa):**
    *   Nếu dùng AWS/Google Cloud: Mở port 8000 trong Security Group/Firewall Rules.
    *   Nếu dùng VPS Linux (UFW):
        ```bash
        sudo ufw allow 8000
        ```

---

## Hướng dẫn sử dụng Admin

1.  Truy cập `/admin`.
2.  Vào mục **Users** để quản lý danh sách học viên.
3.  Vào mục **Modules** để tạo một Module mới (Ví dụ: "Module 01: Introduction").
    *   Trong trang tạo Module, bạn có thể cài đặt **Exam Configuration**:
        *   **Time limit:** Thời gian làm bài (phút).
        *   **Show result mode:** Chọn `Immediate` để hiện kết quả ngay sau mỗi câu, hoặc `After submit` để hiện sau khi nộp bài.
4.  Vào mục **Questions** để thêm câu hỏi cho Module.

---

## Hướng dẫn triển khai (Production - Linux with Gunicorn & Nginx)

### 1. Cài đặt các gói cần thiết

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### 2. Thiết lập dự án như phần Development (bước 2-6)

**Lưu ý quan trọng trong file `.env`:**
*   Đặt `DEBUG=False`
*   Đặt `ALLOWED_HOSTS=your_domain_or_ip`
*   Thay đổi `SECRET_KEY` thành chuỗi ký tự ngẫu nhiên, dài và bảo mật.

### 3. Thu thập Static files

```bash
python manage.py collectstatic
```

### 4. Cấu hình Gunicorn

Tạo file service systemd cho Gunicorn: `/etc/systemd/system/gunicorn.service`

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/path/to/ceh_quiz
ExecStart=/path/to/ceh_quiz/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/ceh_quiz/ceh_quiz.sock ceh_quiz.wsgi:application

[Install]
WantedBy=multi-user.target
```

*(Thay đổi `/path/to/ceh_quiz` và `User` cho phù hợp)*

Khởi động Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 5. Cấu hình Nginx

Tạo file config: `/etc/nginx/sites-available/ceh_quiz`

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/ceh_quiz;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/ceh_quiz/ceh_quiz.sock;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ceh_quiz /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
