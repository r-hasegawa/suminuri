import os
from pathlib import Path
from pdf2image import convert_from_path
import glob
import cv2
import numpy as np
import img2pdf
import sys
import random
import shutil

# すべてのページ
# 1ページ目のみ


def draw_ellipse(event, x, y, flags, param):
    global cnt, xc, yc, rx, ry
    color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    if event == cv2.EVENT_MOUSEMOVE:
        img_tmp = img.copy()
        if cnt == 0:
            h, w = img.shape[:2]
            cv2.line(img_tmp, (x,0), (x,h), color)
            cv2.line(img_tmp, (0,y), (w,y), color)
            cv2.imshow(winname, img_tmp)
        elif cnt == 1:
            cv2.rectangle(img_tmp, (xc,yc), (x, y), (0, 0, 0))
            cv2.imshow(winname, img_tmp)

    if event == cv2.EVENT_LBUTTONDOWN:
        cnt = cnt + 1
        if cnt == 1:
            xc, yc = x, y
        elif cnt == 2:
            cv2.rectangle(img, (xc,yc), (x, y), (0, 0, 0), thickness=-1)
            # print((xc,yc), (x, y))
            rx = x
            ry = y
        cv2.imshow(winname, img)



def convert_pdf2png(dirname):
    # PDFファイルのパスを取得し順番に捌いていく
    while True:
        mode = input('PDFの何ページ目を処理しますか?(0の場合全ページ)>')
        try:
            mode = int(mode)
        except:
            print('数字を入力してください．')
        else:
            if (mode >= 0):
                break
            else:
                print('半角で0以上の数字を入力してください．')

    if not os.path.exists(dirname + "/image_file"):
        os.makedirs(dirname + "/image_file")

    for x in glob.glob(dirname + "/pdf_file/*.pdf"):
        pdf_path = Path(x)

        # pdfから画像に変換
        pages = convert_from_path(pdf_path, dpi=150)

        # 画像ファイルを1ページずつ「image_file」に保存する。
        image_dir = Path(dirname +"/image_file")

        if(mode == 0):
            for i, page in enumerate(pages):
                # ファイルネームを決定する。
                file_name = f'{pdf_path.stem}_{i + 1:02}.png'
                image_path = f'{image_dir}/{file_name}'
                # PNGで保存
                page.save(image_path, "PNG")
        else:
            file_name = f'{pdf_path.stem}.png'
            image_path = f'{image_dir}/{file_name}'
            # PNGで保存
            if mode <= len(pages):
                pages[mode - 1].save(image_path, "PNG")
            else:
                print(pdf_path.stem + ": " + str(mode) + "ページ目が存在しないためスキップします.")


    print("Finished: PDF -> PNG")


def suminuri_first_page(dirname):
    global img, img_tmp, cnt,winname, xc, yc, rx, ry
    # PNGファイルのパスを取得しそれぞれの1ページ目を順番に捌いていく
    while True:
        mode = input('全ページ同じ範囲を塗りつぶしますか?(Yes:0 No:1)>')
        try:
            mode = int(mode)
            if (mode == 0 or mode == 1):
                break
            else:
                print('半角で0か1を入力してください．')
        except:
            print('対応する数字を入力してください．')


    print("Anonymizing...")
    cv2.startWindowThread()

    if not os.path.exists(dirname + "/anonymize_image_file"):
        os.makedirs(dirname + "/anonymize_image_file")
    if not os.path.exists(dirname + "/output_pdf_file"):
        os.makedirs(dirname + "/output_pdf_file")

    rect = [0, 0, 0, 0]
    auto = False
    for x in glob.glob(dirname + "/image_file/*.png"):
    # for x in glob.glob(dirname + "/image_file/*_01.png"):
        img = cv2.imread(x)
        if not auto:
            cnt = 0
            winname = "GUI tool"
            cv2.namedWindow(winname)
            cv2.setMouseCallback(winname, draw_ellipse)
            cv2.imshow(winname, img)
            while cnt<2:
                key = cv2.waitKey(1) & 0xFF

            cv2.waitKey(100)
            cv2.destroyAllWindows()
            cv2.waitKey(1)
        else:
            cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 0, 0), thickness=-1)
        
        if mode == 0:
            auto = True
            rect = [xc ,yc, rx, ry]
        file_name = f'{Path(x).stem}_anonymize.png'
        image_dir = Path(dirname + "/anonymize_image_file")
        image_path = f'{image_dir}/{file_name}'

        cv2.imwrite(image_path, img)


        file_name = f'{Path(x).stem}_anonymize.pdf'
        pdf_dir = Path(dirname + "/output_pdf_file")
        pdf_path = f'{pdf_dir}/{file_name}'

        with open(pdf_path,"wb") as f:
            f.write(img2pdf.convert([image_path]))

    print("Finished: PNG -> PDF")


def file_remove(dirname):
    # 中間ファイルの削除
    while True:
        mode = input('中間ファイルを削除しますか?(Yes:0 No:1)>')
        try:
            mode = int(mode)
            if (mode == 0):
                break
            elif (mode == 1):
                return
            else:
                print('半角で0か1を入力してください．')
        except:
            print('対応する数字を入力してください．')

    # for x in glob.glob(dirname + "/image_file/*.png"):
    #     os.remove(x)
    # os.rmdir(dirname + "/image_file")
    # for x in glob.glob(dirname + "/anonymize_image_file/*.png"):
    #     os.remove(x)
    # os.rmdir(dirname + "/anonymize_image_file")
    shutil.rmtree(dirname + "/image_file")
    shutil.rmtree(dirname + "/anonymize_image_file")


def main():
    print("APP START")
    if getattr(sys, 'frozen', False):
        dirname = os.path.dirname(os.path.abspath(sys.executable))
        print('EXE abs dirname: ', os.path.dirname(os.path.abspath(sys.executable)))
    else:
        dirname = os.path.dirname(os.path.abspath(__file__))
        print('PYTHON abs dirname: ', os.path.dirname(os.path.abspath(__file__)))

    # poppler/binを環境変数PATHに追加する
    if os.name == 'nt':
        print("ADD PATH: " + str(dirname + "/poppler/bin"))
        os.environ["PATH"] += os.pathsep + str(dirname + "/poppler/bin")
    else:
        pass
        # print("ADD PATH: " + str(dirname + "/poppler/mac/bin"))
        # os.environ["PATH"] += os.pathsep + str(dirname + "/poppler/mac/bin")

    # PDFファイルのパスを取得し順番に捌いていく
    convert_pdf2png(dirname)

    # PNGファイルのパスを取得しそれぞれの1ページ目を順番に捌いていく
    suminuri_first_page(dirname)

    # 中間ファイルの削除
    file_remove(dirname)


if __name__ == "__main__": 
    main()


