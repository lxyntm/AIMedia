import os
import qrcode
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox, QPushButton, 
    QLineEdit, QHBoxLayout, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIcon
from utils.auth_service import AuthService
from .main_window import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        """界面渲染配置"""
        self.setWindowTitle("登录")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)
        
        # 初始化状态
        self.state = None
        self.query_count = 0
        self.max_query_attempts = 30
        
        self.login_timer = QTimer()
        self.login_timer.timeout.connect(self.check_login_status)
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_qr_code)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建垂直布局
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(20)
        
        # 添加logo图片
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "logo.png")
        logo_pixmap = QPixmap(logo_path).scaled(
            100, 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # 添加登录方式切换按钮
        switch_layout = QHBoxLayout()
        switch_layout.setSpacing(10)
        
        self.wechat_login_btn = QPushButton("微信登录")
        self.email_login_btn = QPushButton("邮箱登录")
        
        self.wechat_login_btn.setStyleSheet("""
            QPushButton {
                background-color: #07C160;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #06A050;
            }
        """)
        self.email_login_btn.setStyleSheet("""
            QPushButton {
                background-color: #E6E6E6;
                color: #333;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #D0D0D0;
            }
        """)
        
        # 默认选中微信登录
        self.wechat_login_btn.setChecked(True)
        
        self.wechat_login_btn.clicked.connect(lambda: self.switch_login_method('wechat'))
        self.email_login_btn.clicked.connect(lambda: self.switch_login_method('email'))
        
        switch_layout.addWidget(self.wechat_login_btn)
        switch_layout.addWidget(self.email_login_btn)
        layout.addLayout(switch_layout)
        
        # 创建堆叠窗口部件来切换登录方式
        self.stacked_widget = QStackedWidget()
        
        # 微信登录界面
        self.wechat_login_widget = self.create_wechat_login_widget()
        self.stacked_widget.addWidget(self.wechat_login_widget)
        
        # 邮箱登录界面
        self.email_login_widget = self.create_email_login_widget()
        self.stacked_widget.addWidget(self.email_login_widget)
        
        layout.addWidget(self.stacked_widget)
        
        # 默认显示微信登录
        self.stacked_widget.setCurrentWidget(self.wechat_login_widget)
    
    def create_wechat_login_widget(self):
        """创建微信登录界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # 添加提示标签
        tip_label = QLabel("请使用微信扫描二维码登录")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #333333;
                font-family: "Microsoft YaHei";
                margin: 10px 0;
                font-weight: 500;
            }
        """)
        layout.addWidget(tip_label)
        
        # 添加二维码容器（白色背景面板）
        qr_container = QWidget()
        qr_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #EEEEEE;
                border-radius: 12px;
            }
        """)
        qr_container.setFixedSize(260, 260)
        
        # 二维码容器使用垂直布局
        qr_layout = QVBoxLayout(qr_container)
        qr_layout.setContentsMargins(10, 10, 10, 10)
        
        # 添加二维码标签
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(240, 240)
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("""
            QLabel {
                background-color: white;
            }
        """)
        qr_layout.addWidget(self.qr_label)
        
        # 将二维码容器添加到主布局
        layout.addWidget(qr_container, alignment=Qt.AlignCenter)
        
        # 添加底部提示
        bottom_tip = QLabel("扫码后请在手机上确认登录")
        bottom_tip.setAlignment(Qt.AlignCenter)
        bottom_tip.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                font-family: "Microsoft YaHei";
                margin-top: 10px;
            }
        """)
        layout.addWidget(bottom_tip)
        
        # 开始微信登录流程
        self.start_login()
        
        return widget
    
    def create_email_login_widget(self):
        """创建邮箱登录界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(15)
        
        # 添加提示标签
        tip_label = QLabel("邮箱登录")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #333333;
                font-family: "Microsoft YaHei";
                margin: 10px 0;
                font-weight: bold;
            }
        """)
        layout.addWidget(tip_label)
        
        # 邮箱输入框
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入邮箱")
        self.email_input.setFixedWidth(260)
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #07C160;
            }
        """)
        layout.addWidget(self.email_input)
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setFixedWidth(260)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #07C160;
            }
        """)
        layout.addWidget(self.password_input)
        
        # 登录按钮
        self.email_login_btn_ui = QPushButton("登录")
        self.email_login_btn_ui.setFixedWidth(260)
        self.email_login_btn_ui.setStyleSheet("""
            QPushButton {
                background-color: #07C160;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #06A050;
            }
        """)
        self.email_login_btn_ui.clicked.connect(self.handle_email_login)
        layout.addWidget(self.email_login_btn_ui)
        
        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.setFixedWidth(260)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #E6E6E6;
                color: #333;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        self.register_btn.clicked.connect(self.handle_email_register)
        layout.addWidget(self.register_btn)
        
        return widget
    
    def switch_login_method(self, method):
        """切换登录方式"""
        if method == 'wechat':
            self.stacked_widget.setCurrentWidget(self.wechat_login_widget)
            self.wechat_login_btn.setChecked(True)
            self.email_login_btn.setChecked(False)
            # 重新开始微信登录流程
            self.start_login()
        elif method == 'email':
            self.stacked_widget.setCurrentWidget(self.email_login_widget)
            self.wechat_login_btn.setChecked(False)
            self.email_login_btn.setChecked(True)
            # 停止微信登录定时器
            self.login_timer.stop()
            self.refresh_timer.stop()
    
    def start_login(self):
        """开始登录流程"""
        try:
            # 获取登录二维码
            self.refresh_qr_code()
            
            # 启动定时器
            self.login_timer.start(2000)  # 每2秒检查一次登录状态
            self.refresh_timer.start(55000)  # 55秒后刷新二维码
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动登录失败: {str(e)}")
    
    def refresh_qr_code(self):
        """刷新二维码"""
        try:
            # 重置查询计数器
            self.query_count = 0
            
            # 获取新的二维码URL和state
            authorize_url, self.state = AuthService.get_login_url()
            
            # 打印完整的二维码链接和调试信息
            print("\n" + "="*50)
            print("二维码链接信息:")
            print("-"*50)
            print(f"URL: {authorize_url}")
            print(f"State: {self.state}")
            print(f"URL长度: {len(authorize_url)}")
            print("-"*50)
            
            # 验证URL格式
            if not authorize_url.startswith('http'):
                raise ValueError(f"无效的URL格式: {authorize_url}")
            
            # 生成二维码前先测试URL
            import requests
            try:
                response = requests.head(authorize_url, timeout=5)
                print(f"URL状态码: {response.status_code}")
                if response.status_code != 200:
                    print(f"警告: URL可能无法访问，状态码: {response.status_code}")
            except Exception as e:
                print(f"警告: URL测试失败: {str(e)}")
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # 降低错误纠正级别
                box_size=10,
                border=4
            )
            qr.add_data(authorize_url)
            qr.make(fit=True)
            
            # 生成图片
            img = qr.make_image()
            
            # 保存二维码到临时文件
            temp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_qr.png")
            img.save(temp_path)
            
            # 显示二维码
            pixmap = QPixmap(temp_path)
            scaled_pixmap = pixmap.scaled(
                240, 240,  # 调整显示尺寸
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 验证生成的图片
            if pixmap.isNull():
                raise ValueError("二维码图片生成失败")
                
            self.qr_label.setPixmap(scaled_pixmap)
            
            # 删除临时文件
            os.remove(temp_path)
            
            # 在窗口标题显示刷新状态
            self.setWindowTitle(f"登录 - 二维码已刷新 ({self.state})")
            
        except Exception as e:
            error_msg = f"刷新二维码失败: {str(e)}"
            print(f"错误: {error_msg}")
            QMessageBox.critical(self, "错误", error_msg)
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            if not self.state:
                return
                
            token = AuthService.check_login_status(self.state)
            if token == "SCAN_FAILED":
                # 增加查询计数
                self.query_count += 1
                
                # 只有在达到最大查询次数后才刷新二维码
                if self.query_count >= self.max_query_attempts:
                    print(f"查询{self.query_count}次后扫码仍未成功，刷新二维码")
                    self.refresh_qr_code()
            elif token:  # 获取到access token
                # 停止定时器
                self.login_timer.stop()
                self.refresh_timer.stop()
                
                # 保存token
                AuthService.save_token(token)
                
                # 打开主窗口
                self.open_main_window()
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"检查登录状态失败: {str(e)}")
    
    def open_main_window(self):
        """打开主窗口"""
        from views.main_window import MainWindow
        self.main_window = MainWindow()
        
        # 设置测试用户信息
        self.main_window.update_user_info(
            nickname="测试用户",
            avatar_path="docs/default_avatar.png",
            is_vip=True,  # 设置为VIP用户便于测试
            vip_expire_date="2024-12-31"  # 设置会员到期日期
        )
        
        self.main_window.show()
        self.close()
    
    def handle_email_login(self):
        """处理邮箱登录"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email:
            QMessageBox.warning(self, "警告", "请输入邮箱")
            return
            
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
        
        try:
            # 调用API进行邮箱登录
            import requests
            import json
            
            # 获取后端地址
            backend_url = AuthService.get_backend_url()
            login_url = f"{backend_url}/api/users/login/"
            
            payload = {
                'username': email,  # 可以是邮箱、手机号或open_id
                'password': password
            }
            
            response = requests.post(login_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    token_data = result.get('data', {})
                    access_token = token_data.get('access')
                    
                    if access_token:
                        # 保存token
                        AuthService.save_token(access_token)
                        
                        # 打开主窗口
                        self.open_main_window()
                    else:
                        QMessageBox.critical(self, "错误", "登录失败：未获取到访问令牌")
                else:
                    error_msg = result.get('msg', '登录失败')
                    QMessageBox.critical(self, "错误", f"登录失败: {error_msg}")
            else:
                QMessageBox.critical(self, "错误", f"登录请求失败: {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录过程中发生错误: {str(e)}")
    
    def handle_email_register(self):
        """处理邮箱注册"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email:
            QMessageBox.warning(self, "警告", "请输入邮箱")
            return
            
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
        
        # 验证邮箱格式
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "警告", "请输入有效的邮箱地址")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "警告", "密码长度不能少于6位")
            return
        
        try:
            # 调用API进行邮箱注册
            import requests
            import json
            
            # 获取后端地址
            backend_url = AuthService.get_backend_url()
            register_url = f"{backend_url}/api/users/register/"
            
            payload = {
                'email': email,
                'password': password,
                'nickname': email.split('@')[0]  # 使用邮箱用户名部分作为昵称
            }
            
            response = requests.post(register_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    token_data = result.get('data', {})
                    access_token = token_data.get('access')
                    
                    if access_token:
                        # 保存token
                        AuthService.save_token(access_token)
                        
                        # 打开主窗口
                        self.open_main_window()
                    else:
                        QMessageBox.critical(self, "错误", "注册失败：未获取到访问令牌")
                else:
                    error_msg = result.get('msg', '注册失败')
                    QMessageBox.critical(self, "错误", f"注册失败: {error_msg}")
            else:
                QMessageBox.critical(self, "错误", f"注册请求失败: {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"注册过程中发生错误: {str(e)}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.login_timer.stop()
        self.refresh_timer.stop()
        super().closeEvent(event)
