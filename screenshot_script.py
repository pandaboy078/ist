import asyncio
from playwright.async_api import async_playwright
import os
import subprocess
import time

async def main():
    # Ensure images directory exists
    os.makedirs("images", exist_ok=True)
    
    # Start the flask app
    app_process = subprocess.Popen(["python3", "app.py"])
    time.sleep(5)  # wait for server to start

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a large viewport to capture nice dashboards
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(2000)

        # 1. Landing Page
        await page.screenshot(path="images/1_Landing_Page.jpeg", type="jpeg", quality=90)
        
        # Click "Enter Dashboard"
        await page.click("#lp-hero-enter")
        await page.wait_for_timeout(2000)

        # 2. Dashboard Overview
        await page.screenshot(path="images/2_Dashboard_Overview.jpeg", type="jpeg", quality=90)

        # 3. Key Metrics Page (Scroll down slightly in Dashboard)
        await page.evaluate("window.scrollBy(0, 500)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/3_Key_Metrics.jpeg", type="jpeg", quality=90)

        # 10. Dataset Overview
        await page.click("button[data-section='about']")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="images/10_Dataset_Overview.jpeg", type="jpeg", quality=90)

        # Go to Results
        await page.click("button[data-section='results']")
        await page.wait_for_timeout(3000)  # Wait for charts to render
        
        # 4. Sampling Comparison Results
        await page.screenshot(path="images/4_Sampling_Comparison.jpeg", type="jpeg", quality=90)

        # 5. ML Model Comparison (Scroll down a bit)
        await page.evaluate("window.scrollBy(0, 400)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/5_ML_Model_Comparison.jpeg", type="jpeg", quality=90)

        # 6. Final Verdict
        await page.evaluate("window.scrollBy(0, 400)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/6_Final_Verdict.jpeg", type="jpeg", quality=90)

        # 9. R2, MAE, RMSE Results Page (Click the table tab)
        await page.click("button[data-target='viz-table']")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/9_R2_MAE_RMSE_Results.jpeg", type="jpeg", quality=90)

        # Go to SDG Sustainability Page
        await page.click("button[data-section='sdg']")
        await page.wait_for_timeout(2000)

        # 7. Green Dot Ball Sustainability Page
        await page.screenshot(path="images/7_Sustainability_Page.jpeg", type="jpeg", quality=90)

        # 8. Trees Planted / Sustainability Impact Chart (Scroll down)
        await page.evaluate("window.scrollBy(0, 400)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/8_Trees_Planted_Impact.jpeg", type="jpeg", quality=90)
        
        await browser.close()
    
    # Terminate the flask app
    app_process.terminate()
    print("Done generating screenshots.")

if __name__ == "__main__":
    asyncio.run(main())
