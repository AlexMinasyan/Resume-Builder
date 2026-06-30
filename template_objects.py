# MARK: Packages
import copy, math
import PIL
from fpdf import FlexTemplate, FPDF
from enum import Enum

# MARK: Document Object
class BorderType(Enum):
    FULL = 'full'
    TOP = 'top'
    RIGHT = 'right'
    BOTTOM = 'bottom'
    LEFT = 'left'

class Border():
    def __init__(self, border_type: BorderType = BorderType.FULL, size: int = 0.2, color = 0x000000, offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        self.border_type = border_type
        self.size = size
        self.color = color
        self.offset = offset

        if not set(self.offset.keys()).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys.")

        self.offset['top'] = self.offset['top'] if 'top' in self.offset.keys() else 0
        self.offset['right'] = self.offset['right'] if 'right' in self.offset.keys() else 0
        self.offset['bottom'] = self.offset['bottom'] if 'bottom' in self.offset.keys() else 0
        self.offset['left'] = self.offset['left'] if 'left' in self.offset.keys() else 0

    def __getitem__(self, key):
        if key == 'size':
            return self.size
        if key == 'color':
            return self.color
        if key == 'offset':
            return self.offset
        if key == 'side':
            return self.border_type.value
        
    def __str__(self):
        return f'{self.border_type.value.capitalize()} - Border size: {self.size}), color: {self.color}, offset: ({tuple(self.offset.values())})'

# Note: Single Borders cannot have color so far, but that will be changed soon
class Document_Object():
    def __init__(self, x: float, y: float, width: float, height: float, priority: int,
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, link = ''):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.priority = priority
        self.margin = margin
        self.borders = []
        self.side_borders = []
        self.link = link

        self.set_margin(margin)
        self.total_border_size = 0
        self.total_border_color = 0
        self.total_border_offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}

    def set_margin(self, margin):
        if not set(margin.keys()).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys")
        
        self.top_margin = margin['top'] if 'top' in margin else 0
        self.right_margin = margin['right'] if 'right' in margin else 0
        self.bottom_margin = margin['bottom'] if 'bottom' in margin else 0
        self.left_margin = margin['left'] if 'left' in margin else 0

    def remove_margin(self):
        self.top_margin, self.right_margin, self.bottom_margin, self.left_margin = (0, 0, 0, 0)

    def with_margin(self, margin):
        self.set_margin(margin)
        return self

    def add_borders(self, *args: Border):
        for border in args:
            self.borders.append(border)     
    
    def with_borders(self, *args: Border):
        self.add_borders(*args)
        return self

    # Returns position adjusted for margin
    def __true_pos(self):
        return {'x1': self.x + self.left_margin, 'y1': self.y + self.top_margin, 'x2': self.x + self.left_margin + self.width + self.right_margin, 'y2': self.y + self.top_margin + self.height + self.bottom_margin }

    def add_link(self, link):
        self.link = link

    def with_link(self, link):
        self.add_link(link)
        return self

    # Returns the list of objects of the PDF Styling
    # Note an Important Difference: classic borders take the original position and squish the object into the bounds of the border and its offset.
    # Single Borders operate by adjusting their offsets to a locked objects, the object remains fixed and the border is shifted.
    def render_as_flex_template_object(self):
        base_template_object = {
            'name': 'OBJECT', 'priority': self.priority,
            'x1': self.__true_pos()['x1'], 'x2': self.__true_pos()['x2'], 'y1': self.__true_pos()['y1'], 'y2': self.__true_pos()['y2'],
            'link': self.link
        }
        return [base_template_object]

    # Renders all of the borders
    def render_borders(self): # Note: The `final_border` object can be changed to a `Box` or `Line` that is then rendered, may save space and be more organized
        all_sub_template_objects = []
        for border in self.borders:
            if border.border_type == BorderType.FULL:
                final_border = {
                    'name': 'BORDER', 'priority': self.priority - 1, 'type': 'B', 
                    'size': border['size'], 'foreground': border['color'], 
                    'x1': self.__true_pos()['x1'] - border['offset']['left'], 'x2': self.__true_pos()['x2'] + border['offset']['right'],
                    'y1': self.__true_pos()['y1'] - (border['offset']['top'] + 0.2), 'y2': self.__true_pos()['y2'] + border['offset']['bottom']
                }
            else:
                if border.border_type in [BorderType.TOP, BorderType.BOTTOM]:
                    y_pos = self.__true_pos()['y1'] - border['offset']['top'] if border['side'] == 'top' else self.__true_pos()['y2'] + border['offset']['bottom']
                    final_border = {
                        'name': f'SIDE_BORDER_{border['side'].upper()}', 'priority': self.priority + 1, 'type': 'L',
                        'size': border['size'], 'foreground': border['color'],
                        'x1': self.__true_pos()['x1'] - border['offset']['left'], 'y1': y_pos, 'y2': y_pos,
                        'x2': self.__true_pos()['x2'] + border['offset']['right']# - (self.__true_pos()['x1'] - border['offset']['left'])
                    }
                else:
                    x_pos = self.__true_pos()['x1'] - border['offset']['left'] if border['side'] == 'left' else self.__true_pos()['x2'] + border['offset']['right']
                    final_border = {
                        'name': f'SIDE_BORDER_{border['side'].upper()}', 'priority': self.priority + 1, 'type': 'L',
                        'size': border['size'], 'foreground': border['color'],
                        'x1': x_pos, 'x2': x_pos, 'y1': self.__true_pos()['y1'] - border['offset']['top'],
                        'y2': self.__true_pos()['y2'] + border['offset']['bottom']# - (self.__true_pos()['y1'] - border['offset']['top']),
                    }
            all_sub_template_objects.append(final_border)
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
    def __init__(self, text: str, font_size: float, x, y, width, height, priority, 
                 font = 'helvetica', align = 'L', font_color = 0x000000, 
                 multiline = False, underline = False, bold = False, italic = False,
                 margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}, link = ''):
        super().__init__(x, y, width, height, priority, margin)
        self.text = text
        self.font = font
        self.align = align
        self.font_size = font_size
        self.font_color = font_color

        self.multiline = multiline
        self.underline = underline
        self.bold = bold
        self.italic = italic

        # Later going to adjust height to include multiple lines
        # self.height = get_text_length(text, font, font_size)

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'T'
        base_template_object['text'] = self.text
        base_template_object['font'] = self.font
        base_template_object['align'] = self.align
        base_template_object['size'] = self.font_size
        base_template_object['foreground'] = self.font_color
        base_template_object['multiline'] = self.multiline
        base_template_object['underline'] = int(self.underline == True)
        base_template_object['bold'] = int(self.bold == True)
        base_template_object['italic'] = int(self.italic == True)
        base_template_object['link'] = self.link

        return [base_template_object] + super().render_as_flex_template_object()[1:] + self.render_borders()
    

# MARK: Lines
class Line(Document_Object):
    def __init__(self, x, y, width, height, priority, size = 0.2, color = 0x000000, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.size = size
        self.color = color

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'L'
        base_template_object['size'] = self.size
        base_template_object['foreground'] = self.color

        return [base_template_object] + self.render_borders()
    
    def __str__(self):
        return f'{(self.x, self.y, self.width, self.height)}, size = {self.size}, margin = {(self.margin['top'], self.margin['right'], self.margin['bottom'], self.margin['left'])}'
    
class HLine(Line):
    def __init__(self, x, y, width, priority, size = 0.2, color = 0x000000, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, 0, priority, size, color, margin)

    def render_item_as_flex_template_objects(self):
        return super().render_item_as_flex_template_objects()

class VLine(Line):
    def __init__(self, x, y, height, priority, size = 0.2, color = 0x000000, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, 0, height, priority, size, color, margin)

    def render_item_as_flex_template_objects(self):
        return super().render_item_as_flex_template_objects()
    

# MARK: Box  
class Box(Document_Object): 
    def __init__(self, x, y, width, height, priority, size = 0.2, color = 0x000000, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.size = size
        self.color = color

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'B'
        base_template_object['size'] = self.size
        base_template_object['foreground'] = self.color
        
        return [base_template_object]
    
# MARK: Image
class Image(Document_Object):
    def __init__(self, x, y, width, height, priority, image_link, margin: dict = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        super().__init__(x, y, width, height, priority, margin)
        self.image_link = image_link

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'I'
        base_template_object['text'] = self.image_link

        return [base_template_object]
    

# MARK: Some Extensions
def get_text_length(text, font, size):
    image_font = PIL.ImageFont.truetype(font, size)
    pxls = image_font.getlength(text)
    return px_to_mm(pxls)

def px_to_mm(px, dpi = 67):
    return (px * 25.4) / dpi

def to_matrix(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def image_size(path):
    im = PIL.Image.open(path)
    width, height = im.size
    return (width, height)


# MARK: Testing
if __name__=="__main__":
    testing_border_stack = Image(10, 10, 50, 50, 0, image_link = '2026-01-23 15.28.16.jpg')

    # for obj in full_page_stack_2.render_item_as_flex_template_objects():
    #     print(obj.__repr__())

    pdf = FPDF(orientation = 'portrait', format = 'A4')
    pdf.add_page()
    pdf.add_font('dejavu-sans-mono', style = '', fname = 'dejavu-sans-mono/DejaVuSansMono.ttf')

    templ = FlexTemplate(pdf, elements = testing_border_stack.render_item_as_flex_template_objects())# + testing_bottom_border.render_item_as_flex_template_objects())
    templ.render(offsetx = 0, offsety = 0, rotate = 0, scale = 1)

    pdf.set_margin(0)
    pdf.output('Testing Results/testing_template_version_2.pdf')