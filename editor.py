import tkinter as tk
from tkinter import filedialog, messagebox, Scale, colorchooser
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
import threading

# AI લાઈબ્રેરી ઇમ્પોર્ટ કરીએ
try:
    from rembg import remove
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class ProEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Photo Lab - Final Version")
        self.root.geometry("1200x800")
        
        # --- થીમ સેટિંગ્સ ---
        self.bg_color = "#0f0f0f"
        self.panel_color = "#1a1a1a"
        self.accent_color = "#00e5ff" # Neon Blue
        self.root.configure(bg=self.bg_color)

        self.original_image = None
        self.working_image = None
        self.final_image = None
        self.text_color = "white" # Default text color

        # --- હેડર ---
        header_frame = tk.Frame(root, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=10)
        tk.Label(header_frame, text="AI PHOTO LAB", font=("Impact", 28), 
                 bg=self.bg_color, fg=self.accent_color).pack()

        # --- મેઈન લેઆઉટ ---
        main_frame = tk.Frame(root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # 1. ડાબી બાજુ: ફોટો (Canvas)
        self.image_label = tk.Label(main_frame, text="ફોટો ઓપન કરો...", 
                                    bg="black", fg="#333", font=("Arial", 14))
        self.image_label.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)

        # 2. જમણી બાજુ: કંટ્રોલ પેનલ
        controls_frame = tk.Frame(main_frame, bg=self.panel_color, width=350, relief=tk.RAISED, bd=2)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # --- ફાઈલ મેનેજમેન્ટ ---
        file_frame = tk.Frame(controls_frame, bg=self.panel_color)
        file_frame.pack(fill=tk.X, pady=5)
        tk.Button(file_frame, text="📂 Open Image", command=self.open_image, bg="#333", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="💾 Save Image", command=self.save_image, bg="#2e7d32", fg="white", width=15).pack(side=tk.LEFT, padx=5)

        # --- AI SECTION ---
        self.build_ai_section(controls_frame)
        
        # --- CROP & ROTATE ---
        self.build_crop_section(controls_frame)

        # --- TEXT EDITOR ---
        self.build_text_section(controls_frame)

        # --- ADJUSTMENTS ---
        self.build_adjustment_section(controls_frame)

        # Reset
        tk.Button(controls_frame, text="❌ Reset All", command=self.reset_image, bg="#d32f2f", fg="white").pack(fill=tk.X, padx=10, pady=15)

        # સ્ટેટસ બાર
        self.status_label = tk.Label(root, text="Ready", bg=self.bg_color, fg="white", anchor="w")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=10)

        self.bright_val = 1.0
        self.contrast_val = 1.0

    # --- UI SUB-ROUTINES ---
    def build_ai_section(self, parent):
        # AI SECTION
        tk.Label(parent, text="--- ARTIFICIAL INTELLIGENCE ---", bg=self.panel_color, fg=self.accent_color, font=("Arial", 10, "bold")).pack(pady=(15, 5))
        if AI_AVAILABLE:
            self.ai_btn = tk.Button(parent, text="🤖 REMOVE BACKGROUND\n(AI Magic)", command=self.start_bg_removal, 
                      bg="#6200ea", fg="white", font=("Arial", 11, "bold"), height=2)
            self.ai_btn.pack(fill=tk.X, padx=10, pady=5)
            tk.Button(parent, text="✨ Auto Enhance Colors", command=self.auto_adjust, 
                      bg="#ff6d00", fg="white").pack(fill=tk.X, padx=10, pady=5)
        else:
            tk.Label(parent, text="⚠ rembg લાઈબ્રેરી ઇન્સ્ટોલ નથી!", bg=self.panel_color, fg="red").pack(pady=10)

    def build_crop_section(self, parent):
        # CROP & ROTATE
        tk.Label(parent, text="--- CROP & ROTATE ---", bg=self.panel_color, fg="gray").pack(pady=(10, 5))
        crop_frame = tk.Frame(parent, bg=self.panel_color)
        crop_frame.pack(fill=tk.X, padx=10)

        tk.Button(crop_frame, text="Crop 16:9", command=lambda: self.apply_crop(16/9), width=10).pack(side=tk.LEFT, padx=3)
        tk.Button(crop_frame, text="Crop Square", command=lambda: self.apply_crop(1), width=10).pack(side=tk.LEFT, padx=3)
        tk.Button(crop_frame, text="Rotate 90°", command=self.rotate_image, width=10).pack(side=tk.LEFT, padx=3)

    def build_text_section(self, parent):
        # TEXT EDITOR
        tk.Label(parent, text="--- ADD TEXT ---", bg=self.panel_color, fg="gray").pack(pady=(10, 5))
        
        self.text_entry = tk.Entry(parent, width=40, bg="#333", fg="white", insertbackground="white")
        self.text_entry.pack(padx=10)

        text_btn_frame = tk.Frame(parent, bg=self.panel_color)
        text_btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(text_btn_frame, text="🎨 Color", command=self.choose_color, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(text_btn_frame, text="Apply Text", command=self.apply_text, bg="#008080", fg="white", width=20).pack(side=tk.LEFT, padx=5)


    def build_adjustment_section(self, parent):
        # ADJUSTMENTS (Sliders)
        tk.Label(parent, text="--- MANUAL ADJUST ---", bg=self.panel_color, fg="gray").pack(pady=10)
        self.create_slider(parent, "Brightness", self.update_sliders)
        self.create_slider(parent, "Contrast", self.update_sliders)
        
    def create_slider(self, parent, label, cmd):
        tk.Label(parent, text=label, bg=self.panel_color, fg="white").pack()
        s = Scale(parent, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, 
                  bg=self.panel_color, fg=self.accent_color, command=lambda v, l=label: self.slider_change(l, v))
        s.set(1.0)
        s.pack(fill=tk.X, padx=10)
        return s

    # --- LOGIC ---

    # File and Display Logic
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.original_image = Image.open(file_path).convert("RGB") # Only RGB for Text/Draw
            self.reset_image()

    def reset_image(self):
        if self.original_image:
            self.working_image = self.original_image.copy()
            self.show_image(self.working_image)

    def show_image(self, img):
        img_copy = img.copy()
        img_copy.thumbnail((750, 600)) 
        self.display_image = ImageTk.PhotoImage(img_copy)
        self.image_label.config(image=self.display_image, text="")
        self.final_image = img 

    # CROP and ROTATE Logic
    def rotate_image(self):
        if self.working_image:
            self.working_image = self.working_image.rotate(-90, expand=True)
            self.show_image(self.working_image)

    def apply_crop(self, aspect_ratio):
        if not self.working_image: return
        w, h = self.working_image.size
        
        # મોટા ભાગની બાજુને આધારે ક્રોપ કરો
        if w / h > aspect_ratio: # ક્રોપ પહોળો છે
            new_h = int(w / aspect_ratio)
            top = (new_h - h) // 2
            bottom = h - top
            self.working_image = self.working_image.crop((0, top, w, h - top))
        else: # ક્રોપ ઊભો છે
            new_w = int(h * aspect_ratio)
            left = (new_w - w) // 2
            right = w - left
            self.working_image = self.working_image.crop((left, 0, w - left, h))

        self.show_image(self.working_image)


    # TEXT Logic
    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color")
        if color_code:
            self.text_color = color_code[1]
            self.status_label.config(text=f"Color selected: {self.text_color}", fg=self.text_color)

    def apply_text(self):
        if not self.working_image: return
        text_to_add = self.text_entry.get()
        if not text_to_add: return
        
        # ટેમ્પરરી ઈમેજ પર ટેક્સ્ટ એડ કરો
        draw = ImageDraw.Draw(self.working_image)
        try:
            # સિસ્ટમ ફોન્ટ વાપરીએ (Arial)
            font = ImageFont.truetype("arial.ttf", size=50)
        except IOError:
            # જો arial ન મળે તો ડીફોલ્ટ ફોન્ટ વાપરો
            font = ImageFont.load_default() 
        
        # ફોટાની મધ્યમાં ટેક્સ્ટ મૂકીએ
        w, h = self.working_image.size
        text_width, text_height = draw.textsize(text_to_add, font=font)
        
        draw.text(((w - text_width) // 2, (h - text_height) // 2), 
                  text_to_add, 
                  fill=self.text_color, 
                  font=font)
        
        self.show_image(self.working_image)


    # SLIDER Logic
    def slider_change(self, label, val):
        if label == "Brightness": self.bright_val = float(val)
        if label == "Contrast": self.contrast_val = float(val)
        self.update_sliders()

    def update_sliders(self):
        if self.working_image:
            # Sliders applied to the working image (text/crop will be preserved)
            temp = self.working_image.copy()
            temp = ImageEnhance.Brightness(temp).enhance(self.bright_val)
            temp = ImageEnhance.Contrast(temp).enhance(self.contrast_val)
            self.show_image(temp)

    # AI Logic (Simplified for final code)
    def start_bg_removal(self):
        if not self.original_image: return
        self.status_label.config(text="AI Processing... Please Wait", fg=self.accent_color)
        self.root.update()
        threading.Thread(target=self.process_ai).start()

    def process_ai(self):
        try:
            output = remove(self.original_image)
            self.working_image = output
            self.show_image(output)
            self.status_label.config(text="Done! Background Removed.", fg=self.accent_color)
        except Exception as e:
            messagebox.showerror("Error", f"AI Error: {e}")
            self.status_label.config(text="Error occurred", fg="red")

    def auto_adjust(self):
        if self.original_image:
            temp = ImageOps.autocontrast(self.original_image)
            self.working_image = ImageEnhance.Color(temp).enhance(1.3)
            self.show_image(self.working_image)
            self.status_label.config(text="Auto Enhance Applied!", fg="#ff6d00")

    def save_image(self):
        if self.final_image:
            file_type = ".png" if self.final_image.mode == 'RGBA' else ".jpg"
            save_path = filedialog.asksaveasfilename(defaultextension=file_type)
            if save_path:
                self.final_image.save(save_path)
                messagebox.showinfo("Saved", "ફોટો સેવ થઈ ગયો!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProEditor(root)
    root.mainloop()