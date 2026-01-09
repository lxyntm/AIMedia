import os
import platform
import random
import shutil
import subprocess
import time
from io import BytesIO

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from auto_browser.baijiahao import publish_baijiahao

from auto_browser.qiehao import publish_qiehao
from auto_browser.weixin import publish_weixin

if platform.system() == "Windows":
    import win32clipboard
    import pyperclip
    from win32com import client as win_client
    import pythoncom

elif platform.system() == "Darwin":  # macOS
    from AppKit import NSPasteboard, NSImage


class AutoTools(object):
    def __init__(self):
        self.platform_url = {
            "头条号": "https://mp.toutiao.com/auth/page/login",
            "抖音热点宝": "https://douhot.douyin.com/welcome",
            "百家号": "https://baijiahao.baidu.com/builder/theme/bjh/login",
            "微信公众号":"https://mp.weixin.qq.com/",
            "企鹅号":"https://om.qq.com/main/creation/article"
        }

    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式git
        chrome_options.add_argument("--disable-gpu")
        current_path = os.path.dirname(__file__)
        parent_path = os.path.dirname(current_path)
        if platform.system() == "Windows":
            chrome_path = os.path.join(parent_path, "chrome", "chrome.exe")
            pythoncom.CoInitialize()
            win_obj = win_client.Dispatch("Scripting.FileSystemObject")
            chrome_version = win_obj.GetFileVersion(chrome_path)
            chrome_version = chrome_version.strip()
        else:
            chrome_path = os.path.join(
                parent_path,
                "chrome-mac-arm64",
                "Google Chrome for Testing.app",
                "Contents",
                "MacOS",
                "Google Chrome for Testing",
            )
            result = subprocess.run(
                [chrome_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            chrome_version = result.stdout.decode("utf-8").strip().split()[-1]

        chrome_options.binary_location = chrome_path
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # 使用指定路径的ChromeDriver
        current_path = os.path.dirname(__file__)
        parent_path = os.path.dirname(current_path)
        chromedriver_path = os.path.join(parent_path, "chrome", "chromedriver.exe")
        
        # 检查ChromeDriver文件是否存在
        if os.path.exists(chromedriver_path):
            # 使用指定路径的ChromeDriver
            driver = webdriver.Chrome(
                options=chrome_options,
                service=Service(chromedriver_path),
            )
        else:
            # 如果指定路径不存在，抛出异常
            raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}. Please download ChromeDriver and place it in the chrome directory.")
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            },
        )
        screen_width = driver.execute_script("return window.screen.width")
        screen_height = driver.execute_script("return window.screen.height")
        window_width = screen_width
        window_height = screen_height
        driver.set_window_size(window_width, window_height)
        
        # 确保COM对象被正确释放
        if platform.system() == "Windows":
            try:
                pythoncom.CoUninitialize()
            except:
                pass
        
        return driver

    def connect_driver(self, random_number, chrome_path, user_data_dir):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option(
            "debuggerAddress", f"127.0.0.1:{random_number}"
        )
        if platform.system() == "Windows":
            pythoncom.CoInitialize()
            chrome_options.add_argument(rf"--user-data-dir={user_data_dir}")
            
            # 获取Chrome版本，尝试当前路径，如果失败则尝试替代路径
            chrome_version = None
            try:
                win_obj = win_client.Dispatch("Scripting.FileSystemObject")
                chrome_version = win_obj.GetFileVersion(chrome_path)
                chrome_version = chrome_version.strip()
            except Exception:
                # 如果当前路径获取失败，尝试检查是否有其他可执行文件
                current_dir = os.path.dirname(chrome_path)
                chrome_exe_path = os.path.join(current_dir, "chrome.exe")
                chrome1_exe_path = os.path.join(current_dir, "chrome1.exe")
                
                # 尝试chrome.exe
                if chrome_path != chrome_exe_path and os.path.exists(chrome_exe_path):
                    try:
                        win_obj = win_client.Dispatch("Scripting.FileSystemObject")
                        chrome_version = win_obj.GetFileVersion(chrome_exe_path)
                        chrome_version = chrome_version.strip()
                        chrome_path = chrome_exe_path  # 更新chrome_path为实际使用的路径
                    except Exception:
                        pass
                
                # 如果chrome.exe也失败，尝试chrome1.exe
                if not chrome_version and chrome_path != chrome1_exe_path and os.path.exists(chrome1_exe_path):
                    try:
                        win_obj = win_client.Dispatch("Scripting.FileSystemObject")
                        chrome_version = win_obj.GetFileVersion(chrome1_exe_path)
                        chrome_version = chrome_version.strip()
                        chrome_path = chrome1_exe_path  # 更新chrome_path为实际使用的路径
                    except Exception:
                        pass
            
            # 如果仍然无法获取版本，使用默认版本号
            if not chrome_version:
                chrome_version = "130.0.0.0"  # 默认版本号
                
            user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
        else:
            chrome_version = (
                os.popen(f'"{chrome_path}" --version')
                .read()
                .strip()
                .replace("Google Chrome for Testing ", "")
            )
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")

        # 使用指定路径的ChromeDriver
        current_path = os.path.dirname(__file__)
        parent_path = os.path.dirname(current_path)
        chromedriver_path = os.path.join(parent_path, "chrome", "chromedriver.exe")
        
        try:
            # 检查ChromeDriver文件是否存在
            if os.path.exists(chromedriver_path):
                # 使用指定路径的ChromeDriver
                driver = webdriver.Chrome(
                    options=chrome_options,
                    service=Service(chromedriver_path),
                )
            else:
                # 如果指定路径不存在，抛出异常
                raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}. Please download ChromeDriver and place it in the chrome directory.")
        finally:
            # 确保COM对象被正确释放
            if platform.system() == "Windows":
                try:
                    pythoncom.CoUninitialize()
                except:
                    pass

        return driver, random_number

    def run_as_admin(self, cmd):
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(cmd, shell=True, startupinfo=startupinfo)
        else:
            # macOS 无需 Windows 的 STARTUPINFO，直接运行命令即可
            process = subprocess.Popen(cmd, shell=True)
        return process

    def close_chrome_tab(self, port):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/json")
            response.raise_for_status()
            data = response.json()
            for tab in data:
                if tab["type"] == "page":
                    tab_id = tab["id"]
                    requests.get(f"http://127.0.0.1:{port}/json/close/{tab_id}")
                    print(f"Closed tab with ID: {tab_id}")
        except requests.RequestException as e:
            print(f"Error: {e}")

    def get_cookies(self, platform_):
        driver = self.get_driver()
        driver.get(self.platform_url[platform_])
        driver.delete_all_cookies()
        
        # 检查是否需要登录 - 先等待页面加载
        time.sleep(3)
        
        nickName, cookies, uid = "", "", ""
        
        # 设置最大等待时间（秒）
        max_wait_time = 120  # 最多等待120秒，给用户更多时间登录
        waited_time = 0
        
        # 添加标记变量，确保只在首次检测到登录时执行一次用户信息获取逻辑
        info_fetched = False
        
        while waited_time < max_wait_time:
            # 首先检查是否已经获取过用户信息，如果是则直接跳出循环
            if info_fetched:
                print("已获取过用户信息，直接返回结果")
                break
                
            try:
                time.sleep(1)
                waited_time += 1
                
                # 检查用户是否已登录 - 根据不同平台使用不同的检测方法
                if platform_ == "头条号":
                    # 对于头条号，检查是否存在用户头像或用户名元素
                    logged_in = False
                    try:
                        # 尝试多种方法检测登录状态
                        # 1. 查找用户头像元素
                        elements_to_check = [
                            ("class name", "auth-avator-name"),
                            ("css selector", ".user-name"),
                            ("css selector", ".user-info .name"),
                            ("xpath", "//div[contains(@class, 'user') and contains(@class, 'name')]"),
                            ("css selector", "[data-user-name]"),  # data属性
                            ("xpath", "//span[contains(@class, 'name') or contains(@class, 'nickname')]"),
                            ("css selector", ".username"),
                            ("css selector", ".nickname"),
                        ]
                        
                        for by_method, selector in elements_to_check:
                            try:
                                element = driver.find_element(by_method, selector)
                                if element and element.text.strip():
                                    nickName = element.text.strip()
                                    logged_in = True
                                    print(f"检测到用户昵称: {nickName}")
                                    break
                            except:
                                continue
                        
                        # 2. 如果没有找到用户名，尝试通过URL判断（登录后URL通常会变化）
                        if not logged_in:
                            current_url = driver.current_url
                            print(f"当前URL: {current_url}")
                            # 如果URL包含特定的登录后路径，说明已登录
                            if "profile" in current_url or "dashboard" in current_url or "auth" not in current_url:
                                # 尝试直接获取用户名
                                try:
                                    # 查找可能包含用户名的元素（更精确的选择器）
                                    for by_method, selector in [("css selector", ".username"), ("css selector", ".user-name"), ("css selector", ".nickname"), ("css selector", "[data-username]"), ("css selector", ".profile-name"), ("xpath", "//span[contains(@class, 'name') or contains(@class, 'username')]")]:
                                        try:
                                            user_elements = driver.find_elements(by_method, selector)
                                            for elem in user_elements:
                                                elem_text = elem.text.strip()
                                                # 检查元素文本是否可能是用户名（避免按钮等）
                                                if elem_text and len(elem_text) > 1 and len(elem_text) < 20 and not any(word in elem_text for word in ["登录", "注册", "退出", "设置", "首页", "发布", "消息", "通知", "草稿", "管理"]):
                                                    if elem.get_attribute("href") or "user" in elem.get_attribute("class", "") or "profile" in elem.get_attribute("class", ""):
                                                        nickName = elem_text
                                                        logged_in = True
                                                        print(f"通过页面元素检测到用户: {nickName}")
                                                        break
                                            if logged_in:
                                                break
                                        except:
                                            continue
                                except:
                                    pass
                        
                        # 3. 如果仍未检测到登录状态，检查是否存在登录按钮（未登录时显示）
                        if not logged_in:
                            try:
                                # 查找登录相关的按钮或链接
                                login_elements = driver.find_elements(By.XPATH, "//button[contains(text(), '登录') or contains(text(), '立即登录') or contains(text(), 'Sign') or contains(text(), 'sign')] | //a[contains(text(), '登录') or contains(text(), '立即登录')]")
                                if not login_elements:
                                    # 如果没有找到登录相关的元素，可能已经登录
                                    logged_in = True
                                    print("未找到登录按钮，可能已经登录")
                            except:
                                pass
                                
                    except Exception as e:
                        print(f"检测登录状态时出错: {str(e)}")
                        import traceback
                        traceback.print_exc()
                elif platform_ == "百家号":
                    # 对于百家号的专门登录状态检测
                    logged_in = False
                    try:
                        # 尝试点击登录按钮（如果存在）
                        try:
                            login_button = driver.find_element(By.CLASS_NAME, 'btnlogin--bI826')
                            login_button.click()
                            time.sleep(1)
                        except:
                            pass
                        
                        # 关闭引导弹窗
                        try:
                            driver.find_element(By.XPATH, '//*[@id="react-joyride-step-0"]/div/div/div[1]/div[2]/button').click()
                            time.sleep(1)
                        except:
                            pass
                        try:
                            driver.find_element(By.XPATH, '//*[@id="react-joyride-step-1"]/div/div/div[1]/div[2]/button[2]').click()
                            time.sleep(1)
                        except:
                            pass
                        try:
                            driver.find_element(By.XPATH, '//*[@id="react-joyride-step-2"]/div/div/div[1]/div[2]/button[2]').click()
                            time.sleep(1)
                        except:
                            pass
                        try:
                            driver.find_element(By.XPATH,'//*[@id="react-joyride-step-3"]/div/div/div[1]/div[2]/button[2]').click()
                            time.sleep(1)
                        except:
                            pass
                        
                        # 尝试多种方法检测登录状态
                        login_check_methods = [
                            ("id", "asideMenuItem-个人中心"),  # 如果存在个人中心菜单，说明已登录
                            ("xpath", "//div[contains(@class, 'username')]"),
                            ("xpath", "//span[contains(@class, 'nickname')]"),
                            ("xpath", "//div[contains(text(), '个人中心')]"),
                            ("css selector", ".pRvnIfCutwzU_pTdvz9Q"),  # 原有的昵称选择器
                        ]
                        
                        for by_method, selector in login_check_methods:
                            try:
                                element = driver.find_element(by_method, selector)
                                if by_method == "id":
                                    # 存在个人中心按钮，说明已登录
                                    logged_in = True
                                    print("检测到个人中心按钮，已登录")
                                    break
                                elif element and element.text.strip():
                                    nickName = element.text.strip()
                                    logged_in = True
                                    print(f"检测到用户昵称: {nickName}")
                                    break
                            except:
                                continue
                        
                        # 通过URL判断登录状态
                        if not logged_in:
                            current_url = driver.current_url
                            print(f"百家号当前URL: {current_url}")
                            if "builder" in current_url and "login" not in current_url:
                                logged_in = True
                                print("通过URL判断已登录")
                        
                    except Exception as e:
                        print(f"百家号检测登录状态时出错: {str(e)}")
                        import traceback
                        traceback.print_exc()
                else:
                    # 对于其他平台使用原来的逻辑
                    try:
                        avatar_name_element = driver.find_element("class name", "auth-avator-name")
                        nickName = avatar_name_element.text
                        logged_in = bool(nickName)
                    except:
                        logged_in = False
                        nickName = ""
                
                if not logged_in:
                    # 如果未登录，继续等待
                    print(f"等待用户登录到{platform_}... ({waited_time}/{max_wait_time}秒)")
                    continue
                
                # 如果已经获取过用户信息，直接跳出循环
                if info_fetched:
                    print("已获取过用户信息，直接返回结果")
                    break
                
                # 如果检测到已登录，获取用户信息
                print(f"检测到已登录，正在获取用户信息...")
                
                # 获取cookies
                cookies = driver.get_cookies()
                print(f"获取到 {len(cookies)} 个cookies")
                
                # 调试：显示所有cookie名称
                cookie_names = [cookie.get('name') for cookie in cookies]
                print(f"所有cookie名称: {cookie_names}")
                
                # 如果已经获取过用户信息，不再重复执行UID获取逻辑
                if info_fetched:
                    print("已获取过用户信息，直接返回结果")
                    break
                
                # 根据不同平台获取UID
                if platform_ == "头条号":
                    try:
                        # 头条号特殊处理：需要访问www.toutiao.com获取存储在该域的UID cookies
                        original_url = driver.current_url
                        print(f"当前URL: {original_url}")
                        
                        # 访问www.toutiao.com获取该域的cookies
                        try:
                            driver.get("https://www.toutiao.com")
                            time.sleep(2)  # 等待页面加载
                            www_cookies = driver.get_cookies()
                            print(f"从www.toutiao.com获取到 {len(www_cookies)} 个cookies")
                            
                            # 调试：显示www.toutiao.com的cookie名称
                            www_cookie_names = [cookie.get('name') for cookie in www_cookies]
                            print(f"www.toutiao.com的cookie名称: {www_cookie_names}")
                            
                            # 合并两个域的cookies
                            all_cookies = cookies + www_cookies
                            print(f"合并后共有 {len(all_cookies)} 个cookies")
                        except Exception as e:
                            print(f"访问www.toutiao.com时出错: {str(e)}")
                            # 如果访问失败，使用原cookies
                            all_cookies = cookies
                        
                        # 首先尝试从合并后的cookies中获取UID
                        uid_keys = ["uid", "tt_webid", "toutiao_uid", "webid"]
                        # 将cookie名称转换为小写进行匹配，避免大小写问题
                        cookie_dict = {cookie.get('name', '').lower(): cookie.get('value', '') for cookie in all_cookies}
                        
                        for key in uid_keys:
                            lower_key = key.lower()
                            if lower_key in cookie_dict:
                                uid = cookie_dict[lower_key]
                                if uid:
                                    print(f"从cookie '匹配的{key}' 中获取到UID: {uid}")
                                    break
                        else:
                            # 如果没有找到匹配的cookie，继续尝试遍历所有cookie
                            print("没有找到直接匹配的UID cookie，尝试遍历所有cookie查找包含uid的名称...")
                            for cookie in all_cookies:
                                cookie_name = cookie.get('name', '').lower()
                                if 'uid' in cookie_name:
                                    uid = cookie.get('value', '')
                                    if uid:
                                        print(f"从cookie '{cookie.get('name')}' 中获取到UID: {uid}")
                                        break
                        
                        # 如果从cookies中没有获取到UID，尝试从页面元素获取
                        if not uid:
                            uid_selectors = [
                                '//*[@id="root"]/div/div[1]/div[1]/div[2]/div[5]/div/div[2]',  # 原来的选择器
                                '//div[contains(text(), "账号ID")]/following-sibling::div',  # 包含"账号ID"文本的元素的兄弟元素
                                '//div[contains(text(), "ID") and contains(@class, "id")]',  # 包含ID的元素
                                '//span[contains(text(), "ID")]/following-sibling::*',  # ID文本后的兄弟元素
                                '//div[contains(text(), "UID") or contains(text(), "uid") or contains(text(), "用户ID")]/following-sibling::*',
                                '//div[contains(text(), "复制ID")]/preceding-sibling::*',
                                '//div[contains(@class, "id") or contains(@class, "uid")]',
                            ]
                            
                            for selector in uid_selectors:
                                try:
                                    uid_element = driver.find_element("xpath", selector)
                                    if uid_element and uid_element.text.strip():
                                        element_text = uid_element.text.strip()
                                        # 确保获取的UID长度合理，避免获取到导航菜单
                                        if len(element_text) <= 50 and not any(nav_word in element_text for nav_word in ["主页", "创作", "文章", "视频", "微头条", "音频", "管理", "评论", "草稿", "数据", "收益", "作品", "粉丝", "进阶", "付费", "专栏", "提现", "成长", "指南", "首发", "激励", "权益", "认证", "灵感", "训练营", "工具", "功能", "实验室", "直播", "加油包", "保护", "素材", "设置"]):
                                            uid = element_text
                                            uid = uid.replace("复制ID", "").replace("\n", "").replace("\t", "")
                                            print(f"通过选择器 '{selector}' 找到UID: {uid}")
                                            break
                                        else:
                                            print(f"跳过可能的导航文本: {element_text[:50]}...")
                                except:
                                    continue
                        
                        # 如果仍没找到UID，尝试访问个人资料页面
                        if not uid:
                            print("在当前页面未找到UID，尝试导航到个人资料页面...")
                            try:
                                # 直接导航到头条号个人详情页面获取UID
                                print("直接导航到头条号个人详情页面...")
                                profile_url = "https://mp.toutiao.com/profile_v4/personal/info?click_from=header"
                                driver.get(profile_url)
                                time.sleep(3)  # 等待页面加载
                                profile_clicked = True
                                
                                # 在个人资料页面再次尝试查找UID
                                if profile_clicked and not uid:
                                    for selector in uid_selectors:
                                        try:
                                            uid_element = driver.find_element("xpath", selector)
                                            element_text = uid_element.text.strip()
                                            # 确保获取的UID长度合理，避免获取到导航菜单
                                            if element_text and len(element_text) <= 50 and not any(nav_word in element_text for nav_word in ["主页", "创作", "文章", "视频", "微头条", "音频", "管理", "评论", "草稿", "数据", "收益", "作品", "粉丝", "进阶", "付费", "专栏", "提现", "成长", "指南", "首发", "激励", "权益", "认证", "灵感", "训练营", "工具", "功能", "实验室", "直播", "加油包", "保护", "素材", "设置"]):
                                                uid = element_text
                                                uid = uid.replace("复制ID", "").replace("\n", "").replace("\t", "")
                                                print(f"在个人资料页通过选择器 '{selector}' 找到UID: {uid}")
                                                break
                                            else:
                                                if element_text:
                                                    print(f"跳过可能的导航文本: {element_text[:50]}...")
                                        except:
                                            continue
                            except Exception as e:
                                print(f"访问个人资料页面时出错: {str(e)}")
                                
                    except Exception as e:
                        print(f"获取{platform_} UID时遇到异常: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                # 针对不同平台获取UID
                if platform_ == "头条号":
                    try:
                        # 头条号特殊处理：需要访问www.toutiao.com获取存储在该域的UID cookies
                        original_url = driver.current_url
                        print(f"当前URL: {original_url}")
                        
                        # 访问www.toutiao.com获取该域的cookies
                        try:
                            driver.get("https://www.toutiao.com")
                            time.sleep(2)  # 等待页面加载
                            www_cookies = driver.get_cookies()
                            print(f"从www.toutiao.com获取到 {len(www_cookies)} 个cookies")
                            
                            # 调试：显示www.toutiao.com的cookie名称
                            www_cookie_names = [cookie.get('name') for cookie in www_cookies]
                            print(f"www.toutiao.com的cookie名称: {www_cookie_names}")
                            
                            # 合并两个域的cookies
                            all_cookies = cookies + www_cookies
                            print(f"合并后共有 {len(all_cookies)} 个cookies")
                        except Exception as e:
                            print(f"访问www.toutiao.com时出错: {str(e)}")
                            # 如果访问失败，使用原cookies
                            all_cookies = cookies
                        
                        # 首先尝试从合并后的cookies中获取UID
                        uid_keys = ["uid", "tt_webid", "toutiao_uid", "webid"]
                        # 将cookie名称转换为小写进行匹配，避免大小写问题
                        cookie_dict = {cookie.get('name', '').lower(): cookie.get('value', '') for cookie in all_cookies}
                        
                        for key in uid_keys:
                            lower_key = key.lower()
                            if lower_key in cookie_dict:
                                uid = cookie_dict[lower_key]
                                if uid:
                                    print(f"从cookie '匹配的{key}' 中获取到UID: {uid}")
                                    break
                        else:
                            # 如果没有找到匹配的cookie，继续尝试遍历所有cookie
                            print("没有找到直接匹配的UID cookie，尝试遍历所有cookie查找包含uid的名称...")
                            for cookie in all_cookies:
                                cookie_name = cookie.get('name', '').lower()
                                if 'uid' in cookie_name:
                                    uid = cookie.get('value', '')
                                    if uid:
                                        print(f"从cookie '{cookie.get('name')}' 中获取到UID: {uid}")
                                        break
                        
                        # 如果从cookies中没有获取到UID，尝试从页面元素获取
                        if not uid:
                            uid_selectors = [
                                '//*[@id="root"]/div/div[1]/div[1]/div[2]/div[5]/div/div[2]',  # 原来的选择器
                                '//div[contains(text(), "账号ID")]/following-sibling::div',  # 包含"账号ID"文本的元素的兄弟元素
                                '//div[contains(text(), "ID") and contains(@class, "id")]',  # 包含ID的元素
                                '//span[contains(text(), "ID")]/following-sibling::*',  # ID文本后的兄弟元素
                                '//div[contains(text(), "UID") or contains(text(), "uid") or contains(text(), "用户ID")]/following-sibling::*',
                                '//div[contains(text(), "复制ID")]/preceding-sibling::*',
                                '//div[contains(@class, "id") or contains(@class, "uid")]',
                            ]
                            
                            for selector in uid_selectors:
                                try:
                                    uid_element = driver.find_element("xpath", selector)
                                    if uid_element and uid_element.text.strip():
                                        element_text = uid_element.text.strip()
                                        # 确保获取的UID长度合理，避免获取到导航菜单
                                        if len(element_text) <= 50 and not any(nav_word in element_text for nav_word in ["主页", "创作", "文章", "视频", "微头条", "音频", "管理", "评论", "草稿", "数据", "收益", "作品", "粉丝", "进阶", "付费", "专栏", "提现", "成长", "指南", "首发", "激励", "权益", "认证", "灵感", "训练营", "工具", "功能", "实验室", "直播", "加油包", "保护", "素材", "设置"]):
                                            uid = element_text
                                            uid = uid.replace("复制ID", "").replace("\n", "").replace("\t", "")
                                            print(f"通过选择器 '{selector}' 找到UID: {uid}")
                                            break
                                        else:
                                            print(f"跳过可能的导航文本: {element_text[:50]}...")
                                except:
                                    continue
                        
                        # 如果仍没找到UID，尝试访问个人资料页面
                        if not uid:
                            print("在当前页面未找到UID，尝试导航到个人资料页面...")
                            try:
                                # 直接导航到头条号个人详情页面获取UID
                                print("直接导航到头条号个人详情页面...")
                                profile_url = "https://mp.toutiao.com/profile_v4/personal/info?click_from=header"
                                driver.get(profile_url)
                                time.sleep(3)  # 等待页面加载
                                profile_clicked = True
                                
                                # 在个人资料页面再次尝试查找UID
                                if profile_clicked and not uid:
                                    for selector in uid_selectors:
                                        try:
                                            uid_element = driver.find_element("xpath", selector)
                                            element_text = uid_element.text.strip()
                                            # 确保获取的UID长度合理，避免获取到导航菜单
                                            if element_text and len(element_text) <= 50 and not any(nav_word in element_text for nav_word in ["主页", "创作", "文章", "视频", "微头条", "音频", "管理", "评论", "草稿", "数据", "收益", "作品", "粉丝", "进阶", "付费", "专栏", "提现", "成长", "指南", "首发", "激励", "权益", "认证", "灵感", "训练营", "工具", "功能", "实验室", "直播", "加油包", "保护", "素材", "设置"]):
                                                uid = element_text
                                                uid = uid.replace("复制ID", "").replace("\n", "").replace("\t", "")
                                                print(f"在个人资料页通过选择器 '{selector}' 找到UID: {uid}")
                                                break
                                            else:
                                                if element_text:
                                                    print(f"跳过可能的导航文本: {element_text[:50]}...")
                                        except:
                                            continue
                            except Exception as e:
                                print(f"访问个人资料页面时出错: {str(e)}")
                                 
                    except Exception as e:
                        print(f"获取{platform_} UID时遇到异常: {str(e)}")
                        import traceback
                        traceback.print_exc()
                elif platform_ == "百家号":
                    try:
                        # 百家号特殊处理：尝试从cookies中获取UID
                        print("尝试获取百家号UID...")
                        
                        # 登录成功后，访问百家号首页获取cookies
                        print("尝试访问百家号首页以触发必要cookies的设置...")
                        try:
                            driver.get("https://baijiahao.baidu.com")
                            time.sleep(3)  # 等待页面加载和cookies设置
                        except Exception as e:
                            print(f"访问百家号首页时出错: {str(e)}")
                        
                        # 重新获取cookies，确保包含所有最新的cookies
                        cookies = driver.get_cookies()
                        print(f"重新获取后，共有 {len(cookies)} 个cookies")
                        
                        # 打印所有cookies的详细信息，方便调试
                        print("所有cookies的详细信息:")
                        for cookie in cookies:
                            print(f"  - {cookie.get('name')}: {cookie.get('value')[:50]}...")
                        
                        # 从cookies中获取UID
                        # ab_bid和ab_jid更适合作为百家号的UID，优先使用
                        baijiahao_uid_keys = ["ab_bid", "ab_jid", "BAIDUID"]
                        # 将cookie名称转换为小写进行匹配，避免大小写问题
                        cookie_dict = {cookie.get('name', '').lower(): cookie.get('value', '') for cookie in cookies}
                        # 初始化uid变量为None，避免未定义错误
                        uid = None
                        
                        # 打印所有可用的cookie键（小写），方便调试
                        print(f"所有可用的cookie键（小写）: {list(cookie_dict.keys())}")
                                    
                        # 尝试从指定的键中获取UID
                        uid = None
                        for key in baijiahao_uid_keys:
                            lower_key = key.lower()
                            print(f"正在检查cookie键: {key} (小写: {lower_key})")
                            if lower_key in cookie_dict:
                                uid = cookie_dict[lower_key]
                                if uid:
                                    print(f"成功从cookie '{key}' 中获取到UID: {uid}")
                                    break
                        
                        # 仅接受指定的cookie键作为有效UID，不使用其他cookie
                        if uid is None:
                            print("没有找到指定的UID cookie (ab_bid, ab_jid, BAIDUID)，将从个人中心获取")
                        
                        # 如果从cookies中没有获取到UID，尝试从页面元素获取
                        if not uid:
                            print("尝试从页面元素获取百家号UID...")
                            
                            # 首先尝试跳转到个人中心页面，确保能看到UID信息
                            try:
                                print("直接导航到百家号个人中心页面...")
                                profile_url = "https://baijiahao.baidu.com/builder/rc/settings/accountSet"
                                driver.get(profile_url)
                                time.sleep(3)  # 等待页面加载
                                print("成功导航到百家号个人中心页面")
                            except Exception as e:
                                print(f"导航到个人中心页面时出错: {str(e)}")
                                # 如果直接导航失败，尝试点击个人中心按钮
                                try:
                                    print("尝试点击个人中心按钮...")
                                    personal_center_elements = driver.find_elements(By.XPATH, 
                                                                                 "//div[text()='个人中心'] | //span[text()='个人中心'] | //a[contains(text(), '个人中心')]")
                                    for elem in personal_center_elements:
                                        try:
                                            elem.click()
                                            time.sleep(2)  # 等待页面加载
                                            print("成功点击个人中心按钮")
                                            break
                                        except Exception as e:
                                            print(f"点击个人中心按钮时出错: {str(e)}")
                                            continue
                                except Exception as e:
                                    print(f"点击个人中心按钮时出错: {str(e)}")
                            
                            # 无论导航是否成功，都尝试提取UID
                            print("开始从个人中心页面提取UID...")
                            uid_selectors = [
                                '//*[@id="layout-main-content"]/div[2]/div/div/div/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div/span',
                                "//div[contains(text(), '账号ID')]/following-sibling::div/span",
                                "//div[contains(text(), '账号ID')]/parent::div//span",
                                "//div[contains(text(), 'ID')]/following-sibling::div/span",
                                "//div[contains(@class, 'id') or contains(@class, 'uid')]//span",
                                "//div[text()='账号ID']/../../..//span",
                                "//*[contains(text(), '账号ID')]/../*[2]/span",
                                "//*[contains(text(), 'ID')]/../span",
                                "//span[contains(@class, 'id')]",
                                "//div[contains(@class, 'account-id')]",
                            ]
                            
                            for selector in uid_selectors:
                                try:
                                    uid_element = driver.find_element("xpath", selector)
                                    if uid_element and uid_element.text.strip():
                                        uid = uid_element.text.strip()
                                        print(f"通过选择器 '{selector}' 找到UID: {uid}")
                                        break
                                except Exception as e:
                                    pass  # 简化错误输出，避免过多调试信息
                            
                            if not uid:
                                print("所有选择器都未能找到UID元素")
                    except Exception as e:
                        print(f"获取百家号UID时遇到异常: {str(e)}")
                        import traceback
                        traceback.print_exc()

                # 成功获取所有信息，跳出循环
                if cookies and (nickName or uid):
                    # 只要有cookies和昵称或UID中的一个就算成功
                    if not uid:
                        # 如果没有找到UID，使用昵称作为UID或者生成一个默认值
                        uid = nickName if nickName else f"{platform_.lower()}_user_{int(time.time())}"
                        print(f"未找到明确的UID，使用默认值: {uid}")
                    
                    # 对于头条号，使用合并后的cookies
                    if platform_ == "头条号" and 'all_cookies' in locals():
                        cookies = all_cookies
                    
                    # 设置标记，表明已经获取过用户信息
                    info_fetched = True
                    
                    print(f"成功获取{platform_}信息: 昵称={nickName}, UID={uid}")
                    break
            except Exception as e:
                # 输出错误信息以便调试
                print(f"获取{platform_}信息时遇到异常: {str(e)}")
                import traceback
                traceback.print_exc()
                # 继续等待用户登录或重试
                
        # 确保浏览器关闭
        try:
            driver.quit()
        except:
            pass
            
        # 返回结果（可能为空值）
        return (nickName.strip() if nickName else ""), cookies, (uid.strip() if uid else "")

    def get_cookies_douy_hot(self, platform_):
        driver = self.get_driver()
        driver.get(self.platform_url[platform_])
        driver.delete_all_cookies()
        time.sleep(1)
        nickName, cookies, uid = None, None, None
        try:
            driver.find_element(
                By.XPATH, '//*[@id="root"]/section/header/div/div[2]/button'
            ).click()
        except:
            pass
        while True:
            try:
                time.sleep(1)
                cookies = driver.get_cookies()
            except:
                pass
            time.sleep(1)
            try:
                elm = driver.find_element(
                    By.XPATH,
                    '//*[@id="root"]/section/header/div/div[2]/div[2]/div/span/img',
                )
            except:
                elm = None
            if elm:
                break
        return cookies

    def publish(self, cookie, content, platform_, imgs_path):
        urls = {"头条号": "https://mp.toutiao.com/profile_v4/graphic/publish",
                "百家号":"https://baijiahao.baidu.com/builder/rc/edit?type=news&is_from_cms=1",
                "微信公众号":"https://mp.weixin.qq.com/",
                "企鹅号":"https://om.qq.com/main/creation/article"
                }
        if platform_ == "头条号":
            url = urls[platform_]
            current_path = os.path.dirname(__file__)
            parent_path = os.path.dirname(current_path)
            if platform.system() == "Windows":
                chrome_path = os.path.join(parent_path, "chrome", "chrome.exe")
            else:
                chrome_path = os.path.join(
                    parent_path,
                    "chrome-mac-arm64",
                    "Google Chrome for Testing.app",
                    "Contents",
                    "MacOS",
                    "Google Chrome for Testing",
                )
            random_number = random.randint(9000, 9999)
            if platform.system() == "Windows":
                new_chrome_path = chrome_path
                user_data_dir = rf"C:\selenium\ChromeProfile{random_number}"
            else:
                new_chrome_path = chrome_path
                user_data_dir = rf"./ChromeProfile{random_number}"
            cmd = rf'"{new_chrome_path}" --remote-debugging-port={random_number} --user-data-dir="{user_data_dir}" --start-maximized --no-first-run --no-default-browser-check'
            self.run_as_admin(cmd)
            driver, random_number = self.connect_driver(
                random_number, new_chrome_path, user_data_dir
            )
            driver.delete_all_cookies()
            driver.get(url)
            time.sleep(1)

            try:
                for ck in cookie:
                    driver.add_cookie(ck)
            except Exception as e:
                print(e)
            time.sleep(2)
            lines = content.splitlines()
            title = lines[0].strip()
            title = title.replace("#", "")
            info = "\n".join(lines[1:]).strip()
            info = info.replace("#", "")
            is_copy_content = False
            out_flag = False
            publish_flag = False
            time_out = 60 * 2
            tart_time = time.time()
            imgs_list = os.listdir(imgs_path)
            imgs_list_len = len(imgs_list)
            result = {
                "status": False,
                "msg": "",
            }
            time.sleep(10)
            while True:
                try:
                    if is_copy_content is False:
                        textarea = driver.find_element(
                            By.XPATH,
                            '//*[@id="root"]/div/div[1]/div/div[1]/div[3]/div/div/div[2]/div/div/div/textarea',
                        )
                        textarea.send_keys(title)
                        time.sleep(random.randint(1, 2))
                        time.sleep(1)
                        info_tag = driver.find_element(
                            By.XPATH,
                            '//*[@id="root"]/div/div[1]/div/div[1]/div[4]/div/div[1]',
                        )

                        if imgs_list_len == 0:
                            pyperclip.copy(info)
                            info_tag.send_keys(Keys.CONTROL, "v")
                            time.sleep(0.5)
                            time.sleep(0.5)
                            info_tag.send_keys(Keys.DOWN)
                            is_copy_content = True
                        else:
                            info_len = info.split("\n")
                            tep = int(len(info_len) / imgs_list_len)
                            info1 = [i + "\n" for i in info_len[0:tep] if len(i) > 0]
                            info2 = [i + "\n" for i in info_len[tep : tep * 2] if len(i) > 0]
                            info3 = [i + "\n" for i in info_len[tep * 2 :] if len(i) > 0]
                            ct = [info1, info2, info3]
                            img_idx = 0
                            for info_txt in ct:
                                try:
                                    # 检查操作系统
                                    if platform.system() == "Windows":
                                        image = Image.open(
                                            os.path.join(imgs_path, imgs_list[img_idx])
                                        )
                                        output = BytesIO()
                                        image.save(output, "BMP")
                                        data = output.getvalue()[14:]
                                        output.close()
                                        win32clipboard.OpenClipboard()
                                        win32clipboard.EmptyClipboard()
                                        win32clipboard.SetClipboardData(
                                            win32clipboard.CF_DIB, data
                                        )
                                        win32clipboard.CloseClipboard()
                                        info_tag.send_keys(Keys.CONTROL, "v")
                                        time.sleep(0.5)
                                        # info_tag.send_keys(Keys.DOWN)
                                    elif platform.system() == "Darwin":  # macOS
                                        image = Image.open(
                                            os.path.join(imgs_path, imgs_list[img_idx])
                                        )
                                        # 将图像转换为 NSImage
                                        output = BytesIO()
                                        image.save(output, "BMP")
                                        output.seek(0)
                                        ns_image = NSImage.alloc().initWithData_(
                                            output.getvalue()
                                        )
                                        # 获取系统剪贴板
                                        pasteboard = NSPasteboard.generalPasteboard()
                                        pasteboard.clearContents()
                                        # 将 NSImage 写入剪贴板
                                        pasteboard.writeObjects_([ns_image])
                                        info_tag.send_keys(Keys.COMMAND, "v")
                                        time.sleep(0.5)
                                        # info_tag.send_keys(Keys.DOWN)
                                except:
                                    pass
                                if platform.system() == "Windows":
                                    pyperclip.copy("".join(info_txt))
                                    info_tag.send_keys(Keys.CONTROL, "v")
                                else:
                                    pasteboard = NSPasteboard.generalPasteboard()
                                    pasteboard.clearContents()
                                    pasteboard.writeObjects_(info_txt)
                                    info_tag.send_keys(Keys.COMMAND, "v")
                                time.sleep(0.5)
                                info_tag.send_keys(Keys.DOWN)
                                is_copy_content = True
                                img_idx += 1
                except:
                    pass

                print(is_copy_content, "is_copy_content")
                if is_copy_content:
                    print("投放广告赚收益")
                    tags = driver.find_elements(By.CLASS_NAME, "edit-input")
                    for i in tags:
                        time.sleep(1)
                        txt = i.text
                        if txt == "投放广告赚收益不投放广告":
                            try:
                                i.find_element(By.CLASS_NAME, "byte-radio-inner").click()
                            except:
                                pass
                        if "头条首发" in txt:
                            driver.execute_script("arguments[0].scrollIntoView();", i)
                            if "授权平台自动维权" not in txt:
                                try:
                                    i.find_element(
                                        By.CLASS_NAME, "byte-checkbox-wrapper"
                                    ).click()
                                except:
                                    pass
                        # if "发布得更多收益" in txt:
                        #     try:
                        #         checked = i.find_element(By.CLASS_NAME, "combine-tip-wrap")
                        #         child_elements = checked.find_element(By.TAG_NAME, "label")
                        #         class_name = child_elements.get_attribute("class")
                        #         if class_name == "byte-checkbox item-checkbox":
                        #             i.find_element(
                        #                 By.CLASS_NAME, "byte-checkbox-wrapper"
                        #             ).click()
                        #     except:
                        #         pass
                        if "个人观点" in txt:
                            try:
                                source = i.find_element(By.CLASS_NAME, "source-info-wrap")
                                labels = source.find_element(
                                    By.CLASS_NAME, "byte-checkbox-group"
                                )
                                child_elements = labels.find_elements(By.TAG_NAME, "label")
                                for info_e in child_elements:
                                    if info_e.text == "个人观点，仅供参考":
                                        class_name = info_e.get_attribute("class")
                                        if class_name == "byte-checkbox checkbot-item":
                                            info_e.find_element(
                                                By.CLASS_NAME, "byte-checkbox-wrapper"
                                            ).click()
                                            break
                                    # if info_e.text == "引用AI":
                                    #     class_name = info_e.get_attribute("class")
                                    #     if class_name == "byte-checkbox checkbot-item checkbox-with-tip":
                                    #         info_e.find_element(
                                    #                     By.CLASS_NAME, "byte-checkbox-wrapper"
                                    #                 ).click()
                                    #         break
                            except:
                                pass
                if is_copy_content:
                    if imgs_list_len == 0:
                        time.sleep(1)
                        tags = driver.find_elements(By.CLASS_NAME, "byte-tabs-header-title")
                        for item in tags:
                            for a in range(0, 5):
                                if "1" in item.text:
                                    item.click()
                                    time.sleep(2)
                                    driver.find_element(
                                        By.XPATH,
                                        '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/div[2]/ul/li[1]',
                                    ).click()
                                    publish_flag = True
                                    time.sleep(2)
                                    break
                                elif "2" in item.text:
                                    item.click()
                                    time.sleep(2)
                                    driver.find_element(
                                        By.XPATH,
                                        '//*[@id="root"]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/ul/li[1]',
                                    ).click()
                                    publish_flag = True
                                    time.sleep(2)
                                    break
                                elif "内容建议" in item.text:
                                    item.click()
                                    driver.find_element(
                                        By.XPATH,
                                        '//*[@id="root"]/div/div[2]/div[2]/div/div/div/div[2]/div/div[2]/div/div/div[1]/div/a',
                                    ).click()
                                    time.sleep(5)
                                else:
                                    pass
                    else:
                        publish_flag = True
                print("publish_flag:", publish_flag)
                if publish_flag:
                    try:
                        driver.find_element(By.CLASS_NAME, "publish-btn-last").click()
                        time.sleep(3)
                        driver.find_element(By.CLASS_NAME, "publish-btn-last").click()
                        out_flag = True
                        time.sleep(3)
                    except:
                        pass
                end_time = time.time()
                if out_flag:
                    result["status"] = True
                    break
                elif end_time - tart_time > time_out:
                    break
                else:
                    is_copy_content = False
                    out_flag = False
                    publish_flag = False
                    driver.refresh()
                    time.sleep(3)
            driver.delete_all_cookies()
            driver.quit()
            time.sleep(3)
            self.close_chrome_tab(random_number)
            try:
                time.sleep(3)
                shutil.rmtree(user_data_dir)
            except:
                pass
            return result
        elif platform_ == "百家号":
            driver = self.get_driver()
            url = urls[platform_]
            driver.get(url)
            driver.delete_all_cookies()
            time.sleep(1)
            try:
                for ck in cookie:
                    driver.add_cookie(ck)
            except Exception as e:
                print(e)
            driver.get(url)
            res = publish_baijiahao(driver, content, imgs_path)
            return res
        elif platform_ == "微信公众号":
            driver = self.get_driver()
            url = urls[platform_]
            driver.get(url)
            # driver.delete_all_cookies()
            time.sleep(1)
            try:
                for ck in cookie:
                    driver.add_cookie(ck)
            except Exception as e:
                print(e)
            time.sleep(2)
            driver.get(url)
            res = publish_weixin(driver, content, imgs_path)
            return res
        elif platform_ == "企鹅号":
            driver = self.get_driver()
            url = urls[platform_]
            driver.get(url)
            driver.delete_all_cookies()
            time.sleep(1)
            try:
                for ck in cookie:
                    driver.add_cookie(ck)
            except Exception as e:
                print(e)
            driver.get(url)
            res = publish_qiehao(driver, content, imgs_path)
            return res

    def get_acconut_data(self, cookie, platform_):
        urls = {"头条号": "https://mp.toutiao.com/profile_v4/index",
                "百家号": "https://baijiahao.baidu.com/builder/rc/analysiscontent",
                "微信公众号":"https://mp.weixin.qq.com",
                "企鹅号":"https://om.qq.com/main"
                }
        driver = self.get_driver()
        driver.get(urls[platform_])
        driver.delete_all_cookies()
        try:
            for ck in cookie:
                driver.add_cookie(ck)
        except Exception as e:
            print(e)
        driver.get(urls[platform_])
        time.sleep(60*30)
        return driver


if __name__ == "__main__":
    a = AutoTools()
