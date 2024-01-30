#! /bin/sh


Dir_SESSION='/usr/local/apache2/session'  # セッションファイル置き場
COOKIE_LIFETIME_MIN=30                    # Cookieの有効期限

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


print_stderr() {
	echo "$@" >&2
}

mkdir -p "$Dir_SESSION" || error500_exit 'cannot create session directory'


session-check "${HTTP_COOKIE:-}"

if [ $? -eq 0 ]; then
	# セッションが有効ならば、ログイン済みとしてトップページへリダイレクト
	cat <<-__HTTP_RESPONSE
		Status: 302 Found
		Location: /index.html?session_id=$session_id
__HTTP_RESPONSE

fi

body=$(dd bs=$CONTENT_LENGTH | cgi-name)
print_stderr "$body"
user=$(printf '%s' "$body" | grep '^username ' | sed 's/^[^ ]* //')
pass=$(printf '%s' "$body" | grep '^password ' | sed 's/^[^ ]* //')
print_stderr "$user"
print_stderr "$pass"

# ユーザー名とパスワードのチェック

# もしユーザー名とパスワードが正しくなければログインフォームをへリダイレクト

if [ $user != 'admin' -o $pass != 'admin' ]; then
	# ユーザー名とパスワードが正しくなければログインフォームをへリダイレクト
	cat <<-__HTTP_RESPONSE
		Status: 302 Found
		Location: /login.html?error=1

__HTTP_RESPONSE

	exit 0
fi


# セッションIDを生成
# セッションIDは、ランダムな英数字16文字とする
File_session=$(mktemp $Dir_SESSION/XXXXXXXXXXXXXXXX)
[ $? -eq 0 ] || error500_exit 'cannot create session file'
session_id=${File_session##*/}

# セッションファイルにユーザー名を書き込む
echo "$user" > "$File_session"

# セッションIDをCookieにセット
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
# --- このCGIが動いているのはHTTPか、それともHTTPSか -----------------
case "${HTTPS:-off}" in [Oo][Nn]) secure='; secure';; *) secure='';; esac

#
# --- Cookie文字列生成 -----------------------------------------------
cookie_sid=$(printf 'Set-Cookie: session_id=%s; expires=%s; path=/; %s' \
                    "$session_id" "$expire" "$secure"          )


# ログイン成功したらトップページへリダイレクト
cat <<-__HTTP_RESPONSE
	Status: 302 Found
	Location: /index.html?session_id=$session_id
	$cookie_sid

__HTTP_RESPONSE

exit 0
