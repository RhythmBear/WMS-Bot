from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, NoSuchFrameException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ActionChains
import time
import os
from dotenv import load_dotenv
import pickle
from course import Course, Lesson
import json

load_dotenv()


class WmsBot:

    def __init__(self):
        self.username = os.getenv("WMS_USERNAME")
        self.password = os.getenv("WMS_PASSWORD")
        self.course_page = "https://worshipministryschool.com/course-library/"
        self.course_url = "https://worshipministryschool.com/courses"
        self.user_profile = ""

        # Initialize Chrome Driver
        self.driver = self.initialize_chrome_driver()
        self.action = ActionChains(self.driver)

    def login_to_website(self):
        # Try to load cookies first
        try:
            print("Loading cookies..")
            self.load_cookie_session()

        except FileNotFoundError:
            print("Cookies not found...")

            print("Attempting to login...")
            # Open the login page
            self.driver.get("https://worshipministryschool.com/wp-login.php")
            time.sleep(5)

            # Enter Username
            self.driver.find_element(By.XPATH, '//input[@name="log"]').send_keys(self.username)
            time.sleep(1)

            # Enter Password
            self.driver.find_element(By.XPATH, '//input[@name="pwd"]').send_keys(self.password)
            time.sleep(1)

            # Click remember me button
            self.driver.find_element(By.XPATH, '//input[@name="rememberme"]').click()
            time.sleep(1)

            # Click Submit button
            self.driver.find_element(By.XPATH, '//input[@name="wp-submit"]').click()

            time.sleep(10)
            # Attempt to save cookies
            self.save_cookie_session()

    @staticmethod
    def initialize_chrome_driver():
        # Chrome driver path
        driver_path = "chromedriver.exe"

        # Create Chrome options instance
        options = Options()

        # Add My chrome profile
        # options.add_argument(r"--user-data-dir=C:\\Users\\Windows\\AppData\\Local\\Google\\Chrome\\User Data")
        # options.add_argument(r'--profile-directory=Default')
        options.add_argument("--start-maximized")

        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Load Extensions
        options.add_extension(r"downloader_extension.crx")
        options.add_extension(r"vimeo_extension.crx")

        # Exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)

        # Run in the headless browser
        options.headless = False

        # Setting the driver path and requesting a page
        driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)

        # Changing the property of the navigator value for webdriver to undefined
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def save_cookie_session(self):
        # Save the cookie session id
        pickle.dump(self.driver.get_cookies(), open("wms_cookies.pkl", "wb"))
        print("cookies saved successfully")

    def load_cookie_session(self):
        # load Cookies from saved session
        cookies = pickle.load(open("wms_cookies.pkl", "rb"))

        for cookie in cookies:
            self.driver.add_cookie(cookie)
        print("Loaded cookies from previous session...")

    def open_website(self):
        self.driver.get(self.course_page)

        time.sleep(6)

    def get_all_courses(self):
        # Check to make sure the courses.json file exists
        if not os.path.exists("courses.json"):

            # If it does not exist then get the courses list.
            courses_list = []

            self.open_website()
            courses = self.driver.find_elements(By.XPATH, '//ul[@class="bb-card-list bb-course-items grid-view bb-grid"]/li[@class="bb-course-item-wrap"]')

            # loops through all the courses and pulls the data one needs.
            for course in courses:
                name = course.find_element(By.TAG_NAME, 'a').get_attribute('title')
                url = course.find_element(By.TAG_NAME, 'a').get_attribute('href')
                number_of_lessons = course.find_element(By.CLASS_NAME, 'course-lesson-count').text
                lessons = int(number_of_lessons.split(' ')[0])

                courses_list.append({'name': name, 'url': url, 'lessons': lessons})

            with open('courses.json', 'w', encoding='utf-8') as f:
                json.dump(courses_list, f)

            return True
        else:
            return True

    def scrape_course(self, course_dict: dict):
        new_course = Course()

        new_course.course_name = course_dict['name']
        new_course.number_of_lessons = course_dict['lessons']
        new_course.course_url = course_dict['url']
        new_course.has_materials = self.has_materials()

        self.driver.get(course_dict['url'])

        course_contents = self.get_all_lessons(course_dict['url'])
        new_course.list_of_lessons = course_contents

        return new_course

    def get_all_lessons(self, course_url):
        print(f"Getting Lessons for {course_url}")
        time.sleep(5)
        self.driver.get(course_url)
        lessons_json = []

        lessons = self.driver.find_elements(By.XPATH, '//div[@class="ld-item-list-item-preview"]')

        for lesson in lessons:
            lesson_title = lesson.find_element(By.TAG_NAME, 'span').text
            lesson_url = lesson.find_element(By.TAG_NAME, 'a').get_attribute('href')

            lessons_json.append({'lesson_name': lesson_title, 'lesson_url': lesson_url})

        return lessons_json

    def has_materials(self):
        try:
            materials_tab_exists = self.driver.find_element(By.XPATH, '//span[@class="ld-icon ld-icon-materials"]')

        except NoSuchElementException:
            return False

        else:
            return True

    def get_materials(self, lesson_name):

        # Check for the materials tab and click it.
        materials_tab = self.driver.find_element(By.XPATH, '//span[@class="ld-icon ld-icon-materials"]')
        materials_tab.click()

        time.sleep(3)
        # Get Materials Div
        materials = self.driver.find_element(By.XPATH, '//div[@aria-labelledby="materials"]')

        # Specify the file path to the HTML file
        # remove every space in the name to ensure the html file has no spaces
        file_name_1 = lesson_name.replace(" ", "").replace("'", "").replace('.', '').replace('/', '').replace('\\', '')

        # This checks to make sure the file name is not greater than 15 characters.
        file_name = file_name_1[:15] if len(file_name_1) > 15 else file_name_1

        file_path = rf"C:\Users\Windows\Downloads\{file_name}_links.html"

        # Iterate through the elements and append their HTML code to the file
        with open(file_path, "w", encoding="utf-8") as html_file:
            # Write the heading to the file
            heading = f"<h1>{lesson_name}</h1> <br>"
            html_file.write(heading + "\n")

            html_code = materials.get_attribute("outerHTML")
            html_file.write(html_code + "\n")

    def is_video_wistia(self):
        # Check if the video is hosted by wistia

        try:
            download_button = self.driver.find_element(By.XPATH, '//button[@title="Wistia Video Downloader"]')
        except NoSuchElementException:
            print("Failed to locate Wistia download button\n")
            return False

    def is_video_vimeo(self):
        # Try to locate the vimeo download button
        time.sleep(3)
        try:
            #Switch to frame
            frame = self.driver.find_element(By.XPATH, '//iframe[@name="fitvid0"]')
            self.driver.switch_to.frame(frame)

            download_button = self.driver.find_element(By.XPATH, '//button[@class="ext_dl-button rounded-box"]')
        except (NoSuchElementException, NoSuchFrameException):
            return False

        else:
            return True

    def download_vimeo_video(self):
        # Look for the Download button and click on the 720p option

        self.driver.find_element(By.XPATH, '//button[@class="ext_dl-button rounded-box"]').click()
        time.sleep(3)

        # Click on the 720 Video resolution button
        try:
            download_720 = self.driver.find_element(By.XPATH, '//a[@data-quality="720"]')
            download_720.click()
        except NoSuchElementException:
            print("failed to located button the first time. retrying...")
            time.sleep(3)
            download_720 = self.driver.find_element(By.XPATH, '//a[@data-quality="720"]')
            download_720.click()

        self.driver.switch_to.default_content()

    def is_video_youtube(self):

        try:
            video_youtube = self.driver.find_element(By.XPATH, '//a[@class="ytp-impression-link"]').get_attribute('href')

        except NoSuchElementException:
            print("Failed to locate Youtube download button.\n")
            return None

        else:
            return video_youtube

    def download_scrape_lesson(self, lesson_url, quality: int, download: str):
        self.driver.get(lesson_url)
        time.sleep(3)

        # Create Lesson object and get attributes from site
        new_lesson = Lesson()

        new_lesson.lesson_url = lesson_url
        new_lesson.name = self.driver.find_element(By.TAG_NAME, 'h1').text
        new_lesson.lesson_number = self.driver.find_element(By.XPATH, '//span[@class="bb-pages"]').text
        new_lesson.course_name = self.driver.find_element(By.XPATH, '//h2[@class="course-entry-title"]').text
        new_lesson.has_materials = self.has_materials()

        # Find the download button, if found click on it and return the lesson object.
        try:
            time.sleep(5)
            download_button = self.driver.find_element(By.XPATH, '//button[@title="Wistia Video Downloader"]')
        except NoSuchElementException:
            print("Failed to locate Wistia download Button...")
            new_lesson.is_wistia = False
            new_lesson.youtube_url = self.is_video_youtube()

            # Since the video is not a YouTube or wisita video check to see if the video is vimeo
            if self.is_video_vimeo():
                print("Successfully found vimeo video")
                time.sleep(1)

            self.download_vimeo_video()
            print(f"Downloading {new_lesson.course_name}...")

            if self.has_materials():
                self.get_materials(new_lesson.name)
            return new_lesson

        else:
            new_lesson.is_wistia = True
            time.sleep(5)

            # Change quality to 540 pixels
            self.action.move_to_element(download_button).perform()

            # try:
            #     self.driver.find_element(By.XPATH, '//button[@title="Pick resolution"]').click()
            # except ElementNotInteractableException:
            #     time.sleep(3)
            #     self.driver.find_element(By.XPATH, '//button[@title="Pick resolution"]').click()
            #
            # # Click the right resolution button
            # self.driver.find_element(By.XPATH, f'//li[@data-type="{quality}p"]/span[@role="checkbox"]').click()

            if download == 'yes':
                download_button.click()
                print(f"Downloading --> {new_lesson.course_name} - {new_lesson.name}  ...")
                time.sleep(2)

                if self.has_materials():
                    self.get_materials(new_lesson.name)

            return new_lesson
