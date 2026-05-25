# PyPI पर प्रकाशन

यह प्रोजेक्ट **GitHub Actions + Trusted Publishing (OIDC)** के माध्यम से PyPI पर प्रकाशित किया
जाता है। रिपॉज़िटरी के secrets में कोई दीर्घजीवी API token संग्रहित नहीं किया जाता।

## प्रथम-बार सेटअप (एक बार, मैनुअल)

ये चरण पहले रिलीज़ से पहले रिपॉज़िटरी के स्वामी द्वारा निष्पादित किए जाने चाहिए।

### 1. एक PyPI खाता बनाएँ

https://pypi.org/account/register/

2FA को सक्षम करें (प्रकाशन के लिए आवश्यक)।

### 2. प्रोजेक्ट नाम आरक्षित करें

चूँकि `release-information` अभी PyPI पर मौजूद नहीं है, हम एक **pending publisher** का उपयोग
करते हैं:

1. https://pypi.org/manage/account/publishing/ पर जाएँ
2. "Add a new pending publisher" फ़ॉर्म भरें:
   - **PyPI Project Name**: `release-information`
   - **Owner**: `kou135`
   - **Repository name**: `release-information`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
3. Submit करें।

### 3. GitHub Environment बनाएँ

1. https://github.com/kou135/release-information/settings/environments पर जाएँ
2. **New environment** क्लिक करें, इसका नाम `pypi` रखें।
3. (वैकल्पिक) `Required reviewers` = स्वयं को जोड़ें, ताकि प्रत्येक प्रकाशन के लिए मैनुअल
   स्वीकृति क्लिक की आवश्यकता हो।
4. Save करें।

## नया संस्करण रिलीज़ करना

```bash
# 1. pyproject.toml में संस्करण bump करें (उदाहरण: 0.1.0 -> 0.1.1)
# 2. CHANGELOG.md अपडेट करें
# 3. Commit और push करें
git commit -am "release: v0.1.1"
git push

# 4. Tag लगाएँ और tag को push करें (यह publish workflow को ट्रिगर करता है)
git tag v0.1.1
git push --tags
```

`Publish to PyPI` workflow निम्न करेगा:
1. `sdist` + `wheel` बिल्ड करेगा।
2. Environment स्वीकृति की प्रतीक्षा करेगा (यदि required reviewers कॉन्फ़िगर किए गए हों)।
3. OIDC के माध्यम से PyPI पर अपलोड करेगा — किसी token की आवश्यकता नहीं।

सफलता के बाद, पैकेज https://pypi.org/project/release-information/ पर उपलब्ध होगा
और `pip install release-information` से इंस्टॉल किया जा सकेगा।

## पहले सफल प्रकाशन के बाद

"pending publisher" स्वचालित रूप से एक नियमित publisher बन जाता है।
बाद के रिलीज़ के लिए केवल एक नए tag की आवश्यकता है — PyPI dashboard में कोई बदलाव नहीं।

## रोलबैक करना

PyPI एक ही संस्करण को फिर से अपलोड करने की **अनुमति नहीं देता**। यदि कुछ टूट गया है, तो
PyPI पर रिलीज़ को yank करें और एक नया patch संस्करण प्रकाशित करें:

```bash
# Web UI के माध्यम से yank करें: https://pypi.org/manage/project/release-information/releases/
# फिर:
# pyproject.toml में 0.1.2 तक bump करें + CHANGELOG, commit, tag, push।
```
