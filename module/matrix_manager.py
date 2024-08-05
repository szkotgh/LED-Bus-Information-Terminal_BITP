import os
import sys
import time

# import pillow
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:
    sys.exit(f'pillow module import failed. {e}\n')
# import module.utils
try:
    import module.utils as utils
except Exception as e:
    sys.exit(f'module.utils module import failed : {e}')
# import rgbmatrix
# try:
#     from rgbmatrix import RGBMatrix, RGBMatrixOptions
# except Exception as e:
#     sys.exit(f'RGBMatrix module import failed : {e}')

class MatrixManager:
    def __init__(self, station_datas: dict | None = []) -> None:
        # # Configuration for the matrix
        # # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/include/led-matrix.h#L57
        # options = RGBMatrixOptions()
        # options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
        # options.rows = 32
        # options.cols = 64
        # options.chain_length = 7
        # #https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/examples-api-use#remapping-coordinates
        # options.pixel_mapper_config = "V-mapper;Rotate:90"
        # options.pwm_lsb_nanoseconds = 100
        # options.gpio_slowdown = 5
        # options.pwm_bits = 5
        # options.pwm_dither_bits = 0
        # options.show_refresh_rate = False
        # self.matrix = RGBMatrix(options = options)
        
        # self.size = (self.matrix.width, self.matrix.height)
        self.size = (224, 64)
        
        self.font8  = ImageFont.truetype(os.path.join('fonts', 'SCDream4.otf'), 8)
        self.font10 = ImageFont.truetype(os.path.join('fonts', 'SCDream4.otf'), 11)
        self.font12 = ImageFont.truetype(os.path.join('fonts', 'SCDream5.otf'), 12)
        self.font14 = ImageFont.truetype(os.path.join('fonts', 'SCDream4.otf'), 14)
        self.font16 = ImageFont.truetype(os.path.join('fonts', 'SCDream5.otf'), 16)
        self.font26 = ImageFont.truetype(os.path.join('fonts', 'SCDream8.otf'), 26)
        
        self.station_datas = station_datas
        
    def update_station_info(self, station_datas: dict) -> None:
        self.station_datas = station_datas
    
    def get_text_width(self, text, font) -> int:
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]  # Right - Left
        return text_width
    
    def show_test_page(self):
        display = Image.new('RGB', self.size, color = 'black')
        draw = ImageDraw.Draw(display)
        
        delay_time = 1
        test_color = ["red", "lime", "blue", "white"]
        
        for color in test_color:
            draw.rectangle(((0, 0), (self.size[0], self.size[1])), color)
            self.refresh(display)
            time.sleep(delay_time)
        
        draw.rectangle(((0, 0), (self.size[0], self.size[1])), "black")
        self.refresh(display)
        
    def show_text_page(self, set_text: str | list = ""):
        canvas = Image.new('RGB', self.size, "black")
        draw = ImageDraw.Draw(canvas)
        draw.fontmode = "1"

        if isinstance(set_text, str):
            draw.text((1, 1), str(set_text), "white", self.font12)
        elif isinstance(set_text, list):
            x_loca_row = [0, 13, 26, 39, 51]
            for i, text in enumerate(set_text):
                if i > 4:
                    break
                draw.text((1, x_loca_row[i]), str(text), "white", self.font12)

        self.refresh(canvas)
    
    def duk_50th_anniversary_page(self):
        for i in range(1, -460, -1):
            text = [
                "덕영고 50주년!!",
                "50년의 빛나는 역사, 미래를 향한 무궁한 발전을 기원합니다."
            ]
            
            canvas = Image.new('RGB', self.size, "black")
            draw = ImageDraw.Draw(canvas)
            ## 안티에일리어싱 해제
            draw.fontmode="1"
            
            draw.text((1, 1), text[0], "white", self.font26)
            draw.text((i, 32), text[1], "white", self.font26)
            
            self.refresh(canvas)
            
            if i == 1:
                time.sleep(1)
            time.sleep(0.005)
        time.sleep(1.5)
    
    def test(self):
        display = Image.new('RGB', self.size, color = 'black')
        draw = ImageDraw.Draw(display)
        
        draw.fontmode = "1"
        draw.text([10, 10], "Hello World", fill="white", font=ImageFont.load_default())
        
        self.refresh(display)
        pass    
    
    def refresh(self, display):
        # save image
        display.save('./display.png')