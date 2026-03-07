from fpdf import FlexTemplate, FPDF
import itertools, json
from template_objects import HStack, VStack, Text, FreeStack, VLine, Table
from datetime import datetime
from pick import pick

#MARK: Assisting Extensions
def convert_date_to_desired_format(date, original_format, desired_format):
    if type(date) == str:
        date = datetime.strptime(date, original_format)

    return datetime.strftime(date, desired_format)


#MARK: Template
class Template():
    def __init__(self, user_data, template_specifications):
        self.user_data = user_data

        self.work_objects = user_data['work']
        self.education_objects = user_data['education']
        self.project_objects = user_data['projects']
        self.skill_objects = user_data['skills']
        self.language_objects = user_data['languages']

    def generate_work_object(self, index: int):
        work_object = self.work_objects[index]
        
        start_date = convert_date_to_desired_format(work_object['start-date'], '%m/%Y', '%b %Y').upper()
        end_date = convert_date_to_desired_format(work_object['end-date'], '%m/%Y', '%b %Y').upper()

        work_stack = VStack(0, 0, 150, 0, 0, [
            Text(end_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_border(0.3),
            VStack(6, 0, 140, 0, 0, [
                Text(work_object['title'], 16, 0, 0, 134, 6, 0, 'helvetica').with_margin({'top': 1}),
                Text(work_object['name'], 12, 0, 0, 134, 4, 0, 'helvetica'),
                VStack(4, 0, 131, 0, 0, [
                    Text(f' - {x}', 8, 0, 0, 126, 3, 0) for x in work_object['tasks-achievements']
                ], 0.8).with_margin({'top': 0.5})
            ]).add_single_border('left', 0.3, 0, offset = {'left': 1, 'bottom': 1}),
            Text(start_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_border(0.3).with_margin({'top': 1.5}),
        ]).with_margin({'left': 5})

        return work_stack
    
    def generate_education_object(self, index: int):
        edu_object = self.education_objects[index]
        
        start_date = convert_date_to_desired_format(edu_object['start-date'], '%m/%Y', '%b %Y').upper()
        end_date = 'PRESENT' if edu_object['end-date'] == 'PRESENT' else convert_date_to_desired_format(edu_object['end-date'], '%m/%Y', '%b %Y').upper()

        work_stack = VStack(0, 0, 150, 0, 0, [
            Text(end_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_border(0.3),
            VStack(6, 0, 140, 0, 0, [
                Text(edu_object['degree'], 16, 0, 0, 134, 6, 0, 'helvetica').with_margin({'top': 1}),
                Text(edu_object['name'], 12, 0, 0, 134, 4, 0, 'helvetica'),
                VStack(4, 0, 131, 0, 0, [
                    Text(f' - {x}', 8, 0, 0, 126, 3, 0) for x in edu_object['courses-important']
                ], 0.8).with_margin({'top': 0.5})
            ]).add_single_border('left', 0.3, 0, offset = {'left': 1, 'bottom': 1}),
            Text(start_date, 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_border(0.3).with_margin({'top': 1.5}),
        ]).with_margin({'left': 5})

        return work_stack
    
    def generate_project_object(self, index: int):
        project_object = self.project_objects[index]

        project_stack = VStack(0, 0, 75, 0, 0, [
            Text(project_object['name'], 11, 0, 0, 75, 5, 0),
            Text(project_object['description'], 8, 0, 0, 75, 3, 0, multiline = True)
        ])

        return project_stack
    
    def generate_skill_object(self, index: int):
        skill = self.skill_objects[index]

        return Text(skill['name'], 8, 0, 0, 1.7 * len(skill['name']) + 2.1, 5, 0, 'dejavu-sans-mono').with_border()

    def generate_language_object(self, index: int):
        lang = self.language_objects[index]
        return VStack(0, 0, 48, 0, 0, [
            Text(lang['name'], 10, 0, 0, 48, 5, 0, 'helvetica').with_margin({'left': 1}), 
            Text(lang['level'], 8, 0, 0, 47, 4, 0).with_margin({'left': 2})
        ])
        


# MARK: Generation
with open(f'User Data/admin_info_english.json') as f:
    user_data = json.loads(f.read())

    new_user_data = { 'contact': user_data['contact'], 'bio': user_data['bio'], 'skills': user_data['skills'] }
 
    # The capping of a max number of options has not been implemented
    remaining_headers = sorted(list(user_data.keys() - ['bio', 'contact', 'skills']))
    # selected_categories = []
    # for header in remaining_headers: # We will ignore skills for now as you can have like 20.
    #     title = f'Please Select the {header.capitalize()} Objects you want'
    #     options = [obj['name'] for obj in user_data[header]]
    #     selected_categories.append(pick(options, title, multiselect = True, min_selection_count = 0))

    # for i in range(0, len(remaining_headers)):
    #     sel_obj = selected_categories[i]
    #     sel_obj_indices = [selection[1] for selection in sel_obj]
    #     new_user_data[remaining_headers[i]] = [user_data[remaining_headers[i]][j] for j in sel_obj_indices]

    # Just Selects the top items (for testing)
    for i in range(0, len(remaining_headers)):
        new_user_data[remaining_headers[i]] = [user_data[remaining_headers[i]][j] for j in range(0, min(len(user_data[remaining_headers[i]]), 4))]
    # print(json.dumps(new_user_data, indent = 4))

    my_template = Template(new_user_data, template_specifications = {})

# Note: (210, 297) is the mm size of A4 paper.
full_page_hstack_2 = HStack(0, 0, 210, 297, 0, [

    # Left Hand Stack
    VStack(0, 0, 50, 297, 0, [
        Text("Alexander Minasyan", 24, x = 0, y = 0, width = 49, height = 12, priority = 0, font = 'dejavu-sans-mono', align = 'L', multiline = True),
        Text("Professional Summary", 13, 0, 0, 49, 6, 0, 'helvetica', 'L', True, True).with_margin({'top': 16}),
        Text('I am a hardworking and creative problem solver that loves to learn and gain experience', 9, 0, 0, 48, 4, 0, 'helvetica', 'L', True).with_margin({'top': 2}),
        Text('Contact', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 15}),
        VStack(0, 0, 49, 0, 0, [
            Text('alexander_minasyan@edu.aua.am', 8, 0, 0, 49, 4, 0), 
            Text('(098) 422-922', 8, 0, 0, 49, 4, 0),
            Text('Yerevan, Armenia', 8, 0, 0, 49, 4, 0),
            Text('GitHub: AlexMinasyan', 8, 0, 0, 49, 4, 0, link = 'https://github.com/AlexMinasyan') # Links don't work yet
        ], 2).with_padding({'top': 2}),
        Text('Skills', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 7.5}),
        FreeStack(0, 0, 47, 0, 0, 
                [my_template.generate_skill_object(i) for i in range(0, min(len(my_template.skill_objects), 25))], 
            1, 1, margin = {'top': 2.5}).with_padding({'left': 1, 'right': 1}),
        Text('Languages', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 10}),
        VStack(0, 0, 49, 0, 0, [
            my_template.generate_language_object(i) for i in range(0, min(len(my_template.language_objects), 4))
        ])
    ]).with_padding({'top': 5, 'left': 1}), 

    # Righthand Stack
    VStack(0, 0, 160, 297, 0, [
        Text('Work Experience', 25, 0, 0, 157, 6, 0).with_margin({'top': 3, 'left': 1.5}),
        VStack(0, 0, 150, 0, 0, [
            my_template.generate_work_object(i) for i in range(0, min(len(my_template.work_objects), 4))
        ], 3, VLine(15, 0, 2.7, 0, 0.3)).with_margin({'top': 2}),
        Text('Education', 25, 0, 0, 157, 6, 0).with_margin({'top': 4, 'left': 1.5}),
        VStack(0, 0, 150, 0, 0, [
            my_template.generate_education_object(i) for i in range(0, min(len(my_template.education_objects), 2))
        ], 3, VLine(15, 0, 2.7, 0, 0.3)).with_margin({'top': 2}),
        Text('Personal Projects', 25, 0, 0, 157, 6, 0).with_margin({'top': 2, 'left': 1.5}),
        Table(0, 0, 150, 0, 0, [
            my_template.generate_project_object(i) for i in range(0, min(len(my_template.project_objects), 4))
        ], (2, 2), 0, 8, margin = {'top': 1, 'left': 4})
    ])
        
], gap_filler = VLine(0, 0, 297, 0, 0.1))


pdf = FPDF(orientation = 'portrait', format = 'A4')
pdf.add_page()
pdf.add_font('dejavu-sans-mono', style = '', fname = 'dejavu-sans-mono/DejaVuSansMono.ttf')

# Note: do not call `render_item_as_flex_template_objects` more than once
all_rendering_items = full_page_hstack_2.render_item_as_flex_template_objects()
for item in all_rendering_items:
    if 'link' in item.keys() and item['link'] != '':
        pdf.link(x = item['x1'], y = item['y1'], w = item['x2'] - item['x1'], h = item['y2'] - item['y1'], link = item['link'])
        print(item)
# Idea: the link looks wierd because it spans the entire column, create a function or a specification that fits the width to the length of the string
# Idea: call `render_item_as_flex_template_objects` and a separate get objects just to obtain the result of the former, without redoing all calcuations (or just run a resent in the `render_item_as_flex_template_objects`)
# Idea: Add clickable links to each work object and project

templ = FlexTemplate(pdf, elements = all_rendering_items)
templ.render(offsetx = 0, offsety = 0, rotate = 0, scale = 1)

pdf.set_margin(0)
pdf.output('Testing Results/testing_template_version.pdf')

# For Template Specifications, I can later add a character limit for the fit
# Figure out how to rearrange the fit for a FreeStack (make it a parameter `auto_fit`)