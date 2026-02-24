import streamlit as st

from receipt_service import (
    LogoLoadError,
    ReceiptData,
    generate_receipt_pdf,
    validate_receipt_inputs,
)

st.set_page_config(
    page_title="Bewirti - Der Bewirtungsbeleg Buddy",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://yannik.swokiz.com/contact',
        'Report a bug': "https://github.com/ykorzikowski/belegi/issues",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title("🧾 Bewirti - Der Bewirtungsbeleg Buddy")
st.logo("res/logo.png", size="large")

col1, col2 = st.columns([0.3, 0.7])
with col1:
    st.image("res/logo_square.png")
with col2:
    st.markdown("""
    Dieses Tool hilft dir dabei, schnell und unkompliziert einen professionellen
    Bewirtungsbeleg zu erstellen.
    Du kannst folgende Angaben machen:

    - Anlass und Datum der Bewirtung
    - Die bewirteten Personen
    - Betrag, Trinkgeld und Gesamtbetrag
    - Ein Foto machen oder ein bereits vorhandenes Belegdokument hochladen
    - Der generierte PDF-Beleg enthält außerdem ein Feld für die Unterschrift

    Klicke unten auf **"Generiere Beleg"**, um die PDF-Datei zu erstellen und herunterzuladen.
    """)

reason = st.text_input("Anlass der Bewirtung")
date = st.date_input("Tag der Bewirtung")
location = st.text_input("Ort der Bewirtung")

host = st.text_input("Bewirtende Person")

persons_str = st.text_area("Bewirtete Personen")
persons = [p.strip() for p in persons_str.split("\n") if p.strip()]

amount = st.number_input("Betrag", min_value=0.1, format="%.2f")
tip = st.number_input("Trinkgeld", min_value=0.0, format="%.2f")

add_logo = st.checkbox("Logo hinzufügen", value=True)
upload_existing_file = st.checkbox("Bestehenden Beleg hochladen", value=True)
took_picture = None
uploaded_file = None

if upload_existing_file:
    uploaded_file = st.file_uploader("Beleg", disabled=not upload_existing_file)
else:
    took_picture = st.camera_input("Take a picture", disabled=upload_existing_file)

btn_generate_pdf = st.button("Generiere Beleg", type="primary")

if btn_generate_pdf:
    errors = validate_receipt_inputs(
        host=host,
        location=location,
        reason=reason,
        persons=persons,
        has_receipt_attachment=bool(took_picture or uploaded_file),
    )

    if errors:
        for error in errors:
            st.error(error)
        st.stop()

    attachment_bytes = None
    attachment_filename = None
    if took_picture:
        attachment_bytes = took_picture.getvalue()
        attachment_filename = "camera.jpg"
    elif uploaded_file:
        attachment_bytes = uploaded_file.read()
        attachment_filename = uploaded_file.name

    receipt = ReceiptData(
        reason=reason,
        date=date,
        location=location,
        host=host,
        persons=persons,
        amount=amount,
        tip=tip,
    )

    try:
        result_pdf = generate_receipt_pdf(
            receipt=receipt,
            add_logo=add_logo,
            logo_path="res/bewirti_logo.png",
            attachment_bytes=attachment_bytes,
            attachment_filename=attachment_filename,
        )
    except LogoLoadError as e:
        st.warning(f"Logo konnte nicht geladen werden: {e}")
        result_pdf = generate_receipt_pdf(
            receipt=receipt,
            add_logo=False,
            logo_path="res/bewirti_logo.png",
            attachment_bytes=attachment_bytes,
            attachment_filename=attachment_filename,
        )
    except Exception as e:
        st.error(f"PDF konnte nicht erstellt werden: {e}")
        st.stop()

    st.download_button("Download Beleg-PDF", result_pdf, file_name="bewirtungsbeleg.pdf")
    if attachment_filename and attachment_filename.lower().endswith(".pdf"):
        st.success("Beleg erstellt mit hochgeladenem PDF.")
    else:
        st.success("Beleg erfolgreich erstellt.")

# Add footer with Impressum link
st.markdown("""
---
Bitte beachten Sie, dass dieser Service keine steuerliche oder rechtliche Beratung ersetzt.
**Unter Ausschluss jeglicher Gewährleistung!**
📄 [Impressum](https://yannik.swokiz.com/impressum/)
📄 [GitHub](https://github.com/ykorzikowski/belegi)
""", unsafe_allow_html=True)
