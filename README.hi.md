# release-information

🌐 [English](./README.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md) | **हिन्दी**

[![CI](https://github.com/kou135/release-information/actions/workflows/ci.yml/badge.svg)](https://github.com/kou135/release-information/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

रिलीज़ नोट्स और डिज़ाइन विनिर्देशों के लिए, git pre-commit द्वारा संचालित Markdown से एकल HTML
फ़ाइल बनाने वाला रेंडरर। `docs/release-information/` के अंदर एक Markdown फ़ाइल रखें और commit
करें — Anthropic शैली की **Midnight Museum** डार्क थीम, इनलाइन CSS, स्वचालित विषय-सूची, और
शून्य बाहरी निर्भरताओं वाला एक स्वयं-निहित HTML दस्तावेज़ पुनः जनरेट होकर उसी commit में
स्टेज हो जाता है।

## यह OSS क्यों (और सीधे `python-markdown` / MkDocs / Quarto / Pandoc क्यों नहीं)?

साधारण `python-markdown` से आपको HTML तो मिल जाता है, लेकिन वह *उस तरह का* HTML नहीं होता
जिसे आप किसी टीम के साथी या Claude को सौंपना चाहेंगे। MkDocs, Quarto और Pandoc बेहतरीन उपकरण
हैं, लेकिन वे क्रमशः एक पूरी साइट / थीम लगाई हुई बहु-पृष्ठ कलाकृति / Lua-विस्तार योग्य टूलचेन
प्रदान करते हैं। `release-information` जानबूझकर संकीर्ण है:

- **विनिर्देश-स्तर की डार्क थीम एक पैकेज में, रिपॉज़िटरीज़ के बीच कॉपी की जाने वाली स्निपेट के
  रूप में नहीं।** Anthropic शैली का *Midnight Museum* CSS (गहरा `#0F172A` पृष्ठभूमि, serif मुख्य
  पाठ, sans शीर्षक, Pygments monokai कोड, स्वचालित `[TOC]`) कन्वर्टर के *साथ* शिप होता है,
  जिससे हर रिपॉज़िटरी में जहाँ इसे इंस्टॉल किया गया है, दृश्य पहचान एक समान बनी रहती है।
  अब `style.css` के क्लोन इधर-उधर बिखरकर बदलते नहीं रहेंगे।
- **`docs/release-information/` संकल्पना को pre-commit hook द्वारा प्रवर्तित किया जाता है।**
  `release-information install` कमांड एक शेल hook लिखता है जो *केवल उस एक* glob से मेल खाने वाले
  स्टेज किए गए Markdown को पुनः रेंडर करता है — और कुछ नहीं — और जनरेट हुई HTML को उसी commit
  में `git add` कर देता है। कोई साइट डायरेक्टरी नहीं, कोई `mkdocs build` नहीं, कोई CI चरण
  नहीं: कलाकृति अपने स्रोत के बगल में उसी commit में रहती है।
- **एकल HTML आउटपुट, इनलाइन CSS, शून्य CDN — Claude की context window में पेस्ट करने योग्य।**
  प्रत्येक `.html` एक फ़ाइल है। कोई `_site/` नहीं, कोई asset डायरेक्टरी नहीं, बाहरी फ़ॉन्ट्स के
  लिए कोई `<link rel>` नहीं। पूरा दस्तावेज़ सघन और स्वयं-निहित है, और शैली खोए बिना AI एजेंट
  या Slack में कॉपी-पेस्ट किया जा सकता है। मौजूदा उपकरण इसी अंतर को छोड़ देते हैं: वे
  *प्रकाशन* के लिए अनुकूलित हैं, जबकि यह OSS *सघन संदर्भ को पाठक (मनुष्य या मॉडल) तक पहुँचाने*
  के लिए अनुकूलित है।

यदि आपको केवल "Markdown को HTML में" बदलना है, तो सीधे `python-markdown` का उपयोग करें।
यदि आपको एक दस्तावेज़ीकरण साइट चाहिए, तो MkDocs या Quarto का उपयोग करें। `release-information`
तब चुनें जब आप **हर** प्रोजेक्ट में **एक ही** डार्क, सघन, एकल-फ़ाइल रिलीज़-नोट HTML चाहते हों, जो
हर commit पर बिना सोचे जनरेट हो।

## इंस्टॉल

वर्तमान में GitHub से सीधे इंस्टॉल किया जाता है। `pipx` की सिफारिश की जाती है ताकि CLI किसी
प्रोजेक्ट के venv को प्रदूषित किए बिना वैश्विक रूप से उपलब्ध रहे।

```bash
pipx install git+https://github.com/kou135/release-information.git
# या: pip install git+https://github.com/kou135/release-information.git
```

`release-information` के लिए Python 3.10+ आवश्यक है। macOS और Linux समर्थित हैं; Windows
रोडमैप पर है (बंडल किया हुआ pre-commit hook एक POSIX शेल स्क्रिप्ट है)।

> **PyPI**: एक publish workflow कॉन्फ़िगर है (`.github/workflows/publish.yml`) लेकिन अभी तक
> ट्रिगर नहीं हुआ है। यदि आप fork करके अपनी कॉपी प्रकाशित करना चाहते हैं तो
> [`docs/PUBLISHING.hi.md`](./docs/PUBLISHING.hi.md) देखें।

## त्वरित प्रारंभ

शून्य से एक रेंडर की हुई HTML रिलीज़ नोट तक का पाँच-मिनट का रास्ता:

```bash
# 1. CLI को वैश्विक रूप से इंस्टॉल करें
pipx install git+https://github.com/kou135/release-information.git

# 2. उस रिपॉज़िटरी में जाएँ जहाँ आप HTML रिलीज़ नोट्स चाहते हैं
cd ~/workspace/your-project

# 3. pre-commit hook को <repo>/.git/hooks/pre-commit में इंस्टॉल करें
#    (यदि docs/release-information/ नहीं है तो वह भी बन जाती है — नीचे "install" अनुभाग देखें)
release-information install
#   - पहले से pre-commit hook मौजूद है? पहले बैकअप लें: release-information install --force
#   - .git गायब है? आपको एक स्पष्ट त्रुटि मिलती है, और कुछ नहीं लिखा जाता।

# 4. एक रिलीज़ नोट जोड़ें (ऊपर का install डायरेक्टरी बना चुका है, mkdir की आवश्यकता नहीं)
cat > docs/release-information/v1.0.0.md <<'EOF'
# v1.0.0

## Highlights
- First public release.

## Breaking changes
- None.
EOF

# 5. commit करें। hook docs/release-information/v1.0.0.html को रेंडर करता है और
#    उसे उसी commit के हिस्से के रूप में स्वचालित रूप से स्टेज कर देता है।
git add docs/release-information/v1.0.0.md
git commit -m "docs: add v1.0.0 release notes"

# 6. सत्यापित करें
ls docs/release-information/
# v1.0.0.md  v1.0.0.html   <- एक साथ जनरेट हुए और commit हुए
```

## उपयोग

```text
release-information [--version]
release-information --help
release-information render <FILE.md>
release-information render-all [--root .]
release-information install [--repo-root PATH] [--force]
release-information uninstall [--repo-root PATH]
release-information delete --file <NAME> [--repo-root PATH]
release-information version
```

### `render` — एकल फ़ाइल

```bash
release-information render docs/release-information/v1.0.0.md
# docs/release-information/v1.0.0.html लिखता है (वही stem, वही डायरेक्टरी)
# आउटपुट का absolute path stdout पर प्रिंट करता है
```

### `render-all` — थोक पुनः-रेंडरिंग

```bash
release-information render-all                # CWD को --root के रूप में उपयोग करता है
release-information render-all --root ./repo  # --root स्पष्ट रूप से

# docs/release-information/**/*.md (पुनरावर्ती) को glob करता है और प्रत्येक को पुनः रेंडर करता है।
# कोई मेल नहीं मिलना त्रुटि *नहीं* है: exit code 0।
```

### `install` / `uninstall` — pre-commit hook का प्रबंधन

```bash
release-information install                   # <repo>/.git/hooks/pre-commit लिखता है
release-information install --force           # मौजूदा hook को अधिलेखित करता है (बैकअप के साथ)
release-information uninstall                 # बैकअप पुनर्स्थापित करता है, या हमारा hook हटाता है
```

साइड-इफ़ेक्ट: `install` `<repo>/docs/release-information/` को भी बनाता है
(`mkdir -p`, idempotent)। पहले Quick start में दिए गए
`mkdir -p docs/release-information` चरण की अब आवश्यकता नहीं है।

hook केवल `docs/release-information/**/*.md` से मेल खाने वाली स्टेज की हुई फ़ाइलों पर ही कार्य
करता है। किसी अन्य Markdown फ़ाइल (कोई `README.md`, कोई `docs/blog/*.md`, आदि) में किए गए
संपादन पूरी तरह से अनदेखे कर दिए जाते हैं; hook exit 0 के साथ शॉर्ट-सर्किट हो जाता है।

### `delete` — एक विनिर्देश और उसके HTML को हटाएँ

```bash
release-information delete --file v1.0.0
# docs/release-information/v1.0.0.md और docs/release-information/v1.0.0.html हटाता है
# `--file` तर्क `v1.0.0` और `v1.0.0.md` दोनों को स्वीकार करता है (एक्सटेंशन हटा दिया जाता है)
```

`.md` और `.html` दोनों एक ही कॉल में हटा दिए जाते हैं। यदि जोड़े में से केवल एक ही
मौजूद हो, तो केवल वह फ़ाइल हटाई जाती है। पथ ट्रैवर्सल (`..`, `/`, पूर्ण पथ) और
`docs/release-information/` के अंतर्गत सिमलिंक exit code 2 के साथ अस्वीकार किए
जाते हैं। यदि कोई भी फ़ाइल मौजूद नहीं है, तो कमांड exit code 2 के साथ समाप्त होती
है और stderr पर `no such file` संदेश प्रिंट करती है।

## डिज़ाइन दर्शन

### विनिर्देशों के लिए HTML क्यों?

Anthropic टीम और 2026 के कई लेखक (Lenny's Newsletter, Simon Willison, ChatPRD पर Thariq
Shihipar) स्वतंत्र रूप से एक ही निष्कर्ष पर पहुँचे: AI एजेंट्स को संदर्भ सौंपने के लिए HTML
Markdown की तुलना में अधिक जानकारी-घनत्व वाला फ़ॉर्मेट है। आप एक ही फ़ाइल में टाइपोग्राफी,
रंग, विषय-सूची, सिंटैक्स-हाइलाइट किया हुआ कोड और इनलाइन डेटा एक साथ रख सकते हैं, जिसे एक मॉडल
बिना किसी पूर्व-प्रसंस्करण के पार्स कर लेता है। `release-information` इसी अवलोकन पर आधारित है।

### "Midnight Museum" क्यों?

डिफ़ॉल्ट थीम अपनी रंग-संगति और टाइपोग्राफी को लेखक के `minima` वर्कस्पेस विनिर्देश रेंडरर से
विरासत में लेती है: गहरा `#0F172A` पृष्ठभूमि, serif मुख्य पाठ (macOS पर Hiragino Mincho, Noto
Serif JP fallback), sans-serif शीर्षक, कोड के लिए Pygments *monokai*। सौंदर्यबोध एक दस्तावेज़ीकरण
साइट से अधिक एक गैलरी की दीवार पर लगे कार्ड के निकट है — जहाँ ज़रूरी नहीं वहाँ कम कंट्रास्ट
और शांत, जहाँ ज़रूरी है वहाँ उच्च कंट्रास्ट। थीम `core/theme.py` में एक इनलाइन `<style>`
ब्लॉक के रूप में शिप होती है; render या view के समय किसी बाहरी फ़ॉन्ट CDN को हिट नहीं किया जाता।

### एक साइट के बजाय एकल HTML आउटपुट क्यों?

एक रिलीज़ नोट एक बार पढ़ा जाता है, हमेशा के लिए संग्रहित होता है, और कभी-कभी AI के context
window में पेस्ट किया जाता है। इनमें से कोई भी वर्कफ़्लो `_site/` डायरेक्टरी नहीं चाहता।
प्रति `.md` एक फ़ाइल आउटपुट को आसानी से `cat` करने योग्य, ईमेल करने योग्य, संलग्न करने योग्य,
और एक ही GitHub diff में समीक्षा करने योग्य बनाए रखती है।

### सन्दर्भ

- Lenny Rachitsky — *HTML is the new Markdown* (Lenny's Newsletter, 2026)
- Simon Willison — *The Unreasonable Effectiveness of HTML* (2026-05-08)
- Thariq Shihipar — ChatPRD पर साक्षात्कार (*How I AI*, "Claude Code at Anthropic")

## योगदान

```bash
git clone https://github.com/kou135/release-information.git
cd release-information
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

Issues और PRs का स्वागत है। यह प्रोजेक्ट **रेंडर की हुई HTML आउटपुट की स्थिरता** के लिए
अनुकूलित है (इनलाइन CSS एक सार्वजनिक अनुबंध है; इसे बदलने से सभी डाउनस्ट्रीम रिपॉज़िटरीज़ को
पुनः रेंडर करना पड़ता है); व्यवहार में बदलाव के लिए `CHANGELOG.md` के *Changed* या *Breaking*
खंड में एक प्रविष्टि आवश्यक है।

## रिलीज़ करना

मेंटेनर्स के लिए: PyPI रिलीज़ वर्कफ़्लो (tag-driven, OIDC के माध्यम से Trusted Publishing — कोई
API tokens नहीं) के लिए [`docs/PUBLISHING.hi.md`](./docs/PUBLISHING.hi.md) देखें।

## रोडमैप (v0.1.0 के दायरे से बाहर)

- `pre-commit` फ़्रेमवर्क (`.pre-commit-hooks.yaml`) का बंडल किए गए hook के साथ एकीकरण
- CLI flag के माध्यम से बहु-थीम स्विचिंग
- Front-matter से चालित रिलीज़ नोट संरचना (`version`, `date`, `breaking` keys)
- npm वितरण / Husky bridge
- Windows pre-commit hook (PowerShell)

## लाइसेंस

[MIT](./LICENSE)
