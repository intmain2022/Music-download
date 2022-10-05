import os
import json
import requests
from tkinter import *


class couldmusic(object):

    def __init__(self, tk_root):
        """初始化"""

        self.root = tk_root

        self.playlist_id = StringVar()
        self.song_id = StringVar()
        self.song_name = StringVar()
        self.song_name.set("")
        self.var = StringVar()
        self.var.set("开始")

        self.index = 0

        self.song_list = {}
        self.save_path = os.path.abspath(".")
        self.save_path = os.path.join(self.save_path, "音乐")

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        }

        # 绘制UI
        self.layout()

    def process(self):
        """下载进度条"""

        total_length = 260
        if len(self.song_list) > 0:
            length = total_length * self.index / len(self.song_list)
            self.canvas.coords(self.processbar, (0, 0, length, 26))
            self.var.set("{self.index}/{len(self.song_list)}")
            if length == total_length:
                self.song_name.set("下载完成")
        self.root.update()

    def reset(self):
        """重置"""

        self.song_id.set("")
        self.playlist_id.set("")
        self.song_list.clear()
        self.var.set("开始")
        self.index = 0
        self.save_path = os.path.abspath(".")
        self.save_path = os.path.join(self.save_path, "音乐")

    def get_playlist(self, playlist_id):

        playlist_api = "http://music.163.com/api/playlist/detail?id="  # 歌单详情API
        playlist_url = playlist_api + playlist_id

        r = requests.get(playlist_url, headers=self.headers)
        json_data = json.loads(r.text)

        # 尝试提取指定信息
        try:
            song_list_name = json_data['result']['creator']['nickname']
            self.song_name.set("{song_list_name} 的歌单")
            self.save_path = os.path.join(self.save_path, song_list_name)
            if not os.path.isdir(self.save_path):
                os.mkdir(self.save_path)
        except:
            self.song_name.set("请输入有效的歌单ID或歌曲ID")
            return

        # 提取歌曲信息
        for i in json_data['result']['tracks']:
            song_name = i["name"].split("/")[0]
            song_id = i['id']
            self.song_list[song_name] = song_id
        return song_list_name

    def get_song_info(self, song_id):
        """获取单首歌曲信息"""

        song_detail_api = "http://music.163.com/api/song/detail/?id=song_id&ids=%5Bsong_id%5D"
        song_url = song_detail_api.replace("song_id", self.song_id.get())

        r = requests.get(song_url, headers=self.headers)
        json_data = json.loads(r.text)

        # 尝试提取指定信息
        try:
            for i in json_data['songs']:
                self.song_list[i['name']] = self.song_id.get()
        except:
            self.song_name.set("请输入有效的歌单ID或歌曲ID_2")

    def download(self):
        """下载 "self.song_list" 中歌曲"""

        api = "http://music.163.com/song/media/outer/url?id=song_id.mp3"
        # api = "https://www.apicp.cn/API/wyy/api.php?id="
        self.index = 0

        for item in self.song_list:
            self.index += 1
            song_url = api.replace("song_id", str(self.song_list[item]))
            name = item + ".mp3"
            split_list = ["<", ">", "/", "\\"]
            for x in split_list:
                name = name.split(x)[0]
            path = os.path.join(self.save_path, name)
            self.song_name.set(name)
            content = requests.get(song_url, headers=self.headers).content
            if content[0] != 0x49:
                self.song_name.set("VIP歌曲无法下载")
                continue
            if not os.path.isfile(path):
                with open(path, "wb") as f:
                    f.write(content)
            self.process()

    def run(self):
        """获取输入信息, 并执行程序"""

        playlist_id = self.playlist_id.get()
        song_id = self.song_id.get()

        if not os.path.isdir(self.save_path):
            os.mkdir(self.save_path)

        if playlist_id == "" and song_id == "":
            self.song_name.set("请输入有效的歌单ID或歌曲ID_1")
            return
        elif playlist_id:
            self.get_playlist(playlist_id)
        elif song_id:
            self.get_song_info(song_id)

        self.download()
        self.reset()

    def layout(self):
        """绘制界面"""

        self.root.title("Music Download       by int main")
        self.root.geometry("260x100+600+300")
        self.root.bind("<Return>", lambda x: self.run())

        # 歌单ID
        Label(self.root, text="歌单ID:").grid(row=0, column=0)
        Entry(self.root, textvariable=self.playlist_id).grid(row=0, column=1, sticky=N + E + S + W)

        # 歌曲ID
        Label(self.root, text="歌曲ID:").grid(row=1, column=0)
        Entry(self.root, textvariable=self.song_id).grid(row=1, column=1, sticky=N + E + S + W)

        # 正在下载的歌曲信息
        Label(self.root, text="正在下载:").grid(row=2, column=0)
        Entry(self.root, textvariable=self.song_name).grid(row=2, column=1, sticky=N + E + S + W)

        # 进度条
        self.canvas = Canvas(self.root, height=26, bg="white")
        self.canvas.grid(row=3, column=1)
        self.processbar = self.canvas.create_rectangle(0, 0, 0, 0, width=0, fill="green")

        # 开始
        Button(self.root, textvariable=self.var, command=self.run).grid(row=3, column=0, sticky=N + E + S + W)


if __name__ == "__main__":
    root = Tk()
    couldmusic(root)
    root.mainloop()