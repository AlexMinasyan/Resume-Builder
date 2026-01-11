from fpdf import FlexTemplate, FPDF
import copy, itertools
from PIL import ImageFont

# MARK: Document Object
# Later add the ability to make a single border at a time
class Document_Object():
    def __init__(self, x: float, y: float, width: float, height: float, priority: int, 
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.priority = priority
        self.is_single_border = None

        self.set_margin(margin)
        self.total_border_size = 0
        self.total_border_color = 0
        self.total_border_offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}

    # For margin, excepts a dictionary of 'top', 'right', 'bottom', and 'left' keys with values being an int determining the size
    def set_margin(self, margin):
        if not set(margin.keys()).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys")
        
        self.top_margin = margin['top'] if 'top' in margin else 0
        self.right_margin = margin['right'] if 'right' in margin else 0
        self.bottom_margin = margin['bottom'] if 'bottom' in margin else 0
        self.left_margin = margin['left'] if 'left' in margin else 0

    # Allows one to remove the margin
    def remove_margin(self):
        self.top_margin, self.right_margin, self.bottom_margin, self.left_margin = (0, 0, 0, 0)

    # Re-returns the object with an added margin (for a Swift-like programming style)
    def with_margin(self, margin):
        self.set_margin(margin)
        return self

    # Adds a Border 
    def add_border(self, size = 0.2, color = 0x000000, offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        if not set(offset.keys()).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys")
        
        self.is_single_border = True
        self.total_border_size = size
        self.total_border_color = color
        self.total_border_offset = offset

    # Re-returns the object with a border
    def with_border(self, size = 0.2, color = 0x000000, offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        self.add_border(size, color, offset)
        return self

    # Returns the list of objects of the PDF Styling
    def render_as_flex_template_object(self):
        base_template_object = {
            'name': 'OBJECT_1', 'priority': self.priority,
            'x1': self.x + self.left_margin, 'x2': self.left_margin + self.x + self.width + self.right_margin, 'y1': self.y + self.top_margin, 'y2': self.top_margin + self.y + self.height + self.bottom_margin
        }
        all_sub_template_objects = [base_template_object]

        if self.is_single_border is True:
            all_sub_template_objects.append({
                'name': 'BORDER_1', 'priority': self.priority - 1, 'type': 'B', 
                'size': self.total_border_size, 'foreground': self.total_border_color, 
                'x1': self.x + self.left_margin + self.total_border_offset['left'], 'x2': self.left_margin + self.x + self.width + self.right_margin + self.total_border_offset['right'] + self.total_border_offset['left'],
                'y1': self.y + self.top_margin + self.total_border_offset['top'], 'y2': self.top_margin + self.y + self.height + self.bottom_margin + self.total_border_offset['top'] + self.total_border_offset['bottom']
            })
            base_template_object['x1'] += self.total_border_offset['left']
            base_template_object['x2'] -= self.total_border_offset['right']
            base_template_object['y1'] += self.total_border_offset['top'] + 0.2
            base_template_object['y2'] -= self.total_border_offset['bottom']

        # elif self.is_single_border is False:

        return all_sub_template_objects

# MARK: Stacks
class Stack(Document_Object):
    def __init__(self, x, y, width, height, priority, children, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.children = children

        self.set_padding(padding)

    def set_padding(self, padding): # For padding, I can just have the render add margin to the children...
        if not set(padding).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys")
        
        self.top_padding = padding['top'] if 'top' in padding else 0
        self.right_padding = padding['right'] if 'right' in padding else 0
        self.bottom_padding = padding['bottom'] if 'bottom' in padding else 0
        self.left_padding = padding['left'] if 'left' in padding else 0

    def with_padding(self, padding):
        self.set_padding(padding)
        return self

class AlignedStack(Stack):
    def __init__(self, x, y, width, height, priority, children, inner_gap = 0.0, gap_filler: Document_Object = None, vertical = True,
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}):
        super().__init__(x, y, width, height, priority, children, margin, padding)
        self.inner_gap = inner_gap
        self.gap_filler = gap_filler
        self.vertical = vertical
    
    def render_item_as_flex_template_objects(self):
        if len(self.children) == 0:
            raise Exception("You cannot have an empty stack")
        
        # Defining which axes (x or y) and sides (left / right or top / bottom) will be the incremented ones and the locked ones.
        if self.vertical:
            axis, close_side, far_side, size = ('y', 'top', 'bottom', 'height')
            locked_axis, locked_close_side = ('x', 'left')
        else:
            axis, close_side, far_side, size = ('x', 'left', 'right', 'width')
            locked_axis, locked_close_side = ('y', 'top')

        # Defining the Initial Positions
        locked_offset = getattr(self, f'{locked_close_side}_padding') + getattr(self, locked_axis) + getattr(self, f'{locked_close_side}_margin')
        axis_init = getattr(self, f'{close_side}_padding') + getattr(self, axis) + getattr(self, f'{close_side}_margin')
        axis_increment = axis_init

        # # Setting the Positions to generate the objects
        all_template_objects = []
        for i, child in enumerate(self.children):
            setattr(child, locked_axis, locked_offset + getattr(child, f'{locked_close_side}_margin') + getattr(child, locked_axis))
            setattr(child, axis, axis_increment)
            all_template_objects += child.render_item_as_flex_template_objects()

            if (not (self.gap_filler is None)) or (i > len(self.children) - 1):
                filler = copy.deepcopy(self.gap_filler)
                setattr(filler, axis, axis_increment + getattr(filler, axis) + getattr(child, size) + getattr(filler, f'{close_side}_margin') + child.total_border_offset[close_side] + child.total_border_offset[far_side])
                setattr(filler, locked_axis, filler.y + getattr(filler, locked_axis) + getattr(filler, f'{locked_close_side}_margin'))
                all_template_objects += filler.render_item_as_flex_template_objects()
            
            axis_increment = getattr(child, axis) + getattr(child, f'{close_side}_margin') + child.total_border_offset[close_side] + getattr(child, size) + getattr(child, f'{far_side}_margin') + child.total_border_offset[far_side] + self.inner_gap

        setattr(self, size, axis_increment - axis_init - self.inner_gap) # Updating the size of the Stack
        return all_template_objects

# MARK: HStack
class HStack(AlignedStack):
    def __init__(self, x, y, width, height, priority, children, inner_gap = 0.0, gap_filler: Document_Object = None, 
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, children, margin, padding, vertical = False)
        self.inner_gap = inner_gap
        self.gap_filler = gap_filler
    
    def render_item_as_flex_template_objects(self):
        return super().render_item_as_flex_template_objects()

# MARK: VStack
class VStack(AlignedStack):
    def __init__(self, x, y, width, height, priority, children, inner_gap = 0, gap_filler = None, 
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, children, margin, padding)
        self.inner_gap = inner_gap
        self.gap_filler = gap_filler

    def render_item_as_flex_template_objects(self):
        return super().render_item_as_flex_template_objects()
    
# MARK: FreeStack
class FreeStack(Stack):
    def __init__(self, x, y, width, height, priority, children, x_gap, y_gap, 
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, children, margin, padding)
        self.x_gap = x_gap
        self.y_gap = y_gap

    def render_item_as_flex_template_objects(self):
        if len(self.children) == 0:
            raise Exception("You cannot have an empty stack")
        
        y_init = self.top_padding + self.y + self.top_margin
        x_init = self.left_padding + self.x + self.left_margin
        x_bound = x_init + self.width - self.right_padding - self.right_margin

        default_height = self.children[0].height
        for child in self.children[1:]:
            if child.height != default_height:
                raise Exception("All children must be of the same height (this will change later)")
            child_bounding_box = child.total_border_offset['left'] + child.left_margin + child.width + child.right_margin + child.total_border_offset['right']
            if child_bounding_box > x_bound - x_init: # This maximizes the width of the child to avoid overflow issues
                child.width = x_bound - x_init - (child_bounding_box - child.width) # Set its width equal to the entire boundary width

        all_template_objects = []
        x, y = (x_init, y_init)
        for child in self.children:
            child_bounding_box = child.total_border_offset['left'] + child.left_margin + child.width + child.right_margin + child.total_border_offset['right']
            if x + child_bounding_box + self.x_gap > x_bound:
                x = x_init
                y += child.height + self.y_gap
            child.x = x
            child.y = y

            x += child_bounding_box + self.x_gap
            all_template_objects += child.render_item_as_flex_template_objects()

        self.height = y - y_init
        return all_template_objects


# MARK: Text
class Text(Document_Object):
    def __init__(self, text: str, font_size: float, x, y, width, height, priority, font = 'helvetica', align = 'L', multiline = False, underline = False, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.text = text
        self.font = font
        self.align = align
        self.font_size = font_size
        self.multiline = multiline
        self.underline = underline
        # Later going to adjust height to include multiple lines
        # self.height = get_text_length(text, font, font_size)

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'T'
        base_template_object['text'] = self.text
        base_template_object['font'] = self.font
        base_template_object['align'] = self.align
        base_template_object['size'] = self.font_size
        base_template_object['multiline'] = self.multiline
        base_template_object['underline'] = int(self.underline == True)

        return [base_template_object] + super().render_as_flex_template_object()[1:]
    
# MARK: Lines
class HLine(Document_Object):
    def __init__(self, x, y, width, priority, size = 0.2, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, 0, priority, margin)
        self.size = size

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'L'
        base_template_object['size'] = self.size

        return [base_template_object]

class VLine(Document_Object):
    def __init__(self, x, y, height, priority, size = 0.2, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, 0, height, priority, margin)
        self.size = size

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'L'
        base_template_object['size'] = self.size
        
        return [base_template_object]
# MARK: Box  
class Box(Document_Object): 
    def __init__(self, x, y, width, height, priority, size = 0.2, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.size = size

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'B'
        base_template_object['size'] = self.size
        
        return [base_template_object]
    
# MARK: Some Extensions
def get_text_length(text, font, size):
    image_font = ImageFont.truetype(font, size)
    pxls = image_font.getlength(text)
    return px_to_mm(pxls)

def px_to_mm(px, dpi = 67):
    return (px * 25.4) / dpi


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