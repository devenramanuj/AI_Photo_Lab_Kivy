import os

# Kivy ને OpenGL બેકએન્ડનો ઉપયોગ કરવા માટે ફોર્સ કરો
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2' 

# import kivy 
# ... (બાકીનો કોડ જેમ છે તેમ રાખો)import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.lang import Builder
from kivy.core.image import Image as CoreImage
from io import BytesIO
import os
import threading

# Pillow Libraries (પહેલાની જેમ જ)
from PIL import Image, ImageEnhance, ImageOps

# AI Library (rembg) - Check
try:
    from rembg import remove
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    
# Kivy નો UI (KV Language) - Size_Hint સુધારેલા છે
kv_code = """
<MobileEditorWidget>:
    orientation: 'horizontal'
    # MobileEditorWidget (મુખ્ય BoxLayout) આખી વિન્ડો ભરી દેશે.
    
    # 1. ડાબી બાજુ: ફોટો ડિસ્પ્લે
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        size_hint_x: 0.7  # 70% પહોળાઈ
        
        KivyImage:
            id: photo_display
            # size_hint default (1, 1) છે, જે આ BoxLayout માં બાકીની જગ્યા ભરી દેશે.
            allow_stretch: True
            keep_ratio: True
        
        Button:
            text: '📂 Load New Image'
            size_hint_y: None
            height: 40
            on_press: root.load_image(default=False)

    # 2. જમણી બાજુ: કંટ્રોલ પેનલ
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 15
        size_hint_x: 0.3  # 30% પહોળાઈ
        canvas.before:
            Color:
                rgb: 0.15, 0.15, 0.15
            Rectangle:
                size: self.size
                pos: self.pos
                
        Label:
            text: 'ADJUSTMENTS'
            size_hint_y: None
            height: 30
            
        # Brightness Slider (બાકીના Widgets પણ size_hint: None વાપરે છે અથવા ડિફોલ્ટ છે)
        Label:
            text: 'Brightness'
            size_hint_y: None
            height: 20
        Slider:
            id: bright_slider
            min: 0.1
            max: 2.0
            value: 1.0
            step: 0.1
            on_value: root.apply_edits()
            
        # Contrast Slider
        Label:
            text: 'Contrast'
            size_hint_y: None
            height: 20
        Slider:
            id: contrast_slider
            min: 0.1
            max: 2.0
            value: 1.0
            step: 0.1
            on_value: root.apply_edits()

        # --- Filter Buttons ---
        Label:
            text: 'FILTERS'
            size_hint_y: None
            height: 30
            
        BoxLayout:
            size_hint_y: None
            height: 40
            padding: 5
            spacing: 5
            Button:
                text: 'B & W'
                on_press: root.apply_bw()
            Button:
                text: 'Sepia'
                on_press: root.apply_sepia()
            Button:
                text: 'Rotate'
                on_press: root.rotate_image()
                
        Button:
            text: '❌ Reset All'
            size_hint_y: None
            height: 40
            on_press: root.reset_image()
                
        Button:
            text: '💾 Save Image'
            size_hint_y: None
            height: 50
            on_press: root.save_image()
"""

class MobileEditorWidget(BoxLayout):
    
    def __init__(self, **kwargs):
        super(MobileEditorWidget, self).__init__(**kwargs)
        self.original_image = None
        self.working_image_pil = None
        # અહીં Kivy ને તૈયાર થવાનો થોડો સમય આપવા માટે Clock.schedule_once વાપરીએ
        Clock.schedule_once(lambda dt: self.load_image(default=True), 0.1) 
        
    def update_kivy_display(self, pil_img):
        # ... (કોડ પહેલાની જેમ જ) ...
        if not pil_img: return
        img_buffer = BytesIO()
        pil_img.save(img_buffer, format='png')
        img_buffer.seek(0)
        kivy_img = CoreImage(img_buffer, ext='png')
        self.ids.photo_display.texture = kivy_img.texture
        self.ids.photo_display.source = '' 

    def load_image(self, default=False):
        # ... (કોડ પહેલાની જેમ જ - dummy_image.jpg સાથે) ...
        path = 'dummy_image.jpg' 
        if default:
            if not os.path.exists(path):
                try:
                    Image.new('RGB', (300, 300), color = 'red').save(path)
                except Exception as e:
                    print(f"Error creating default image: {e}")
            
        if os.path.exists(path):
            self.original_image = Image.open(path).convert("RGB")
            self.working_image_pil = self.original_image.copy()
            self.update_kivy_display(self.working_image_pil)
            
    # બાકીના બધા methods (reset_image, apply_edits, filters, save_image)
    # જેમ છે તેમ રાખો, તેમાં કોઈ ફેરફાર કરવાની જરૂર નથી.
    def reset_image(self):
        if self.original_image:
            self.ids.bright_slider.value = 1.0
            self.ids.contrast_slider.value = 1.0
            self.working_image_pil = self.original_image.copy()
            self.update_kivy_display(self.working_image_pil)

    def apply_edits(self, *args):
        if not self.working_image_pil: return
        bright_val = self.ids.bright_slider.value
        contrast_val = self.ids.contrast_slider.value
        temp_img = self.working_image_pil.copy()
        temp_img = ImageEnhance.Brightness(temp_img).enhance(bright_val)
        temp_img = ImageEnhance.Contrast(temp_img).enhance(contrast_val)
        self.update_kivy_display(temp_img)
        
    def apply_filter_to_working_image(self, img_process_func):
        if not self.working_image_pil: return
        self.working_image_pil = img_process_func(self.working_image_pil)
        self.ids.bright_slider.value = 1.0
        self.ids.contrast_slider.value = 1.0
        self.update_kivy_display(self.working_image_pil)
        
    def apply_bw(self):
        self.apply_filter_to_working_image(lambda img: img.convert("L").convert("RGB"))

    def apply_sepia(self):
        def sepia_func(img):
            gray = img.convert("L")
            return ImageOps.colorize(gray, "#3e2723", "#fff3e0").convert("RGB") 
        self.apply_filter_to_working_image(sepia_func)

    def rotate_image(self):
        self.apply_filter_to_working_image(lambda img: img.rotate(-90, expand=True))
        
    def save_image(self):
        if self.working_image_pil:
            try:
                self.working_image_pil.save('final_output.png')
                print("Image saved as final_output.png in project folder.")
            except Exception as e:
                print(f"Save error: {e}")
            
class MobileEditorApp(App):
    def build(self):
        self.title = 'Kivy Mobile Editor'
        return Builder.load_string(kv_code)

if __name__ == '__main__':
    MobileEditorApp().run()