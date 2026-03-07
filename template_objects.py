# MARK: Packages
import copy, math
from PIL import ImageFont
from fpdf import FlexTemplate, FPDF

# MARK: Document Object
# Note: Single Borders cannot have color so far, but that will be changed soon
class Document_Object():
    def __init__(self, x: float, y: float, width: float, height: float, priority: int, 
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.priority = priority
        self.margin = margin
        self.side_borders = []

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
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys.")
        
        offset['top'] = offset['top'] if 'top' in offset.keys() else 0
        offset['right'] = offset['right'] if 'right' in offset.keys() else 0
        offset['bottom'] = offset['bottom'] if 'bottom' in offset.keys() else 0
        offset['left'] = offset['left'] if 'left' in offset.keys() else 0

        self.total_border_size = size
        self.total_border_color = color
        self.total_border_offset = offset

    def add_single_border(self, side, size = 0.2, color = 0x000000, offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        # Making Sure that the offsets are in order
        if not set(offset.keys()).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys.")
        
        if not side in ['top', 'right', 'bottom', 'left']:
            raise Exception('You must pick a valid side among "top", "right", "bottom", "left"')
        
        remaining_offsets = ['top', 'right', 'bottom', 'left'] - offset.keys()
        for off in remaining_offsets:
            offset[off] = 0

        self.side_borders.append(
            {'side': side, 'size': size, 'color': color, 'offset': offset}
        )
        return self
        

    # Re-returns the object with a border
    def with_border(self, size = 0.2, color = 0x000000, offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        self.add_border(size, color, offset)
        return self

    def __true_pos(self):
        return {'x1': self.x + self.left_margin, 'y1': self.y + self.top_margin, 'x2': self.x + self.left_margin + self.width + self.right_margin, 'y2': self.y + self.top_margin + self.height + self.bottom_margin }

    # Returns the list of objects of the PDF Styling
    # Note an Important Difference: classic borders take the original position and squish the object into the bounds of the border and its offset.
    # Single Borders operate by adjusting their offsets to a locked objects, the object remains fixed and the border is shifted.
    def render_as_flex_template_object(self):
        base_template_object = {
            'name': 'OBJECT', 'priority': self.priority,
            'x1': self.__true_pos()['x1'], 'x2': self.__true_pos()['x2'], 'y1': self.__true_pos()['y1'], 'y2': self.__true_pos()['y2']
        }
        return [base_template_object]
    
    def render_borders(self):
        all_sub_template_objects = []
        if self.total_border_size != 0:
            border = {
                'name': 'BORDER', 'priority': self.priority - 1, 'type': 'B', 
                'size': self.total_border_size, 'foreground': self.total_border_color, 
                'x1': self.__true_pos()['x1'] - self.total_border_offset['left'], 'x2': self.__true_pos()['x2'] + self.total_border_offset['right'],
                'y1': self.__true_pos()['y1'] - (self.total_border_offset['top'] + 0.2), 'y2': self.__true_pos()['y2'] + self.total_border_offset['bottom']
            }
            all_sub_template_objects.append(border)

        generated_side_borders = []
        for border in self.side_borders:
            if border['side'] in ['top', 'bottom']:
                y_pos = self.__true_pos()['y1'] - border['offset']['top'] if border['side'] == 'top' else self.__true_pos()['y2'] + border['offset']['bottom']
                line = {
                    'name': f'SIDE_BORDER_{border['side'].upper()}', 'priority': self.priority + 1, 'type': 'L',
                    'size': border['size'], 'foreground': border['color'],
                    'x1': self.__true_pos()['x1'] - border['offset']['left'], 'y1': y_pos, 'y2': y_pos,
                    'x2': self.__true_pos()['x2'] + border['offset']['right']# - (self.__true_pos()['x1'] - border['offset']['left'])
                }
                generated_side_borders.append(line)
            else:
                x_pos = self.__true_pos()['x1'] - border['offset']['left'] if border['side'] == 'left' else self.__true_pos()['x2'] + border['offset']['right']
                line = {
                    'name': f'SIDE_BORDER_{border['side'].upper()}', 'priority': self.priority + 1, 'type': 'L',
                    'size': border['size'], 'foreground': border['color'],
                    'x1': x_pos, 'x2': x_pos, 'y1': self.__true_pos()['y1'] - border['offset']['top'],
                    'y2': self.__true_pos()['y2'] + border['offset']['bottom']# - (self.__true_pos()['y1'] - border['offset']['top']),
                }
                generated_side_borders.append(line)
        for b in generated_side_borders:
            all_sub_template_objects.append(b)

        return all_sub_template_objects


# MARK: Stacks
class Stack(Document_Object):
    def __init__(self, x, y, width, height, priority, children, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.children = children
        self.padding = padding

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
    def __init__(self, x, y, width, height, priority, children, inner_gap: int = 0.0, gap_filler: Document_Object = None, vertical = True,
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}):
        super().__init__(x, y, width, height, priority, children, margin, padding)
        self.inner_gap = inner_gap
        self.gap_filler = gap_filler
        self.vertical = vertical

        self.width, self.height = self.get_size()

    # Basically the same code as the rendering one, but only does calculations and gets attributes, no setting
    def get_size(self):
        if self.vertical:
            axis, close_side, far_side, size = ('y', 'top', 'bottom', 'height')
        else:
            axis, close_side, far_side, size = ('x', 'left', 'right', 'width')

        # Defining the Initial Positions
        axis_init = getattr(self, f'{close_side}_padding') + getattr(self, axis) + getattr(self, f'{close_side}_margin')
        axis_increment = axis_init

        for i, child in enumerate(self.children):

            axis_increment += getattr(child, f'{close_side}_margin') + child.total_border_offset[close_side] + getattr(child, size) + getattr(child, f'{far_side}_margin') + child.total_border_offset[far_side] + self.inner_gap

        if self.vertical:
            final_size = (self.width, axis_increment - axis_init - self.inner_gap)
        else:
            final_size = (axis_increment - axis_init - self.inner_gap, self.height)

        return final_size
    
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

            if not(self.gap_filler is None) and i < len(self.children) - 1:
                filler = copy.deepcopy(self.gap_filler)
                setattr(filler, axis, axis_increment + getattr(filler, axis) + getattr(child, size) + getattr(filler, f'{close_side}_margin') + child.total_border_offset[close_side] + child.total_border_offset[far_side])
                setattr(filler, locked_axis, locked_offset + getattr(filler, locked_axis) + getattr(filler, f'{locked_close_side}_margin'))
                all_template_objects += filler.render_item_as_flex_template_objects()
            
            axis_increment = getattr(child, axis) + getattr(child, f'{close_side}_margin') + child.total_border_offset[close_side] + getattr(child, size) + getattr(child, f'{far_side}_margin') + child.total_border_offset[far_side] + self.inner_gap

        setattr(self, size, axis_increment - axis_init - self.inner_gap) # Updating the size of the Stack

        all_template_objects += self.render_borders()

        return all_template_objects


# MARK: HStack
class HStack(AlignedStack):
    def __init__(self, x, y, width, height, priority, children, inner_gap = 0.0, gap_filler: Document_Object = None, 
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, children, inner_gap, gap_filler, False, margin, padding)
    
    def render_item_as_flex_template_objects(self):
        return super().render_item_as_flex_template_objects()


# MARK: VStack
class VStack(AlignedStack):
    def __init__(self, x, y, width, height, priority, children, inner_gap = 0, gap_filler = None, 
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, padding: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, children, inner_gap, gap_filler, True, margin, padding)

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
        return all_template_objects + self.render_borders()
    

#MARK: Table
# Currently the borders do not work
# You cannot use 'with_margin' for the table just yet.
class Table(Stack):
    def __init__(self, x, y, width, height, priority, children, size: tuple, x_gap, y_gap, inner_borders = None, 
                 margin: dict = { 'top': 0,'right': 0,'bottom': 0,'left': 0 }, padding: dict = { 'top': 0,'right': 0,'bottom': 0,'left': 0 }):
        super().__init__(x, y, width, height, priority, children, margin, padding)
        self.size = size
        self.x_gap, self.y_gap = (x_gap, y_gap)
        self.innner_borders = inner_borders

    def render_item_as_flex_template_objects(self):
        if len(self.children) == 0:
            raise Exception("You cannot have an empty stack")
        if len(self.size) != 2:
            raise Exception("Your size tuple must define a 2D matrix structure")
        if math.prod(self.size) < len(self.children):
            raise Exception('You cannot have more children than the input size permits')
        
        children_2d = to_matrix(self.children, self.size[0])

        all_children_rows = []
        for child_row in children_2d:
            
            max_height = max([child.height for child in child_row])

            col_stack = HStack(0, 0, 0, max_height, 0, child_row, self.x_gap)
            all_children_rows.append(col_stack)

        final_row_stack = VStack(self.x, self.y, self.width, self.height, self.priority, all_children_rows, self.y_gap, None, self.margin, self.padding)
        self.width = max([row.width for row in all_children_rows])
        self.height = final_row_stack.height

        return final_row_stack.render_item_as_flex_template_objects() + self.render_borders()



# MARK: Text
class Text(Document_Object):
    def __init__(self, text: str, font_size: float, x, y, width, height, priority, font = 'helvetica', align = 'L', multiline = False, underline = False, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, link = ''):
        super().__init__(x, y, width, height, priority, margin)
        self.text = text
        self.font = font
        self.align = align
        self.font_size = font_size
        self.multiline = multiline
        self.underline = underline
        self.link = link
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
        base_template_object['link'] = self.link

        return [base_template_object] + super().render_as_flex_template_object()[1:] + self.render_borders()
    

# MARK: Lines
class Line(Document_Object):
    def __init__(self, x, y, width, height, priority, size = 0.2, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.size = size

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'L'
        base_template_object['size'] = self.size

        return [base_template_object] + self.render_borders()
    
    def __repr__(self):
        return f'{(self.x, self.y, self.width, self.height)}, size = {self.size}, margin = {(self.margin['top'], self.margin['right'], self.margin['bottom'], self.margin['left'])}'
    
class HLine(Line):
    def __init__(self, x, y, width, priority, size = 0.2, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, 0, priority, size, margin)

    def render_item_as_flex_template_objects(self):
        return super().render_item_as_flex_template_objects()

class VLine(Line):
    def __init__(self, x, y, height, priority, size = 0.2, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, 0, height, priority, size, margin)

    def render_item_as_flex_template_objects(self):
        return super().render_item_as_flex_template_objects()
    

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

def to_matrix(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


# MARK: Testing
full_page_stack_2 = Table(0, 0, 0, 0, 0, [
    VStack(0, 0, 78.5, 0, 0, [
        Text('The Walks for Dogs Foundation', 11, 0, 0, 78.5, 5, 0),
        Text('Created a non-profit organization to allow students to improve their community while getting sought after community service hours', 8, 0, 0, 78.5, 3, 0, multiline = True)
    ]),
    VStack(0, 0, 78.5, 0, 0, [
        Text('The Walks for Dogs Foundation', 11, 0, 0, 78.5, 5, 0),
        Text('Created a non-profit organization to allow students to improve their community while getting sought after community service hours', 8, 0, 0, 78.5, 3, 0, multiline = True)
    ]),
    VStack(0, 0, 78.5, 0, 0, [
        Text('The Walks for Dogs Foundation', 11, 0, 0, 78.5, 5, 0),
        Text('Created a non-profit organization to allow students to improve their community while getting sought after community service hours', 8, 0, 0, 78.5, 3, 0, multiline = True)
    ]),
    VStack(0, 0, 78.5, 0, 0, [
        Text('The Walks for Dogs Foundation', 11, 0, 0, 78.5, 5, 0),
        Text('Created a non-profit organization to allow students to improve their community while getting sought after community service hours', 8, 0, 0, 78.5, 3, 0, multiline = True)
    ])
], (2, 2), 5, 9, margin = {'top': 20, 'left': 20}).with_border(0.2)#.add_single_border('left', 0.4)

testing_stack = VStack(0, 0, 78.5, 0, 0, [
    Text('The Walks for Dogs Foundation', 11, 0, 0, 78.5, 5, 0),
    Text('Created a non-profit organization to allow students to improve their community while getting sought after community service hours', 8, 0, 0, 78.5, 3, 0, multiline = True)
]).with_margin({'top': 20, 'left': 20})


testing_text = Text('The Walks for Dogs Foundation', 11, 0, 0, 78.5, 9, 0).with_margin({'top': 20, 'left': 20}).with_border(0.2, offset={'left': 2})#.add_single_border('left', 0.2, 0)
testing_offset = {'left': 2, 'right': 2, 'bottom': 0}
testing_bottom_border = HLine(testing_text.x + testing_text.left_margin - testing_offset['left'], 
                              testing_text.y + testing_text.top_margin + testing_text.height + testing_offset['bottom'], 
                              testing_text.width + testing_offset['left'] + testing_offset['right'], 
                              0, 0.3)

work_stack = VStack(0, 0, 150, 0, 0, [
    Text('DEC 2024', 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_border(0.3),
    VStack(6, 0, 140, 0, 0, [
        Text('Research Assistant', 16, 0, 0, 134, 6, 0, 'helvetica').with_margin({'top': 1}),
        Text('The Central Bank of Armenia', 12, 0, 0, 134, 4, 0, 'helvetica'),
            VStack(4, 0, 131, 0, 0, [
                Text(x, 8, 0, 0, 126, 3, 0) for x in ['Point 1', 'Point 2', 'Point 3']
            ], 0.8).with_margin({'top': 0.5})
        ]).with_border(0.3).add_single_border('left', 1, 0),
    Text('OCT 2024', 8, 0, 0, 18, 5, 0, 'dejavu-sans-mono', 'C').with_border(0.3).with_margin({'top': 1.5}),
]).with_margin({'left': 5})

# for obj in full_page_stack_2.render_item_as_flex_template_objects():
#     print(obj.__repr__())

pdf = FPDF(orientation = 'portrait', format = 'A4')
pdf.add_page()
pdf.add_font('dejavu-sans-mono', style = '', fname = 'dejavu-sans-mono/DejaVuSansMono.ttf')

templ = FlexTemplate(pdf, elements = work_stack.render_item_as_flex_template_objects())# + testing_bottom_border.render_item_as_flex_template_objects())
templ.render(offsetx = 0, offsety = 0, rotate = 0, scale = 1)

pdf.set_margin(0)
pdf.output('Testing Results/testing_template_version_2.pdf')