# -*- coding: utf-8 -*-
"""Remove all emoji from Python files in ocean-core"""
import os
import re

ocean_core = r"c:\Users\Admin\Desktop\Kloud-cloud\ocean-core"

emoji_map = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARN]',
    '⏳': '[WAIT]',
    '🧠': '[BRAIN]',
    '🔄': '[SYNC]',
    '📊': '[DATA]',
    '🎯': '[TARGET]',
    '💡': '[INFO]',
    '🚀': '[START]',
    '⚡': '[FAST]',
    '🔍': '[SEARCH]',
    '📝': '[NOTE]',
    '🌊': '[OCEAN]',
    '→': '->',
    '←': '<-',
    '↔': '<->',
    '•': '*',
    '—': '-',
    '–': '-',
    '"': '"',
    '"': '"',
    ''': "'",
    ''': "'",
    '…': '...',
    '🤖': '[BOT]',
    '📡': '[API]',
    '🔧': '[FIX]',
    '⚙️': '[CONFIG]',
    '📦': '[PKG]',
    '🎨': '[UI]',
    '💾': '[SAVE]',
    '🔒': '[LOCK]',
    '🔓': '[UNLOCK]',
    '✨': '[NEW]',
    '🐛': '[BUG]',
    '🔥': '[HOT]',
    '💥': '[BOOM]',
    '🌐': '[WEB]',
    '📈': '[UP]',
    '📉': '[DOWN]',
    '⭐': '[STAR]',
    '🏠': '[HOME]',
    '📁': '[DIR]',
    '📂': '[FOLDER]',
    '🗂️': '[FILES]',
    '🔗': '[LINK]',
    '⬆️': '[UP]',
    '⬇️': '[DOWN]',
    '➡️': '->',
    '⬅️': '<-',
    '🔴': '[RED]',
    '🟢': '[GREEN]',
    '🟡': '[YELLOW]',
    '🔵': '[BLUE]',
    '⚪': '[WHITE]',
    '⚫': '[BLACK]',
    '💪': '[STRONG]',
    '👍': '[GOOD]',
    '👎': '[BAD]',
    '🎉': '[DONE]',
    '🚨': '[ALERT]',
    '⛔': '[STOP]',
    '🛑': '[STOP]',
    '✖': '[X]',
    '✓': '[OK]',
    '●': '*',
    '○': 'o',
    '■': '#',
    '□': '[]',
    '▶': '>',
    '◀': '<',
    '▲': '^',
    '▼': 'v',
    '★': '*',
    '☆': '*',
}

count = 0
for filename in os.listdir(ocean_core):
    if filename.endswith('.py'):
        filepath = os.path.join(ocean_core, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Replace known emoji
            for emoji, replacement in emoji_map.items():
                content = content.replace(emoji, replacement)
            
            # Remove any remaining non-ASCII characters
            content = re.sub(r'[^\x00-\x7F]', '', content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[OK] {filename}")
                count += 1
            else:
                print(f"[--] {filename} (no changes)")
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")

print(f"\n{count} files cleaned from emoji")

