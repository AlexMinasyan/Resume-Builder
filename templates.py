from template_objects import HStack, VStack, Text, FreeStack, VLine, Table, Border, BorderType
from datetime import datetime
from functools import reduce
import operator

#MARK: Assisting Extensions
def convert_date_to_desired_format(date, original_format, desired_format):
    if type(date) == str:
        date = datetime.strptime(date, original_format)

    return datetime.strftime(date, desired_format)

def keys_exists(element, *keys):
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True

def get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)

#MARK: Super
class Template():
    def __init__(self, user_data, template_specifications):
        self.user_data = user_data
        self.template_specifications = template_specifications

        self.__check_given_data()
    
    def __check_given_data(self):
        usr_dat = self.user_data
        tem_spe = self.template_specifications

        required_fields = tem_spe['single_required_items']
        for field in required_fields:
            if not keys_exists(usr_dat, *field.split('-')):
                raise Exception(f'Key `{field}` is missing from given user data.')
            
        for key in list(tem_spe.keys() - ['single_required_items']):
            if len(usr_dat[key]) < tem_spe[key][0] or len(usr_dat[key]) > tem_spe[key][1]:
                raise Exception(f'`{key.capitalize()}` Objects has a wrong number of objects in given user data.')

#MARK: TimelineWithResearchTemplate
class TimelineWithResearchTemplate(Template):
    def __init__(self, user_data):
        templ_specs = {
            "single_required_items": ["bio-name", "bio-title", "bio-description", "contact-email", "contact-phone", "contact-residence", "contact-github"],
            "work": [1, 4],
            "education": [1, 1],
            "projects": [1, 4],
            "research": [1, 1],
            "skills": [1, 50],
            "languages": [1, 5]
        }
        super().__init__(user_data, template_specifications = templ_specs)

    def generate_overall_template(self):
        return HStack(0, 0, 210, 297, 0, [
            # Left Hand Stack
            VStack(0, 0, 50, 297, 0, [
                Text(self.user_data['bio']['name'], 24, x = 0, y = 0, width = 49, height = 12, priority = 0, font = 'dejavu-sans-mono', align = 'L', multiline = True),
                Text(self.user_data['bio']['title'], 12, 0, 0, 49, 4, 0, 'helvetica', 'L', multiline = True).with_margin({'top': 13}),
                Text("Professional Summary", 13, 0, 0, 49, 6, 0, 'helvetica', 'L', multiline = True, underline = True).with_margin({'top': 10}),
                Text(self.user_data['bio']['description'], 9, 0, 0, 48, 4, 0, 'helvetica', 'L', multiline = True).with_margin({'top': 2}),
                Text('Contact', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 15}),
                VStack(0, 0, 49, 0, 0, [
                    Text(self.user_data['contact']['email'], 8, 0, 0, 49, 4, 0), 
                    Text(self.user_data['contact']['phone'], 8, 0, 0, 49, 4, 0),
                    Text(self.user_data['contact']['residence'], 8, 0, 0, 49, 4, 0),
                    Text(f'GitHub: {self.user_data['contact']['github']}', 8, 0, 0, 49, 4, 0, auto_resizing = True, font_file_link = '/System/Library/Fonts/Helvetica.ttc').with_link('https://github.com/AlexMinasyan') # Links don't work yet
                ], 2).with_padding({'top': 2}),
                Text('Skills', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 7.5}),
                FreeStack(0, 0, 47, 0, 0, 
                        [self.generate_skill_object(skill) for skill in self.user_data['skills']], 
                    1, 1, margin = {'top': 2.5}).with_padding({'left': 1, 'right': 1}),
                Text('Languages', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 10}),
                VStack(0, 0, 49, 0, 0, 
                       [self.generate_language_object(lang) for lang in self.user_data['languages']]
                )
            ]).with_padding({'top': 5, 'left': 1}), 

            # Righthand Stack
            VStack(0, 0, 160, 297, 0, [
                Text('Work Experience', 25, 0, 0, 157, 6, 0).with_margin({'top': 3, 'left': 1.5}),
                VStack(0, 0, 150, 0, 0, 
                       [self.generate_work_object(work) for work in self.user_data['work']], 
                3, VLine(15, 0, 2.7, 0, 0.3)).with_margin({'top': 2}),
                Text('Education', 25, 0, 0, 157, 6, 0).with_margin({'top': 4, 'left': 1.5}),
                VStack(0, 0, 150, 0, 0, 
                       [self.generate_education_object(edu) for edu in self.user_data['education']], 
                3, VLine(15, 0, 2.7, 0, 0.3)).with_margin({'top': 2}),
                Text('Ongoing Research', 25, 0, 0, 157, 6, 0).with_margin({'top': 2, 'left': 1.5}),
                VStack(0, 0, 150, 0, 0, 
                       [self.generate_research_object(research) for research in self.user_data['research']], 
                3, VLine(15, 0, 2.7, 0, 0.3)).with_margin({'top': 2}),
                Text('Personal Projects', 25, 0, 0, 157, 6, 0).with_margin({'top': 8.5, 'left': 1.5}),
                Table(0, 0, 150, 0, 0, 
                      [self.generate_project_object(proj) for proj in self.user_data['projects']],
                (2, 2), 0, 8, margin = {'top': 1, 'left': 4})
            ])
                
        ], gap_filler = VLine(0, 0, 297, 0, 0.1))

    def generate_work_object(self, work_object):
        start_date = convert_date_to_desired_format(work_object['start-date'], '%m/%Y', '%b %Y').upper()
        end_date = 'PRESENT' if work_object['end-date'] == 'PRESENT' else convert_date_to_desired_format(work_object['end-date'], '%m/%Y', '%b %Y').upper()

        work_stack = VStack(0, 0, 150, 0, 0, [
            Text(end_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)),
            VStack(6, 0, 140, 0, 0, [
                Text(work_object['title'], 16, 0, 0, 134, 6, 0, 'helvetica').with_margin({'top': 1}),
                Text(work_object['name'], 12, 0, 0, 134, 4, 0, 'helvetica'),
                VStack(4, 0, 131, 0, 0, [
                    Text(f' - {x}', 8, 0, 0, 126, 3, 0) for x in work_object['tasks-achievements']
                ], 0.8).with_margin({'top': 0.5})
            ]).with_borders(Border(BorderType.LEFT, 0.3, 0, offset = {'left': 1, 'bottom': 1})),
            Text(start_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)).with_margin({'top': 1.5}),
        ]).with_margin({'left': 5})

        return work_stack
    
    def generate_education_object(self, edu_object):
        start_date = convert_date_to_desired_format(edu_object['start-date'], '%m/%Y', '%b %Y').upper()
        end_date = 'PRESENT' if edu_object['end-date'] == 'PRESENT' else convert_date_to_desired_format(edu_object['end-date'], '%m/%Y', '%b %Y').upper()

        work_stack = VStack(0, 0, 150, 0, 0, [
            Text(end_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)),
            VStack(6, 0, 140, 0, 0, [
                Text(edu_object['degree'], 16, 0, 0, 134, 6, 0, 'helvetica').with_margin({'top': 1}),
                Text(edu_object['name'], 12, 0, 0, 134, 4, 0, 'helvetica'),
                VStack(4, 0, 131, 0, 0, [
                    Text(f' - {x}', 8, 0, 0, 126, 3, 0) for x in edu_object['courses-important']
                ], 0.8).with_margin({'top': 0.5})
            ]).with_borders(Border(BorderType.LEFT, 0.3, 0, offset = {'left': 1, 'bottom': 1})),
            Text(start_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)).with_margin({'top': 1.5}),
        ]).with_margin({'left': 5})

        return work_stack
    
    def generate_research_object(self, research_object):
        research_stack = VStack(0, 0, 150, 0, 0, [
            Text(research_object['name'], 9, 6, 0, 134, 5, 0),
            Text(research_object['description'], 7, 6, 0, 134, 3, 0, multiline = True)
        ])
        return research_stack
    
    def generate_project_object(self, project_object):
        project_stack = VStack(0, 0, 75, 0, 0, [
            Text(project_object['name'], 11, 0, 0, 75, 5, 0),
            Text(project_object['description'], 8, 0, 0, 75, 3, 0, multiline = True)
        ])
        return project_stack
    
    def generate_skill_object(self, skill):
        return Text(skill['name'], 8, 0, 0, 1.7 * len(skill['name']) + 2.1, 5, 0, 'dejavu-sans-mono').with_borders(Border())

    def generate_language_object(self, lang):
        return VStack(0, 0, 48, 0, 0, [
            Text(lang['name'], 10, 0, 0, 48, 5, 0, 'helvetica').with_margin({'left': 1}), 
            Text(lang['level'], 8, 0, 0, 47, 4, 0).with_margin({'left': 2})
        ])


#MARK: TimelineBaseTemplate
class TimelineBaseTemplate(Template):
    def __init__(self, user_data):
        templ_specs = {
            "single_required_items": ["bio-name", "bio-title", "bio-description", "contact-email", "contact-phone", "contact-residence", "contact-github"],
            "work": [1, 4],
            "education": [1, 2],
            "projects": [1, 4],
            "research": [0, 0],
            "skills": [1, 50],
            "languages": [1, 5]
        }
        super().__init__(user_data, template_specifications = templ_specs)

    def generate_overall_template(self):
        return HStack(0, 0, 210, 297, 0, [
            # Left Hand Stack
            VStack(0, 0, 50, 297, 0, [
                Text(self.user_data['bio']['name'], 24, x = 0, y = 0, width = 49, height = 12, priority = 0, font = 'dejavu-sans-mono', align = 'L', multiline = True),
                Text(self.user_data['bio']['title'], 12, 0, 0, 49, 4, 0, 'helvetica', 'L', True).with_margin({'top': 13}),
                Text("Professional Summary", 13, 0, 0, 49, 6, 0, 'helvetica', 'L', True, True).with_margin({'top': 10}),
                Text(self.user_data['bio']['description'], 9, 0, 0, 48, 4, 0, 'helvetica', 'L', True).with_margin({'top': 2}),
                Text('Contact', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 15}),
                VStack(0, 0, 49, 0, 0, [
                    Text(self.user_data['contact']['email'], 8, 0, 0, 49, 4, 0), 
                    Text(self.user_data['contact']['phone'], 8, 0, 0, 49, 4, 0),
                    Text(self.user_data['contact']['residence'], 8, 0, 0, 49, 4, 0),
                    Text(f'GitHub: {self.user_data['contact']['github']}', 8, 0, 0, 49, 4, 0, link = 'https://github.com/AlexMinasyan') # Links don't work yet
                ], 2).with_padding({'top': 2}),
                Text('Skills', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 7.5}),
                FreeStack(0, 0, 47, 0, 0, 
                        [self.generate_skill_object(skill) for skill in self.user_data['skills']], 
                    1, 1, margin = {'top': 2.5}).with_padding({'left': 1, 'right': 1}),
                Text('Languages', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 10}),
                VStack(0, 0, 49, 0, 0, 
                       [self.generate_language_object(lang) for lang in self.user_data['languages']]
                )
            ]).with_padding({'top': 5, 'left': 1}), 

            # Righthand Stack
            VStack(0, 0, 160, 297, 0, [
                Text('Work Experience', 25, 0, 0, 157, 6, 0).with_margin({'top': 3, 'left': 1.5}),
                VStack(0, 0, 150, 0, 0, 
                       [self.generate_work_object(work) for work in self.user_data['work']], 
                3, VLine(15, 0, 2.7, 0, 0.3)).with_margin({'top': 2}),
                Text('Education', 25, 0, 0, 157, 6, 0).with_margin({'top': 4, 'left': 1.5}),
                VStack(0, 0, 150, 0, 0, 
                       [self.generate_education_object(edu) for edu in self.user_data['education']], 
                3, VLine(15, 0, 2.7, 0, 0.3)).with_margin({'top': 2}),
                Text('Personal Projects', 25, 0, 0, 157, 6, 0).with_margin({'top': 8.5, 'left': 1.5}),
                Table(0, 0, 150, 0, 0, 
                      [self.generate_project_object(proj) for proj in self.user_data['projects']],
                (2, 2), 0, 8, margin = {'top': 1, 'left': 4})
            ])
                
        ], gap_filler = VLine(0, 0, 297, 0, 0.1))

    def generate_work_object(self, work_object):
        start_date = convert_date_to_desired_format(work_object['start-date'], '%m/%Y', '%b %Y').upper()
        end_date = 'PRESENT' if work_object['end-date'] == 'PRESENT' else convert_date_to_desired_format(work_object['end-date'], '%m/%Y', '%b %Y').upper()

        work_stack = VStack(0, 0, 150, 0, 0, [
            Text(end_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)),
            VStack(6, 0, 140, 0, 0, [
                Text(work_object['title'], 16, 0, 0, 134, 6, 0, 'helvetica').with_margin({'top': 1}),
                Text(work_object['name'], 12, 0, 0, 134, 4, 0, 'helvetica'),
                VStack(4, 0, 131, 0, 0, [
                    Text(f' - {x}', 8, 0, 0, 126, 3, 0) for x in work_object['tasks-achievements']
                ], 0.8).with_margin({'top': 0.5})
            ]).with_borders(Border(BorderType.LEFT, 0.3, 0, offset = {'left': 1, 'bottom': 1})),
            Text(start_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)).with_margin({'top': 1.5}),
        ]).with_margin({'left': 5})

        return work_stack
    
    def generate_education_object(self, edu_object):
        start_date = convert_date_to_desired_format(edu_object['start-date'], '%m/%Y', '%b %Y').upper()
        end_date = 'PRESENT' if edu_object['end-date'] == 'PRESENT' else convert_date_to_desired_format(edu_object['end-date'], '%m/%Y', '%b %Y').upper()

        work_stack = VStack(0, 0, 150, 0, 0, [
            Text(end_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)),
            VStack(6, 0, 140, 0, 0, [
                Text(edu_object['degree'], 16, 0, 0, 134, 6, 0, 'helvetica').with_margin({'top': 1}),
                Text(edu_object['name'], 12, 0, 0, 134, 4, 0, 'helvetica'),
                VStack(4, 0, 131, 0, 0, [
                    Text(f' - {x}', 8, 0, 0, 126, 3, 0) for x in edu_object['courses-important']
                ], 0.8).with_margin({'top': 0.5})
            ]).with_borders(Border(BorderType.LEFT, 0.3, 0, offset = {'left': 1, 'bottom': 1})),
            Text(start_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_borders(Border(size = 0.3)).with_margin({'top': 1.5}),
        ]).with_margin({'left': 5})

        return work_stack
    
    def generate_research_object(self, research_object):
        research_stack = VStack(0, 0, 150, 0, 0, [
            Text(research_object['name'], 9, 6, 0, 134, 5, 0),
            Text(research_object['description'], 7, 6, 0, 134, 3, 0, multiline = True)
        ])
        return research_stack
    
    def generate_project_object(self, project_object):
        project_stack = VStack(0, 0, 75, 0, 0, [
            Text(project_object['name'], 11, 0, 0, 75, 5, 0),
            Text(project_object['description'], 8, 0, 0, 75, 3, 0, multiline = True)
        ])
        return project_stack
    
    def generate_skill_object(self, skill):
        return Text(skill['name'], 8, 0, 0, 1.7 * len(skill['name']) + 2.1, 5, 0, 'dejavu-sans-mono').with_borders(Border())

    def generate_language_object(self, lang):
        return VStack(0, 0, 48, 0, 0, [
            Text(lang['name'], 10, 0, 0, 48, 5, 0, 'helvetica').with_margin({'left': 1}), 
            Text(lang['level'], 8, 0, 0, 47, 4, 0).with_margin({'left': 2})
        ])