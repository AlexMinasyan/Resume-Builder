from fpdf import FlexTemplate, FPDF
import copy

# MARK: Document Object
# Im not a fan of the has_borders construction.
class Document_Object():
    def __init__(self, x: float, y: float, width: float, height: float, priority: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.priority = priority
        self.is_single_border = None

        self.top_margin, self.right_margin, self.bottom_margin, self.left_margin = (0, 0, 0, 0)
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

    def remove_margin(self):
        self.top_margin, self.right_margin, self.bottom_margin, self.left_margin = (0, 0, 0, 0)

    def add_border(self, size = 0.2, color = 0x000000, offset = {'top': 0, 'right': 0, 'bottom': 0, 'left' : 0}):
        if not set(offset.keys()).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys")
        
        self.is_single_border = True
        self.total_border_size = size
        self.total_border_color = color
        self.total_border_offset = offset

    # For borders, excepts a dictionary of 'top', 'right', 'bottom', and 'left' keys with values being an tuple of (int, string) <- (width, color)
    # def add_borders(self, borders):
    #     if not set(borders.keys()).issubset(set('top', 'right', 'bottom', 'left')):
    #         raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and on others keys")
        
    #     self.has_borders = True
    #     self.top_border_size, self.top_border_color = borders['top'] if borders['top'] else (None, None)
    #     self.right_border_size, self.right_border_color = borders['right'] if borders['right'] else (None, None)
    #     self.bottom_border_size, self.bottom_border_color = borders['bottom'] if borders['bottom'] else (None, None)
    #     self.left_border_size, self.left_border_color = borders['left'] if borders['left'] else (None, None)

    def render_as_flex_template_object(self):
        base_template_object = {
            'name': 'OBJECT_1', 'priority': self.priority,
            'x1': self.x + self.left_margin, 'x2': self.x + self.width + self.right_margin, 'y1': self.y + self.top_margin, 'y2': self.y + self.height + self.bottom_margin
        }
        all_sub_template_objects = [base_template_object]

        if self.is_single_border is True:
            all_sub_template_objects.append({
                'name': 'BORDER_1', 'priority': self.priority - 1, 'type': 'B', 
                'size': self.total_border_size, 'foreground': self.total_border_color, 
                'x1': self.x, 'x2': self.x + self.width + self.total_border_offset['right'] + self.total_border_offset['left'],
                'y1': self.y, 'y2': self.y + self.height + self.total_border_offset['top'] + self.total_border_offset['bottom']
            })
            base_template_object['x1'] += self.total_border_offset['left']
            base_template_object['x2'] += self.total_border_offset['left']
            base_template_object['y1'] += self.total_border_offset['top'] + 0.2
            base_template_object['y2'] += self.total_border_offset['top'] + 0.2

        # elif self.is_single_border is False:

        return all_sub_template_objects

# MARK: Stacks
class Stack(Document_Object):
    def __init__(self, x, y, width, height, priority, children, inner_gap = 0.0, gap_filler: Document_Object = None):
        super().__init__(x, y, width, height, priority)
        self.children = children
        self.inner_gap = inner_gap
        self.gap_filler = gap_filler

        self.top_padding, self.right_padding, self.bottom_padding, self.left_padding = (0, 0, 0, 0)

    def set_padding(self, padding): # For padding, I can just have the render add margin to the children...
        if not set(padding).issubset({'top', 'right', 'bottom', 'left'}):
            raise Exception("you must specific at least one of 'top', 'right', 'bottom', or 'left' and no others keys")
        
        self.top_padding = padding['top'] if 'top' in padding else 0
        self.right_padding = padding['right'] if 'right' in padding else 0
        self.bottom_padding = padding['bottom'] if 'bottom' in padding else 0
        self.left_padding = padding['left'] if 'left' in padding else 0

class HStack(Stack):
    def __init__(self, x, y, width, height, priority, children, inner_gap = 0.0, gap_filler: Document_Object = None):
        super().__init__(x, y, width, height, priority, children, inner_gap, gap_filler)

    def render_item_as_flex_template_objects(self):
        if len(self.children) == 0:
            raise Exception("You cannot have an empty stack")

        x = self.left_padding + self.x + self.left_margin
        y_offset = self.top_padding + self.y + self.top_margin
        all_template_objects = []
        for i, child in enumerate(self.children):
            child.x = x
            child.y = y_offset
            all_template_objects += child.render_item_as_flex_template_objects()

            if not (self.gap_filler is None) and (i < len(self.children) - 1):
                filler = copy.deepcopy(self.gap_filler)
                filler.x = x + filler.x + child.width + filler.left_margin + child.total_border_offset['left'] + child.total_border_offset['right']
                filler.y = filler.y + y_offset + filler.top_margin
                all_template_objects += filler.render_item_as_flex_template_objects()

            x += child.width + self.inner_gap + child.right_margin + child.total_border_offset['left'] + child.total_border_offset['right']
        return all_template_objects

class VStack(Stack):
    def __init__(self, x, y, width, height, priority, children, inner_gap, gap_filler):
        super().__init__(x, y, width, height, priority, children, inner_gap, gap_filler)

    def render_item_as_flex_template_objects(self):
        if len(self.children) == 0:
            raise Exception("You cannot have an empty stack")

        x_offset = self.left_padding + self.x + self.left_margin
        y = self.top_padding + self.y + self.top_margin
        all_template_objects = []
        for i, child in enumerate(self.children):
            child.x = x_offset
            child.y = y
            all_template_objects += child.render_item_as_flex_template_objects()

            if not (self.gap_filler is None) and (i < len(self.children) - 1):
                filler = copy.deepcopy(self.gap_filler)
                filler.y = y + filler.y + child.height + filler.top_margin + child.total_border_offset['top'] + child.total_border_offset['bottom']
                filler.x = filler.x + x_offset + filler.left_margin
                all_template_objects += filler.render_item_as_flex_template_objects()

            y += child.height + self.inner_gap + child.bottom_margin + child.total_border_offset['top'] + child.total_border_offset['bottom']
        return all_template_objects

# MARK: Text
class Text(Document_Object):
    def __init__(self, text: str, font_size: float, x, y, width, height, priority, font = 'helvetica', align = 'L', multiline = False, underline = False):
        super().__init__(x, y, width, height, priority)
        self.text = text
        self.font = font
        self.align = align
        self.font_size = font_size
        self.multiline = multiline
        self.underline = underline

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
    def __init__(self, x, y, width, priority, size = 0.2):
        super().__init__(x, y, width, 0, priority)
        self.size = size

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'L'
        base_template_object['size'] = self.size

        return [base_template_object]

class VLine(Document_Object):
    def __init__(self, x, y, height, priority, size = 0.2):
        super().__init__(x, y, 0, height, priority)
        self.size = size

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'L'
        base_template_object['size'] = self.size
        
        return [base_template_object]
# MARK: Box  
class Box(Document_Object): 
    def __init__(self, x, y, width, height, priority, size = 0.2):
        super().__init__(x, y, width, height, priority)
        self.size = size

    def render_item_as_flex_template_objects(self):
        base_template_object = super().render_as_flex_template_object()[0]
        base_template_object['type'] = 'B'
        base_template_object['size'] = self.size
        
        return [base_template_object]


# MARK: Testing
full_page_hstack = HStack(0, 0, 210, 297, 0, [
    Box(0, 0, 50, 297, 0), Box(50, 0, 160, 297, 0)
], gap_filler = VLine(0, 0, 297, 0, 0.1))

pdf = FPDF(orientation = 'portrait', format = 'A4')
pdf.add_page()

templ = FlexTemplate(pdf, elements = full_page_hstack.render_item_as_flex_template_objects())
templ.render(offsetx = 0, offsety = 0, rotate = 0, scale = 1)

pdf.set_margin(0)
pdf.output('testing_template_version.pdf')