========== ========== ==========
  suminuri  ver.2.0
========== ========== ==========

【 ソフト名 】suminuri
【 製 作 者 】Ryosuke Hasegawa
【 開発環境 】Windows10/MacOS
【 動作環境 】Windows10/MacOS
【バージョン】2.0
【最終更新日】2022/05/19
【ファイル名】suminuri.exe(Windows)/suminuri(Mac)

---------- ----------
◇ 概要 ◇
PDFの指定した範囲を黒く塗りつぶすアプリケーションです。
一度にたくさんの書類の個人情報を隠したいときなどにご利用ください。

◇ 動作条件 ◇
Window10/MacOSともに動作確認済み
ただしマシンスペックなどで動かない恐れがあります。
何かエラーが発生したら報告ください。
報告時にPCスペックなどを添えていただけると原因解明の助けになります。

◇ ファイル構成 ◇
suminuri_app
├suminuri : Mac用実行ファイル
├suminuri.exe : Windows用実行ファイル
├poppler : Windows用PDF変換ライブラリ(MacOSのユーザは削除してもOK)
├pdf_file : オリジナルのPDFファイルを格納します。
│└sample.pdf : PDFのサンプル
└output_pdf_file : 墨塗りしたPDFファイルが保存されます。
 └sample_anonymize.pdf : PDFのサンプル

◇ インストール ◇
● Windows10
Zipファイルを解凍すればすぐに利用できます

● MacOS
1. Homebrewを下記のURLに従ってインストールします。
https://brew.sh/index_ja
次のコマンドからインストールできます。
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Homebrewを使ってpopplerをインストールします。
次のコマンドからインストールできます
brew install poppler

◇ アンインストール ◇
フォルダごと削除してください。


◇ つかいかた ◇
pdf_fileフォルダに黒塗りしたいPDFファイルを格納し、実行ファイルをダブルクリックします。
実行するとコンソールが開きます。
コンソール上でいくつか入力を受け付けるため、その指示に従ってコンソールに入力してください。

● 入力内容
  1. PDFの何ページ目を処理しますか?(0の場合全ページ)
  2. 全ページ同じ範囲を塗りつぶしますか?(Yes:0 No:1)
  3. 中間ファイルを削除しますか?(Yes:0 No:1)

入力内容2と3の間で、PDFが表示されます。
表示されたPDFの塗りつぶしたい範囲(対角2点)をクリックします。
入力内容2で0(No)を入力した場合、1ページずつ毎回範囲指定の作業が要求されます。
入力内容2で1(Yes)を入力した場合、全ページの同じ範囲を自動で黒塗りします。

最後に中間ファイルの削除を選択できます。
本アプリケーションでは
PDF -> PNG -> 黒塗りPNG -> 黒塗りPDF
という過程で塗りつぶし作業を行なっています。
ここの「PNG」と「黒塗りPNG」が中間ファイルになります。

◇ 免責 ◇


----------
◇ 連絡先 ◇
    E-mail : r-hasegawa@mspa.med.osaka-u.ac.jp

◇ 履歴 ◇
    20220519 ver.1.0 : Mac用アプリ作成
    20220519 ver.2.0 : Windows用アプリの追加
