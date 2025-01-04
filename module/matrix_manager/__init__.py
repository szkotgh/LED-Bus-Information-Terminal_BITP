import module.config as config
from PIL import Image, ImageDraw, ImageFont

matrix = config.matrix

def show_test_page(self, _test_type: int = 0, _delay_time:int = 1):
    display = Image.new('RGB', self.size, color = 'black')
    draw = ImageDraw.Draw(display)
    test_color = ["red", "lime", "blue", "white"]
    if _test_type == 0:
        for color in test_color:
            draw.rectangle(((0, 0), (self.size[0], self.size[1])), color)
            self.refresh(display, status_prt=False)
            time.sleep(_delay_time)
    elif _test_type == 1:
        for i in range(0, self.size[0]):
            for j in range(0, self.size[1]):
                draw.point((i, j), test_color[(i+j) % 4])
            self.refresh(display, status_prt=False)
            time.sleep(0.01)
        time.sleep(_delay_time)
    elif _test_type == 2:
        for y in range(0, self.size[1], 7):
            draw.line((0, y, self.size[0], y), fill='white')
        for x in range(0, self.size[0], 9):
            draw.line((x, 0, x, self.size[1]), fill='white')
        self.refresh(display, status_prt=False)
        time.sleep(_delay_time)
    draw.rectangle(((0, 0), (self.size[0], self.size[1])), "black")
    self.refresh(display, status_prt=False)