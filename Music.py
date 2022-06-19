import os
import json
import requests
from tkinter import *


class couldmusic(object):

    def __init__(self, tk_root):
        """初始化"""

        self.root = tk_root

        self.playlist_id = StringVar()  # 歌单ID，可以通过网易云歌单详情页面获地址栏取
        self.song_id = StringVar()  # 歌曲ID，可以通过歌曲播放页面地址栏获取
        self.song_name = StringVar()  # 歌曲名字，用于显示下载信息
        self.song_name.set("")
        self.var = StringVar()  # 下载进度值
        self.var.set("开始")

        self.index = 0

        self.song_list = {}
        self.save_path = os.path.abspath(".")  # 获取工作目录
        self.save_path = os.path.join(self.save_path, "音乐")  # 生成音乐文件夹路径

        # 浏览器Headers信息
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        }

        # 绘制UI
        self.layout()

    def process(self):
        """下载进度条"""

        total_length = 260  # 进度条总长度
        if len(self.song_list) > 0:  # 判断歌曲列表非空
            length = total_length * self.index / len(self.song_list)  # 计算下载进度长度
            self.canvas.coords(self.processbar, (0, 0, length, 26))  # 创建进度条(起始X坐标，起始Y坐标, 长度，高度)
            self.var.set("{self.index}/{len(self.song_list)}")  # 设定进度值
            if length == total_length:  # 判断是否下载完成
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
        playlist_url = playlist_api + playlist_id  # 获取歌单详情地址

        r = requests.get(playlist_url, headers=self.headers)  # 获取源码
        json_data = json.loads(r.text)  # 源码转换Json格式

        # 尝试提取指定信息
        try:
            song_list_name = json_data['result']['creator']['nickname']  # 提取歌单名字
            self.song_name.set("{song_list_name} 的歌单")
            self.save_path = os.path.join(self.save_path, song_list_name)  # 生成歌单文件路径
            if not os.path.isdir(self.save_path):  # 判断路径是否存在
                os.mkdir(self.save_path)  # 创建歌单文件夹
        except:
            self.song_name.set("请输入有效的歌单ID或歌曲ID")
            return

        # 提取歌曲信息
        for i in json_data['result']['tracks']:
            song_name = i["name"].split("/")[0]  # 获取歌曲名字，并移除 "/"
            song_id = i['id']  # 获取歌曲ID信息
            self.song_list[song_name] = song_id  # 将歌曲信息加入到字典备用

        return song_list_name

    def get_song_info(self, song_id):
        """获取单首歌曲信息"""

        song_detail_api = "http://music.163.com/api/song/detail/?id=song_id&ids=%5Bsong_id%5D"  # 歌曲信息API
        song_url = song_detail_api.replace("song_id", self.song_id.get())  # 生成歌曲信息Url

        r = requests.get(song_url, headers=self.headers)  # 获取源码
        json_data = json.loads(r.text)  # 源码转换Json格式

        # 尝试提取指定信息
        try:
            for i in json_data['songs']:  # 获取Json_data中 ‘songs’内容
                self.song_list[i['name']] = self.song_id.get()  # 将歌曲信息加入到字典备用
        except:
            self.song_name.set("请输入有效的歌单ID或歌曲ID_2")

    def download(self):
        """下载 "self.song_list" 中歌曲"""

        api = "http://music.163.com/song/media/outer/url?id=song_id.mp3"
        # api = "https://www.apicp.cn/API/wyy/api.php?id="                        # 网易云解析API, 第三方提供
        self.index = 0

        for item in self.song_list:  # 遍历歌曲列表
            self.index += 1  # 歌曲次序
            song_url = api.replace("song_id", str(self.song_list[item]))  # 解析地址
            name = item + ".mp3"  # 歌曲名字
            split_list = ["<", ">", "/", "\\"]  # Windows名字机制，移除特殊字符
            for x in split_list:
                name = name.split(x)[0]
            path = os.path.join(self.save_path, name)  # 歌曲保存路径
            self.song_name.set(name)  # 更新UI信息
            content = requests.get(song_url, headers=self.headers).content  # 获取源码
            if content[0] != 0x49:  # 判断返回值是否属于音频文件
                self.song_name.set("VIP歌曲无法下载")  # 灰色歌曲无法下载
                continue  # 跳出本次循环
            if not os.path.isfile(path):  # 判断文件是否存在
                with open(path, "wb") as f:  # 保存文件
                    f.write(content)
            self.process()

    def run(self):
        """获取输入信息, 并执行程序"""

        playlist_id = self.playlist_id.get()  # 获取页面输入歌单ID信息
        song_id = self.song_id.get()  # 获取页面输入歌曲ID信息

        if not os.path.isdir(self.save_path):  # 判断路径是否存在
            os.mkdir(self.save_path)  # 创建文件夹

        # 判断输入歌单ID和歌曲ID有效
        if playlist_id == "" and song_id == "":  # 判断歌单/歌曲非空
            self.song_name.set("请输入有效的歌单ID或歌曲ID_1")
            return
        elif playlist_id:  # 歌单ID非空，执行歌单处理函数
            self.get_playlist(playlist_id)
        elif song_id:  # 歌曲ID非空，执行歌曲处理函数
            self.get_song_info(song_id)

        self.download()  # 执行歌曲下载函数
        self.reset()  # 重置

    def layout(self):
        """绘制界面"""

        self.root.title("音乐下载器 作者:叶晨")  # 标题
        self.root.geometry("260x100+600+300")  # 位置
        self.root.bind("<Return>", lambda x: self.run())  # 绑定回车键

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