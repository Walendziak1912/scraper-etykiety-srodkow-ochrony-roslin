import re
import urllib.request

SUB = "https://www.gov.pl/web/rolnictwo/a-b1"
INDEX = "https://www.gov.pl/web/rolnictwo/etykiety-srodkow-ochrony-roslin"

index_html = urllib.request.urlopen(INDEX).read().decode("utf-8")
links = re.findall(r'<div class="title">\s*<a href="([^"]+)"', index_html)
print("index links:", len(links))
for link in links:
    print(" ", link)

sub_html = urllib.request.urlopen(SUB).read().decode("utf-8")
pdf_hrefs = [m for m in re.findall(r'href="([^"]+)"', sub_html) if ".pdf" in m.lower()]
print("\npdf hrefs:", len(pdf_hrefs))
for x in pdf_hrefs[:5]:
    print(" ", x[:120])

attachment_hrefs = [m for m in re.findall(r'href="([^"]+)"', sub_html) if "/attachment/" in m.lower()]
print("\nattachment hrefs:", len(attachment_hrefs))
for x in attachment_hrefs[:5]:
    print(" ", x[:120])

idx = sub_html.find("attachment")
print("\nfirst attachment context:")
print(sub_html[idx : idx + 1200] if idx >= 0 else "none")
