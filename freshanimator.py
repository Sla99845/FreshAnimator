import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageTk
import json, os, base64

class FreshAnimator:
    def __init__(self, root):
        self.root = root
        self.root.title("FreshAnimator")
        self.frames = []
        self.current_frame_index = 0
        self.drawing = False
        self.erase_mode = False
        self.last_x, self.last_y = None, None
        self.canvas_width = 800
        self.canvas_height = 600
        self.brush_size = 5
        self.onion_skin = True
        self.setup_ui()
        self.new_frame()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 10), padding=5, background='#333', foreground='white')
        style.configure('TLabel', font=('Segoe UI', 10), background='#222', foreground='white')

        self.root.configure(bg='#222')

        self.canvas = tk.Canvas(self.root, bg="white", width=self.canvas_width, height=self.canvas_height, bd=2, relief="ridge")
        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset_draw)

        control = tk.Frame(self.root, bg="#222")
        control.pack(side="right", fill="y", padx=5, pady=5)

        ttk.Button(control, text="Novo Quadro", command=self.new_frame).pack(fill="x", pady=2)
        ttk.Button(control, text="Deletar Quadro", command=self.delete_frame).pack(fill="x", pady=2)
        ttk.Button(control, text="Salvar", command=self.save_animation).pack(fill="x", pady=2)
        ttk.Button(control, text="Carregar", command=self.load_animation).pack(fill="x", pady=2)
        ttk.Button(control, text="Exportar GIF", command=self.export_gif).pack(fill="x", pady=2)
        ttk.Button(control, text="Play", command=self.play_animation).pack(fill="x", pady=2)
        ttk.Button(control, text="Modo Desenho", command=self.set_draw_mode).pack(fill="x", pady=2)
        ttk.Button(control, text="Borracha", command=self.toggle_eraser).pack(fill="x", pady=2)
        ttk.Button(control, text="+ Tamanho", command=self.increase_brush).pack(fill="x", pady=2)
        ttk.Button(control, text="- Tamanho", command=self.decrease_brush).pack(fill="x", pady=2)
        ttk.Button(control, text="Toggle Onion Skin", command=self.toggle_onion_skin).pack(fill="x", pady=2)

        self.status = ttk.Label(control, text="Modo: Desenho  |  Quadro: 0", anchor="center")
        self.status.pack(pady=10)

        self.root.bind("<Left>", lambda e: self.prev_frame())
        self.root.bind("<Right>", lambda e: self.next_frame())
        self.root.bind("<Control-s>", lambda e: self.save_animation())

    def new_frame(self):
        img = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        draw = ImageDraw.Draw(img)
        self.frames.append((img, draw))
        self.current_frame_index = len(self.frames) - 1
        self.update_canvas()

    def delete_frame(self):
        if self.frames:
            self.frames.pop(self.current_frame_index)
            if self.current_frame_index > 0:
                self.current_frame_index -= 1
            self.update_canvas()

    def save_animation(self):
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if not path: return
        frames_data = []
        for img, _ in self.frames:
            b = img.tobytes()
            encoded = base64.b64encode(b).decode("utf-8")
            frames_data.append(encoded)
        with open(path, "w") as f:
            json.dump({"frames": frames_data}, f)

    def load_animation(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path: return
        with open(path, "r") as f:
            raw = json.load(f)
        self.frames.clear()
        for encoded_data in raw["frames"]:
            raw_bytes = base64.b64decode(encoded_data)
            img = Image.frombytes("RGB", (self.canvas_width, self.canvas_height), raw_bytes)
            self.frames.append((img, ImageDraw.Draw(img)))
        self.current_frame_index = 0
        self.update_canvas()

    def export_gif(self):
        path = filedialog.asksaveasfilename(defaultextension=".gif")
        if not path: return
        images = [frame[0] for frame in self.frames]
        if images:
            images[0].save(path, save_all=True, append_images=images[1:], duration=100, loop=0)

    def play_animation(self):
        def play(i=0):
            if i >= len(self.frames): return
            self.current_frame_index = i
            self.update_canvas()
            self.root.after(100, lambda: play(i + 1))
        play()

    def toggle_eraser(self):
        self.erase_mode = True
        self.update_canvas()

    def set_draw_mode(self):
        self.erase_mode = False
        self.update_canvas()

    def increase_brush(self):
        self.brush_size += 2
        self.update_canvas()

    def decrease_brush(self):
        if self.brush_size > 2:
            self.brush_size -= 2
        self.update_canvas()

    def toggle_onion_skin(self):
        self.onion_skin = not self.onion_skin
        self.update_canvas()

    def start_draw(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        if not self.drawing or not self.frames: return
        img, draw = self.frames[self.current_frame_index]
        color = "white" if self.erase_mode else "black"
        draw.line((self.last_x, self.last_y, event.x, event.y), fill=color, width=self.brush_size)
        self.last_x, self.last_y = event.x, event.y
        self.update_canvas()

    def reset_draw(self, event):
        self.drawing = False
        self.last_x, self.last_y = None, None

    def update_canvas(self):
        if not self.frames:
            self.canvas.delete("all")
            return

        base = self.frames[self.current_frame_index][0].copy()
        if self.onion_skin and self.current_frame_index > 0:
            prev_img = self.frames[self.current_frame_index - 1][0].copy().convert("RGBA")
            base = base.convert("RGBA")
            overlay = prev_img.copy()
            overlay.putalpha(100)
            base.alpha_composite(overlay)

        display_img = base.convert("RGB")
        self.tk_image = ImageTk.PhotoImage(display_img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        modo = 'Borracha' if self.erase_mode else 'Desenho'
        self.status.config(text=f"Modo: {modo}  |  Quadro: {self.current_frame_index + 1}/{len(self.frames)}  | Tamanho: {self.brush_size}  | Onion: {'Ligado' if self.onion_skin else 'Desligado'}")

    def next_frame(self):
        if self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.update_canvas()

    def prev_frame(self):
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.update_canvas()

if __name__ == '__main__':
    root = tk.Tk()
    app = FreshAnimator(root)
    root.mainloop()
