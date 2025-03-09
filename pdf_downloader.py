import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def setup_download_directory(directory_path):
    """Create download directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path

def configure_browser(download_directory):
    """Configure Chrome browser with custom download directory"""
    chrome_options = Options()
    
    # Set download directory
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # Don't open PDFs in browser
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Optional: Run headless (no UI)
    # chrome_options.add_argument("--headless")  # Uncomment to run without browser UI
    
    return webdriver.Chrome(options=chrome_options)

def download_pdfs_from_cambridge_moodle(url, download_directory):
    """Download all PDFs from Cambridge Moodle website"""
    # Setup
    download_dir = setup_download_directory(download_directory)
    driver = configure_browser(download_dir)
    
    try:
        # Navigate to the website
        print(f"Accessing {url}...")
        driver.get(url)
        
        # Get all course links
        course_buttons = driver.find_elements(By.CLASS_NAME, "course-btn")
        course_ids = []
        
        # Extract course IDs
        for button in course_buttons:
            onclick_attr = button.get_attribute("onclick")
            if onclick_attr and "showCourse" in onclick_attr:
                # Extract course ID from showCourse('4f13')
                course_id = onclick_attr.split("'")[1]
                course_ids.append(course_id)
        
        print(f"Found {len(course_ids)} courses: {', '.join(course_ids)}")
        
        # Iterate through each course
        for course_id in course_ids:
            # Navigate to course page
            print(f"\nNavigating to course {course_id}...")
            course_button = driver.find_element(By.XPATH, f"//a[@onclick=\"showCourse('{course_id}'); return false;\"]")
            course_button.click()
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, f"{course_id}-page"))
            )
            
            # Check if there are active download buttons (files that have been uploaded)
            active_downloads = driver.find_elements(By.CLASS_NAME, "active-download")
            
            if active_downloads:
                print(f"Found {len(active_downloads)} downloadable files in course {course_id}")
                
                # Click each active download button
                for download_btn in active_downloads:
                    button_id = download_btn.get_attribute("id")
                    file_type = "coursework" if "course-download" in button_id else "example paper"
                    print(f"  Downloading {file_type} from {course_id}...")
                    
                    # Click the download button
                    download_btn.click()
                    
                    # Wait briefly to ensure download begins
                    time.sleep(1)
            else:
                print(f"No downloadable files found in course {course_id}")
            
            # Return to home page
            back_button = driver.find_element(By.XPATH, "//a[contains(@class, 'back-btn')]")
            back_button.click()
            
            # Wait for home page to load
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "home-page"))
            )
            
        print(f"\nAll downloads complete. Files saved to: {download_dir}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Give time for downloads to complete
        print("Waiting for downloads to complete...")
        time.sleep(5)
        
        # Close the browser
        driver.quit()

if __name__ == "__main__":


    url = "Moodle.html"  
    # Directory to save downloaded PDFs
    download_directory = os.path.join(os.path.expanduser("~"), "Downloads", "Cambridge_PDFs")
    
    download_pdfs_from_cambridge_moodle(url, download_directory)