import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

# --- KONFIGURACJA ---
MOVIE_ID = "8085s2r"  # Spider-Man: Całkiem Nowy Dzień
CINEMA_ID = "1060"  # Cinema City Sadyba Warszawa

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")


def send_email():
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL.strip() if SENDER_EMAIL else ""
    msg["To"] = RECEIVER_EMAIL.strip() if RECEIVER_EMAIL else ""
    msg["Subject"] = "🚨 BILETY NA FILMY SĄ DOSTĘPNE W SADYBIE!"

    body = (
        f"Sprzedaż biletów właśnie ruszyła w Cinema City Sadyba!\n\n"
        f"Link do zakupu: https://cinema-city.pl"
    )
    msg.attach(MIMEText(body, "plain"))

    try:
        # .strip() usuwa wszelkie ukryte spacje z nazwy serwera
        clean_server = SMTP_SERVER.strip()
        print(f"Łączenie z serwerem pocztowym: '{clean_server}'...")
        
        server = smtplib.SMTP_SSL(clean_server, SMTP_PORT, timeout=15)
        server.login(SENDER_EMAIL.strip(), SENDER_PASSWORD.strip())
        server.sendmail(SENDER_EMAIL.strip(), RECEIVER_EMAIL.strip(), msg.as_string())
        server.quit()
        print("E-mail powiadomienia został pomyślnie wysłany!")
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")



def check_tickets():
    # Ogólny endpoint dla kina, sprawdzany bezpieczną metodą tekstową
    url = f"https://cinema-city.pl"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)

        # Jeżeli strona zawiera ID naszego filmu, oznacza to, że został on dodany do repertuaru Sadyby
        if MOVIE_ID in response.text:
            print("🚨 Wykryto ID filmu w systemie rezerwacji kina!")
            return True

        print("Film nie pojawił się jeszcze w repertuarze Sadyby.")
        return False

    except Exception as e:
        print(f"Wystąpił błąd podczas sprawdzania strony: {e}")
        return False


if __name__ == "__main__":
    print("Sprawdzam dostępność filmu Spider-Man w CC Sadyba...")
    if check_tickets():
        send_email()
