## inspect_html.py

To pomocniczy skrypt diagnostyczny nie jest częścią głównego scrapera.
Służył do zbadania struktury HTML gov.pl przed implementacją spidera.
Uruchamienie: uv run python scripts/inspect_html.py

Pobiera stronę indeksu i wypisuje linki z div.title > a (10 zakresów alfabetu: a-b1, c-d1 itd.).
Pobiera podstronę testową a-b1 i liczy:
linki z .pdf w URL,
linki /attachment/{uuid} (właściwy format załączników gov.pl).
Wyświetla fragment HTML wokół pierwszego załącznika, żeby zobaczyć strukturę a.file-download, span.extension itd..
Dzięki temu ustaliliśmy, że PDF-y nie mają bezpośrednich linków .pdf, tylko idą przez /attachment/..., i na tej podstawie napisane zostały selektory w spiderze.
Można go spokojnie usunąć albo zostawić jako narzędzie do debugowania, gdy gov.pl zmieni layout strony.

## verify_incremental.py

To skrypt testowy sprawdzający, czy Scrapy nie pobiera ponownie plików, które już są na dysku.
Uruchomienie: uv run python scripts/verify_incremental.py

Liczy PDFy w .artifacts/downloads-test przed uruchomieniem pdf_before
Uruchamia spidera na tym samym katalogu (FILES_STORE) z limitem CLOSESPIDER_ITEMCOUNT=3 (krótki test).
Zbiera statystyki Scrapy po zakończeniu:
downloaded — nowo pobrane pliki,
uptodate — pliki już istniejące, pominięte przez FilesPipeline,
pdf_before / pdf_after — liczba plików przed i po.

Przykładowy wynik z testów:
{'downloaded': 423, 'uptodate': 2589, 'pdf_before': 2589, 'pdf_after': 3012}
uptodate: 2589 oznacza, że 2589 plików zostało rozpoznanych jako już pobrane i nie zostały ściągnięte drugi raz. Reszta (downloaded: 423) to pliki, których wcześniejszy test nie zdążył pobrać.

## verify_scraper.py

Skrypt kontrolny, który sprawdza czy scraper i pobrane pliki spełniają założenia z planu.

Uruchomienie: uv run python scripts/verify_scraper.py

Składa się z trzech funkcji:
count_index_links() - pobiera stronę indeksu i liczy linki do zakresów alfabetu (div.title > a). Oczekiwane: 10.
count_ab_pdfs() - pobiera podstronę a-b1 i liczy prawidłowe PDF-y w sekcji Materiały (a.file-download + span.extension), pomijając śmieci typu @.pdf. Oczekiwane: >100.
verify_downloads() - sprawdza katalog .artifacts/downloads-test:
ile plików .pdf jest na dysku,
czy pierwsze 20 ma poprawny nagłówek %PDF,
ile wpisów jest w manifest.jsonl.

Przykładowy wynik:
index_links: 10
a-b1_pdfs: 513
downloads: {'pdf_files': 1232, 'valid_pdf_headers_sample': 20, 'manifest_lines': 643}

## Podsumowanie

inspect_html.py — odkrywa strukturę HTML,
verify_scraper.py — weryfikuje, czy wszystko działa poprawnie,
verify_incremental.py — testuje pomijanie już pobranych plików.
Żaden z nich nie jest potrzebny do normalnego pobierania etykiet.
