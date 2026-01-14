import webbrowser
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
    QScrollArea, QWidget, QPushButton, QHBoxLayout, QTextBrowser)
from PySide6.QtCore import Qt

class ArticleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新闻详情")
        self.resize(600, 400)
        
        # 设置对话框背景颜色
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
            QWidget {
                background-color: #FFFFFF;
            }
            QTextBrowser {
                border: none;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # 内容容器
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        scroll.setWidget(content_widget)
        
        layout.addWidget(scroll)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # 查看原页面按钮
        self.original_page_btn = QPushButton("查看原页面")
        self.original_page_btn.setFixedWidth(120)
        self.original_page_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        # 连接按钮点击事件
        self.original_page_btn.clicked.connect(self.open_original_page)
        # 初始禁用按钮
        self.original_page_btn.setEnabled(False)
        btn_layout.addWidget(self.original_page_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def open_original_page(self):
        """打开原始页面"""
        if self.article_url:
            webbrowser.open(self.article_url)
    
    def set_article(self, article):
        """设置文章内容"""
        # 清除现有内容
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().deleteLater()
        
        # 提取原始链接
        self.article_url = article.get("raw_data", {}).get("article_url", "")
        
        # 设置按钮状态
        self.original_page_btn.setEnabled(bool(self.article_url))
        
        # 标题
        title = QTextBrowser()
        title.setPlainText(article["title"])
        title.setStyleSheet("""
            QTextBrowser {
                font-size: 20px;
                font-weight: bold;
                color: #2C3E50;
                padding: 10px 0;
            }
        """)
        title.setMaximumHeight(60)
        title.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_layout.addWidget(title)
        
        # 元信息
        meta = QTextBrowser()
        meta.setPlainText(f"{article['platform']} · {article['category']} · {article['time']}")
        meta.setStyleSheet("""
            QTextBrowser {
                color: #7F8C8D;
                font-size: 13px;
            }
        """)
        meta.setMaximumHeight(30)
        meta.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_layout.addWidget(meta)
        
        # 分隔线
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #ECF0F1;")
        self.content_layout.addWidget(line)
        
        # 内容
        content = QTextBrowser()
        content.setPlainText(article["content"])
        content.setStyleSheet("""
            QTextBrowser {
                font-size: 15px;
                color: #34495E;
                line-height: 1.6;
                padding: 10px 0;
            }
        """)
        content.setOpenExternalLinks(True)
        self.content_layout.addWidget(content)
        
        # 原始链接
        if self.article_url:
            url_label = QTextBrowser()
            url_text = f'<a href="{self.article_url}">{self.article_url}</a>'
            url_label.setHtml(f"<p style='color: #3498DB; font-size: 13px; margin: 10px 0;'>原始链接: {url_text}</p>")
            url_label.setOpenExternalLinks(True)
            url_label.setMaximumHeight(40)
            url_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.content_layout.addWidget(url_label)
        
        # 底部留白
        self.content_layout.addStretch()
