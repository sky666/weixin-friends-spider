import os, re, math
import itchat
import jieba
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import PIL.Image as Image
from wordcloud import WordCloud


# 中文乱码设置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.family']='sans-serif'


# 微信好友性别分析
def friends_sex_analysis(friends):
    sex_count = friends.groupby('Sex')['Sex'].count()  # 统计各性别的好友数量
    sex_count_order = sex_count.sort_values(ascending=False)  # 降序排列
    # Sex 为 0 代表“未设置性别”, Sex 为 1 代表“男”, Sex 为 2 代表“女”
    df_sex = pd.DataFrame(sex_count_order.values, index=['男', '女', '未设置'], columns=['Sex'])
    plt.pie(df_sex['Sex'], labels=df_sex.index, autopct='%.2f%%')  # 饼图
    plt.title('微信好友性别分析', fontsize=18)  # 设置标题
    plt.savefig('微信好友性别分析.jpg')  # 保存图片
    plt.show()


# 微信好友城市分布
def friends_city_analysis(friends):
    province_count = friends.groupby('Province')['Province'].count()  # 统计各省份的好友数量
    province_count_order = province_count.sort_values(ascending=False)  # 降序排列
    plt.bar(province_count_order.index[:10], province_count_order.values[:10])  # 条形图,只查看前 10 个省份的好友分布
    plt.title('微信好友省份分布', fontsize=18)  # 设置标题
    plt.savefig('微信好友省份分布.jpg')  # 保存图片
    plt.show()

    city_count = friends.groupby('City')['City'].count()  # 统计各市的好友数量
    city_count_order = city_count.sort_values(ascending=False)  # 降序排列
    plt.bar(city_count_order.index[:10], city_count_order.values[:10])  # 条形图,只查看前 10 个市的好友分布
    plt.title('微信好友市区分布', fontsize=18)  # 设置标题
    plt.savefig('微信好友市区分布.jpg')  # 保存图片
    plt.show()


# 微信好友签名词云图
def signature_analysis(friends):
    signature_string = ''

    signature = friends['Signature']  # 签名列
    for i in signature.values:
        i = re.sub('<span.*?</span>', '', i)  # 正则表达式去除签名中的 <span> 无用信息
        signature_string += ''.join(i)
    print(signature_string)  # 签名信息
    create_word_cloud(signature_string)  # 生成词云图


# 去除停用词
def move_stop_words(f):
    stop_words = ['不是', '就是', '什么', '没有', '只有', '不要', '最后', '既然', '如果', '因为',
                  '而是', '而后', '不会', '不能', '一个', '只是', '一种', '一次']
    for stop_word in stop_words:
        f = f.replace(stop_word, '')
    return f


# 生成词云
def create_word_cloud(f):
    print('生成词云')
    f = move_stop_words(f)
    text = ' '.join(jieba.cut(f, cut_all=False, HMM=True))
    wc = WordCloud(
        font_path='./SimHei.ttf',  # 设置中文字体,字体放在当前程序目录下
        max_words=100,  # 设置最大的字数
        width=2000,  # 设置画布的宽度
        height=1200,  # 设置画布的高度
    )
    wordcloud = wc.generate(text)
    # 写词云图片
    wordcloud.to_file('wordcloud.jpg')
    # 显示词云文件
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()


# 获取好友头像并整合在一张图片上
def get_image(friends):
    # 当前目录下新建一个图片保存文件夹
    folder = "Picture"
    if not os.path.exists(folder):
        os.makedirs(folder)

    num = 0
    for i in friends:
        img = itchat.get_head_img(i["UserName"])  # 获取头像图片
        with open('./Picture/' + str(num) + ".png",'wb') as f:
            f.write(img)  # 将图片写入文件夹
            num += 1

    #获取文件夹内的文件个数
    length = len(os.listdir('./Picture'))
    #根据总面积求每一个图片的大小
    each_size = int(math.sqrt(float(810*810)/length))
    #每一行可以放多少个图片
    lines = int(810/each_size)
    #生成白色背景新图片
    image = Image.new('RGBA', (810, 810), 'white')
    x = 0
    y = 0
    for i in range(0,length):
        try:
            img = Image.open('./Picture/' + str(i) + ".png")
        except IOError:  # 图片出错信息显示
            print(i)
            print("Error")
        else:
            img = img.resize((each_size, each_size), Image.ANTIALIAS)  # 重新设置图片
            image.paste(img, (x * each_size, y * each_size))
            x += 1
            if x == lines:
                x = 0
                y += 1
    image.save("图片整合.png")


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)  # hotReload=True 使得程序关闭后一定时间内也可以登录,不用重新扫码
    friends = itchat.get_friends(update=True)  # 获取好友相关信息,返回 json 文件
    df_friends = pd.DataFrame(friends)
    df_friends.to_csv('./friends.csv', encoding='utf_8_sig')  # 保存信息到 csv 文件
    friends_sex_analysis(df_friends)
    friends_city_analysis(df_friends)
    signature_analysis(df_friends)
    get_image(friends)
