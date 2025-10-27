import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import json
import os


def clean_price(price_text):
    # Fiyat metninden sadece sayıları alır
    return re.sub(r'[^\d]', '', price_text)


def save_links_to_file(links, filename="buca_links.json"):
    #Linkleri JSON dosyasına kaydet
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(links), f, ensure_ascii=False, indent=2)
    print(f"✓ {len(links)} link '{filename}' dosyasına kaydedildi.")


def load_links_from_file(filename="buca_links.json"):
    #JSON dosyasından linkleri yükle
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            links = json.load(f)
        print(f"✓ {len(links)} link '{filename}' dosyasından yüklendi.")
        return set(links)
    return set()


def save_progress(data, filename="buca_progress.json"):
    # İlerlemeyi kaydet (hangi linkler işlendi)
    progress = {
        'processed_links': [d['Link'] for d in data],
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_processed': len(data)
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def load_progress(filename="buca_progress.json"):
    # Kaydedilmiş ilerlemeyi yükle
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        print(f"✓ İlerleme yüklendi: {progress['total_processed']} ilan işlenmiş.")
        return set(progress['processed_links'])
    return set()


def scroll_page_smoothly(driver, pause_time=1.0):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_attempts = 8

    while scroll_attempts < max_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            scroll_attempts += 1
            if scroll_attempts >= 2:
                break
        else:
            scroll_attempts = 0
            last_height = new_height

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.3)


def get_all_listing_links(driver, start_page=1):
    base_url = "https://www.hepsiemlak.com/en/buca-satilik?page="

    # Önceden kaydedilmiş linkleri yükle
    all_links = load_links_from_file()
    initial_count = len(all_links)

    current_page = start_page
    consecutive_empty_pages = 0
    max_empty_pages = 2

    print(f"\nAşama 1: Buca Satılık ilan linkleri toplanıyor...")
    if initial_count > 0:
        print(f"Daha önce {initial_count} link toplanmış. Sayfa {start_page}'den devam ediliyor...")

    cookie_handled = (start_page > 1)  # Eğer sayfa 1'den başlamıyorsak cookie zaten halledilmiş

    try:
        while True:
            if current_page == 1:
                url = "https://www.hepsiemlak.com/en/buca-satilik"
            else:
                url = base_url + str(current_page)

            print(f"\n{'=' * 50}")
            print(f"Sayfa {current_page} taranıyor... (Toplam link: {len(all_links)})")
            print(f"{'=' * 50}")

            try:
                driver.get(url)
            except Exception as e:
                print(f"✗ Sayfa yüklenirken hata: {e}")
                break

            if current_page == 1 and not cookie_handled:
                print("\n" + "=" * 50)
                print("TARAYICI AÇILDI. SCRIPT DURDURULDU.")
                print("Lütfen açılan Edge penceresine gidin ve ÇEREZ (COOKIE) uyarısını")
                print("manuel olarak ('Accept All' vb.) tıklayarak kapatın.")
                print("\nİşlemi bitirince bu terminal ekranına dönün ve")
                print("DEVAM ETMEK İÇİN ENTER TUŞUNA BASIN...")
                print("=" * 50)
                input()
                print("Kullanıcı onayı alındı, script devam ediyor...\n")
                cookie_handled = True
                time.sleep(2)

            time.sleep(1)

            # Lazy loading için sayfayı kaydır
            scroll_page_smoothly(driver, pause_time=1.0)

            link_selectors = [
                "a.card-link",
                "li.list-view-item a.card-link",
                "li.list-view-item a",
            ]

            listings = []
            for selector in link_selectors:
                temp_listings = driver.find_elements(By.CSS_SELECTOR, selector)
                if temp_listings and len(temp_listings) > len(listings):
                    listings = temp_listings

            if not listings:
                consecutive_empty_pages += 1
                print(f"⚠️ Bu sayfada ilan bulunamadı. Boş sayfa: {consecutive_empty_pages}/{max_empty_pages}")

                if consecutive_empty_pages >= max_empty_pages:
                    print(f"\n{max_empty_pages} ardışık boş sayfa. İşlem sonlandırılıyor.")
                    break

                time.sleep(2)
                current_page += 1
                continue
            else:
                consecutive_empty_pages = 0

            # Linkleri topla
            links_before = len(all_links)

            for listing in listings:
                try:
                    link = listing.get_attribute("href")
                    if link and link.startswith("http") and "satilik" in link:
                        all_links.add(link)
                except Exception as e:
                    pass

            new_links = len(all_links) - links_before
            print(f"✓ Bu sayfadan {new_links} yeni link eklendi")
            print(f"Toplam benzersiz link: {len(all_links)}")

            # Her 5 sayfada bir kaydet
            if current_page % 5 == 0:
                save_links_to_file(all_links)
                print(f"💾 İlerleme kaydedildi (Sayfa {current_page})")

            if new_links == 0:
                print("⚠️ Yeni link eklenemedi. Son sayfaya ulaşıldı olabilir.")
                break

            current_page += 1
            time.sleep(1.5)  # Rate limiting

    except KeyboardInterrupt:
        print("\n\n⚠️ Kullanıcı tarafından durduruldu!")
        save_links_to_file(all_links)
        print(f"Son durum: Sayfa {current_page}, Toplam {len(all_links)} link")
        raise
    except Exception as e:
        print(f"\n✗ Beklenmeyen hata: {e}")
        save_links_to_file(all_links)
        raise

    # Son kayıt
    save_links_to_file(all_links)
    return list(all_links)


def scrape_detail_page(driver, link):
    """Tek bir ilan detay sayfasını ziyaret eder ve tüm özellikleri çeker."""
    try:
        driver.get(link)
    except Exception as e:
        print(f"✗ Sayfa açılamadı: {e}")
        return None

    data = {"Link": link}

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.fontRB"))
        )

        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, "h1.fontRB")
            data['Baslik'] = title_elem.text.strip()
        except NoSuchElementException:
            data['Baslik'] = "N/A"

        try:
            price_elem = driver.find_element(By.CSS_SELECTOR, "p.fz24-text.price")
            price_text = price_elem.text.strip()
            data['Fiyat (Metin)'] = price_text
            data['Fiyat (Sayisal)'] = re.sub(r'[^\d]', '', price_text)
        except NoSuchElementException:
            data['Fiyat (Metin)'] = "N/A"
            data['Fiyat (Sayisal)'] = "N/A"

        try:
            location_elements = driver.find_elements(By.CSS_SELECTOR, "div.bread-crumb ul li a span")
            location_text = " > ".join([elem.text for elem in location_elements if elem.text])
            data['Konum'] = location_text if location_text else "N/A"
        except NoSuchElementException:
            data['Konum'] = "N/A"

        feature_items = driver.find_elements(By.CSS_SELECTOR, "ul.adv-info-list li.spec-item")
        for item in feature_items:
            try:
                key = item.find_element(By.CSS_SELECTOR, "span.txt").text.strip()
                all_text = item.text
                value = all_text.replace(key, '').strip()
                key = key.replace('/', ' / ')
                if key:
                    data[key] = value if value else "N/A"
            except Exception:
                continue

        return data

    except TimeoutException:
        print(f"⚠️ Sayfa zaman aşımına uğradı: {link}")
        return None
    except Exception as e:
        print(f"⚠️ Beklenmeyen hata: {e}")
        return None


def scrape_details_from_links(driver, links, output_file="buca_emlak_detayli_SATILIK_veriler.csv"):

    # Daha önce işlenmiş linkleri yükle
    processed_links = load_progress()

    # Daha önce kaydedilmiş veriyi yükle
    all_listings_data = []
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file, encoding='utf-8-sig')
            all_listings_data = df_existing.to_dict('records')
            print(f"✓ Önceki veriler yüklendi: {len(all_listings_data)} ilan")
        except:
            pass

    # Henüz işlenmemiş linkleri filtrele
    remaining_links = [link for link in links if link not in processed_links]

    print(f"\n{'=' * 50}")
    print(f"Aşama 2: Detay Bilgileri Çekiliyor")
    print(f"Toplam link: {len(links)}")
    print(f"İşlenmiş: {len(processed_links)}")
    print(f"Kalan: {len(remaining_links)}")
    print(f"{'=' * 50}\n")

    if not remaining_links:
        print("✓ Tüm ilanlar zaten işlenmiş!")
        return all_listings_data

    try:
        for i, link in enumerate(remaining_links):
            print(f"\n--- İlan {i + 1} / {len(remaining_links)} (Toplam: {len(all_listings_data) + i + 1}) ---")
            print(f"Link: {link[:60]}...")

            details = scrape_detail_page(driver, link)
            if details:
                all_listings_data.append(details)
                print(f"✓ Başarılı: {details.get('Baslik', 'N/A')[:50]}...")
            else:
                print(f"✗ Detay çekilemedi")

            # Her 10 ilanda bir kaydet
            if (i + 1) % 10 == 0:
                df = pd.DataFrame(all_listings_data)
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                save_progress(all_listings_data)
                print(f"💾 İlerleme kaydedildi ({len(all_listings_data)} ilan)")

            time.sleep(1.0)  # Rate limiting

    except KeyboardInterrupt:
        print("\n\n⚠️ Kullanıcı tarafından durduruldu!")
        print("Mevcut veriler kaydediliyor...")
    except Exception as e:
        print(f"\n✗ Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Her durumda kaydet
        if all_listings_data:
            df = pd.DataFrame(all_listings_data)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            save_progress(all_listings_data)
            print(f"💾 Veriler kaydedildi: {len(all_listings_data)} ilan")

    return all_listings_data


def run_scraper(mode="full", start_page=1):
    """
    Ana scraper fonksiyonu
    """

    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    )

    driver_path = "msedgedriver.exe"
    service = Service(executable_path=driver_path)

    try:
        driver = webdriver.Edge(service=service, options=options)
        print("✓ Edge WebDriver başarıyla başlatıldı.")
    except Exception as e:
        print(f"✗ HATA: 'msedgedriver.exe' başlatılamadı. Hata: {e}")
        return

    all_listings_data = []

    try:
        # Link toplama aşaması
        if mode in ["full", "links"]:
            all_links = get_all_listing_links(driver, start_page=start_page)
        else:
            # Sadece detay çekme modunda önceki linkleri yükle
            all_links = list(load_links_from_file())
            if not all_links:
                print("✗ Hiç link bulunamadı! Önce 'links' modunu çalıştırın.")
                return

        if not all_links:
            print("\n⚠️ Hiç ilan linki bulunamadı.")
            return

        # Detay çekme aşaması
        if mode in ["full", "details"]:
            all_listings_data = scrape_details_from_links(driver, all_links)

    finally:
        driver.quit()

        if all_listings_data:
            print(f"\n{'=' * 50}")
            print(f"✓ İŞLEM TAMAMLANDI!")
            print(f"Toplam {len(all_listings_data)} ilan işlendi")
            print(f"Dosya: buca_emlak_detayli_SATILIK_veriler.csv")
            print(f"{'=' * 50}")


if __name__ == "__main__":
    # 1. STANDART
    # run_scraper(mode="full", start_page=1)

    # 2. SADECE LİNK TOPLA
    # run_scraper(mode="links", start_page=1)

    # 3. KALDIĞI YERDEN DEVAM ET
    # run_scraper(mode="links", start_page=41)

    # 4. SADECE DETAY ÇEK

     run_scraper(mode="details")