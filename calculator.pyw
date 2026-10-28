import tkinter as tk
import pygame
import os
import numexpr as ne
import numpy as np
from tkinter import font as tkfont
from PIL import ImageTk, Image

class calculator:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap('icon.ico')
        self.root.title("калькулятор")  
        self.root.geometry("350x500")
        self.root.resizable(False, False)
        self.root.configure(bg='#2d2d2d')
        
        # Инициализация звуков
        pygame.mixer.init()
        self.sounds = {
            'click_down': None,
            'click_up': None,
            'error': None
        }
        self.load_sounds()
        self.set_volume(0.3)
        
        # Загрузка текстур
        self.textures = {}
        self.load_textures()
        
        # Поле ввода
        custom_font = tkfont.Font(size=18, weight='bold')
        self.entry = tk.Entry(
            root, font=custom_font, borderwidth=0,
            justify='right', bg='#3a3a3a', fg='white',
            insertbackground='white'
        )
        self.entry.grid(row=0, column=0, columnspan=5, padx=10, pady=20,
                       ipady=15, sticky="nsew")
        self.entry.insert(0, "0")
        
        # Кнопки
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('(', 1, 4),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3), (')', 2, 4),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3), ('⌫', 3, 4),
            ('C', 4, 0), ('0', 4, 1), ('.', 4, 2), ('+', 4, 3), ('=', 4, 4)
        ]
        
        self.buttons = {}
        for (text, row, col) in buttons:
            btn = tk.Button(
                root,
                image=self.textures.get(text, {}).get('normal'),  
                borderwidth=0,
                bg='#2d2d2d',
                activebackground='#2d2d2d',
                command=lambda t=text: self.button_click(t)
            )
            
            btn.bind('<Enter>', lambda e, t=text: self.on_enter(t))
            btn.bind('<Leave>', lambda e, t=text: self.on_leave(t))
            btn.bind('<ButtonPress-1>', lambda e, t=text: self.on_press(t))
            btn.bind('<ButtonRelease-1>', lambda e, t=text: self.on_release(t))
            
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.buttons[text] = btn
        
        # Настройка сетки
        for i in range(5):
            root.grid_columnconfigure(i, weight=1)
        for i in range(5):
            root.grid_rowconfigure(i, weight=1)

    def load_sounds(self):
        """Загрузка звуков с обработкой ошибок"""
        sound_files = {
            'click_down': 'sounds/click_down.wav',
            'click_up': 'sounds/click_up.wav',
            'error': 'sounds/error.wav'
        }
        
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Ошибка загрузки звука {name}: {e}")

    def set_volume(self, volume=0.5):
        """Установка громкости для всех звуков"""
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(volume)

    def load_textures(self):
        """Загрузка или создание текстур для кнопок"""
        button_textures = {
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            '.': 'point',
            '+': 'plus', '-': 'minus', '*': 'multiplication', '/': 'division',
            '=': 'equals', 'C': 'c', ')': 'paren_right','(': 'paren_left', 
            '⌫': 'backspace'
        }
        
        for btn, name in button_textures.items():
            try:
                normal_img = self.load_image(f"textures/{name}_normal.png")
                hover_img = self.load_image(f"textures/{name}_hover.png")
                pressed_img = self.load_image(f"textures/{name}_pressed.png")
                
                self.textures[btn] = {
                    'normal': normal_img,
                    'hover': hover_img,
                    'pressed': pressed_img
                }
            except:
                
                color = (60, 60, 60)
                if btn == 'C': color = (200, 50, 50)
                elif btn == '=': color = (70, 170, 70)
                elif btn == '⌫': color = (150, 50, 50)
                
                img = Image.new('RGB', (64, 64), color)
                photo = ImageTk.PhotoImage(img)
                self.textures[btn] = {
                    'normal': photo,
                    'hover': photo,
                    'pressed': photo
                }

    def load_image(self, path, size=(64, 64)):
        """Загрузка изображения"""
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Ошибка загрузки изображения {path}: {e}")
            
            img = Image.new('RGB', size, (0, 0, 0))
            return ImageTk.PhotoImage(img)

    def on_enter(self, button_text):
        """Смена текстуры при наведении"""
        if button_text in self.textures:
            self.buttons[button_text].config(image=self.textures[button_text]['hover'])

    def on_leave(self, button_text):
        """Возврат обычной текстуры"""
        if button_text in self.textures:
            self.buttons[button_text].config(image=self.textures[button_text]['normal'])

    def on_press(self, button_text):
        """Смена текстуры при нажатии"""
        if button_text in self.textures:
            self.buttons[button_text].config(image=self.textures[button_text]['pressed'])
            self.play_sound('click_down')

    def on_release(self, button_text):
        """Смена текстуры при отпускании"""
        if button_text in self.textures:
            self.buttons[button_text].config(image=self.textures[button_text]['hover'])
            self.play_sound('click_up')

    def play_sound(self, sound_name):
        """Воспроизведение звука с проверкой"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Ошибка воспроизведения звука {sound_name}: {e}")

    def show_error(self):
        """Визуальное отображение ошибки"""
        current_fg = self.entry.cget('fg')
        self.entry.config(fg='red')
        self.entry.after(1000, lambda: self.entry.config(fg=current_fg))

    def button_click(self, char):
        """Обработка нажатия кнопок"""
        current = self.entry.get()
        error_states = ("Ошибка", "∞")

        if current in error_states:
            self.entry.delete(0, tk.END)
            current = "0"

        if char == 'C':
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "0")
            return
            
        if char == '⌫':
            new_length = len(current) - 1
            self.entry.delete(new_length, tk.END)
            if new_length == 0:
                self.entry.insert(0, "0")
            return
        
        if char == '=':
            if current in error_states:
                self.play_sound('error')
                self.show_error()
            else:
                try:
                    result = ne.evaluate(current)
                    self.entry.delete(0, tk.END)
                    if isinstance(result, float) and result.is_integer():
                        self.entry.insert(0, str(int(result)))
                    else:
                        self.entry.insert(0, str(result))
                except ZeroDivisionError:
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, '∞')
                    self.play_sound('error')
                    self.show_error()
                except Exception as e:
                    print(f"Ошибка вычисления: {e}")
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, "Ошибка")
                    self.play_sound('error')
                    self.show_error()
        
        if current == "0" and char not in '+-*/().^':
            self.entry.delete(0, tk.END)
        
        self.entry.insert(tk.END, char)

    def calculate_result(self):
        """Вычисление"""
        current = self.entry.get()
        if current in error_states:
            self.play_sound('error')
            self.show_error()
        else:
            try:
                expr = current.replace('^', '**')
                result = ne.evaluate(expr)
                
                # Форматирование результата
                if isinstance(result, (float, np.floating)):
                    if result.is_integer():
                        result_str = str(int(result))
                    else:
                        result_str = f"{result:.6f}".rstrip('0').rstrip('.')
                else:
                    result_str = str(result)
                
                self.entry.delete(0, tk.END)
                self.entry.insert(0, result_str)
                
            except ZeroDivisionError:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, '∞')
                self.play_sound('error')
                self.show_error()
            except Exception as e:
                print(f"Ошибка вычисления: {e}")
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Ошибка")
                self.play_sound('error')
                self.show_error()

    def handle_error(self, message):
        """Обработка ошибок"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, message)
        self.play_sound('error')
        self.show_error()

if __name__ == "__main__":
    os.makedirs("textures", exist_ok=True)
    os.makedirs("sounds", exist_ok=True)
    #os.makedirs("textures/frames_for_animation", exist_ok=True)
    #os.makedirs("sounds/fun", exist_ok=True)
    
    try:
        from PIL import ImageTk, Image
        import pygame
        import numexpr
        import numpy
    except ImportError as e:
        print("Установите необходимые библиотеки:")
        print("pip install pillow; pygame; numpy numexpr")
        exit(1)
    
    root = tk.Tk()
    app = calculator(root)
    root.mainloop()