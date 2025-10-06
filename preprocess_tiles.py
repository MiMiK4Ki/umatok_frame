# preprocess_tiles.py
# 画像を 4 分割（1:左上, 2:右上, 3:左下, 4:右下）し、指定サイズにリサイズして保存します。
# o.png -> 58x58、logo.png -> 112x112
# どんな元サイズでも動くように、安全な丸め処理＆高品質リサイズ（LANCZOS）を採用。

from pathlib import Path
from PIL import Image, ImageOps

# === 設定 ===
ASSETS_DIR = Path("assets")  # 入出力フォルダ
INPUTS = [
    # (ファイル名, 出力プレフィックス, 出力サイズ)
    ("o.png",    "o",    58),
    ("logo.png", "logo", 112),
]
# 四分割の命名規則: 1=左上, 2=右上, 3=左下, 4=右下
# 出力ファイル名: <prefix>_<idx>_<size>.png 例) o_1_58.png, logo_4_112.png

def split_quads(im: Image.Image):
    """画像を 4 分割して (idx, Image) を返す。idxは 1..4。"""
    w, h = im.size
    # 奇数でも安全に分割できるように、整数で中央を決める
    cx = w // 2
    cy = h // 2
    boxes = {
        1: (0,   0,  cx,  cy),  # 左上
        2: (cx,  0,  w,   cy),  # 右上
        3: (0,   cy, cx,  h),   # 左下
        4: (cx,  cy, w,   h),   # 右下
    }
    quads = []
    for idx in (1,2,3,4):
        quad = im.crop(boxes[idx])
        quads.append((idx, quad))
    return quads

def to_square_and_resize(im: Image.Image, size: int) -> Image.Image:
    """
    念のため安全に正方形化→指定サイズへ。
    分割後が正方形でない場合でも中央トリミングして正方形にし、その後リサイズ。
    """
    # まず中央で正方形にトリミング
    w, h = im.size
    if w != h:
        side = min(w, h)
        left   = (w - side) // 2
        top    = (h - side) // 2
        right  = left + side
        bottom = top  + side
        im = im.crop((left, top, right, bottom))
    # 高品質リサイズ
    im = im.resize((size, size), Image.Resampling.LANCZOS)
    return im

def process_one(input_name: str, prefix: str, size: int):
    src_path = ASSETS_DIR / input_name
    if not src_path.exists():
        print(f"[WARN] {src_path} が見つかりません。スキップします。")
        return
    im = Image.open(src_path).convert("RGBA")
    for idx, quad in split_quads(im):
        out = to_square_and_resize(quad, size)
        out_path = ASSETS_DIR / f"{prefix}_{idx}_{size}.png"
        out.save(out_path, format="PNG")
        print(f"[OK] -> {out_path}")

def main():
    print(f"[INFO] 入出力ディレクトリ: {ASSETS_DIR.resolve()}")
    for fname, prefix, size in INPUTS:
        process_one(fname, prefix, size)
    print("[DONE] すべての出力が完了しました。")

if __name__ == "__main__":
    main()
