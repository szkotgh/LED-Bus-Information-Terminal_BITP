from rgbmatrix import RGBMatrix
import modules.config as config
import modules.utils as utils
from modules.matrix_manager.pages import MatrixPages

Pages = MatrixPages()
matrix = RGBMatrix(options = config.MATRIX_OPTIONS)
MATRIX_SIZE = (matrix.width, matrix.height)

def refresh(display, status_prt: bool = True):    
    matrix.SetImage(display.convert('RGB'))

