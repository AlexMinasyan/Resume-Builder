# MARK: Setup
from fpdf import FlexTemplate, FPDF
import json
from pprint import pprint

pdf = FPDF(orientation = 'portrait', format = 'A4')
pdf.add_page()
pdf.add_font('dejavu-sans-mono', style = '', fname = 'dejavu-sans-mono/DejaVuSansMono.ttf')

# Some Specs for this Template
# Work Experiences: 4, Projects: 4, Educational Institutions: 2, 
# Work Bullet Points (Total): 12, Educational Bullet Points (Total): 6

# MARK: Assiting Extensions
def standard_date_string_to_alternate(date_str) -> str:
    if (date_str == 'PRESENT'):
        return date_str
    # The default format is MM/YYYY
    components = date_str.split('/')
    # Returns [MMM, YY]
    return f'{standard_date_string_to_components(date_str)[0]} {standard_date_string_to_components(date_str)[1]}'

def standard_date_string_to_components(date_str) -> list:
    # The default format is MM/YYYY
    components = date_str.split('/')
    # Returns [MMM, YY]
    return [month_num_to_3char(components[int(0)]), int(components[1][2:4])]

def month_num_to_3char(mon) -> str:
    return ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'][int(mon) - 1]

# Returns a single number composed of YYMM for the purposes of sorting
def date_components_for_sort(date_str) -> int:
    components = date_str.split('/')
    return int(components[1][2:4] + components[0])

with open(f'User Data/admin_info_english.json') as f:
    user_data = json.loads(f.read())

# MARK: Important Aspect Class
class ImportantAspect:
    def __init__(self, start_x, start_y):
        self.start_x, self.start_y = (start_x, start_y)

    # Returns the PDF Element objects
    def get_generated_elements(self, experience_number) -> list:
        end_date_box_obj = {
            'name': f'end_date_box_{experience_number}', 'type': 'B', 'x1': self.start_x + 10, 'x2': self.start_x + 28, 'y1': self.start_y, 'y2': self.start_y + 5, 
            'font': 'dejavu-sans-mono', 'size': 0.3, 'align': 'C', 'priority': 0
        }
        end_date_text_obj = {
            'name': f'end_date_box_text_{experience_number}', 'type': 'T', 'x1': self.start_x + 10, 'x2': self.start_x + 28, 'y1': self.start_y + 1, 'y2': self.start_y + 4.5, 
            'font': 'helvetica', 'size': 9, 'align': 'C', 'priority': 1, 'text': f'{standard_date_string_to_alternate(self.end_date)}'
        }
        title_obj = {
            'name': f'experience_title_{experience_number}', 'type': 'T', 'x1': self.start_x + 16, 'x2': 210, 'y1': self.start_y + 6, 'y2': self.start_y + 12, 
            'font': 'helvetica', 'size': 16, 'text': self.title 
        }
        company_obj = {
            'name': f'experience_company_{experience_number}', 'type': 'T', 'x1': self.start_x + 16, 'x2': 210, 'y1': self.start_y + 11, 'y2': self.start_y + 16, 
            'font': 'helvetica', 'size': 12, 'text': self.company
        }
        
        task_achievement_objs = []
        for i, task in enumerate(self.tasks_achievements):
            task_achievement_objs.append(
                {
                    'name': f'experience_{experience_number}_point_{i + 1}', 'type': 'T', 'x1': self.start_x + 20, 'x2': 210, 'y1': self.start_y + 16 + (i * 4), 'y2': self.start_y + 19 + (i * 4), 
                    'font': 'helvetica', 'size': 8, 'text': f' - {task}'
                    }
                )

        bullet_points = len(task_achievement_objs)
        start_date_box_obj = {
            'name': f'start_date_box_{experience_number}', 'type': 'B', 'x1': self.start_x + 10, 'x2': self.start_x + 28, 'y1': self.start_y + 16 + (4 * bullet_points), 'y2': self.start_y + 21 + (4 * bullet_points), 
            'font': 'helvetica', 'size': 0.3, 'align': 'C', 'priority': 0
        }
        start_date_text_obj = {
            'name': f'start_date_box_text_{experience_number}', 'type': 'T', 'x1': self.start_x + 10, 'x2': self.start_x + 28, 'y1': self.start_y + 17 + (4 * bullet_points), 'y2': self.start_y + 20.5 + (4 * bullet_points),
            'font': 'dejavu-sans-mono', 'size': 9, 'align': 'C', 'priority': 1, 'text': f'{standard_date_string_to_alternate(self.start_date)}'
        }
        timeline_obj = {
            'name': f'timeline_{experience_number}', 'type': 'L', 'x1': self.start_x + 14, 'x2': self.start_x + 14, 'y1': self.start_y + 5, 'y2': self.start_y  + 16 + (4 * bullet_points), 
            'size': 0.3
        }

        return [end_date_box_obj, end_date_text_obj, title_obj, company_obj] + task_achievement_objs + [start_date_box_obj, start_date_text_obj, timeline_obj]
    
    # Returns the height of the PDF Object Group
    def get_cumulative_height(self) -> int:
        bullet_points = len(self.tasks_achievements)
        return 21 + (4 * bullet_points)

# MARK: Edu Class
class EducationalInstitution(ImportantAspect):
    # Initializer
    def __init__(self, education_object, start_x, start_y):
        self.start_x, self.start_y = (start_x, start_y)

        self.title = education_object['name']
        self.company = education_object['degree']
        self.tasks_achievements = education_object['courses-important']
        self.start_date = education_object['start-date']
        self.end_date = education_object['end-date']
        
# MARK: Work Class
class WorkExperience(ImportantAspect):
    # Initializer
    def __init__(self, work_object, start_x, start_y):
        self.start_x, self.start_y = (start_x, start_y)

        self.title = work_object['title']
        self.company = work_object['name']
        self.tasks_achievements = work_object['tasks-achievements']
        self.start_date = work_object['start-date']
        self.end_date = work_object['end-date']

# MARK: Project Class
class Project:
    # Initializer
    def __init__(self, project_object, start_x, start_y):
        self.start_x, self.start_y = (start_x, start_y)

        self.name = project_object['name']
        self.start_date = project_object['start-date']
        self.end_date = project_object['end-date']
        self.description = project_object['description']

    # Returns the PDF Element objects
    def get_generated_elements(self, project_number) -> list:
        project_name = {'name': f'project_name_{project_number}', 'type': 'T', 'x1': self.start_x + 8, 'x2': self.start_x + 105,
                        'y1': self.start_y, 'y2': self.start_y + 5, 'font': 'helvetica', 'size': 11, 'text': self.name}
        project_description = {'name': f'project_description_{project_number}', 'type': 'T', 'x1': self.start_x + 8, 
                               'x2': self.start_x + 80, 'y1': self.start_y + 5, 'y2': self.start_y + 8, 
                               'font': 'helvetica', 'size': 8, 'multiline': True, 'text': self.description }
        
        return [project_name, project_description]
        
    # Returns the height of the PDF Object Group
    def get_cumulative_height(self) -> int:
        return 12
    
# MARK: Skill Class
class Skill:
    # Initializers
    def __init__(self, skill_object, start_x = 0, start_y = 0):
        self.start_x, self.start_y = (start_x, start_y)

        self.name = skill_object['name']
        self.category = skill_object['category']

    def get_generated_elements(self, skill_number) -> list:
        str_len = len(self.name)
        skill_box = { 'name': f'skill_box_{skill_number}', 'type': 'B', 'x1': self.start_x, 
                     'x2': self.start_x + (1.7 * str_len) + 1.9, 'y1': self.start_y, 'y2': self.start_y + 5 }
        skill_text = { 'name': f'skill_text_{skill_number}', 'type': 'T', 'x1': self.start_x, 'x2': self.start_x + 20,
                     'y1': self.start_y, 'y2': self.start_y + 5, 'font': 'dejavu-sans-mono', 'size': 8, 'text': self.name}
        
        return [skill_box, skill_text]
    
    def get_width(self) -> int:
        return (1.7 * len(self.name)) + 1.9
    
# MARK: Language Class
class Language:
    # Initializers
    def __init__(self, language_object, start_x = 0, start_y = 0):
        self.start_x, self.start_y = (start_x, start_y)

        self.name = language_object['name']
        self.level = language_object['level']
    
    def get_generated_elements(self, language_number) -> list:
        language_name = { 'name': f'language_name_{language_number}', 'type': 'T', 'x1': self.start_x, 
                     'x2': 50, 'y1': self.start_y, 'y2': self.start_y + 5, 
                     'font': 'helvetica', 'size': 10, 'text': self.name }
        language_proficiency = { 'name': f'language_proficiency_{language_number}', 'type': 'T', 'x1': self.start_x + 2, 'x2': 50,
                     'y1': self.start_y + 5, 'y2': self.start_y + 9, 'font': 
                     'helvetica', 'size': 8, 'text': self.level }
        
        return [language_name, language_proficiency]
    
    def get_cumulative_height(self) -> int:
        return 9
    

# MARK: Concrete Parts
work_x = 50
elements_part_1 = [
    {'name': 'sideborder', 'type': 'L', 'x1': 50, 'x2': 50, 'y1': 0, 'y2': 297},

    {'name': 'name', 'type': 'T', 'x1': 1, 'x2': 49, 'y1': 5, 'y2': 17, 'font': 'dejavu-sans-mono', 'size': 24, 'multiline': True, 'align': 'L'},

    {'name': 'professional_summary', 'text': 'Professional Summary', 'type': 'T', 'x1': 1, 'x2': 49, 'y1': 33, 'y2': 39, 'font': 'helvetica', 'size': 13, 'multiline': False, 'align': 'L', 'underline': 1},
    {'name': 'bio', 'type': 'T', 'x1': 1, 'x2': 49, 'y1': 41, 'y2': 45, 'font': 'helvetica', 'size': 9, 'multiline': True, 'align': 'L'},

    {'name': 'contact', 'type': 'T', 'text': 'Contact', 'x1': 1, 'x2': 49, 'y1': 60, 'y2': 66, 'font': 'helvetica', 'size': 13, 'multiline': False, 'align': 'L', 'underline': 1},
    {'name': 'email', 'type': 'T', 'x1': 1, 'x2': 49, 'y1': 68, 'y2': 72, 'font': 'helvetica', 'size': 9, 'multiline': False, 'align': 'L'},
    {'name': 'phone', 'type': 'T', 'x1': 1, 'x2': 49, 'y1': 74, 'y2': 78, 'font': 'helvetica', 'size': 9, 'multiline': False, 'align': 'L'},
    {'name': 'residence', 'type': 'T', 'x1': 1, 'x2': 49, 'y1': 80, 'y2': 84, 'font': 'helvetica', 'size': 9, 'multiline': False, 'align': 'L'},

    {'name': 'skills', 'type': 'T', 'text': 'Skills', 'x1': 1, 'x2': 49, 'y1': 90, 'y2': 95, 'font': 'helvetica', 'size': 13, 'multiline': False, 'align': 'L', 'underline': 1},

    {'name': 'work_experience', 'type': 'T', 'text': 'Work Experience', 'x1': work_x + 3, 'x2': 210, 'y1': 3, 'y2': 9, 'size': 25},
]


all_elements =  elements_part_1

# MARK: Fill Experiences
experiences_data = sorted(user_data['work'][0:4], key = lambda x: date_components_for_sort(x['start-date']), reverse = True)
work_experience_objects = []
between_experience_lines = []
work_y = 12
for i, exp in enumerate(experiences_data):
    work_experience_objects += WorkExperience(exp, work_x, work_y).get_generated_elements(i + 1)
    work_y += WorkExperience(exp, work_x, work_y).get_cumulative_height() + 3
cumulative_work_experiences_height = work_y
work_y = 12
for i in range(0, len(experiences_data) - 1):
    obj_height = WorkExperience(experiences_data[i], work_x, work_y).get_cumulative_height()
    between_experience_lines.append({'name': f'between_experience_line_{i + 1}', 'type': 'L', 'x1': work_x + 14, 'x2': work_x + 14, 
                                     'y1': work_y + obj_height, 'y2': work_y + obj_height + 3, 
                                     'size': 0.3})
    work_y += obj_height + 3


all_elements += work_experience_objects + between_experience_lines
all_elements += {'name': 'education', 'type': 'T', 'text': 'Education', 'x1': work_x + 3, 'x2': 210, 
                 'y1': cumulative_work_experiences_height + 2, 'y2': cumulative_work_experiences_height + 8, 'size': 25},


# MARK: Fill Education
education_data = sorted(user_data['education'], key = lambda x: date_components_for_sort(x['start-date']), reverse = True)
educational_objects = []
between_educational_lines = []
edu_y = cumulative_work_experiences_height + 11
for i, edu in enumerate(education_data):
    educational_objects += EducationalInstitution(edu, work_x, edu_y).get_generated_elements(i + 1)
    edu_y += EducationalInstitution(edu, work_x, edu_y).get_cumulative_height() + 3
cumulative_education_y = edu_y
edu_y = cumulative_work_experiences_height + 11
for i in range(0, len(education_data) - 1):
    obj_height = EducationalInstitution(education_data[i], work_x, edu_y).get_cumulative_height()
    between_educational_lines.append({'name': f'between_eduction_line_{i + 1}', 'type': 'L', 'x1': work_x + 14, 
                                      'x2': work_x + 14, 'y1': edu_y + obj_height, 'y2': edu_y + obj_height + 3, 'size': 0.3})
    edu_y += obj_height + 3

all_elements += educational_objects + between_educational_lines
all_elements += {'name': 'projects', 'type': 'T', 'text': 'Personal Projects', 'x1': work_x + 3, 'x2': 210, 
                 'y1': cumulative_education_y + 1, 'y2': cumulative_education_y + 6, 'size': 25},


# MARK: Fill Projects
projects_data = user_data['projects'] # sorted(user_data['projects'], key = lambda x: date_components_for_sort(x['start-date']), reverse = True) (I am not going to sort this one)
project_objects = []
project_x, project_y = (work_x, cumulative_education_y + 8)
for i, project in enumerate(projects_data):
    project_object = Project(project, project_x, project_y)
    project_objects += project_object.get_generated_elements(i + 1)
    project_size = (80, project_object.get_cumulative_height())
    if i % 2 == 0:
        project_x += project_size[0] - 5
    else:
        project_x = work_x
        project_y += project_size[1] + 3

all_elements += project_objects


# MARK: Fill Skills
skills_data = user_data['skills']
skill_objects = []
skill_x, skill_y = (2, 98)
for i, skill in enumerate(skills_data):
    skill_object = Skill(skill)
    if skill_x + skill_object.get_width() > 46: # 46 => 50 left-hand bar - 2mm margins on each side
        skill_x = 2
        skill_y += 6

    skill_object.start_x, skill_object.start_y = (skill_x, skill_y)
    skill_objects += skill_object.get_generated_elements(i + 1)
    skill_x += skill_object.get_width() + 1

all_elements += skill_objects
all_elements += {'name': 'languages', 'type': 'T', 'text': 'Languages', 'x1': 1, 'x2': 49, 'y1': skill_y + 10, 
                 'y2': skill_y + 15, 'font': 'helvetica', 'size': 13, 'multiline': False, 'align': 'L', 'underline': 1},

# MARK: Language Skills
languages_data = user_data['languages']
languages_objects = []
language_x, language_y = (2, skill_y + 16)
for i, language in enumerate(languages_data):
    language_object = Language(language, language_x, language_y)
    languages_objects += language_object.get_generated_elements(i + 1)
    language_y += language_object.get_cumulative_height()

all_elements += languages_objects

# MARK: Generate PDF 

templ = FlexTemplate(pdf, elements = all_elements)

templ['name'] = 'Alexander Minasyan'
templ['bio'] = 'I am a hardworking and creative problem solver that loves to learn and gain experience'
templ['email'] = 'alexander_minasyan@edu.aua.am'
templ['phone'] = '(098) 422922'
templ['residence'] = 'Yerevan, Armenia'


templ.render(offsetx = 0, offsety = 0, rotate = 0, scale = 1)
pdf.set_margin(0)
pdf.output('testing.pdf')