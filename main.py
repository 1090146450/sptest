import random

import cv2
from moviepy.editor import *


class AutoVideoClips:
    def __init__(self, input_name, outp_name, play_speed, ta="1.mp4"):
        self.input_name = input_name  # 输入视频
        self.outp_name = outp_name  # 输出视频
        self.play_speed = play_speed  # 变速
        self.au = VideoFileClip(self.input_name)  # 创建了一个VideoFileClip对象，
        self.ta = VideoFileClip(ta)

    def Slicing(self, videoLen) -> list:  # 切割视频
        if not isinstance(videoLen, list):
            raise Exception("视频切割位置请传入列表类型")
        if len(videoLen) == 0:
            print("获取视频长度")
            vidolen = self.au.duration  # 获取视频长度
            print("视频长度为：" + str(vidolen))
            videoLen = []  # 视频切割位置
            if vidolen < 300:
                raise Exception("输入视频长度小于5分钟不需要剪辑")
            for i in (0, 100):
                vi = random.randint(0, int(vidolen))  # 随机挑选视频片段
                if vi + 300 <= vidolen:
                    videoLen += [vi, vi + 300]
                    break
            else:
                videoLen += [0, 300]
            videoall = self.au.subclip(*videoLen)  # 获取第一次切割的对象
            return [videoall.subclip((0), (40)), videoall.subclip((40), (90)), videoall.subclip((90), (120)),
                    videoall.subclip((120), (240)), videoall.subclip((240), (300))]
        else:
            return self.au.subclip(*videoLen)

    def Shifting(self, au):  # 变速视频
        codec = 'libx264'  # 使用H.264编解码器
        bitrate = '5000k'  # 设置比特率为5000 kbps
        new_au = au.fl_time(lambda t: self.play_speed * t, apply_to=['mask', 'audio'])  # 对视频和音频应用时间转换，
        new_au = new_au.set_duration(au.duration / self.play_speed)
        new_au.write_videofile(self.outp_name, codec=codec, bitrate=bitrate)  # 设置修改后剪辑的持续时间，并将其写入新的视频文件。

    def add_fade_in_out(self, clips, fade_duration=1) -> list:
        """添加转场视频"""
        fali = []
        for clip in clips:
            # 添加淡入效果
            fade_in = clip.fadein(fade_duration)
            # 添加淡出效果
            fade_out = fade_in.fadeout(fade_duration)
            fali.append(fade_out)  # 将结果传入列表
        return fali

    def Synthesis(self, videoList, transition):  # 合成视频
        if not isinstance(videoList, list) and not isinstance(transition, list):
            raise Exception("视频合成列表请传入列表类型")

        transition1 = []  # 设置拼接视频列表
        for i in transition:  # 创建拼接视频对象
            transition1.append(VideoFileClip(i))
        print(len(transition1), len(videoList))
        print("开始处理转场效果")
        return concatenate_videoclips(
            [self.ta.subclip((0), (1)), videoList[0], videoList[1], videoList[2], videoList[3],
             videoList[4]])

    def czsp(self, au) -> VideoFileClip:
        """对视频进行抽帧处理"""
        x, y = 0, 0
        aulist = []
        for i in range(int(au.duration) - 100):
            x = y
            y = i + random.random()
            aulist.append(au.subclip((x), (y + 0.01)))
            y = y + 0.01
        print("视频抽帧成功")
        return concatenate_videoclips(aulist)

    def onevideo(self, video):
        vidolen = video.duration  # 获取视频长度
        print("获取长度:", vidolen)
        x, y = 0, 0
        while True:
            x = x + random.randint(10, 50)
            y = x + 300
            if y > vidolen:
                print("视频长度已经切割完成")
                break
            else:
                print("开始切割并保存")
                video.subclip((x), (y)).write_videofile("input" + str(x) + ".mp4")

    def run(self):
        transitionList = []  # 转场视频
        print("开始切割视频")
        x = input("切割方法：1、单独切割 2、去重切割")
        if int(x) == 1:
            self.onevideo(self.au)
            return 0
        auall = self.Slicing([])  # 切割视频，返回切割完视频列表
        for i in range(0, 10):  # 找当前文件夹下10个以内视频
            if os.path.isfile(str(i) + ".mp4"):
                transitionList.append(str(i) + ".mp4")
        print("将视频添加转场")
        auall = self.add_fade_in_out(auall)
        print("开始合成视频")
        video = self.Synthesis(auall, transitionList)
        print("修改视频帧率等操作")
        video = video.set_fps(60)
        video = video.resize((720, 1280))
        print("开始抽帧处理")
        video = self.czsp(video)
        print("开始变速视频")
        self.Shifting(video)


class DyVideoClips:
    """抖音视频去重"""

    def __init__(self, input_name, outp_name):
        self.input_name = input_name  # 输入视频
        self.outp_name = outp_name  # 输出视频
        self.play_speed = 1.2

    def Shifting(self, au):  # 变速视频
        codec = 'libx264'  # 使用H.264编解码器
        bitrate = '5000k'  # 设置比特率为5000 kbps
        au = au.set_fps(60)
        au = vfx.colorx(au, 0.8)  # 将视频的颜色饱和度减半
        new_au = au.fl_time(lambda t: self.play_speed * t, apply_to=['mask', 'audio'])  # 对视频和音频应用时间转换，
        new_au = new_au.set_duration(au.duration / self.play_speed)
        new_au.write_videofile(self.outp_name, codec=codec)  # 设置修改后剪辑的持续时间，并将其写入新的视频文件。

    def czsp(self, au) -> VideoFileClip:
        """对视频进行抽帧处理"""
        x, y = 0, 0
        aulist = []
        for i in range(int(au.duration) - 2):
            x = y
            y = i + random.random()
            aulist.append(au.subclip((x), (y + 0.01)))
            y = y + 0.01
        print("视频抽帧成功")
        return concatenate_videoclips(aulist)

    def run(self):
        print("打开视频")
        au = VideoFileClip(self.input_name)
        print("切割视频")
        au = au.subclip(0.5, )
        au.fadein(1)
        print("视频反转")
        au = au.fx(vfx.mirror_x)
        au = self.czsp(au)
        self.Shifting(au)


intp_name = './input.mp4'
outp_name = './outp.mp4'
play_speed = 1.15
x = input("请输入:1、抖音短视频处理")
if int(x) == 1:
    avc = DyVideoClips(intp_name, outp_name)
else:
    avc = AutoVideoClips(intp_name, outp_name, play_speed)

avc.run()
