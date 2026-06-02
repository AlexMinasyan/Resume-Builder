from fpdf import FlexTemplate, FPDF
import json, sys, glob
from pick import pick
from templates import TimelineWithResearchTemplate, TimelineBaseTemplate


# MARK: User Data
def prompt_data_file():
    title = 'Please select a data file to user'
    options = glob.glob('User Data/*.json')
    options = [
        f.split('/')[1].removesuffix('.json')
        for f in options
    ]
    selection = pick(options, title, multiselect = False, indicator = '=>', min_selection_count = 1)
    return selection[0]

def prompt_specs(data_file):
    headers = ['work', 'education', 'projects', 'research', 'languages']
    specs = {  }
    for header in headers:
        title = f'Please Select the {header.capitalize()} Objects you want'
        options = [obj['name'] for obj in data_file[header]]
        selections = pick(options, title, indicator = '=>', multiselect = True)
        indices = [sel[1] for sel in selections]
        specs[header] = indices
    return specs

def filter_out_user_data(user_data, specs):
    new_user_data = user_data.copy()
    for header in specs.keys():
        new_user_data[header] = [user_data[header][i] for i in specs[header]]

    return new_user_data

if __name__ == "__main__":

    # MARK: Running Specs

    # Schematics: python3 testing_templates.py [testing] [data_file] [prebuild_file]
    testing = True if len(sys.argv) <= 1 or str(sys.argv[1]).lower()  == 'true' else False

    # Getting the JSON file
    json_file_name = None
    specs_file_name = None
    if testing == True:
        json_file_name = 'dummy_info'
        specs_file_name = 'specs'
    else:
        if len(sys.argv) > 2:
            json_file_name = str(sys.argv[2])
        else:
            json_file_name = prompt_data_file()

    with open(f'User Data/{json_file_name}.json') as f:
        user_data = json.load(f)

    # Getting the User's choices
    user_specs = ''
    if specs_file_name != None:
        with open(f'{specs_file_name}.json') as f:
            user_specs = json.load(f)
    elif len(sys.argv) > 3:
        specs_file_name = str(sys.argv[3])
        with open(f'{specs_file_name}.json') as f:
            user_specs = json.load(f)
    else:
        user_specs = prompt_specs(user_data)

    new_user_data = filter_out_user_data(user_data, user_specs)
    # print(json.dumps(new_user_data, indent = 4))


    # MARK: Generation
    my_template = TimelineWithResearchTemplate(new_user_data)
    full_page_hstack_2 = my_template.generate_overall_template()

    pdf = FPDF(orientation = 'portrait', format = 'A4')
    pdf.add_page()
    pdf.add_font('dejavu-sans-mono', style = '', fname = 'dejavu-sans-mono/DejaVuSansMono.ttf')

    # Note: do not call `render_item_as_flex_template_objects` more than once
    all_rendering_items = full_page_hstack_2.render_item_as_flex_template_objects()
    for item in all_rendering_items:
        if 'link' in item.keys() and item['link'] != '':
            pdf.link(x = item['x1'], y = item['y1'], w = item['x2'] - item['x1'], h = item['y2'] - item['y1'], link = item['link'])

    templ = FlexTemplate(pdf, elements = all_rendering_items)
    templ.render(offsetx = 0, offsety = 0, rotate = 0, scale = 1)

    pdf.set_margin(0)
    output_link = 'Testing Results/testing_template_version.pdf'
    pdf.output(output_link)

# MARK: TO-DO
# Idea: the link looks wierd because it spans the entire column, create a function or a specification that fits the width to the length of the string
# Idea: call `render_item_as_flex_template_objects` and a separate get objects just to obtain the result of the former, without redoing all calcuations (or just run a resent in the `render_item_as_flex_template_objects`)
# Idea: Add clickable links to each work object and project

# Filter Skills Objects
# Include Testing in command
# Run file with certain specifications for faster running
# For Template Specifications, I can later add a character limit for the fit
# Figure out how to rearrange the fit for a FreeStack (make it a parameter `auto_fit`)
# Skills Categories
# Multiline Freestack
# Handling Missing Sections
# You need to be able to add a second page