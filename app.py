from flask import Flask, render_template, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_code', methods=['GET'])
def get_code():
    try:
        with sync_playwright() as p:
            # فتح المتصفح في الخلفية (بدون واجهة)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # فتح موقع Unlockr
            page.goto("https://web.unlockr.app", wait_until="networkidle", timeout=15000)
            
            # استنى 3.5 ثانية عشان الكود يتولد
            page.wait_for_timeout(3500)
            
            # محاولة سحب النص اللي شكله كود (5 أو 6 حروف/أرقام)
            # بناءً على الصورة، الكود غالباً في عنصر h1 أو div كبير
            code_element = page.locator("text=/^[A-Z0-9]{5,6}$/").first
            
            if code_element.count() > 0:
                code_text = code_element.inner_text()
                browser.close()
                return jsonify({"success": True, "code": code_text})
            else:
                # لو ملقاش النص، نرجع أول نص طويل شكله كود
                browser.close()
                return jsonify({"success": False, "error": "مقدرتش ألاقي الكود، ممكن الموقع غير شكله."})
                
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
