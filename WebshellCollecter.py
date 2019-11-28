# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Webshell自动收集器
# - 作者：ArrowQin
# - 更新时间：2019.11.27
# ---
# ## 功能说明
# 1. Github上webshell项目代码的自动更新
# 2. webshell代码重复检测
# 3. webshell静态特征提取
# 4. 本地webshell存储
# %% [markdown]
# ## 一、导入相关的包

# %%
import requests
import urllib3
from urllib import request
import zipfile
import os
import re
import time
import difflib
import shutil
import random

# %% [markdown]
# ## 二、程序日志保存
# 1. error_log：程序错误日志
# 2. run_log：程序运行日志

# %%
def error_log(information):
    print(information)
    run_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(time.strftime("%Y-%m-%d")+"errorlog.txt","a+",encoding='utf-8') as file:
        information = run_time + "  " + information + "\n"
        file.writelines(information)
def run_log(information):
    print(information)
    run_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(time.strftime("%Y-%m-%d")+"runlog.txt","a+",encoding='utf-8') as file:
        information = run_time + "  " + information + "\n"
        file.writelines(information)

# %% [markdown]
# ## 三、程序初始化

# %%
def initialize():
    # 1.创建文件夹
    foldernames=['Webshell-code','Webshell-code-temp','Webshell-feature','Webshell-storage','Zip']
    for foldername in foldernames:
        if not os.path.exists(foldername):
            os.makedirs(foldername)
            print('创建路径:',foldername)
# initialize()

# %% [markdown]
# ## 四、从Github仓库下载Webshell

# %%
# 下载github仓库zip压缩包到ZIP文件夹
def download_zip_from_github(url,save_path='./Zip/'):
    file_name = url.split('/')[-1]
    response = requests.get(url)
    content = response.text
    btn = content.split('btn btn-outline get-repo-btn js-anon-download-zip-link ')[1]
    zip_url = 'https://github.com' + btn.split('href="')[1].split('"')[0].strip()
    def reporthook(down,block,size): #当前传输的块数,块的大小,总数据大小
        #显示下载进度
        per = 100.0 * down * block / size
        down_byte = down * block
        down_KB = down_byte / 1024
        down_MB = down_KB / 1024
        # print(down,block,size)  #当无法得到size时，size=-1，下载进度出错，为正常现象
        if per > 100:
            per = 100
        if size != -1:
            print(url,'已下载:','%.2f%%'%per)
        else:
            if down_MB > 1:
                print(url,'已下载:',down_MB,"MB")
            else:
                if down_KB > 1:
                    print(url,'已下载:',down_KB,'KB')
                else:
                    print(url,'已下载:',down_byte,'B')
    try:
        request.urlretrieve(zip_url, save_path + file_name + '.zip',reporthook=reporthook)
    except:
        try:
            with open(save_path + file_name + '.zip', 'wb') as code:
                code.write(requests.get(zip_url).content)
        except:
            try:
                http = urllib3.PoolManager()
                r = http.request('GET', zip_url)
                with open(save_path + file_name + '.zip', 'wb') as code:
                    code.write(r.data)
            except Exception as e:
                error_log(str(e))
                run_log(url + ' 下载失败')
                return 0
    run_log(url + ' 下载完成')

# 解压ZIP压缩包到Webshell-code-temp文件夹
def un_zip(un_zip_filename,path='./Webshell-code-temp'):
    zip_file = zipfile.ZipFile(un_zip_filename)
    zip_file.extractall(path=path)
    run_log(un_zip_filename+'已解压')

# %% [markdown]
# ## 五、判断github仓库是否更新
# 1. 与本地仓库webshell-code文件夹内容进行比较
# 2. 将更新的文件路径添加到列表update_list

# %%
def contrast_dir(foldername):
    update_list=[]
    dir_old = './Webshell-code/'+foldername
    dir_temp = './Webshell-code-temp/'+foldername
    for dirpath, dirnames, filenames in os.walk(dir_temp):
        for filename in filenames:
            pathname1 = os.path.join(dirpath, filename) # temp文件的路径
            pathname2 = re.sub('-temp','',pathname1,1) # 对应仓库中的文件路径
            if os.path.exists(pathname2):
                pass
            else:
                run_log('发现更新的文件:'+pathname1)
                update_list.append(pathname1)
    if len(update_list) == 0:
        run_log('没有文件更新:'+dir_temp)
    return update_list

# %% [markdown]
# ## 六、webshell相似度比较
# 1. 使用python自带的difflib.SequenceMatcher方法比较两个文件的相似度
# 2. 将更新的webshell与本地webshell-storage文件夹下没有重复webshell进行相似度比较
# 3. 如果相似度>0.95,则认为storge中以及存在相似的webshell,否则将webshell加入到storage中
# 4. 并将这些不同的webshell的路径，通过列表different_list返回，并存储到different_webshell.txt

# %%
def similarity_detect(update_list):
    different_list = []
    for update_file_path in update_list:
        try:
            with open(update_file_path,'r',encoding='utf-8') as file:
                new_file=file.read()
        except:
            try:
                with open(update_file_path,'r',encoding='ISO-8859-2') as file:
                    new_file=file.read()
            except Exception as e:
                error_log(str(e))
                print(e)          
        dir_storage = './Webshell-storage/'
        flag = 0 #flag=0不存在相似文件
        for dirpath, dirnames, filenames in os.walk(dir_storage):
            for filename in filenames:
                storage_file_path = os.path.join(dirpath, filename)
                try:
                    with open(storage_file_path,'r',encoding='utf-8') as file:
                        storage_file=file.read()
                except:
                    try:
                        with open(storage_file_path,'r',encoding='ISO-8859-2') as file:
                            storage_file=file.read()
                    except Exception as e:
                        error_log(str(e))
                        print(e)     
                similarity = difflib.SequenceMatcher(None, new_file, storage_file).quick_ratio()
                # print('文件差异度：',round(similarity,4),'\tupdate-file:',update_file_path,'\tstorage-file:',storage_file_path)
                if similarity > 0.95:
                    print('存在相似文件','update-file:',update_file_path,'\tstorage-file:',storage_file_path,'文件差异度：',round(similarity,4))
                    flag = 1 #flag=1 存在相似文件
                    break
        if flag == 0: #不存在相似文件
            src = update_file_path
            dst = dir_storage + os.path.basename(update_file_path)
            shutil.copyfile(src, dst)
            different_list.append(update_file_path)
            run_log('发现新webshell，复制文件到webshell-storage: '+update_file_path)
    
    with open("different_webshell.txt",'a+',encoding='utf-8') as file:
        for d in different_list:        
            d+='\n'
            file.writelines(d)
    return different_list

# %% [markdown]
# ## 七、提取静态特征
# 1. 目前只提取id=与form特征
# 2. 对于重名的webshell,修改文件名为 原文件名-随机0-10数字

# %%
def get_feature(files):
    if files == None:
        run_log("不存在新的Webshell，无需提取特征")
        return 0
    for filename in files:
        features=[]
        try:
            with open(filename,'r',encoding='utf-8') as file:
                lines = file.readlines()
        except:
            try:
                with open(filename,'r',encoding='ISO-8859-1') as file:
                    lines = file.readlines()
            except Exception as e:
                error_log(str(e))
                error_log("get_feature()无法读取文件:"+filename)
                continue
        for line in lines:
            if 'id=' in line or 'form ' in line:
                # print(re.sub(" ","",line))
                for l in re.findall("<.*?>",line):
                    if len(l) > 10: #去除标签
                        features.append(re.sub("\\\\","",l))
        if len(features) != 0:
            features = [feature+'\n' for feature in features]
            save_path ='./Webshell-feature/'+ os.path.basename(update_file_path)
            while os.path.exists(save_path+'.txt'):  #处理重名
                save_path+='-'
                save_path+=str(random.randint(1,10))
            with open(save_path+'.txt','w',encoding='utf-8') as file:
                file.writelines(features)
                run_log("update feature:"+save_path)

# %% [markdown]
# # 八、更新本地webshell仓库
# 1. 更新update_list中的文件到webshell-code
# 2. 删除webshell-code-temp

# %%
def update_code(update_list):
    try:
        # 将更新的webshell覆盖到webshell-code
        for update_file_path in update_list:
            dst = re.sub('-temp','',update_file_path,1)
            dir_name = os.path.dirname(dst)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print('创建路径:',dir_name)
            src = update_file_path
            shutil.copyfile(src, dst)
            run_log('更新webshell到本地: '+update_file_path)

        # 删除Webshell-code-temp全部内容
        if os.path.exists('./Webshell-code-temp/'):
            shutil.rmtree('./Webshell-code-temp/',True)
            print('已删除：./Webshell-code-temp/')
            os.mkdir('Webshell-code-temp')

    except Exception as e:
        error_log('更新wenshell-code出现错误：'+str(e))

# %% [markdown]
# # 九、运行程序  
# 说明：目前收录github上5个项目的webshell源码文件  
# 'https://github.com/tennc/webshell',  
# 'https://github.com/ysrc/webshell-sample',  
# 'https://github.com/JohnTroony/php-webshells',  
# 'https://github.com/xl7dev/WebShell'  
# 'https://github.com/b374k/b374k'  

# %%
def dataprocess(url):
    download_zip_from_github(url) #从github上下载对应项目的zip文件
    un_zip(un_zip_filename='./Zip/'+ url.split('/')[-1] +'.zip') #对zip文件进行解压，存储到webshell-code-temp目录下
    update_list = contrast_dir(foldername=url.split('/')[-1]+'-master') #将webshell-code-temp目录下的代码和webshell-code下的代码进行比较，找出更新的代码
    different_list = similarity_detect(update_list) # 输入更新的代码，与webshell-storage中的代码进行相似度比较
    ### print("different_list:",different_list)
    get_feature(different_list) #获取可能的特征,目前只有id和form
    update_code(update_list) # 更新webshell-code,删除webshell-code-temp

def webshell_collecter():
    initialize() #程序初始化
    webshell_git_repository_url = [
        'https://github.com/tennc/webshell',
        'https://github.com/ysrc/webshell-sample',
        'https://github.com/JohnTroony/php-webshells',
        'https://github.com/xl7dev/WebShell',
        'https://github.com/b374k/b374k'
    ]
    for url in webshell_git_repository_url:
        dataprocess(url)

# %% [markdown]
# ## 十、提取webshell特征  
# 1. 输入：webshell路径的txt文件
# 

# %%
def get_feature_from_file(filename):
    with open(filename,'r',encoding='utf-8') as file:
        different_list = file.readlines()
    different_list = [list[:-1] for list in different_list]
    get_feature(different_list)
    # 导入成功后删除文件中的内容
    os.remove(filename)
    print(filename,"已删除")


# get_feature_from_file("different_webshell.txt") #导入失败使用

