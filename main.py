import selenium
from bot import WmsBot
import time
import json
from course import Course

# Create Worship Ministry School Bot
bot = WmsBot()

# Open WMS website
bot.open_website()

# Login to website
bot.login_to_website()

# Scrape all courses
bot.get_all_courses()

# Open Courses json
with open("courses.json", 'r') as file:
    data = json.load(file)
    # print(data)


# Collect User input to get the course to scrape
course_exists = False
course_index = 0

while not course_exists:
    course_to_scrape = input("What Course do you want to download from worship ministry online? \n--> ")

    for index, course in enumerate(data):
        if course_to_scrape == course['name']:
            course_exists = True
            course_index = index



    print(f"Successfully located {course_to_scrape}" if course_exists else
          f"{course_to_scrape} is not a valid course. Please Try again!\n")


number = int(input("\nWhere do you want to start downloading from? e.g 1 from the start --> \n"))
yes_no = input("\nDo you want to download or just scrape details? yes to download, no to scrape? -->\n")
quality = int(input("\nWhat quality do you want to download? e.g 720, 540, 1080 e.t.c? --> \n"))
waiting_time = int(input("\nHow long to wait in between downloads? --> \n"))

# Scrape course
scraped_course = bot.scrape_course(data[course_index])
print(f"Downloading Lessons from {scraped_course.course_name}")

# Download each video
for lesson in scraped_course.list_of_lessons[number:]:
    print(f"\nAttempting to download {lesson['lesson_name']}...")
    time.sleep(2)
    download_result = bot.download_scrape_lesson(lesson_url=lesson['lesson_url'],
                                                 quality=quality,
                                                 download=yes_no)

    scraped_course.results.append(download_result.to_json())

    time.sleep(waiting_time)

# After download, Create a json file for the result
with open(f'results/{scraped_course.course_name}.json', 'w') as f:
    print(f"Creating json dump for {scraped_course.course_name}")
    json.dump(scraped_course.to_json(), f)
    print(f"Successfully created Json dump for {scraped_course.course_name}")

time.sleep(1000)
