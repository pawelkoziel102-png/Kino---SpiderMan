import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

# --- KONFIGURACJA ZACIĄGANA Z SEKRETÓW GITHUBA ---
MOVIE_ID = "8085s2r"  # Spider-Man: Całkiem Nowy Dzień
CINEMA_ID = "1060"  # Cinema City Sadyba Warszawa

SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")


def send_email(date_found, formats_found):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg[
        "Subject"
    ] = "🚨 BILETY IMAX NA SPIDER-MANA SĄ DOSTĘPNE W SADYBIE!"

    body = (
        f"Sprzedaż biletów ruszyła!\n\n"
        f"Film: Spider-Man: Całkiem Nowy Dzień\n"
        f"Kino: Cinema City Sadyba\n"
        f"Wykryta data seansu: {date_found}\n"
        f"Dostępne formaty: {', '.join(formats_found)}\n\n"
        f"Link do zakupu: https://cinema-city.pl"
    )
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("E-mail powiadomienia został pomyślnie wysłany!")
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")


def check_tickets_for_next_days():
    url = f"https://cinema-city.pl{CINEMA_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get("body", {}).get("events", [])
            films = data.get("body", {}).get("films", [])

            target_film = next(
                (f for f in films if str(f.get("id")) == MOVIE_ID), None
            )

            if target_film:
                imax_screenings = []
                for event in events:
                    if str(event.get("filmId")) == MOVIE_ID:
                        attribute_ids = event.get("attributeIds", [])
                        is_imax = any(
                            "imax" in str(attr).lower()
                            for attr in attribute_ids
                        )
                        if is_imax:
                            imax_screenings.append(event)

                if imax_screenings:
                    first_event = imax_screenings[0]
                    event_date = first_event.get(
                        "businessDay", "Nieznana data"
                    )
                    formats = first_event.get("attributeIds", ["IMAX"])
                    print(
                        f"🚨 SUKCES! Znaleziono seans IMAX na dzień: {event_date}."
                    )
                    return True, event_date, formats

                print(
                    "Film jest w bazie kina Sadyba, ale jeszcze BRAK seansów IMAX."
                )
                return False, None, None
            else:
                print("Brak filmu w aktualnej siatce kina Sadyba.")
                return False, None, None
        else:
            print(f"Błąd API (Status: {response.status_code})")
            return False, None, None
    except Exception as e:
        print(f"Wystąpił błąd połączenia: {e}")
        return False, None, None


if __name__ == "__main__":
    print("Sprawdzam bilety IMAX w CC Sadyba...")
    tickets_out, date_found, formats_found = check_tickets_for_next_days()
    if tickets_out:
        send_email(date_found, formats_found)
