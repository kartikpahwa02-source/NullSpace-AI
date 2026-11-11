from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import BROWSER_HEADLESS, BROWSER_TIMEOUT
import time
import os

_driver = None


def get_driver():
    global _driver
    try:
        # Check if existing driver still alive
        if _driver:
            try:
                _driver.title
                return _driver
            except Exception:
                try:
                    _driver.quit()
                except Exception:
                    pass
                _driver = None

        options = Options()
        if BROWSER_HEADLESS:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")

        service = Service(ChromeDriverManager().install())
        _driver = webdriver.Chrome(service=service, options=options)
        _driver.implicitly_wait(BROWSER_TIMEOUT)
        return _driver

    except Exception as e:
        _driver = None
        raise Exception(f"Browser start error: {e}")


def close_driver():
    global _driver
    if _driver:
        try:
            _driver.quit()
        except Exception:
            pass
        _driver = None


def _fix_url(url):
    """URL ko sahi format me convert karo"""
    url = url.strip()

    if not url:
        return "https://www.google.com"

    # Agar search query hai (space hai)
    if " " in url and "." not in url:
        return f"https://www.google.com/search?q={url.replace(' ', '+')}"

    # Agar http/https nahi hai
    if not url.startswith("http://") and not url.startswith("https://"):
        # Agar www. nahi hai aur dot hai
        if "." in url:
            if not url.startswith("www."):
                url = "www." + url
        else:
            # Search term hai
            return f"https://www.google.com/search?q={url.replace(' ', '+')}"

    if not url.startswith("http"):
        url = "https://" + url

    return url


def browse_open(url):
    try:
        d = get_driver()
        url = _fix_url(url)
        d.get(url)
        time.sleep(2)
        title = d.title
        return f"Website khul gaya!\nTitle: {title}\nURL: {d.current_url}"
    except Exception as e:
        return f"Browser Error: {e}"


def browse_content():
    try:
        d = get_driver()
        text = d.find_element(By.TAG_NAME, "body").text
        return text[:3000] if text else "Page empty hai"
    except Exception as e:
        return f"Content Error: {e}"


def browse_click_text(text):
    try:
        d = get_driver()
        element = d.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
        element.click()
        time.sleep(2)
        return f"Click ho gaya: '{text}'"
    except Exception as e:
        return f"Click Error: {e}"


def browse_click_css(selector):
    try:
        d = get_driver()
        element = WebDriverWait(d, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.click()
        time.sleep(2)
        return f"Click ho gaya: {selector}"
    except Exception as e:
        return f"Click Error: {e}"


def browse_type_text(selector, text):
    try:
        d = get_driver()
        element = d.find_element(By.CSS_SELECTOR, selector)
        element.clear()
        element.send_keys(text)
        return f"Type ho gaya: '{text}'"
    except Exception as e:
        return f"Type Error: {e}"


def browse_type_and_enter(selector, text):
    try:
        d = get_driver()
        element = d.find_element(By.CSS_SELECTOR, selector)
        element.clear()
        element.send_keys(text + Keys.RETURN)
        time.sleep(3)
        return f"Typed '{text}' + Enter pressed"
    except Exception as e:
        return f"Type Error: {e}"


def browse_search_google(query):
    try:
        d = get_driver()
        d.get(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        time.sleep(3)

        results = []
        try:
            search_results = d.find_elements(By.CSS_SELECTOR, "div.g")
            for el in search_results[:5]:
                try:
                    title_el = el.find_element(By.TAG_NAME, "h3")
                    title = title_el.text
                    snippet = ""
                    try:
                        snippet_el = el.find_element(By.CSS_SELECTOR, "div[style*='line'], span.st, div.VwiC3b")
                        snippet = snippet_el.text
                    except Exception:
                        pass
                    if title:
                        results.append(f"- {title}\n  {snippet}")
                except Exception:
                    continue
        except Exception:
            pass

        if results:
            return "Google Results:\n" + "\n".join(results)
        else:
            return f"Google search complete: {query}\nURL: {d.current_url}"

    except Exception as e:
        return f"Search Error: {e}"


def browse_scroll(direction="down"):
    try:
        d = get_driver()
        amount = 500 if direction == "down" else -500
        d.execute_script(f"window.scrollBy(0, {amount})")
        time.sleep(1)
        return f"Scrolled {direction}"
    except Exception as e:
        return f"Scroll Error: {e}"


def browse_screenshot():
    try:
        d = get_driver()
        path = os.path.join("uploads", "browser_screen.png")
        d.save_screenshot(path)
        return f"Browser screenshot saved: {path}"
    except Exception as e:
        return f"Screenshot Error: {e}"