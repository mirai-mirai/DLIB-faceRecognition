#!/bin/sh

# パイプで送られればそれを、でなければ引数の文字列を、open_jtalkに与える。
echo $@ | open_jtalk \
-m /usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice \
-x /var/lib/mecab/dic/open-jtalk/naist-jdic \
-ow /dev/stdout \
| aplay --quiet
