#! /bin/sh
#
# シェルスクリプトでHTTPセッションを張るテスト
# ・このシェルスクリプトを動かすには、標準UNIXコマンド以外に下記のものが必要
#   - cgi-name (CGI変数を正規化する。Open usp Tukubaiコマンド)
#     https://github.com/usp-engineers-community/Open-usp-Tukubai/blob/master/COMMANDS.SH/cgi-name
#   - utconv   (UNIX時間との相互変換をする。拙作独自コマンド)
#     https://gist.github.com/richmikan/8703117
# ・セッションファイルは自動的には消されないので、一定時間たった古い物は
#   cron等を利用して別途削除すること。
#

# ===== ０.各種定義 ==================================================
#
Dir_SESSION='/usr/local/apache2/session'  # セッションファイル置き場
SESSION_LIFETIME_MIN=3                         # セッションの有効期限(3分にしてみた)
COOKIE_LIFETIME_MIN=5                          # Cookieの有効期限(5分にしてみた)
#
# --- エラー終了関数定義 ---------------------------------------------
error500_exit() {
  cat <<-__HTTP_RESPONSE
    Status: 500 Internal Server Error
    Content-Type: text/plain

    500 Internal Server Error
    ($@)
__HTTP_RESPONSE
  exit 1
}

mkdir -p "$Dir_SESSION" || error500_exit 'cannot create session directory'

# ===== １.セッションIDの取得とセッションファイルの操作  =============
#
# --- CookieからセッションIDを読み取る -------------------------------
session_id=$(printf '%s' "${HTTP_COOKIE:-}" | # 環境変数からCookie文字列取得
             sed 's/&/%26/g'                | # CGI変数仕様に合せるため,"&"を"%26"に置換
             sed 's/[;,[:blank:]]\{1,\}//g' | # Cookie変数の区切りを"&"に置換
             cgi-name                       | # 1行1変数化及び%エンコードを解除(独自cmd)
             grep '^session_id '            | # 変数名がsession_idの行を取り出す
             sed 's/^[^ ]* //'              ) # 変数名を除去し、中身だけ取り出す
#
# --- セッションIDの有効性検査 ---------------------------------------
session_status='new'                          # デフォルトは「要新規作成」とする
while :; do
  # --- セッションID文字列が正しい書式(英数字16文字とした)でないならNG
  if ! printf '%s' "$session_id" | grep '^[A-Za-z0-9]\{16\}$' >/dev/null; then
    break
  fi
  # --- セッションID文字列で指定されたファイルが存在しないならNG
  [ -f "$Dir_SESSION/$session_id" ] || break
  # --- ファイルが存在しても古すぎだったらNG
  if ! find "$Dir_SESSION" -name "$session_id" -mmin +$SESSION_LIFETIME_MIN |
       awk 'END{if(NR>0){exit 1;}}'
  then
    session_status='expired'
    break
  fi
  # --- これらの検査に全て合格したら使う
  session_status='exist'                 # ←そのまま使う場合
  # session_status='exist_but_update_id'    # ←セッションIDを付け直す場合
  break
done
#
# --- セッションIDに紐づくファイルの操作 -----------------------------
#
if   [ $session_status = 'exist' ]; then
  # --- (a)sessionファイル再利用
  File_session=$Dir_SESSION/$session_id
  touch "$File_session" # タイムスタンプを更新しておく
  #
elif [ $session_status = 'exist_but_update_id' ]; then
  # --- (b)sessionファイルのID付け直し
  File_session=$(mktemp $Dir_SESSION/XXXXXXXXXXXXXXXX)
  [ $? -eq 0 ] || error500_exit 'cannot create session file'
  mv -f "$Dir_SESSION/$session_id" "$File_session"
  session_id=${File_session##*/}
  #
else
  # --- (c)sessionファイル新規作成
  File_session=$(mktemp $Dir_SESSION/XXXXXXXXXXXXXXXX)
  [ $? -eq 0 ] || error500_exit 'cannot create session file'
  session_id=${File_session##*/}
fi


# ===== ２.メイン:セッションファイルの読み書き =======================
#
# --- 読み込み -------------------------------------------------------
msg=$(cat "$File_session")
if   [ \( -z "$msg" \) -a \( "$session_status" = 'new'     \) ]; then
	msg="You are new user!(ID=$session_id)"
elif [ \( -z "$msg" \) -a \( "$session_status" = 'expired' \) ]; then
	msg="Sorry, your session has expired. So, I made new session.(ID=$session_id)"
else
	msg="Hello(ID=$session_id)"
fi
#

# ===== ３.送信用セッションID文字列(Cookie)生成 ======================
#
# --- Cookieの有効期限を設定する -------------------------------------
expire=$(TZ=UTC+0 date +%Y%m%d%H%M%S                | # 現在日時取得
         TZ=UTC+0 utconv                            | # UNIX時間に変換(独自cmd)
         awk '{print $1+'$COOKIE_LIFETIME_MIN'*60}' | # 有効期限
         TZ=UTC+0 utconv -r                         | # UNIX時間から逆変換(独自cmd)
         awk '{                                     #   RFC850形式に変換
           split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec",monthname);
           split("Sun Mon Tue Wed Thu Fri Sat",weekname);
           Y = substr($0, 1,4)*1; M = substr($0, 5,2)*1; D = substr($0, 7,2)*1;
           h = substr($0, 9,2)*1; m = substr($0,11,2)*1; s = substr($0,13,2)*1;
           Y2 = (M<3) ? Y-1 : Y; M2 = (M<3)? M+12 : M;
           w = (Y2+int(Y2/4)-int(Y2/100)+int(Y2/400)+int((M2*13+8)/5)+D)%7;
           printf("%s, %02d-%s-%04d %02d:%02d:%02d GMT\n",
                  weekname[w+1], D, monthname[M], Y, h, m, s);
         }'                          )
#
# --- Cookieの有効なパスを設定する -----------------------------------
mypath='/'           # これは例なので実際はちゃんとしたものを設定すること
#
# --- このCGIが動いているのはHTTPか、それともHTTPSか -----------------
case "${HTTPS:-off}" in [Oo][Nn]) secure='; secure';; *) secure='';; esac

#
# --- Cookie文字列生成 -----------------------------------------------
cookie_sid=$(printf 'Set-Cookie: session_id=%s; expires=%s; path=/; %s' \
                    "$session_id" "$expire" "$secure"          )


# ===== ４.クライアントへ送信 ========================================
#
cat <<-HTTP_RESPONSE
Content-Type: text/html
charset: UTF-8
$cookie_sid

$msg
HTTP_RESPONSE


# ===== ９９.正常終了 ================================================
exit 0

