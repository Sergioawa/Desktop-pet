

#  _  __           _______    _ _    _           #
# | |/ /    /\    |___  / |  | | |  | |   /\     #
# | ' /    /  \      / /| |  | | |__| |  /  \    #
# |  <    / /\ \    / / | |  | |  __  | / /\ \   #
# | . \  / ____ \  / /__| |__| | |  | |/ ____ \  #
# |_|\_\/_/    \_\/_____|\____/|_|  |_/_/    \_\ #


import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageSequence
import json, os, random, threading, time, pygame, webbrowser
import sys

# ---------- 路径兼容打包 ----------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

PET_SIZE   = 128
CONFIG     = os.path.join(BASE_DIR, "config.json")
IMG_DIR    = os.path.join(BASE_DIR, "img")
VOICE_DIR  = os.path.join(BASE_DIR, "voice")
ICON_PATH  = os.path.join(BASE_DIR, "assets", "icon.ico")
DEFAULT_CFG = {"interval": 3}

# 创建目录（如果不存在）
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

# 初始化 pygame
pygame.mixer.init()

# ---------- 工具 ----------
def load_config():
    return json.load(open(CONFIG)) if os.path.isfile(CONFIG) else DEFAULT_CFG.copy()
def save_config(cfg):
    json.dump(cfg, open(CONFIG, "w"))

# ---------- 主桌宠 ----------
class WanPet(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("kuzuha")
        self.configure(bg='white')
        self.wm_attributes("-transparentcolor", 'white')
        self.wm_attributes("-topmost", True)
        self.overrideredirect(True)

        # 固定图标
        if os.path.isfile(ICON_PATH):
            self.iconbitmap(ICON_PATH)

        self.cfg = load_config()
        self.running = True
        self.label = tk.Label(self, bg='white')
        self.label.pack()

        self.refresh_media_lists()
        self.idx = 0
        self.load_media(self.IMG_LIST[0])

        # 事件
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)
        self.bind("<Button-3>", self.popup_menu)

        threading.Thread(target=self.auto_change, daemon=True).start()

    # ---------- 媒体 ----------
    def refresh_media_lists(self):
        self.IMG_LIST   = [os.path.join(IMG_DIR, f) for f in os.listdir(IMG_DIR)
                           if f.lower().endswith(('.png', '.jpg', '.gif'))]
        self.VOICE_LIST = [os.path.join(VOICE_DIR, f) for f in os.listdir(VOICE_DIR)
                           if f.lower().endswith(('.mp3', '.wav'))]
        if not self.IMG_LIST:
            self.IMG_LIST = [None]

    # ---------- 加载图片 / GIF ----------
    def load_media(self, path):
        if path is None:
            return

        # 清空旧帧
        self.gif_frames = None

        if path.lower().endswith('.gif'):
            gif = Image.open(path).convert("RGBA")
            self.gif_frames = [
                ImageTk.PhotoImage(frame.convert("RGBA").resize((PET_SIZE, PET_SIZE), Image.LANCZOS))
                for frame in ImageSequence.Iterator(gif)
            ]
            self.gif_frame_idx = 0
            self.animate_gif()
        else:
            img = Image.open(path).convert("RGBA").resize((PET_SIZE, PET_SIZE), Image.LANCZOS)
            self.now_img = ImageTk.PhotoImage(img)
            self.label.config(image=self.now_img)

    def animate_gif(self):
        if self.gif_frames and self.running:
            self.label.config(image=self.gif_frames[self.gif_frame_idx])
            self.gif_frame_idx = (self.gif_frame_idx + 1) % len(self.gif_frames)
            self.after(100, self.animate_gif)

    # ---------- 拖拽 ----------
    def start_drag(self, event):
        self.x0, self.y0 = event.x, event.y

    def do_drag(self, event):
        self.geometry(f"+{self.winfo_x()+event.x-self.x0}+{self.winfo_y()+event.y-self.y0}")

    # ---------- 右键菜单 ----------
    def popup_menu(self, event):
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="换图", command=self.rand_img)
        m.add_command(label="随机语音", command=self.play_voice)

        sub = tk.Menu(m, tearoff=0)
        sub.add_command(label="原神wiki", command=self.gwiki)
        sub.add_command(label="桌宠图片", command=self.gcphoto)
        sub.add_command(label="作者B站", command=self.zzbz)
        m.add_cascade(label="外部资源", menu=sub)

        sub = tk.Menu(m, tearoff=0)
        sub.add_command(label="换图间隔", command=self.set_interval)
        sub.add_command(label="添加图片",  command=lambda: self.add_file("img"))
        sub.add_command(label="添加音频",  command=lambda: self.add_file("voice"))
        sub.add_command(label="刷新列表", command=self.refresh_and_show)
        sub.add_command(label="输入彩蛋码", command=self.wanyei)
        sub.add_command(label="ProgramName:kazuha")
        sub.add_command(label="Version:1.0")
        sub.add_command(label="Developer:Hywel/lvaua")
        sub.add_command(label="说明:本程序允许对源代码的二次改动和程序本体的二")
        sub.add_command(label="次分发;但请保留原作者的信息.本程序禁止用于商业！")
        m.add_cascade(label="设置", menu=sub)

        m.add_separator()
        m.add_command(label="退出", command=self.quit)
        m.post(event.x_root, event.y_root)

    # ---------- 功能 ----------
    def rand_img(self):
        if len(self.IMG_LIST) > 1:
            self.idx = (self.idx + 1) % len(self.IMG_LIST)
            self.load_media(self.IMG_LIST[self.idx])

    def play_voice(self):
        if self.VOICE_LIST:
            pygame.mixer.music.load(random.choice(self.VOICE_LIST))
            pygame.mixer.music.play()
        else:
            msgbox.showwarning("万叶", "voice 目录里没有音频文件！")

    def auto_change(self):
        while self.running:
            time.sleep(self.cfg["interval"])
            if self.running and self.IMG_LIST:
                self.idx = (self.idx + 1) % len(self.IMG_LIST)
                self.load_media(self.IMG_LIST[self.idx])

    # ---------- 外部资源 ----------
    def gwiki(self):
        webbrowser.open(url='https://wiki.biligame.com/ys/%E9%A6%96%E9%A1%B5', new=0)

    def gcphoto(self):
        webbrowser.open(url='https://www.miyoushe.com/ys/article/61033923', new=0)
    
    def zzbz(self):
        webbrowser.open(url='https://space.bilibili.com/1484343432', new=0)   

   #----------- 彩蛋 ----------
    def wanyei(self):
      PASSWORD = "wanye1029"

      # 1. 密码输入框
      user_input = simpledialog.askstring(
        title="彩蛋",
        prompt="提示:密码与万叶有关,尽情猜吧\n虽然你可以直接看源代码的,但还是猜猜\n请输入密码(使用英文输入):",
        show="*"
     )

     # 2. 判断 & 结果
      if user_input == PASSWORD:
        # 惊喜窗口
        webbrowser.open(url='https://www.bilibili.com/video/BV1Lg41137kX/', new=0)
        surprise = tk.Toplevel()
        surprise.title("你发现了彩蛋~~~")
        surprise.geometry("2000x1500")

        tk.Label(
            surprise,
            text="「深山踏红叶，耳畔闻鹿鸣」…我很喜欢枫叶，可惜枫叶红时总多离别。\n行走世间，自然会有各种烦恼相伴，但既得与你相遇，不管是武\n艺还是内心都有了新的成长。想必今后的人生也会更加自在吧。",
            font=("微软雅黑", 25),
            fg="#742300"
        ).pack(expand=True)
        tk.Button(surprise, text="关闭", command=surprise.destroy).pack(pady=10)
      else:
        messagebox.showerror("彩蛋", "密码错误,请重试!")


    # ---------- 设置窗口 ----------
    def set_interval(self):
        def save():
            try:
                val = int(entry.get())
                if val <= 0: raise ValueError
                self.cfg["interval"] = val
                save_config(self.cfg)
                msgbox.showinfo("成功", f"换图间隔已设为 {val} 秒")
                top.destroy()
            except ValueError:
                msgbox.showwarning("错误", "请输入正整数！")
        top = tk.Toplevel(self)
        top.title("换图间隔")
        tk.Label(top, text="间隔(秒):").pack(padx=5, pady=5)
        entry = tk.Entry(top, width=5)
        entry.insert(0, self.cfg["interval"])
        entry.pack(padx=5)
        tk.Button(top, text="确定", command=save).pack(pady=5)

    def add_file(self, folder):
        f = filedialog.askopenfilename(
            title=f"选择{folder}",
            filetypes=[("PNG/JPG/GIF" if folder=="img" else "MP3/WAV", "*.*")])
        if f:
            dest = os.path.join(IMG_DIR if folder=="img" else VOICE_DIR, os.path.basename(f))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(f, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
            msgbox.showinfo("成功", f"{os.path.basename(f)} 已复制到 {folder}/")
            self.refresh_media_lists()

    def refresh_and_show(self):
        self.refresh_media_lists()
        msgbox.showinfo("刷新", f"图片：{len(self.IMG_LIST)} 张\n音频：{len(self.VOICE_LIST)} 个")

    def quit(self):
        self.running = False
        pygame.mixer.quit()
        self.destroy()

print("  _  __           _______    _ _    _           ")
print("  | |/ /    /\    |___  / |  | | |  | |   /\    ")
print("  | ' /    /  \      / /| |  | | |__| |  /  \   ")
print("  |  <    / /\ \    / / | |  | |  __  | / /\ \  ")
print("  | . \  / ____ \  / /__| |__| | |  | |/ ____ \ ")
print("  |_|\_\/_/    \_\/_____|\____/|_|  |_/_/    \_\ ")

# ---------- 启动 ----------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    WanPet()
    root.mainloop()


# ______            __     __            __          __     __     __  
#|  ____|           \ \   / /            \ \        / /     \ \   / / 
#| |__ ___ _ __   __ \ \_/ /   _  __ _ _ _\ \  /\  / /_ _ _ _\ \_/ /__ 
#|  __/ _ \ '_ \ / _` \   / | | |/ _` | '_ \ \/  \/ / _` | '_ \   / _ \
#| | |  __/ | | | (_| || || |_| | (_| | | | \  /\  / (_| | | | | |  __/
#|_|  \___|_| |_|\__, ||_| \__,_|\__,_|_| |_|\/  \/ \__,_|_| |_|_|\___|
#                __/ |                                                  
#               |___/                                                   

