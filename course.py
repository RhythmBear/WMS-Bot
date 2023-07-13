class Course:

    def __init__(self):
        self.course_name = ""
        self.course_url = ""
        self.has_materials = False
        self.number_of_lessons = 0
        self.list_of_lessons = []
        self.results = []

    def to_json(self):
        return {
            "course_name": self.course_name,
            "course_url": self.course_url,
            "has_materials": self.has_materials,
            "lesson_count": self.number_of_lessons,
            "lessons": self.list_of_lessons,
            "results": self.results
        }

    def __repr__(self):
        return f"{self.course_id} - {self.course_name}"


class Lesson:

    def __init__(self):
        self.lesson_number = 0
        self.name = ""
        self.course_name = ""
        self.lesson_url = ""
        self.is_wistia = True
        self.youtube_url = ""
        self.has_materials = False

    def to_json(self):
        return {
            "name": self.name,
            "lesson_number": self.lesson_number,
            "parent_course": self.course_name,
            "lesson_url": self.lesson_url,
            "is_wistia": self.is_wistia,
            "youtube_url": self.youtube_url,
            "has_materials": self.has_materials
        }

    def __repr__(self):
        return f"{self.course_name} - {self.name}_{self.lesson_number}"
