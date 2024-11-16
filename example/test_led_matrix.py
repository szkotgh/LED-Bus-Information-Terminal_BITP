from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

options = RGBMatrixOptions()
options.hardware_mapping = 'adafruit-hat'
options.rows = 32
options.cols = 64
options.chain_length = 7
# https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/examples-api-use#remapping-coordinates
options.pixel_mapper_config = "V-mapper;Rotate:90"
options.pwm_lsb_nanoseconds = 50
options.gpio_slowdown = 4
options.pwm_bits = 5
options.pwm_dither_bits = 0
options.show_refresh_rate = True

matrix = RGBMatrix(options=options)

color = graphics.Color(255, 255, 255)
font = graphics.Font()
font.LoadFont("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

def display_text():
    offscreen_canvas = matrix.CreateFrameCanvas()
    text = "Hello, LED Matrix!"
    pos_x = offscreen_canvas.width

    while True:
        offscreen_canvas.Clear()
        pos_x -= 1
        graphics.DrawText(offscreen_canvas, font, pos_x, 20, color, text)
        
        if pos_x + len(text) * 7 < 0:
            pos_x = offscreen_canvas.width

        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        time.sleep(0.05)

try:
    display_text()
except KeyboardInterrupt:
    pass
