# 二维码扫码登录实现指南

## 一、技术方案

### 1.1 核心流程
```
1. PC端访问登录页 → 生成UUID → 显示二维码
2. 移动端扫码 → 获取UUID → 确认登录
3. 后端验证 → WebSocket推送 → PC端自动登录
```

### 1.2 技术栈
- Django Channels（WebSocket）
- Redis（消息队列）
- qrcode（二维码生成）
- JavaScript（前端交互）

## 二、安装依赖

```bash
pip install channels==3.0.4
pip install channels-redis==3.4.1
pip install qrcode==7.3.1
pip install redis==3.5.3
```

## 三、代码实现

### 3.1 配置WebSocket

**settings.py:**
```python
INSTALLED_APPS = [
    'channels',
    # ... 其他应用
]

ASGI_APPLICATION = 'student_management_system.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### 3.2 创建Consumer

**main_app/consumers.py:**
```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QRLoginConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.uuid = self.scope['url_route']['kwargs']['uuid']
        self.room_group_name = f'qr_login_{self.uuid}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def login_success(self, event):
        await self.send(text_data=json.dumps({
            'type': 'login_success',
            'user_id': event['user_id'],
            'redirect_url': event['redirect_url']
        }))
```

### 3.3 添加路由

**main_app/routing.py:**
```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/qr-login/(?P<uuid>[^/]+)/$', consumers.QRLoginConsumer.as_asgi()),
]
```

### 3.4 生成二维码视图

**main_app/views.py:**
```python
import uuid
import qrcode
from io import BytesIO
from django.core.cache import cache
from django.http import HttpResponse

def generate_qr_code(request):
    # 生成唯一UUID
    login_uuid = str(uuid.uuid4())
    
    # 存储到Redis，5分钟过期
    cache.set(f'qr_login_{login_uuid}', 'pending', 300)
    
    # 生成二维码URL
    qr_url = f"{request.scheme}://{request.get_host()}/qr-scan/{login_uuid}/"
    
    # 生成二维码图片
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 返回图片
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='image/png')
    response['X-QR-UUID'] = login_uuid
    return response

def qr_scan_page(request, uuid):
    """移动端扫码后显示的确认页面"""
    if not request.user.is_authenticated:
        return redirect(f'/?next=/qr-scan/{uuid}/')
    
    return render(request, 'main_app/qr_scan_confirm.html', {
        'uuid': uuid
    })

@login_required
def confirm_qr_login(request, uuid):
    """移动端确认登录"""
    if request.method == 'POST':
        # 验证UUID是否有效
        status = cache.get(f'qr_login_{uuid}')
        if status != 'pending':
            return JsonResponse({'success': False, 'message': '二维码已失效'})
        
        # 标记为已确认
        cache.set(f'qr_login_{uuid}', request.user.id, 60)
        
        # 通过WebSocket通知PC端
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'qr_login_{uuid}',
            {
                'type': 'login_success',
                'user_id': request.user.id,
                'redirect_url': get_redirect_url(request.user)
            }
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def get_redirect_url(user):
    if user.user_type == '1':
        return '/admin_home'
    elif user.user_type == '2':
        return '/staff_home'
    else:
        return '/student_home'
```

### 3.5 前端实现

**templates/main_app/login.html:**
```html
<div id="qr-login-section">
    <h4>扫码登录</h4>
    <img id="qr-code" src="" alt="二维码">
    <p id="qr-status">请使用手机扫描二维码</p>
    <button onclick="refreshQRCode()">刷新二维码</button>
</div>

<script>
let ws = null;
let currentUUID = null;

function loadQRCode() {
    fetch('/generate-qr-code/')
        .then(response => {
            currentUUID = response.headers.get('X-QR-UUID');
            return response.blob();
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            document.getElementById('qr-code').src = url;
            connectWebSocket(currentUUID);
        });
}

function connectWebSocket(uuid) {
    if (ws) ws.close();
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/qr-login/${uuid}/`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'login_success') {
            document.getElementById('qr-status').textContent = '登录成功，正在跳转...';
            window.location.href = data.redirect_url;
        }
    };
    
    ws.onerror = function() {
        document.getElementById('qr-status').textContent = '连接失败，请刷新';
    };
}

function refreshQRCode() {
    loadQRCode();
}

// 页面加载时生成二维码
window.onload = loadQRCode;

// 5分钟后自动刷新
setTimeout(refreshQRCode, 300000);
</script>
```

**templates/main_app/qr_scan_confirm.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>确认登录</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div style="text-align: center; padding: 50px;">
        <h2>确认登录</h2>
        <p>您正在登录学生管理系统</p>
        <p>当前账号：{{ request.user.email }}</p>
        <button onclick="confirmLogin()" style="padding: 15px 30px; font-size: 18px;">
            确认登录
        </button>
        <button onclick="cancelLogin()" style="padding: 15px 30px; font-size: 18px;">
            取消
        </button>
        <p id="message"></p>
    </div>
    
    <script>
    function confirmLogin() {
        fetch('/confirm-qr-login/{{ uuid }}/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('message').textContent = '登录成功！';
            } else {
                document.getElementById('message').textContent = data.message;
            }
        });
    }
    
    function cancelLogin() {
        window.close();
    }
    </script>
</body>
</html>
```

### 3.6 URL配置

**main_app/urls.py:**
```python
urlpatterns = [
    # ... 现有路由
    path('generate-qr-code/', views.generate_qr_code, name='generate_qr_code'),
    path('qr-scan/<str:uuid>/', views.qr_scan_page, name='qr_scan_page'),
    path('confirm-qr-login/<str:uuid>/', views.confirm_qr_login, name='confirm_qr_login'),
]
```

## 四、部署说明

### 4.1 安装Redis
```bash
# Windows
# 下载Redis for Windows
# 或使用WSL安装

# Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

### 4.2 运行Daphne（ASGI服务器）
```bash
pip install daphne
daphne -b 0.0.0.0 -p 8000 student_management_system.asgi:application
```

## 五、安全建议

1. UUID使用加密存储
2. 限制扫码次数（防止暴力破解）
3. 二维码5分钟过期
4. 记录登录日志
5. 异常登录预警

## 六、优化方向

1. 添加二维码刷新动画
2. 显示扫码用户头像
3. 支持多设备管理
4. 登录历史记录
