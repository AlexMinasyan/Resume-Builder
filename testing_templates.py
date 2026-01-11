from fpdf import FlexTemplate, FPDF
import itertools
from template_objects import HStack, VStack, Text, FreeStack, VLine

# MARK: Testing
skills = ['HTML, CSS, JavaScript', 'Xcode & Swift', 'Python', 'C++', 'Excel', 'VBA Scripts', 'Calculus', 'Statistics', 'Differential Equations', 'Linear Algebra', 'Numerical Analysis', 'Microeconomics', 'Macroeconomics']
languages = [
    {'name': 'English', 'level': 'Native or Bilingual Proficiency'},
    {'name': 'Russian', 'level': 'Limited Working Proficiency'}
]
full_page_hstack_2 = HStack(0, 0, 210, 297, 0, [

    # Left Hand Stack
    VStack(0, 0, 50, 297, 0, [
        Text("Alexander Minasyan", 24, x= 0, y= 0, width = 49, height = 12, priority = 0, font = 'dejavu-sans-mono', align = 'L', multiline = True),
        Text("Professional Summary", 13, 0, 0, 49, 6, 0, 'helvetica', 'L', True, True).with_margin({'top': 16}),
        Text('I am a hardworking and creative problem solver that loves to learn and gain experience', 9, 0, 0, 48, 4, 0, 'helvetica', 'L', True).with_margin({'top': 2}),
        Text('Contact', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 15}),
        VStack(0, 0, 49, 0, 0, [
            Text('alexander_minasyan@edu.aua.am', 8, 0, 0, 49, 4, 0), 
            Text('(098) 422-922', 8, 0, 0, 49, 4, 0),
            Text('Yerevan, Armenia', 8, 0, 0, 49, 4, 0)
        ], 2).with_padding({'top': 2}),
        Text('Skills', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 7.5}),
        FreeStack(0, 0, 47, 0, 0, 
                [Text(skill, 8, 0, 0, 1.7 * len(skill) + 2.1, 5, 0, 'dejavu-sans-mono').with_border() for skill in skills], 
            1, 1, margin = {'top': 2.5}).with_padding({'left': 1, 'right': 1}),
        Text('Languages', 13, 0, 0, 49, 6, 0, 'helvetica', 'L', False, True).with_margin({'top': 10}),
        VStack(0, 0, 49, 0, 0, 
            list(itertools.chain(*[
                (Text(lang['name'], 10, 0, 0, 48, 5, 0, 'helvetica').with_margin({'left': 1}), 
                Text(lang['level'], 8, 0, 0, 47, 4, 0).with_margin({'left': 2})) for lang in languages
            ]))
        )
    ]).with_padding({'top': 5, 'left': 1}), 

    # Righthand Stack
    VStack(0, 0, 160, 297, 0, [
        Text('Work Experience', 25, 0, 0, 157, 6, 0).with_margin({'top': 3, 'left': 1.5}),
    ])
        
], gap_filler = VLine(0, 0, 297, 0, 0.1))


pdf = FPDF(orientation = 'portrait', format = 'A4')
pdf.add_page()
pdf.add_font('dejavu-sans-mono', style = '', fname = 'dejavu-sans-mono/DejaVuSansMono.ttf')

templ = FlexTemplate(pdf, elements = full_page_hstack_2.render_item_as_flex_template_objects())
templ.render(offsetx = 0, offsety = 0, rotate = 0, scale = 1)

pdf.set_margin(0)
pdf.output('testing_template_version.pdf')

# For Template Specifications, I can later add a character limit for the fit
# Figure out how to rearrange the fit for a FreeStack (make it a parameter `auto_fit`)