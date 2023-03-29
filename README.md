# lambda video thumbnail

S3 への PUT 契機で動画のサムネイル画像を生成する Lambda 関数。
また、既存の動画に対するサムネイル画像を生成するバッチ処理も定義。


## 動作環境

* Python 3.11.2
* ffmpeg version 5.1.2 (ARM64)


## Lambda レイヤーの作成

```
mkdir -p ./layout
cd ./layout

wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz
tar xvf ffmpeg-release-arm64-static.tar.xz

mkdir -p ./ffmpeg/bin
cp ./ffmpeg-5.1.1-arm64-static/ffmpeg ./ffmpeg/bin
cd ffmpeg
zip -r ../ffmpeg.zip .
```

上記で生成した zip を Lambda レイヤーとして登録し、lambda の実行レイヤーとして指定すること。