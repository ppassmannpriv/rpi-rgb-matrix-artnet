from stupidArtnet import StupidArtnetServer;
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics;
import math;
import socket

localIp = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0];


### Fixture Setup
class Matrix:
    def __init__(self, width = 64, height = 32, panelCount = 1):
        self.width = width;
        self.height = height;
        self.panelCount = panelCount;
        self.pixelCount = width * height;
        self.channelCount = self.pixelCount * 3;
        self.universeCount = int(math.ceil(self.channelCount / 510));
        self.universeChannelLimit = int(math.ceil(510 / 3));
        self.universes = [];

fixture = Matrix();


### Server Setup
server = StupidArtnetServer();
universes = [];
universeListeners = [];

def receiveCallback(data, index):
    fixture.universes[index] = index;

for i in range(fixture.universeCount):
    ### initialize with empty tuples? lets see - could make a good init mode...
    fixture.universes.append(None);
    universeListeners.append(server.register_listener(i, callback_function = receiveCallback));


### RGB Matrix - display and matrix are 1:1 so no multiplexing... yet :D
number_of_rows_per_panel = 32;
number_of_columns_per_panel = 64;
number_of_panels = 1;
parallel = 1;

def rgbmatrix_options():
    options = RGBMatrixOptions();
    options.multiplexing = 0;
    options.row_address_type = 0;
    options.brightness = 100;
    options.rows = number_of_rows_per_panel;
    options.cols = number_of_columns_per_panel;
    options.chain_length = number_of_panels;
    options.parallel = parallel;
    options.hardware_mapping = 'adafruit-hat';
    options.inverse_colors = False;
    options.led_rgb_sequence = "RGB";
    options.gpio_slowdown = 2;
    options.pwm_lsb_nanoseconds = 150;
    options.show_refresh_rate = 0;
    options.disable_hardware_pulsing = True;
    options.scan_mode = 0;
    options.pwm_bits = 11;
    options.daemon = 0;
    options.drop_privileges = 0;

    return options;

options = rgbmatrix_options();
display = RGBMatrix(options=options);


### Execution Loop
executionState = True;

font = graphics.Font();
font.LoadFont('fonts/5x7.bdf');
textColor = graphics.Color(255, 0, 0);
graphics.DrawText(display, font, 0, 10, textColor, localIp);

while(executionState):
    x = 0;
    y = -1;
    for i in range(fixture.universeCount):
        buffer = server.get_buffer(universeListeners[i]);
        bufferSize = len(buffer);
        if bufferSize > 0:
            pixelRGBValues = [buffer[n:n+3] for n in range(0, 510, 3)];
            for pixelRGB in pixelRGBValues:
                if (x % fixture.width == 0):
                    x = 0;
                    y += 1;
                if (y > fixture.height - 1):
                    y = 0;
                display.SetPixel(x, y, pixelRGB[0], pixelRGB[1], pixelRGB[2]);
                x += 1;
