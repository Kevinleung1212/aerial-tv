#!/usr/bin/env python3
"""Generate complete Traditional Chinese TV strings and localised phone UI for Aerial v1.47.

Requires: pip install opencc-python-reimplemented==0.1.7
All source string IDs and interpolation placeholders are preserved. Generated outputs
are committed back to the fork by the GitHub Actions customization workflow.
"""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "app/src/main/res"
HTML = ROOT / "app/src/main/assets/web/index.html"
SOURCE = RES / "values-zh/strings.xml"
english = RES / "values/strings.xml"

# Longer phrases first: OpenCC's s2hk/s2tw produce proper Traditional ideographs,
# then these local usages make Taiwan and Hong Kong terminology more natural.
HK_USAGE = {
    "屏保": "螢幕保護程式",
    "螢幕保護程序": "螢幕保護程式",
    "屏幕保護程序": "螢幕保護程式",
    "視頻": "影片",
    "视频": "影片",
    "文件夾": "資料夾",
    "文件夹": "資料夾",
    "應用中心": "應用程式中心",
    "應用程式程式": "應用程式",
    "默認": "預設",
    "設置": "設定",
    "设置": "設定",
    "滑鼠": "滑鼠",
    "後台": "背景",
}
TW_USAGE = {
    "屏保": "螢幕保護程式",
    "螢幕保護程序": "螢幕保護程式",
    "視頻": "影片",
    "文件夾": "資料夾",
    "設置": "設定",
    "默認": "預設",
}
def convert(text: str, converter: OpenCC, usage: dict) -> str:
    out = converter.convert(text)
    for old, new in usage.items():
        out = out.replace(old, new)
    return out

def string_ids(path: Path) -> set:
    return {el.get("name") for el in ET.parse(path).getroot()
            if el.tag in ("string", "plurals", "string-array") and el.get("name")}

def create_resources():
    source = SOURCE.read_text(encoding="utf-8")
    needed = string_ids(SOURCE)
    assert "<resources>" in source and "</resources>" in source
    outputs = [
        ("values-zh-rHK", "s2hk", HK_USAGE),
        ("values-zh-rMO", "s2hk", HK_USAGE),
        ("values-b+yue+Hant+HK", "s2hk", HK_USAGE),
        ("values-b+yue+Hant", "s2hk", HK_USAGE),
        ("values-zh-rTW", "s2twp", TW_USAGE),
        ("values-b+zh+Hant", "s2t", {}),
    ]
    for folder, mode, usage in outputs:
        target = RES / folder / "strings.xml"
        target.parent.mkdir(exist_ok=True)
        result = convert(source, OpenCC(mode), usage)
        if folder in ("values-zh-rHK", "values-zh-rMO", "values-b+yue+Hant+HK", "values-b+yue+Hant"):
            cantonese = {
                "cc_title": "控制中心",
                "cc_inputs": "訊號來源",
                "cc_settings": "設定",
                "cc_personalize": "個人化",
                "cc_no_inputs": "呢部電視搵唔到可用嘅訊號來源",
                "cc_setup_body": "只安裝咗 APK，Aerial 可以打開，但撳主頁鍵、開機或待機後都可能返去原本個桌面。",
                "menu_to_folder": "移至資料夾",
                "menu_new_folder": "新增資料夾",
                "menu_out_of_folder": "移出資料夾",
                "menu_rename_folder": "重新命名",
                "folder_default": "資料夾",
                "hidden_title": "已隱藏嘅應用程式",
                "hidden_empty": "冇隱藏嘅應用程式",
                "hidden_hint": "揀一個應用程式放返主畫面",
                "st_home_one_row": "單排",
                "st_home_standard": "雙排",
                "st_sounds": "按鍵聲",
                "input_connected": "已連接",
                "wp_wallpaper": "壁紙",
                "wp_screensaver": "螢幕保護程式",
                "tile_stock_home": "原本桌面",
            }
            for key, text in cantonese.items():
                pattern = re.compile(r'(<string name="' + re.escape(key) + r'">)(.*?)(</string>)', re.DOTALL)
                result, count = pattern.subn(lambda m: m.group(1) + text + m.group(3), result)
                if count != 1:
                    raise RuntimeError(f"Missing HK UI string: {key}")
        result = result.replace("<resources>", '<resources>\n    <string name="app_name">Aerial</string>', 1)
        target.write_text(result, encoding="utf-8")
        got = string_ids(target)
        if not needed.issubset(got):
            raise RuntimeError(f"Missing resources in {folder}: {needed - got}")
        if "<string name=\"cc_title\">" not in result:
            raise RuntimeError(f"No Control Center title in {folder}")
        print(f"{folder}: {len(got)} localized resource keys")

def phone():
    html = HTML.read_text(encoding="utf-8")
    token = '"zh": ['
    if html.count(token) != 1:
        raise RuntimeError("Unexpected phone language table in v1.47")
    start = html.index(token) + len('"zh": ')
    decoder = json.JSONDecoder()
    zh, count = decoder.raw_decode(html[start:])
    if not isinstance(zh, list):
        raise RuntimeError("Phone zh table is not an array")
    key_start = html.index("const KEYS = ") + len("const KEYS = ")
    keys, _ = decoder.raw_decode(html[key_start:])
    if len(keys) != len(zh):
        raise RuntimeError(f"Phone text keys {len(keys)} != Chinese translations {len(zh)}")

    translations = {
        "zh-HK": [convert(v, OpenCC("s2hk"), HK_USAGE) for v in zh],
        "zh-MO": [convert(v, OpenCC("s2hk"), HK_USAGE) for v in zh],
        "zh-TW": [convert(v, OpenCC("s2twp"), TW_USAGE) for v in zh],
        "zh-Hant": [convert(v, OpenCC("s2t"), {}) for v in zh],
    }
    # Selective Hong Kong Cantonese vocabulary, retaining clear, formal UI grammar.
    index = {k: i for i, k in enumerate(keys)}
    overrides = {
        "tab_home": "主畫面",
        "tab_more": "更多",
        "tab_looks": "桌布與螢幕保護程式",
        "cc_title": "控制中心",
        "hidden_h": "已隱藏的應用程式",
        "hidden_none": "沒有隱藏的應用程式。",
        "to_folder": "移至資料夾",
        "new_folder": "新增資料夾",
        "out_of_folder": "移出資料夾",
        "folder_ph": "資料夾名稱",
        "arrange_hint": "與電視上的排列相同，每排 5 個，第一排就是電視玻璃底板上的一排。長按圖示拖曳可調整順序；點選可重新命名、更換圖示、放入資料夾或隱藏。",
        "inputs_h": "訊號來源",
        "source_device": "已連接裝置",
        "show_on_home": "顯示於主畫面",
        "language": "語言",
    }
    for locale in ("zh-HK", "zh-MO"):
        for key, value in overrides.items():
            if key in index:
                translations[locale][index[key]] = value

    if '"zh-HK": [' not in html:
        end = start + count
        if html[end] != ",":
            raise RuntimeError("Unexpected comma after phone zh table")
        fragment = "\n" + "".join(
            ' "' + key + '": ' + json.dumps(value, ensure_ascii=False, indent=1) + ",\n"
            for key, value in translations.items()
        )
        html = html[:end+1] + fragment + html[end+1:]
    else:
        # A subsequent CI run on the generated branch must be idempotent.
        print("Phone Traditional Chinese tables already generated")
        return

    old = """  for (const l of prefs) { if (!l) continue; const c = String(l).toLowerCase().split('-')[0]; if (LANGS.includes(c)) return c; }"""
    new = """  for (const l of prefs) {
    if (!l) continue;
    const locale = String(l).replace(/_/g, '-').toLowerCase();
    // Android/Chrome zh-HK and zh-MO should not collapse into Simplified Chinese.
    if (locale === 'yue' || locale.startsWith('yue-')) return 'zh-HK';
    const chinese = locale === 'zh' || locale.startsWith('zh-');
    if (chinese) {
      const parts = locale.split('-');
      const preferred = parts.includes('hk') ? 'zh-HK'
        : parts.includes('mo') ? 'zh-MO'
        : parts.includes('tw') ? 'zh-TW'
        : parts.includes('hant') ? 'zh-Hant'
        : 'zh';
      if (LANGS.includes(preferred)) return preferred;
    }
    const baseLanguage = locale.split('-')[0];
    if (LANGS.includes(baseLanguage)) return baseLanguage;
  }"""
    if html.count(old) != 1:
        raise RuntimeError("Phone locale auto-detection code has changed")
    html = html.replace(old, new, 1)
    old_names = "const NAMES = { zh: '中文', en: 'English', ru: 'Русский', uk: 'Українська', kk: 'Қазақша' };"
    new_names = "const NAMES = { zh: '简体中文', 'zh-HK': '繁體中文（香港／粵語）', 'zh-MO': '繁體中文（澳門）', 'zh-TW': '繁體中文（臺灣）', 'zh-Hant': '繁體中文', en: 'English', ru: 'Русский', uk: 'Українська', kk: 'Қазақша' };"
    if html.count(old_names) != 1:
        raise RuntimeError("Phone language labels changed")
    html = html.replace(old_names, new_names, 1)
    HTML.write_text(html, encoding="utf-8")
    print(f"Phone UI: {len(keys)} translated strings x 4 Traditional locales")

if __name__ == "__main__":
    create_resources()
    phone()
