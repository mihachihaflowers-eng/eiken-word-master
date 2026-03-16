# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import sys
import os
import tempfile

# ===== カリキュラム定義 =====
LESSONS = [
    # --- 第1章: 基礎 ---
    {
        "title": "1. はじめてのPython - print()",
        "explanation": """【第1講】はじめてのPython — print()

Pythonで最初に覚える命令は print() です。
画面に文字や数値を表示できます。

■ 基本構文
    print(表示したいもの)

■ ポイント
- 文字列は " " または ' ' で囲む
- 数値はそのまま書く
- print() を複数書けば複数行表示できる
""",
        "code": """print("Hello, World!")
print("Pythonの勉強を始めよう！")
print(42)
print(3.14)
"""
    },
    {
        "title": "2. コメント",
        "explanation": """【第2講】コメント

コメントとはプログラムの説明文です。
実行されません。コードを読みやすくするために使います。

■ 1行コメント
    # シャープの後ろはコメント

■ 複数行コメント（文字列を使う方法）
    '''
    ここはコメント
    '''
""",
        "code": """# これはコメントです（実行されない）
print("コメントは # で書きます")  # 行の途中からもOK

'''
複数行のコメントは
シングルクォート3つで囲みます
'''
print("複数行コメントの後も実行される")
"""
    },
    {
        "title": "3. 変数",
        "explanation": """【第3講】変数

変数はデータに名前をつけて保存する箱です。

■ 変数の作り方
    変数名 = 値

■ 命名ルール
- 英数字とアンダースコア(_)が使える
- 数字で始めてはいけない
- 大文字小文字は区別される

■ 変数名の慣習
- snake_case（小文字+アンダースコア）を使う
  例: my_name, total_score
""",
        "code": """name = "太郎"
age = 20
height = 170.5

print(name)
print(age)
print(height)

# 変数は上書きできる
age = 21
print("来年の年齢:", age)
"""
    },
    {
        "title": "4. 数値型 (int / float)",
        "explanation": """【第4講】数値型 — int と float

Pythonの数値には主に2種類あります。

■ int（整数）
    x = 10
    y = -5

■ float（小数）
    pi = 3.14
    temp = -0.5

■ 確認方法
    type(変数) で型を確認できる

■ よく使う演算
    +  加算
    -  減算
    *  乗算
    /  除算（結果はfloat）
    // 整数除算（切り捨て）
    %  余り
    ** べき乗
""",
        "code": """x = 10
y = 3

print(type(x))   # int
print(type(3.14))  # float

print(x + y)   # 13
print(x - y)   # 7
print(x * y)   # 30
print(x / y)   # 3.333...
print(x // y)  # 3（切り捨て）
print(x % y)   # 1（余り）
print(x ** y)  # 1000（べき乗）
"""
    },
    {
        "title": "5. 文字列型 (str)",
        "explanation": """【第5講】文字列型 — str

文字列は文字の並びです。

■ 作り方
    s1 = "ダブルクォート"
    s2 = 'シングルクォート'
    s3 = \"""複数行
    文字列\"""

■ 連結と繰り返し
    "Hello" + " World"  → "Hello World"
    "abc" * 3           → "abcabcabc"

■ よく使うメソッド
    s.upper()   大文字
    s.lower()   小文字
    s.strip()   前後の空白削除
    s.replace(a, b)  置換
    len(s)      長さ
""",
        "code": """s = "Hello, Python!"
print(s)
print(len(s))          # 文字数
print(s.upper())       # 大文字
print(s.lower())       # 小文字
print(s.replace("Python", "World"))  # 置換

# 連結
first = "太郎"
last = "山田"
full = last + " " + first
print(full)

# 繰り返し
print("=" * 20)
"""
    },
    {
        "title": "6. 真偽値 (bool)",
        "explanation": """【第6講】真偽値 — bool

bool型は True（真）か False（偽）の2値だけを持ちます。

■ 値
    True   正しい
    False  間違い

■ 比較演算子の結果はbool
    5 > 3  → True
    5 < 3  → False

■ bool()で変換できる
- 0, "", [], None → False
- それ以外        → True
""",
        "code": """a = True
b = False

print(a)
print(b)
print(type(a))

# 比較結果はbool
print(10 > 5)    # True
print(10 == 5)   # False
print(10 != 5)   # True

# bool()変換
print(bool(0))    # False
print(bool(1))    # True
print(bool(""))   # False
print(bool("hi")) # True
"""
    },
    {
        "title": "7. 型変換",
        "explanation": """【第7講】型変換

型を別の型に変換できます。

■ 変換関数
    int("123")    → 123（文字列→整数）
    float("3.14") → 3.14（文字列→小数）
    str(42)       → "42"（整数→文字列）
    bool(0)       → False

■ よくある場面
- input() の結果は常に str なので、
  数値として使うには int() や float() が必要
""",
        "code": """# 文字列 → 数値
s = "100"
n = int(s)
print(n + 50)   # 150

# 数値 → 文字列
age = 25
msg = "年齢は" + str(age) + "歳です"
print(msg)

# float変換
pi_str = "3.14"
pi = float(pi_str)
print(pi * 2)

# 整数→floatも可能
print(float(5))  # 5.0
"""
    },
    {
        "title": "8. 算術演算子",
        "explanation": """【第8講】算術演算子

数値の計算に使う演算子です。

■ 一覧
    +    加算
    -    減算
    *    乗算
    /    除算（float）
    //   整数除算（切り捨て）
    %    剰余（余り）
    **   べき乗

■ 複合代入演算子（省略形）
    x += 3   ← x = x + 3
    x -= 3
    x *= 3
    x /= 3
""",
        "code": """a = 17
b = 5

print(a + b)   # 22
print(a - b)   # 12
print(a * b)   # 85
print(a / b)   # 3.4
print(a // b)  # 3
print(a % b)   # 2
print(a ** 2)  # 289

# 複合代入
x = 10
x += 5
print(x)  # 15
x *= 2
print(x)  # 30
"""
    },
    {
        "title": "9. 比較演算子",
        "explanation": """【第9講】比較演算子

2つの値を比較してboolを返します。

■ 一覧
    ==   等しい
    !=   等しくない
    <    より小さい
    >    より大きい
    <=   以下
    >=   以上

■ 注意
    = は代入、== は比較
""",
        "code": """x = 10
y = 20

print(x == y)   # False
print(x != y)   # True
print(x < y)    # True
print(x > y)    # False
print(x <= 10)  # True
print(x >= 10)  # True

# 文字列の比較（辞書順）
print("apple" < "banana")  # True
print("a" == "a")          # True
"""
    },
    {
        "title": "10. 論理演算子",
        "explanation": """【第10講】論理演算子

複数の条件を組み合わせます。

■ 一覧
    and   両方True → True
    or    どちらかTrue → True
    not   反転（True↔False）

■ 例
    True and True   → True
    True and False  → False
    True or False   → True
    not True        → False

■ 短絡評価
- and: 左がFalseなら右を評価しない
- or:  左がTrueなら右を評価しない
""",
        "code": """a = True
b = False

print(a and b)   # False
print(a or b)    # True
print(not a)     # False
print(not b)     # True

# 数値との組み合わせ
x = 15
print(x > 10 and x < 20)   # True
print(x < 5 or x > 10)     # True
print(not (x == 15))        # False
"""
    },
    # --- 第2章: 制御フロー ---
    {
        "title": "11. if文 (条件分岐)",
        "explanation": """【第11講】if文 — 条件分岐

条件によって実行するコードを変えます。

■ 基本構文
    if 条件:
        処理A
    elif 別の条件:
        処理B
    else:
        処理C

■ ポイント
- インデント（スペース4つ）が必須
- elif は何個でも書ける
- else は省略可能
""",
        "code": """score = 75

if score >= 90:
    print("優秀")
elif score >= 70:
    print("合格")
elif score >= 50:
    print("もう少し")
else:
    print("不合格")

# 入れ子のif
age = 20
has_id = True
if age >= 18:
    if has_id:
        print("入場できます")
    else:
        print("IDが必要です")
else:
    print("未成年は入場不可")
"""
    },
    {
        "title": "12. for文 (繰り返し)",
        "explanation": """【第12講】for文 — 繰り返し

リストや範囲の各要素に対して処理を繰り返します。

■ 基本構文
    for 変数 in イテラブル:
        処理

■ range()
    range(5)      → 0,1,2,3,4
    range(1, 6)   → 1,2,3,4,5
    range(0, 10, 2) → 0,2,4,6,8
""",
        "code": """# リストのfor
fruits = ["りんご", "バナナ", "みかん"]
for fruit in fruits:
    print(fruit)

print("---")

# range()のfor
for i in range(5):
    print(i)

print("---")

# 合計を計算
total = 0
for n in range(1, 11):
    total += n
print("1〜10の合計:", total)
"""
    },
    {
        "title": "13. while文 (条件付き繰り返し)",
        "explanation": """【第13講】while文 — 条件付き繰り返し

条件がTrueの間、繰り返します。

■ 基本構文
    while 条件:
        処理

■ 注意
- 条件が永遠にTrueだと無限ループ！
- 必ずループを終わらせる処理を書く
""",
        "code": """# 基本的なwhile
count = 0
while count < 5:
    print("カウント:", count)
    count += 1

print("---")

# カウントダウン
n = 3
while n > 0:
    print(n)
    n -= 1
print("発射！")
"""
    },
    {
        "title": "14. break と continue",
        "explanation": """【第14講】break と continue

ループの流れを制御します。

■ break
    ループを即座に終了する

■ continue
    残りの処理をスキップして次の繰り返しへ

■ 使いどころ
- break: 探しているものが見つかったとき
- continue: 特定の条件をスキップするとき
""",
        "code": """# break の例
print("=== break ===")
for i in range(10):
    if i == 5:
        break
    print(i)
print("ループ終了")

# continue の例
print("=== continue ===")
for i in range(10):
    if i % 2 == 0:  # 偶数をスキップ
        continue
    print(i)
"""
    },
    {
        "title": "15. range()関数",
        "explanation": """【第15講】range()関数

数値の連続した範囲を生成します。

■ 構文
    range(stop)
    range(start, stop)
    range(start, stop, step)

■ 例
    range(5)        → 0,1,2,3,4
    range(1, 6)     → 1,2,3,4,5
    range(0, 10, 2) → 0,2,4,6,8
    range(10, 0, -1)→ 10,9,...,1（逆順）

■ list()で変換して中身を確認
""",
        "code": """# 基本的な使い方
print(list(range(5)))
print(list(range(1, 6)))
print(list(range(0, 10, 2)))

# 逆順
print(list(range(5, 0, -1)))

# for文と組み合わせ
print("1〜5:")
for i in range(1, 6):
    print(i, end=" ")
print()

# 九九（3の段）
for i in range(1, 10):
    print(f"3 × {i} = {3*i}")
"""
    },
    {
        "title": "16. ネストしたループ",
        "explanation": """【第16講】ネストしたループ

ループの中にループを書けます。

■ 構文
    for i in range(3):
        for j in range(3):
            処理

■ 使いどころ
- 九九
- 二次元データの処理
- 組み合わせの列挙

■ 注意
- インデントを正確に書くこと
""",
        "code": """# 九九（一部）
print("=== 掛け算表 ===")
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i}×{j}={i*j}", end="  ")
    print()  # 改行

print("---")

# 三角形を描く
for i in range(1, 6):
    print("*" * i)
"""
    },
    {
        "title": "17. pass文",
        "explanation": """【第17講】pass文

何もしないことを明示する文です。

■ 使いどころ
- 空のif/for/関数/クラスを書くとき
  （Pythonはブロックが空だとエラーになるため）
- 後で実装する予定のコードの場所を確保

■ 構文
    if 条件:
        pass   ← 何もしない
""",
        "code": """# 空のif文
x = 5
if x > 0:
    pass  # 後で処理を書く予定
else:
    print("負の数")

# 空の関数（後で実装予定）
def todo_function():
    pass

# passを使った偶数スキップ（continueと比較）
for i in range(5):
    if i % 2 == 0:
        pass
    else:
        print(i)
"""
    },
    {
        "title": "18. 三項演算子",
        "explanation": """【第18講】三項演算子（条件式）

1行でif/elseを書く方法です。

■ 構文
    値A if 条件 else 値B
    → 条件がTrueなら値A、FalseなB

■ 例
    result = "偶数" if n % 2 == 0 else "奇数"

■ ポイント
- 短い場合は読みやすいが、複雑な条件では
  通常のif文を使う方が良い
""",
        "code": """n = 7
result = "偶数" if n % 2 == 0 else "奇数"
print(result)

# 絶対値
x = -5
abs_x = x if x >= 0 else -x
print(abs_x)

# リストで使う
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for n in numbers:
    label = "偶数" if n % 2 == 0 else "奇数"
    print(f"{n}: {label}")
"""
    },
    {
        "title": "19. match文 (Python 3.10+)",
        "explanation": """【第19講】match文 — パターンマッチング

Python 3.10以降で使えるswitch文のような構文です。

■ 構文
    match 変数:
        case 値1:
            処理
        case 値2:
            処理
        case _:      ← デフォルト（else相当）
            処理

■ ポイント
- _ はワイルドカード（何にでもマッチ）
- 値のリストにもマッチ可能
""",
        "code": """# 曜日の判定
day = "月曜日"

match day:
    case "土曜日" | "日曜日":
        print("休日です")
    case "月曜日":
        print("週の始まりです")
    case "金曜日":
        print("週末が近い！")
    case _:
        print("平日です")

# 数値パターン
score = 85
match score // 10:
    case 10 | 9:
        print("優秀")
    case 8 | 7:
        print("良好")
    case 6:
        print("合格")
    case _:
        print("要努力")
"""
    },
    {
        "title": "20. for/while + else",
        "explanation": """【第20講】ループのelse節

Pythonのfor/whileにはelse節を付けられます。

■ 特徴
- ループが「正常に完了」したとき（breakしなかったとき）にelseが実行される
- breakで終了したときはelseは実行されない

■ 使いどころ
- 「見つからなかった」場合の処理
- 素数判定など
""",
        "code": """# 素数判定
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            print(f"{n} = {i} × {n//i} なので素数ではない")
            break
    else:
        print(f"{n} は素数！")
        return True
    return False

is_prime(7)
is_prime(9)
is_prime(13)

# リストで探す
numbers = [1, 3, 5, 7, 9]
target = 5
for n in numbers:
    if n == target:
        print(f"{target} が見つかった")
        break
else:
    print(f"{target} は見つからなかった")
"""
    },
    # --- 第3章: データ構造 ---
    {
        "title": "21. リスト (list)",
        "explanation": """【第21講】リスト — list

複数の値をまとめて保持するデータ構造です。

■ 作り方
    my_list = [1, 2, 3, 4, 5]
    mixed = [1, "hello", True, 3.14]

■ インデックスアクセス
    my_list[0]   → 1（先頭）
    my_list[-1]  → 5（末尾）

■ スライス
    my_list[1:3] → [2, 3]
    my_list[:3]  → [1, 2, 3]
    my_list[2:]  → [3, 4, 5]
""",
        "code": """fruits = ["りんご", "バナナ", "みかん", "ぶどう"]

# インデックス
print(fruits[0])   # りんご
print(fruits[-1])  # ぶどう

# スライス
print(fruits[1:3])  # ['バナナ', 'みかん']
print(fruits[:2])   # ['りんご', 'バナナ']

# 長さ
print(len(fruits))

# 更新
fruits[0] = "メロン"
print(fruits)

# 確認
print("バナナ" in fruits)  # True
"""
    },
    {
        "title": "22. リストのメソッド",
        "explanation": """【第22講】リストのメソッド

リストを操作するための便利なメソッドです。

■ 追加・削除
    append(x)     末尾に追加
    insert(i, x)  位置iに挿入
    remove(x)     値xを削除（最初の1つ）
    pop()         末尾を取り出して削除
    pop(i)        位置iを取り出して削除
    clear()       全削除

■ 検索・ソート
    index(x)      位置を返す
    count(x)      個数を返す
    sort()        昇順ソート（上書き）
    reverse()     逆順（上書き）
    sorted(list)  新しいソート済みリスト
""",
        "code": """nums = [3, 1, 4, 1, 5, 9, 2, 6]

nums.append(7)
print(nums)

nums.remove(1)  # 最初の1を削除
print(nums)

last = nums.pop()
print("取り出した:", last)
print(nums)

print("5の位置:", nums.index(5))
print("1の個数:", nums.count(1))

nums.sort()
print("ソート後:", nums)

nums.reverse()
print("逆順:", nums)
"""
    },
    {
        "title": "23. タプル (tuple)",
        "explanation": """【第23講】タプル — tuple

変更できないリストです。

■ 作り方
    t = (1, 2, 3)
    t = 1, 2, 3    ← カッコなしでも可

■ リストとの違い
- 変更不可（immutable）
- 辞書のキーになれる
- 複数の値を返すのに便利

■ アンパック（分解）
    x, y, z = (1, 2, 3)
""",
        "code": """point = (10, 20)
print(point)
print(point[0])
print(point[1])

# アンパック
x, y = point
print(f"x={x}, y={y}")

# 複数の値を返す関数に使う
def min_max(nums):
    return min(nums), max(nums)

lo, hi = min_max([3, 1, 4, 1, 5, 9])
print(f"最小={lo}, 最大={hi}")

# タプルはfor文でも使える
rgb = (255, 128, 0)
for val in rgb:
    print(val)
"""
    },
    {
        "title": "24. 辞書 (dict)",
        "explanation": """【第24講】辞書 — dict

キーと値のペアを保持するデータ構造です。

■ 作り方
    d = {"name": "太郎", "age": 20}

■ アクセス
    d["name"]      → "太郎"
    d.get("age")   → 20（キーがなくてもエラーにならない）

■ 追加・更新・削除
    d["email"] = "a@b.com"  # 追加/更新
    del d["age"]            # 削除
""",
        "code": """person = {
    "name": "山田太郎",
    "age": 25,
    "city": "東京"
}

print(person["name"])
print(person.get("age"))
print(person.get("email", "未設定"))  # デフォルト値

# 追加・更新
person["email"] = "yamada@example.com"
person["age"] = 26

print(person)

# キー・値の一覧
print(person.keys())
print(person.values())
print(person.items())
"""
    },
    {
        "title": "25. 辞書のメソッド",
        "explanation": """【第25講】辞書のメソッド

辞書を操作するメソッドです。

■ よく使うメソッド
    keys()    キーの一覧
    values()  値の一覧
    items()   (キー, 値)のペア一覧
    get(k, default)  値取得（キー無しでもOK）
    update(d)  別の辞書で更新
    pop(k)     キーkを削除して値を返す
    in         キーの存在確認

■ forループとの組み合わせ
    for k, v in d.items():
""",
        "code": """scores = {"数学": 85, "英語": 72, "理科": 90}

# forループで全項目を表示
for subject, score in scores.items():
    print(f"{subject}: {score}点")

# 合計・平均
total = sum(scores.values())
avg = total / len(scores)
print(f"合計: {total}, 平均: {avg:.1f}")

# 更新とpop
scores.update({"社会": 78})
removed = scores.pop("英語")
print(f"削除: 英語={removed}")
print(scores)

# キーの確認
print("数学" in scores)
"""
    },
    {
        "title": "26. 集合 (set)",
        "explanation": """【第26講】集合 — set

重複のない要素の集まりです。

■ 作り方
    s = {1, 2, 3}
    s = set([1, 2, 2, 3])  → {1, 2, 3}

■ 特徴
- 重複なし
- 順序なし
- 高速な検索

■ 演算
    A | B   和集合
    A & B   積集合（共通部分）
    A - B   差集合
    A ^ B   対称差（どちらかにだけ含まれる）
""",
        "code": """# 重複を除く
nums = [1, 2, 2, 3, 3, 3, 4]
unique = set(nums)
print(unique)

# 集合演算
A = {1, 2, 3, 4, 5}
B = {3, 4, 5, 6, 7}

print("和集合:", A | B)
print("積集合:", A & B)
print("差集合:", A - B)
print("対称差:", A ^ B)

# 検索（リストより高速）
fruits = {"りんご", "バナナ", "みかん"}
print("バナナ" in fruits)  # True
"""
    },
    {
        "title": "27. リスト内包表記",
        "explanation": """【第27講】リスト内包表記

リストを1行で生成する書き方です。

■ 基本構文
    [式 for 変数 in イテラブル]

■ 条件付き
    [式 for 変数 in イテラブル if 条件]

■ 例
    [x**2 for x in range(5)]  → [0,1,4,9,16]
    [x for x in range(10) if x % 2 == 0]
    → [0,2,4,6,8]
""",
        "code": """# 通常のfor文
squares_for = []
for x in range(1, 6):
    squares_for.append(x ** 2)

# 内包表記
squares = [x ** 2 for x in range(1, 6)]
print(squares)

# 条件付き内包表記
even = [x for x in range(10) if x % 2 == 0]
print(even)

# 文字列処理
words = ["hello", "world", "python"]
upper_words = [w.upper() for w in words]
print(upper_words)

# 2次元
matrix = [[1 if i == j else 0 for j in range(3)] for i in range(3)]
for row in matrix:
    print(row)
"""
    },
    {
        "title": "28. 辞書内包表記",
        "explanation": """【第28講】辞書内包表記

辞書を1行で生成する書き方です。

■ 基本構文
    {キー: 値 for 変数 in イテラブル}

■ 条件付き
    {k: v for k, v in d.items() if 条件}

■ 用途
- 辞書の変換
- 辞書のフィルタリング
""",
        "code": """# 数値の二乗辞書
sq_dict = {x: x**2 for x in range(1, 6)}
print(sq_dict)

# 文字列処理
words = ["apple", "banana", "cherry"]
word_len = {w: len(w) for w in words}
print(word_len)

# フィルタリング
scores = {"国語": 80, "数学": 55, "英語": 90, "理科": 45}
passing = {k: v for k, v in scores.items() if v >= 60}
print("合格科目:", passing)

# キーと値の入れ替え
original = {"a": 1, "b": 2, "c": 3}
reversed_dict = {v: k for k, v in original.items()}
print(reversed_dict)
"""
    },
    {
        "title": "29. スライス",
        "explanation": """【第29講】スライス

リストや文字列の一部を取り出します。

■ 構文
    seq[start:stop:step]

    start: 開始インデックス（省略時は先頭）
    stop:  終了インデックス（含まない、省略時は末尾）
    step:  ステップ（省略時は1）

■ よく使うパターン
    seq[:3]     先頭3要素
    seq[-3:]    末尾3要素
    seq[::2]    1つおき
    seq[::-1]   逆順
""",
        "code": """s = "Hello, Python!"
lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 文字列スライス
print(s[:5])     # Hello
print(s[7:])     # Python!
print(s[::2])    # HloPto!
print(s[::-1])   # 逆順

# リストスライス
print(lst[:3])      # [0, 1, 2]
print(lst[-3:])     # [7, 8, 9]
print(lst[2:8:2])   # [2, 4, 6]
print(lst[::-1])    # 逆順

# スライスでコピー
copy = lst[:]
copy[0] = 999
print(lst[0])   # 0 （元は変わらない）
"""
    },
    {
        "title": "30. ネストしたデータ構造",
        "explanation": """【第30講】ネストしたデータ構造

リストの中に辞書、辞書の中にリストなど
データ構造を入れ子にできます。

■ よく使う組み合わせ
- リストの中に辞書: ユーザー一覧など
- 辞書の中にリスト: カテゴリ別データなど

■ アクセス方法
    data[0]["name"]    リスト→辞書
    data["fruits"][0]  辞書→リスト
""",
        "code": """# リストの中に辞書
students = [
    {"name": "太郎", "score": 85},
    {"name": "花子", "score": 92},
    {"name": "次郎", "score": 78},
]

for s in students:
    print(f"{s['name']}: {s['score']}点")

# 平均点
avg = sum(s["score"] for s in students) / len(students)
print(f"平均: {avg:.1f}点")

# 辞書の中にリスト
schedule = {
    "月曜": ["数学", "英語", "体育"],
    "火曜": ["国語", "理科", "音楽"],
}
for day, subjects in schedule.items():
    print(f"{day}: {', '.join(subjects)}")
"""
    },
    # --- 第4章: 関数 ---
    {
        "title": "31. 関数の定義と呼び出し",
        "explanation": """【第31講】関数の定義と呼び出し

繰り返し使うコードを関数にまとめられます。

■ 構文
    def 関数名(引数1, 引数2):
        処理
        return 戻り値

■ ポイント
- def で定義
- return で値を返す（省略するとNoneを返す）
- 引数は0個以上
- 関数は定義後に呼び出す
""",
        "code": """def greet(name):
    return f"こんにちは、{name}さん！"

print(greet("太郎"))
print(greet("花子"))

# 複数の引数
def add(a, b):
    return a + b

result = add(3, 5)
print(result)

# 引数なし
def show_line():
    print("=" * 30)

show_line()
print("Hello")
show_line()
"""
    },
    {
        "title": "32. デフォルト引数・キーワード引数",
        "explanation": """【第32講】デフォルト引数・キーワード引数

■ デフォルト引数
引数を省略したときに使われるデフォルト値を設定できます。
    def func(name, greeting="こんにちは"):

■ キーワード引数
引数名を指定して呼び出します。
    func(greeting="おはよう", name="太郎")
    ← 順番を変えてもOK

■ 注意
デフォルト引数はデフォルトなし引数の後に書く
""",
        "code": """def greet(name, greeting="こんにちは", end="！"):
    print(f"{greeting}、{name}{end}")

greet("太郎")                         # デフォルト使用
greet("花子", "おはよう")             # 2番目を変更
greet("次郎", end="。")               # キーワード引数
greet(greeting="さようなら", name="四郎")  # 順序変更

# デフォルト値にリストは使わない（注意）
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

print(add_item("a"))
print(add_item("b"))
"""
    },
    {
        "title": "33. 複数の戻り値と*args/**kwargs",
        "explanation": """【第33講】複数の戻り値と可変長引数

■ 複数の戻り値
タプルで複数の値を返せます。
    return min_val, max_val

■ *args（可変長の位置引数）
    def func(*args):   ← タプルとして受け取る

■ **kwargs（可変長のキーワード引数）
    def func(**kwargs):  ← 辞書として受け取る
""",
        "code": """# 複数の戻り値
def stats(nums):
    return min(nums), max(nums), sum(nums)/len(nums)

lo, hi, avg = stats([3, 1, 4, 1, 5, 9])
print(f"最小={lo}, 最大={hi}, 平均={avg:.2f}")

# *args
def total(*args):
    return sum(args)

print(total(1, 2, 3))
print(total(1, 2, 3, 4, 5))

# **kwargs
def profile(**kwargs):
    for key, val in kwargs.items():
        print(f"{key}: {val}")

profile(name="太郎", age=25, city="東京")
"""
    },
    {
        "title": "34. スコープ (local / global)",
        "explanation": """【第34講】スコープ — 変数の有効範囲

■ ローカルスコープ
関数の中で定義した変数は関数の外から見えない

■ グローバルスコープ
関数の外で定義した変数はどこからでも参照できる

■ global文
関数の中でグローバル変数を変更するには
global宣言が必要

■ LEGB規則
Local → Enclosing → Global → Built-in の順で探す
""",
        "code": """x = "グローバル"

def outer():
    x = "エンクロージング"
    def inner():
        x = "ローカル"
        print(x)  # ローカル
    inner()
    print(x)  # エンクロージング

outer()
print(x)  # グローバル

# global文
count = 0
def increment():
    global count
    count += 1

increment()
increment()
print(count)  # 2
"""
    },
    {
        "title": "35. ラムダ式 (lambda)",
        "explanation": """【第35講】ラムダ式 — lambda

1行で書ける無名関数です。

■ 構文
    lambda 引数: 式

■ 使いどころ
- sorted()のキー指定
- map()やfilter()の関数指定
- 短い処理を使い捨てたいとき

■ 注意
複雑な処理は通常のdef関数を使うべき
""",
        "code": """# 基本
square = lambda x: x ** 2
print(square(5))

add = lambda a, b: a + b
print(add(3, 4))

# sorted()でのキー指定
words = ["banana", "apple", "cherry", "date"]
sorted_by_len = sorted(words, key=lambda w: len(w))
print(sorted_by_len)

# 複合条件でソート
people = [("太郎", 25), ("花子", 20), ("次郎", 25)]
# 年齢昇順、同じ年齢なら名前順
sorted_people = sorted(people, key=lambda p: (p[1], p[0]))
print(sorted_people)
"""
    },
    {
        "title": "36. map / filter / sorted",
        "explanation": """【第36講】map / filter / sorted

高階関数（関数を引数に取る関数）です。

■ map(関数, イテラブル)
各要素に関数を適用

■ filter(関数, イテラブル)
関数がTrueの要素だけ取り出す

■ sorted(イテラブル, key=関数, reverse=False)
新しいソート済みリストを返す

■ list()で結果をリストに変換
""",
        "code": """numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map: 全要素を2乗
squared = list(map(lambda x: x**2, numbers))
print("二乗:", squared)

# filter: 偶数だけ
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("偶数:", evens)

# sorted: 絶対値でソート
mixed = [-5, 3, -1, 4, -2]
by_abs = sorted(mixed, key=abs)
print("絶対値順:", by_abs)

# 降順
desc = sorted(numbers, reverse=True)
print("降順:", desc)
"""
    },
    {
        "title": "37. ジェネレータと yield",
        "explanation": """【第37講】ジェネレータと yield

値を一つずつ生成する関数です。

■ yield を使った関数 = ジェネレータ関数
- 呼び出すとジェネレータオブジェクトを返す
- next()またはforで値を1つずつ取り出す
- 全値をメモリに保持しないため省メモリ

■ ジェネレータ式
    (式 for 変数 in イテラブル)  ← ()に注意
""",
        "code": """# ジェネレータ関数
def count_up(n):
    i = 0
    while i < n:
        yield i
        i += 1

gen = count_up(5)
print(next(gen))  # 0
print(next(gen))  # 1

for val in count_up(5):
    print(val, end=" ")
print()

# フィボナッチ数列のジェネレータ
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
print([next(fib) for _ in range(10)])
"""
    },
    {
        "title": "38. デコレータ",
        "explanation": """【第38講】デコレータ

関数を別の関数でラップして機能を追加します。

■ 基本構文
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 前処理
            result = func(*args, **kwargs)
            # 後処理
            return result
        return wrapper

    @decorator
    def my_func():
        ...

■ 使いどころ
- ログ記録、実行時間計測、認証確認など
""",
        "code": """import time

# 実行時間を計測するデコレータ
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}: {end-start:.4f}秒")
        return result
    return wrapper

@timer
def slow_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total

result = slow_sum(100000)
print("合計:", result)

# ログデコレータ
def log(func):
    def wrapper(*args, **kwargs):
        print(f"呼び出し: {func.__name__}{args}")
        return func(*args, **kwargs)
    return wrapper

@log
def add(a, b):
    return a + b

print(add(3, 5))
"""
    },
    {
        "title": "39. 再帰関数",
        "explanation": """【第39講】再帰関数

自分自身を呼び出す関数です。

■ 構造
1. 基底ケース（終了条件）
2. 再帰ケース（自己呼び出し）

■ 例
- 階乗: n! = n × (n-1)!
- フィボナッチ数列

■ 注意
- 再帰の深さには上限がある（デフォルト約1000）
- 深い再帰はループの方が効率的なことも
""",
        "code": """# 階乗
def factorial(n):
    if n <= 1:     # 基底ケース
        return 1
    return n * factorial(n - 1)  # 再帰

print(factorial(5))   # 120
print(factorial(10))  # 3628800

# フィボナッチ（再帰版）
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print([fib(i) for i in range(10)])

# 階層構造を表示
def show_tree(items, indent=0):
    for item in items:
        if isinstance(item, list):
            show_tree(item, indent + 2)
        else:
            print(" " * indent + str(item))

show_tree([1, [2, 3, [4, 5]], 6])
"""
    },
    {
        "title": "40. 関数型プログラミング: functools",
        "explanation": """【第40講】functools モジュール

高階関数を便利に扱うモジュールです。

■ functools.reduce(func, iterable)
畳み込み演算（左から順に適用）

■ functools.partial(func, 引数)
引数を一部固定した新しい関数を作成

■ functools.lru_cache
計算結果をキャッシュして高速化
""",
        "code": """from functools import reduce, partial, lru_cache

# reduce: リストの積
nums = [1, 2, 3, 4, 5]
product = reduce(lambda a, b: a * b, nums)
print("積:", product)  # 120

# partial: 引数を一部固定
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube = partial(power, exp=3)
print(square(5))  # 25
print(cube(3))    # 27

# lru_cache: メモ化でフィボナッチを高速化
@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print(fib(30))   # 高速！
"""
    },
    # --- 第5章: クラス ---
    {
        "title": "41. クラスの基本",
        "explanation": """【第41講】クラスの基本

データと処理をまとめた設計図です。

■ 構文
    class クラス名:
        def __init__(self, 引数):   ← コンストラクタ
            self.属性 = 値

        def メソッド(self):
            処理

■ インスタンス化
    obj = クラス名(引数)
    obj.メソッド()
    obj.属性
""",
        "code": """class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    def bark(self):
        print(f"{self.name}:ワンワン！")

    def info(self):
        print(f"名前: {self.name}, 犬種: {self.breed}")

# インスタンス作成
pochi = Dog("ポチ", "柴犬")
hana = Dog("ハナ", "トイプードル")

pochi.bark()
hana.info()

print(pochi.name)
print(hana.breed)
"""
    },
    {
        "title": "42. 継承",
        "explanation": """【第42講】継承

既存クラスを基に新しいクラスを作ります。

■ 構文
    class 子クラス(親クラス):
        ...

■ super()
    親クラスのメソッドを呼び出す
    super().__init__(...)

■ オーバーライド
    親クラスのメソッドを子クラスで再定義

■ isinstance(obj, クラス)
    インスタンスの確認
""",
        "code": """class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name}が鳴く")

class Dog(Animal):
    def speak(self):                    # オーバーライド
        print(f"{self.name}: ワン！")

class Cat(Animal):
    def speak(self):
        print(f"{self.name}: ニャー！")

class GuideDog(Dog):
    def __init__(self, name, owner):
        super().__init__(name)          # 親の__init__
        self.owner = owner

    def guide(self):
        print(f"{self.name}が{self.owner}を誘導")

animals = [Dog("ポチ"), Cat("タマ"), GuideDog("リード", "太郎")]
for a in animals:
    a.speak()
    if isinstance(a, GuideDog):
        a.guide()
"""
    },
    {
        "title": "43. 特殊メソッド (dunder)",
        "explanation": """【第43講】特殊メソッド — ダンダーメソッド

__ で囲まれた特殊メソッドで、組み込み動作をカスタマイズできます。

■ よく使う特殊メソッド
    __init__    コンストラクタ
    __str__     str()、print()で表示
    __repr__    デバッグ用の表現
    __len__     len()
    __add__     + 演算子
    __eq__      == 演算子
    __lt__      < 演算子（比較・ソート）
""",
        "code": """class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __len__(self):
        return int((self.x**2 + self.y**2) ** 0.5)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1)
print(v1 + v2)
print(len(v1))    # √(9+16) = 5
print(v1 == Vector(3, 4))
"""
    },
    {
        "title": "44. classmethod / staticmethod",
        "explanation": """【第44講】classmethod と staticmethod

■ classmethod
- @classmethod デコレータ
- 第1引数が cls（クラス自体）
- クラス経由でも呼べる
- ファクトリメソッドなどに使う

■ staticmethod
- @staticmethod デコレータ
- self や cls を受け取らない
- クラスに関連するが、状態は必要ない処理
""",
        "code": """class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def __str__(self):
        return f"{self.year}/{self.month:02d}/{self.day:02d}"

    @classmethod
    def from_string(cls, date_str):
        y, m, d = map(int, date_str.split("-"))
        return cls(y, m, d)

    @staticmethod
    def is_valid(year, month, day):
        return 1 <= month <= 12 and 1 <= day <= 31

# 通常の作成
d1 = Date(2024, 3, 15)
print(d1)

# classmethod（ファクトリ）
d2 = Date.from_string("2024-06-01")
print(d2)

# staticmethod
print(Date.is_valid(2024, 13, 1))  # False
print(Date.is_valid(2024, 6, 15))  # True
"""
    },
    {
        "title": "45. property",
        "explanation": """【第45講】property — プロパティ

属性へのアクセスをメソッドでコントロールします。

■ @property
    ゲッター（値の取得）

■ @属性名.setter
    セッター（値の設定）

■ メリット
- 外部からは属性のように見える
- バリデーションや変換を入れられる
- _変数（プライベート変数）を隠蔽できる
""",
        "code": """class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("絶対零度以下にはできません")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32

t = Temperature(25)
print(f"摂氏: {t.celsius}℃")
print(f"華氏: {t.fahrenheit}°F")

t.celsius = 100
print(f"摂氏: {t.celsius}℃")
print(f"華氏: {t.fahrenheit}°F")
"""
    },
    # --- 第6章: 例外・モジュール・ファイル ---
    {
        "title": "46. 例外処理 (try/except)",
        "explanation": """【第46講】例外処理 — try/except

エラーが発生しても処理を継続できます。

■ 構文
    try:
        エラーが起きるかもしれない処理
    except エラー型 as e:
        エラー時の処理
    else:
        エラーがなかった場合の処理
    finally:
        必ず実行される処理

■ よく使う例外
    ValueError, TypeError, ZeroDivisionError,
    FileNotFoundError, IndexError, KeyError
""",
        "code": """# 基本
def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("ゼロ除算エラー！")
        return None
    else:
        print("成功！")
        return result
    finally:
        print("--- 終了 ---")

print(safe_divide(10, 2))
print(safe_divide(10, 0))

# 複数の例外
def convert(value):
    try:
        return int(value)
    except ValueError:
        print(f"'{value}' は数値ではありません")
    except TypeError:
        print("型が違います")

convert("123")
convert("abc")
convert(None)
"""
    },
    {
        "title": "47. カスタム例外",
        "explanation": """【第47講】カスタム例外

独自の例外クラスを作れます。

■ 基本構造
    class MyError(Exception):
        pass

■ メッセージ付き
    class MyError(Exception):
        def __init__(self, message):
            super().__init__(message)

■ raise で例外を発生させる
    raise MyError("エラーメッセージ")
""",
        "code": """# カスタム例外クラス
class AgeError(ValueError):
    def __init__(self, age):
        self.age = age
        super().__init__(f"無効な年齢: {age}")

class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("入金額は正の数にしてください")
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError(f"残高不足（残高: {self.balance}円）")
        self.balance -= amount
        return amount

acc = BankAccount(1000)
try:
    acc.deposit(500)
    print(f"残高: {acc.balance}")
    acc.withdraw(2000)
except ValueError as e:
    print(f"エラー: {e}")

# カスタム例外
try:
    raise AgeError(-5)
except AgeError as e:
    print(e)
"""
    },
    {
        "title": "48. モジュールとimport",
        "explanation": """【第48講】モジュールとimport

■ import方法
    import math            モジュール全体
    from math import sqrt  特定の関数
    from math import *     全て（非推奨）
    import numpy as np     エイリアス

■ よく使う標準ライブラリ
    math      数学関数
    random    乱数
    datetime  日時
    os        OS操作
    sys       システム情報
    json      JSONデータ
    re        正規表現
""",
        "code": """import math
import random
import datetime

# math
print(math.sqrt(16))     # 4.0
print(math.pi)           # 3.14159...
print(math.factorial(5)) # 120
print(math.ceil(3.2))    # 4
print(math.floor(3.8))   # 3

# random
print(random.randint(1, 10))  # 1〜10の乱数
items = ["a", "b", "c", "d"]
random.shuffle(items)
print(items)
print(random.choice(items))

# datetime
now = datetime.datetime.now()
print(now.strftime("%Y年%m月%d日 %H:%M:%S"))
today = datetime.date.today()
print(today)
"""
    },
    {
        "title": "49. ファイルの読み書き",
        "explanation": """【第49講】ファイルの読み書き

■ ファイルを開く
    with open(ファイル名, モード, encoding='utf-8') as f:
        処理

■ モード
    'r'   読み込み（デフォルト）
    'w'   書き込み（上書き）
    'a'   追記
    'rb'  バイナリ読み込み

■ よく使うメソッド
    f.read()        全体読み込み
    f.readlines()   行リストとして読み込み
    f.write(text)   書き込み
    f.writelines(lines)  複数行書き込み

■ with文を使うと自動でclose()される
""",
        "code": """import os
import tempfile

# 一時ファイルを使って動作確認
tmpfile = tempfile.mktemp(suffix=".txt")

# 書き込み
with open(tmpfile, 'w', encoding='utf-8') as f:
    f.write("1行目\\n")
    f.write("2行目\\n")
    f.writelines(["3行目\\n", "4行目\\n"])

# 読み込み
with open(tmpfile, 'r', encoding='utf-8') as f:
    content = f.read()
print("=== 全体 ===")
print(content)

# 行単位で読み込み
with open(tmpfile, 'r', encoding='utf-8') as f:
    lines = f.readlines()
print("=== 行数:", len(lines), "===")
for i, line in enumerate(lines, 1):
    print(f"{i}: {line.rstrip()}")

os.remove(tmpfile)
print("完了！")
"""
    },
    {
        "title": "50. 総合練習 — ミニ図書館システム",
        "explanation": """【第50講】総合練習 — ミニ図書館システム

これまで学んだ内容をすべて使った総合練習です。

■ 使う技術
- クラス（継承、property、特殊メソッド）
- 例外処理
- リスト・辞書
- 内包表記
- ファイル入出力（JSONもどき）
- 関数とデコレータ

自分でコードを変更して試してみてください！
""",
        "code": """from datetime import date, timedelta

class Book:
    def __init__(self, isbn, title, author):
        self.isbn = isbn
        self.title = title
        self.author = author
        self._available = True

    @property
    def available(self):
        return self._available

    def __str__(self):
        status = "貸出可" if self._available else "貸出中"
        return f"[{self.isbn}] {self.title} / {self.author} ({status})"

class Library:
    def __init__(self):
        self.books = {}
        self.loans = {}

    def add_book(self, book):
        self.books[book.isbn] = book
        print(f"登録: {book.title}")

    def lend(self, isbn, borrower):
        if isbn not in self.books:
            raise ValueError(f"ISBN {isbn} が見つかりません")
        book = self.books[isbn]
        if not book.available:
            raise ValueError(f"'{book.title}' は貸出中です")
        book._available = False
        due = date.today() + timedelta(days=14)
        self.loans[isbn] = {"borrower": borrower, "due": due}
        print(f"貸出: {book.title} → {borrower}（返却期限: {due}）")

    def return_book(self, isbn):
        if isbn not in self.loans:
            raise ValueError("貸出記録がありません")
        book = self.books[isbn]
        borrower = self.loans.pop(isbn)["borrower"]
        book._available = True
        print(f"返却: {book.title} （{borrower}より）")

    def search(self, keyword):
        results = [b for b in self.books.values()
                   if keyword in b.title or keyword in b.author]
        return results

# 実行
lib = Library()
lib.add_book(Book("001", "Python入門", "山田太郎"))
lib.add_book(Book("002", "データ分析の基礎", "鈴木花子"))
lib.add_book(Book("003", "Pythonでつくる機械学習", "田中次郎"))

print()
lib.lend("001", "佐藤")
lib.lend("002", "高橋")

print()
print("=== 蔵書一覧 ===")
for book in lib.books.values():
    print(book)

print()
lib.return_book("001")

print()
print("=== Python検索結果 ===")
for b in lib.search("Python"):
    print(b)

try:
    lib.lend("002", "鈴木")  # 貸出中なのでエラー
except ValueError as e:
    print(f"エラー: {e}")
"""
    },
]

# ===== メインアプリ =====
class PythonCourseApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pythonマスターコース — 1〜50講座")
        self.root.geometry("1200x750")
        self.root.configure(bg="#1e1e2e")

        self.current_lesson = 0
        self.completed = set()

        self._build_ui()
        self._load_lesson(0)

    def _build_ui(self):
        root = self.root

        # ===== 左サイドバー =====
        sidebar = tk.Frame(root, bg="#181825", width=240)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        title_lbl = tk.Label(
            sidebar, text="Pythonマスターコース",
            bg="#181825", fg="#cdd6f4",
            font=("Arial", 11, "bold"), wraplength=220
        )
        title_lbl.pack(pady=(12, 4), padx=8)

        prog_lbl = tk.Label(
            sidebar, text="進捗: 0/50",
            bg="#181825", fg="#a6adc8",
            font=("Arial", 9)
        )
        prog_lbl.pack()
        self.prog_lbl = prog_lbl

        tk.Frame(sidebar, bg="#313244", height=1).pack(fill=tk.X, pady=6)

        # リスト（スクロール付き）
        list_frame = tk.Frame(sidebar, bg="#181825")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4)

        scrollbar = tk.Scrollbar(list_frame, bg="#313244")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            bg="#181825", fg="#cdd6f4",
            selectbackground="#89b4fa", selectforeground="#1e1e2e",
            font=("Arial", 9), activestyle="none",
            relief=tk.FLAT, bd=0,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        for lesson in LESSONS:
            self.listbox.insert(tk.END, lesson["title"])

        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # ===== メインエリア =====
        main = tk.Frame(root, bg="#1e1e2e")
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 上部ツールバー
        toolbar = tk.Frame(main, bg="#181825", height=44)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        self.lesson_title = tk.Label(
            toolbar, text="",
            bg="#181825", fg="#89b4fa",
            font=("Arial", 13, "bold")
        )
        self.lesson_title.pack(side=tk.LEFT, padx=14, pady=10)

        btn_next = tk.Button(
            toolbar, text="次の講座 ▶",
            bg="#313244", fg="#cdd6f4",
            activebackground="#45475a", activeforeground="#cdd6f4",
            relief=tk.FLAT, font=("Arial", 9), bd=0,
            padx=10, pady=4,
            command=self._next_lesson
        )
        btn_next.pack(side=tk.RIGHT, padx=6, pady=8)

        btn_prev = tk.Button(
            toolbar, text="◀ 前の講座",
            bg="#313244", fg="#cdd6f4",
            activebackground="#45475a", activeforeground="#cdd6f4",
            relief=tk.FLAT, font=("Arial", 9), bd=0,
            padx=10, pady=4,
            command=self._prev_lesson
        )
        btn_prev.pack(side=tk.RIGHT, padx=0, pady=8)

        # コンテンツエリア（説明 + コード + 出力を縦に並べる）
        paned = tk.PanedWindow(main, orient=tk.VERTICAL, bg="#1e1e2e",
                               sashwidth=6, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        # 説明テキスト
        exp_frame = tk.Frame(paned, bg="#1e1e2e")
        paned.add(exp_frame, minsize=100)

        tk.Label(exp_frame, text="解説", bg="#1e1e2e", fg="#a6adc8",
                 font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=(6, 2))

        self.explanation = scrolledtext.ScrolledText(
            exp_frame,
            bg="#181825", fg="#cdd6f4",
            font=("Consolas", 10), relief=tk.FLAT,
            padx=10, pady=8, wrap=tk.WORD
        )
        self.explanation.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        # コードエリア
        code_frame = tk.Frame(paned, bg="#1e1e2e")
        paned.add(code_frame, minsize=100)

        code_header = tk.Frame(code_frame, bg="#1e1e2e")
        code_header.pack(fill=tk.X, padx=8, pady=(6, 2))

        tk.Label(code_header, text="コード（編集可）", bg="#1e1e2e", fg="#a6adc8",
                 font=("Arial", 9)).pack(side=tk.LEFT)

        run_btn = tk.Button(
            code_header, text="▶ 実行",
            bg="#a6e3a1", fg="#1e1e2e",
            activebackground="#94e2d5", activeforeground="#1e1e2e",
            relief=tk.FLAT, font=("Arial", 9, "bold"),
            padx=14, pady=3, bd=0,
            command=self._run_code
        )
        run_btn.pack(side=tk.RIGHT)

        reset_btn = tk.Button(
            code_header, text="↺ リセット",
            bg="#313244", fg="#cdd6f4",
            activebackground="#45475a", activeforeground="#cdd6f4",
            relief=tk.FLAT, font=("Arial", 9),
            padx=10, pady=3, bd=0,
            command=self._reset_code
        )
        reset_btn.pack(side=tk.RIGHT, padx=(0, 6))

        self.code_editor = scrolledtext.ScrolledText(
            code_frame,
            bg="#11111b", fg="#cdd6f4",
            font=("Consolas", 11), relief=tk.FLAT,
            insertbackground="#cdd6f4",
            padx=10, pady=8, wrap=tk.NONE
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        # 出力エリア
        out_frame = tk.Frame(paned, bg="#1e1e2e")
        paned.add(out_frame, minsize=80)

        tk.Label(out_frame, text="出力", bg="#1e1e2e", fg="#a6adc8",
                 font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=(6, 2))

        self.output = scrolledtext.ScrolledText(
            out_frame,
            bg="#11111b", fg="#a6e3a1",
            font=("Consolas", 10), relief=tk.FLAT,
            padx=10, pady=6, state=tk.DISABLED
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _load_lesson(self, index):
        if index < 0 or index >= len(LESSONS):
            return
        self.current_lesson = index
        lesson = LESSONS[index]

        self.lesson_title.config(text=lesson["title"])

        self.explanation.config(state=tk.NORMAL)
        self.explanation.delete("1.0", tk.END)
        self.explanation.insert(tk.END, lesson["explanation"])
        self.explanation.config(state=tk.DISABLED)

        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert(tk.END, lesson["code"])

        self._clear_output()

        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.see(index)

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if sel:
            self._load_lesson(sel[0])

    def _next_lesson(self):
        if self.current_lesson < len(LESSONS) - 1:
            self._load_lesson(self.current_lesson + 1)

    def _prev_lesson(self):
        if self.current_lesson > 0:
            self._load_lesson(self.current_lesson - 1)

    def _reset_code(self):
        lesson = LESSONS[self.current_lesson]
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert(tk.END, lesson["code"])
        self._clear_output()

    def _clear_output(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)

    def _show_output(self, text, is_error=False):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        color = "#f38ba8" if is_error else "#a6e3a1"
        self.output.config(fg=color)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)

    def _run_code(self):
        code = self.code_editor.get("1.0", tk.END)

        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py',
                encoding='utf-8', delete=False
            ) as f:
                f.write(code)
                tmppath = f.name

            result = subprocess.run(
                [sys.executable, tmppath],
                capture_output=True, text=True,
                timeout=10, encoding='utf-8'
            )

            os.unlink(tmppath)

            if result.returncode == 0:
                output = result.stdout or "（出力なし）"
                self._show_output(output, is_error=False)
                # 完了マーク
                self.completed.add(self.current_lesson)
                self._update_progress()
            else:
                self._show_output(result.stderr, is_error=True)

        except subprocess.TimeoutExpired:
            self._show_output("タイムアウト（10秒）: 無限ループの可能性があります", is_error=True)
        except Exception as e:
            self._show_output(f"実行エラー: {e}", is_error=True)

    def _update_progress(self):
        done = len(self.completed)
        total = len(LESSONS)
        self.prog_lbl.config(text=f"進捗: {done}/{total}")

        # リストのラベルを更新
        idx = self.current_lesson
        title = LESSONS[idx]["title"]
        if idx in self.completed:
            if not title.startswith("✓ "):
                self.listbox.delete(idx)
                self.listbox.insert(idx, "✓ " + title)
                self.listbox.itemconfig(idx, fg="#a6e3a1")
                self.listbox.selection_set(idx)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PythonCourseApp()
    app.run()
