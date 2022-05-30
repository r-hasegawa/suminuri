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
            print('あなたが選択した範囲は\n\t(左上X座標,左上Y座標) = ({}, {})\n\t(右下X座標,右下Y座標) = ({}, {})'.format(xc,yc,x, y))
            rx = x
            ry = y
        cv2.imshow(winname, img)



def convert_pdf2png(dirname, page, dpi_value):
    # PDFファイルのパスを取得し順番に捌いていく
    if page < 0:
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
    else: 
        mode = page

    if not os.path.exists(dirname + "/image_file"):
        os.makedirs(dirname + "/image_file")

    for x in glob.glob(dirname + "/pdf_file/*.pdf"):
        pdf_path = Path(x)

        # pdfから画像に変換
        pages = convert_from_path(pdf_path, dpi=dpi_value)

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


def suminuri_first_page(dirname, is_select, tlx, tly, brx, bry):
    global img, img_tmp, cnt,winname, xc, yc, rx, ry
    # PNGファイルのパスを取得しそれぞれのページを順番に捌いていく
    if is_select < 0 or is_select > 1:
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
    else:
        mode = is_select


    print("Anonymizing...")
    cv2.startWindowThread()

    if not os.path.exists(dirname + "/anonymize_image_file"):
        os.makedirs(dirname + "/anonymize_image_file")
    if not os.path.exists(dirname + "/output_pdf_file"):
        os.makedirs(dirname + "/output_pdf_file")

    xc = tlx
    yc = tly
    rx = brx
    ry = bry
    rect = [xc, yc, rx, ry]
    auto = False
    if is_select == 0:
        auto = True
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

        a4 = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
        layout = img2pdf.get_layout_fun(a4)

        with open(pdf_path,"wb") as f:
            f.write(img2pdf.convert([image_path], layout_fun=layout))

    print("Finished: PNG -> PDF")


def file_remove(dirname, is_delete):
    # 中間ファイルの削除
    if is_delete < 0 or is_delete > 1:
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
    else:
        if is_delete == 1:
            return

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
    # PyInstallerによってビルドされたかどうか判定 カレントディレクトリを取得
    if getattr(sys, 'frozen', False):
        dirname = os.path.dirname(os.path.abspath(sys.executable))
        print('EXE abs dirname: ', os.path.dirname(os.path.abspath(sys.executable)))
    else:
        dirname = os.path.dirname(os.path.abspath(__file__))
        print('PYTHON abs dirname: ', os.path.dirname(os.path.abspath(__file__)))

    # poppler/binを環境変数PATHに追加する
    if os.name == 'nt':
        print("ADD PATH: " + str(dirname + "/poppler/windows/bin"))
        os.environ["PATH"] += os.pathsep + str(dirname + "/poppler/windows/bin")
    else:
        pass
        # print("ADD PATH: " + str(dirname + "/poppler/mac/bin"))
        # os.environ["PATH"] += os.pathsep + str(dirname + "/poppler/mac/bin")

    # 設定デフォルト値
    dpi = 150 
    page = -1 
    is_select = -1 
    # 塗りつぶし範囲
    tlx = 0
    tly = 0
    brx = 0
    bry = 0
    is_delete = -1




    if os.path.exists(dirname + "/config.txt"):
        f = open(dirname + '/config.txt', 'r', encoding='UTF-8')
        configs = f.readlines()
        f.close()
        if len(configs) < 8:
            print('設定ファイル(config.txt)は下記の例ように記載してください。\n'
                + '各行のカンマの前の数値を変更してください。\n'
                + '各ページで範囲指定する場合は4つの座標の数値を0に設定してください。\n\n'
                + '150,画像変換時のDPI(デフォルト150)\n'
                + '1,PDFの何ページ目を処理しますか?(0の場合全ページ)\n'
                + '0,全ページ同じ範囲を塗りつぶしますか?(Yes:0 No:1)\n'
                + '0,塗りつぶし範囲(左上X座標)\n'
                + '0,塗りつぶし範囲(左上Y座標)\n'
                + '0,塗りつぶし範囲(右下X座標)\n'
                + '0,塗りつぶし範囲(右下Y座標)\n'
                + '0,中間ファイルを削除しますか?(Yes:0 No:1)\n'
                )
            exit(-1)
        try:
            dpi = int(configs[0].split(',')[0])
            page = int(configs[1].split(',')[0])
            is_select = int(configs[2].split(',')[0])
            tlx = int(configs[3].split(',')[0])
            tly = int(configs[4].split(',')[0])
            brx = int(configs[5].split(',')[0])
            bry = int(configs[6].split(',')[0])
            is_delete = int(configs[7].split(',')[0])
        except:
            print('設定ファイルが半角の数値で記述されていません')
            exit(-1)



    # PDFファイルのパスを取得し順番に捌いていく
    convert_pdf2png(dirname, page, dpi)

    # PNGファイルのパスを取得しそれぞれの1ページ目を順番に捌いていく
    suminuri_first_page(dirname, is_select, tlx, tly, brx, bry)

    # 中間ファイルの削除
    file_remove(dirname, is_delete)


if __name__ == "__main__": 
    main()


