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

import pandas as pd 
import tensorflow as tf


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class PointList():
  def __init__(self, npoints):
    self.ptlist = []
    self.pos = 0
  
  def add(self, x, y):
    self.ptlist.append([x, y])
    self.pos += 1
    return True


def draw_ellipse(event, x, y, flags, param):
  winname, img, ptlist, cnt = param
  color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
  if event == cv2.EVENT_MOUSEMOVE:
    img_tmp = img.copy()
    if cnt[0] == 0:
      h, w = img.shape[:2]
      cv2.line(img_tmp, (x,0), (x,h), color)
      cv2.line(img_tmp, (0,y), (w,y), color)
      cv2.imshow(winname, img_tmp)
    elif cnt[0] == 1:
      cv2.rectangle(img_tmp, (ptlist.ptlist[0][0],ptlist.ptlist[0][1]), (x, y), (0, 0, 0))
      cv2.imshow(winname, img_tmp)

  if event == cv2.EVENT_LBUTTONDOWN:
    cnt[0] = cnt[0] + 1
    ptlist.add(x, y)



# 数字の部分を手動で範囲選択して、そこにある数字列を読み込む
# 範囲内の数字ひとつひとつの範囲を返す
def detect_no(img, auto, rect):
  
  if not auto:
    cnt = [0]
    winname = "Select ID Area"
    ptlist = PointList(0)
    cv2.namedWindow(winname)
    cv2.setMouseCallback(winname, draw_ellipse, [winname, img, ptlist, cnt])
    
    cv2.imshow(winname, img)
    while cnt[0]<2:
      key = cv2.waitKey(1) & 0xFF

    cv2.waitKey(100)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    print('(ID抽出)あなたが選択した範囲は\n\t(左上X座標,左上Y座標) = ({}, {})\n\t(右下X座標,右下Y座標) = ({}, {})'.format(ptlist.ptlist[0][0],ptlist.ptlist[0][1], ptlist.ptlist[1][0], ptlist.ptlist[1][1]))

    rect = [ptlist.ptlist[0][0], ptlist.ptlist[0][1], ptlist.ptlist[1][0], ptlist.ptlist[1][1]]

  img = img [rect[1]:rect[3], rect[0]:rect[2]]
  # 指定された範囲のサイズを求める
  H, W = img.shape[:2]


  # 画像を二値化(* 2)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # グレースケールに変換
  gray = cv2.GaussianBlur(gray, (5, 5) ,0) # ガウシアンフィルタで画像をぼかす
  im2 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)[1]

  # cv2.imshow("Output", im2)
  # cv2.waitKey(0)

  #輪郭を抽出（*4）
  cnts = cv2.findContours(im2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]

  # 抽出した輪郭を単純なリストに変換(* 4)
  result = []
  for pt in cnts:
    x, y, w, h = cv2.boundingRect(pt)
    # 大きすぎる小さすぎる領域を除去
    if not (H/2 < h < H): 
      continue
    if not (0 < w < H): 
      continue
    result.append([x, y, w, h])

  # 抽出した輪郭が左側から並ぶようソート(* 6)
  result = sorted (result, key=lambda x: x[0])

  # 抽出した輪郭が近すぎるものを除去(* 7)
  result2 =[]
  lastx = -10
  for x, y, w, h in result:
    if (x - lastx) < 10: 
      continue
    result2.append ( [x, y, w, h])
    lastx = x
  # 緑色の枠を描画(*8)
  img_tmp = img.copy()
  for x, y, w, h in result2:
    cv2.rectangle (img_tmp, (x, y), (x+w, y+h), (0, 255, 0), 3)

  # cv2.imshow("contour", img_tmp)
  # cv2.waitKey(0)

  return rect, result2, img


def print_no(model, cnts, img):
  l = [0] * len(cnts)
  offset = 50
  img_tmp = cv2.copyMakeBorder(img, offset, offset, offset, offset, cv2.BORDER_CONSTANT, value=[255,255,255])
  for i, pt in enumerate(cnts):
    # 画像データを取り出す
    im2 = img[pt[1]:pt[1]+pt[3], pt[0]:pt[0]+pt[2]]
    
    # データを学習済みデータに合わせる
    im2gray =cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY) # グレースケールに変換
    im2gray = cv2.threshold(im2gray, 0, 255, cv2.THRESH_OTSU)[1] # 2値化
    im2gray = cv2.copyMakeBorder(im2gray, 8,8,8,8, cv2.BORDER_CONSTANT, value=[255,255,255])
    im2gray = (255 - im2gray) # 白黒反転
    im2gray = cv2.resize(im2gray, (28, 28)) # リサイズ

    # データ予測する
    predict_prob = model.predict(im2gray.reshape(1,28,28),verbose=0)
    res = np.argmax(predict_prob,axis=1)
    # print(res[0])
    l[i] = res[0]

    cv2.rectangle (img_tmp, (offset + pt[0], offset + pt[1]), (offset + pt[0]+pt[2] , offset + pt[1]+pt[3]), (0, 255, 0), 1)
    cv2.putText(img_tmp, str(res[0]), (offset + pt[0], offset + pt[1]), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2, cv2.LINE_AA)

  cv2.imshow("result", img_tmp)
  cv2.waitKey(0)

  print(" ID = \"",end='')
  for num in l:
    print(str(num),end='')
  print("\"")




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

# PNGファイルのパスを取得しそれぞれのページを順番に捌いていく
def suminuri_first_page(dirname, is_select, rect, detectID, rect_ID, auto_ID):

  # 設定ファイルの入力値の確認

  auto = False
  if is_select == 0: # 設定ファイルで全ページ同じ範囲を指定していた場合のみ、範囲も設定ファイルから読み込む
    auto = True
  if is_select < 0 or is_select > 1:
    while True:
      is_select = input('全ページ同じ範囲を塗りつぶしますか?(Yes:0 No:1)>')
      try:
        is_select = int(is_select)
        if (is_select == 0 or is_select == 1):
          break
        else:
          print('半角で0か1を入力してください．')
      except:
        print('対応する数字を入力してください．')

  if detectID < 0 or detectID > 1:
    while True:
      detectID = input('IDの抽出をしますか?(Yes:0 No:1)>')
      try:
        detectID = int(detectID)
        if (detectID == 0 or detectID == 1):
          break
        else:
          print('半角で0か1を入力してください．')
      except:
        print('対応する数字を入力してください．')

  auto2 = False
  if detectID == 0 :
    model = tf.keras.models.load_model(dirname + '/OCR_model/trained_model_v0.h5') # 必要な場合数字認識の学習済みモデルを読み込み

    if auto_ID == 0: # 設定ファイルで全ページ同じ範囲を指定していた場合のみ、範囲も設定ファイルから読み込む
      auto2 = True
    if auto_ID < 0 or auto_ID > 1:
      while True:
        auto_ID = input('IDの範囲は固定ですか?(Yes:0 No:1)>')
        try:
          auto_ID = int(auto_ID)
          if (auto_ID == 0 or auto_ID == 1):
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

  for x in glob.glob(dirname + "/image_file/*.png"):
    img = cv2.imread(x)
    if not auto:
      cnt = [0]
      winname = "Select Anonymizing Area"
      ptlist = PointList(0)
      cv2.namedWindow(winname)
      cv2.setMouseCallback(winname, draw_ellipse, [winname, img, ptlist, cnt])
      cv2.imshow(winname, img)
      while cnt[0]<2:
        key = cv2.waitKey(1) & 0xFF

      cv2.waitKey(100)
      cv2.destroyAllWindows()
      cv2.waitKey(1)

      print('(塗りつぶし)あなたが選択した範囲は\n\t(左上X座標,左上Y座標) = ({}, {})\n\t(右下X座標,右下Y座標) = ({}, {})'.format(ptlist.ptlist[0][0],ptlist.ptlist[0][1], ptlist.ptlist[1][0], ptlist.ptlist[1][1]))
      rect = [ptlist.ptlist[0][0], ptlist.ptlist[0][1], ptlist.ptlist[1][0], ptlist.ptlist[1][1]]
    
    cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 0, 0), thickness=-1)
    
    if is_select == 0:
      auto = True

    file_name = f'{Path(x).stem}_anonymize.png'
    image_dir = Path(dirname + "/anonymize_image_file")
    image_path = f'{image_dir}/{file_name}'

    cv2.imwrite(image_path, img)

    if detectID == 0:
      rect_ID, cnts, img_id = detect_no(img, auto2, rect_ID)
      if auto_ID == 0:
        auto2 = True
      print_no(model, cnts, img_id)


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
      # pass
      print("ADD PATH: " + str(dirname + "/poppler/mac/bin"))
      os.environ["PATH"] += os.pathsep + str(dirname + "/poppler/mac/bin")
      # os.environ["PATH"] += os.pathsep + str(dirname + "/poppler/mac/lib")

  # 設定デフォルト値
  # 画質 DPI
  dpi = 150 
  # 適用するページ (各PDFのXXXページ目 すべてのページの場合"0")
  page = -1 
  # 塗りつぶし範囲選択
  is_select = -1 
  # 塗りつぶし範囲
  rect = [0, 0, 0, 0]
  # 中間ファイル削除
  is_delete = -1

  # ID範囲選択
  is_select_ID = -1
  # ID範囲選択
  is_select_ID_auto = -1
  # ID範囲
  rect_ID = [0, 0, 0, 0]




  if os.path.exists(dirname + "/config.txt"):
    f = open(dirname + '/config.txt', 'r', encoding='UTF-8')
    configs = f.readlines()
    f.close()
    if len(configs) != 14:
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
          + '0,IDの抽出をしますか?(Yes:0 No:1)\n'
          + '0,IDの範囲は固定ですか?(Yes:0 No:1)\n'
          + '0,ID範囲(左上X座標)\n'
          + '0,ID範囲(左上Y座標)\n'
          + '0,ID範囲(右下X座標)\n'
          + '0,ID範囲(右下Y座標)\n'
          )
      exit(-1)
    try:
      dpi = int(configs[0].split(',')[0])
      page = int(configs[1].split(',')[0])
      is_select = int(configs[2].split(',')[0])
      rect[0] = int(configs[3].split(',')[0])
      rect[1] = int(configs[4].split(',')[0])
      rect[2] = int(configs[5].split(',')[0])
      rect[3] = int(configs[6].split(',')[0])
      is_delete = int(configs[7].split(',')[0])
      is_select_ID = int(configs[8].split(',')[0])
      is_select_ID_auto = int(configs[9].split(',')[0])
      rect_ID[0]  = int(configs[10].split(',')[0])
      rect_ID[1]  = int(configs[11].split(',')[0])
      rect_ID[2]  = int(configs[12].split(',')[0])
      rect_ID[3]  = int(configs[13].split(',')[0])
    except:
      print('設定ファイルが半角の数値で記述されていません')
      exit(-1)



  # dirname 内のPDFファイルのパスを取得し順番に捌いていく
  convert_pdf2png(dirname, page, dpi)

  # PNGファイルのパスを取得しそれぞれの is_select ページ目を順番に捌いていく
  suminuri_first_page(dirname, is_select, rect, is_select_ID, rect_ID, is_select_ID_auto)

  # 中間ファイルの削除
  file_remove(dirname, is_delete)


if __name__ == "__main__": 
    main()


