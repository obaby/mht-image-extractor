# -*- coding: utf-8 -*-
"""
@author: obaby
@license: (C) Copyright 2013-2020, obaby@mars.
@contact: root@obaby.org.cn
@link: http://www.obaby.org.cn
        http://www.h4ck.org.cn
        http://www.findu.co
@file: baby_mht_image_extractor.py
@time: 2020/5/22 20:46
@desc:
"""

import base64
import getopt
import os
import quopri
import sys

from pyfiglet import Figlet

current_path = os.path.dirname(os.path.abspath(__file__))
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
current_path = dirname
OUT_PATH = os.path.join(current_path, 'out')


def convert_mht_to_list(boundary, html_content):
    return str(html_content).split(boundary)


def get_boundary(html_content):
    return '--' + str(html_content).split(';')[-1].split('=')[-1]


def make_dir(floder_name):
    PATH = os.path.join(OUT_PATH, floder_name)
    if not os.path.exists(PATH):
        os.makedirs(PATH)
        os.chdir(PATH)
    return PATH


def save_image_file(image_content, path, file_name):
    try:
        file_path = os.path.join(path, file_name)
        make_dir(path)
        with open(file_path, 'wb') as f:
            f.write(image_content)
            print('[S] 保存图片成功')
        return file_path
    except Exception as e:
        # print(e)
        print('[S] 保存图片失败: ' + str(e))
        return None


def get_content_type(sub_content):
    content_type = 'Unknown'
    for l in sub_content:
        if 'Content-Type' in l:
            content_type = l.split(';')[0].split(':')[1]
            break
    return content_type


def get_content_encoding(sub_content):
    content_encoding = 'unknown'
    pass_count = 0
    for l in sub_content:
        if 'Content-Transfer-Encoding' in l:
            content_encoding = l.split(':')[1].replace(' ', '')
            break
        pass_count += 1
    return content_encoding, pass_count


def get_content_type_and_content(line, sub_path_name, index):
    line = str(line)
    sub_content = line.split('\n')
    if 'Content-Disposition' in line:
        try:
            file_name = sub_content[0].split(';')[1].split('=')[1]
            if 'filename*0' in sub_content[0]:
                file_name = 'default.jpg'
        except:
            file_name = 'default.jpg'

        content_type = get_content_type(sub_content)
        content_encoding, psc = get_content_encoding(sub_content)
        content = ''.join(sub_content[psc+1:])

        if 'image' in content_type:
            filename = str(index) + '_' + file_name
            print('[S] 正在保存图片文件:', filename)
            decoded_body = None
            if content_encoding.lower() == 'quoted-printable':
                decoded_body = quopri.decodestring(content)
            if content_encoding.lower() == 'base64':
                decoded_body = base64.b64decode(content)
            if decoded_body:
                save_image_file(decoded_body, sub_path_name, filename)
            else:
                print('[S] 图片解码失败，无法保存')
    return


def print_usage():
    print('*' * 100)
    # f = Figlet(font='slant')
    f = Figlet()
    print(f.renderText('obaby@mars'))
    print('mht image extractor by obaby')
    print('Verson: 0.5.22')
    print('baby_mht_image_extractor -f <input mht file> -o <output path> -p <input path>')
    print('Need Arguments:')
    print('\t -f <input mht file>')
    print('\t -o <output path> ')
    print('Option Arguments:')
    print('\t -p <input path>')
    print('Blog: http://www.h4ck.org.cn')
    print('*' * 100)


def save_mht_all_images(input_path):
    sub_path_name = os.path.join(OUT_PATH, os.path.basename(input_path).title())
    with open(input_path, 'r', ) as f:
        first_line = f.readline()
        body_content = f.read()
        boundary = get_boundary(first_line)
        content_list = convert_mht_to_list(boundary, html_content=body_content)
        index = 0
        for l in content_list:
            get_content_type_and_content(l, sub_path_name, index)
            index += 1


def main(argv):
    global OUT_PATH
    input_path = ''
    outputpath = ''
    input_file = ''
    try:
        opts, args = getopt.getopt(argv, "hf:o:p:", ["file=", "opath=", "ipath="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            input_file = arg
        elif opt in ("-p", "--ipath"):
            input_path = arg
        elif opt in ("-o", "--opath"):
            outputpath = arg

    if input_file == '' and input_path == '':
        print_usage()
        sys.exit(2)

    if outputpath != '':
        OUT_PATH = outputpath

    print('*' * 100)
    print('[S] 开始任务......')
    print('[C] 输入文件:' + input_file)
    print('[C] 输入目录:' + input_path)
    print('[C] 输出目录:' + OUT_PATH)

    if os.path.isfile(input_file):
        save_mht_all_images(input_file)
        print('[D] 导出全部完成。')
        print('*' * 100)
    else:
        if os.path.isdir(input_path):
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    print('[S] 开始处理文件:', file)
                    save_mht_all_images(os.path.join(root, file))
                    print('-' * 80)
            print('[D] 导出全部完成。')
            print('*' * 100)
        else:
            print_usage()


if __name__ == '__main__':
    main(sys.argv[1:])
