from playwright.sync_api import sync_playwright
import time

def save_weibo_login_state():
    """
    使用 Playwright 打开微博登录页面，等待用户手动登录，
    登录成功后保存登录状态到 weibo_state.json
    """
    with sync_playwright() as playwright:
        # 启动浏览器，设置为非无头模式以便手动登录
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 打开微博登录页
        page.goto("https://passport.weibo.com/sso/signin?entry=miniblog&source=miniblog")
        print("请在打开的浏览器窗口中手动登录微博...")
        
        # 等待用户登录成功，检测登录后才会出现的元素
        try:
            # 等待发微博输入框出现，这个元素只有在登录后才会显示
            page.wait_for_selector('textarea[placeholder="有什么新鲜事想分享给大家？"]', timeout=120000)  # 2分钟超时
            print("检测到登录成功，等待5秒确保所有状态保存...")
            time.sleep(5)
            
            # 保存登录状态
            context.storage_state(path='weibo_state.json')
            print("登录状态已保存到 weibo_state.json")
        except Exception as e:
            print("登录超时或发生错误:", str(e))
        finally:
            # 关闭浏览器
            page.close()
            context.close()
            browser.close()

if __name__ == "__main__":
    save_weibo_login_state()
