#!/bin/sh

# パイプで送られればそれを、でなければ引数の文字列を、open_jtalkに与える。
echo $@ | open_jtalk \
-m /home/nttcom/faceRecognition/util/tohoku-f01-sad.htsvoice \
-x /var/lib/mecab/dic/open-jtalk/naist-jdic \
-ow /dev/stdout \
| aplay --quiet
