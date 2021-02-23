import re
import requests
import orodja

stevilo_strani = 7
dejavnost = "Energetika"
vzorec = (
    r'<a href="(?P<naslov>/.*?)" id=".*?" class="contact-link"'
    )

vzorec_bloka = re.compile(
    r'<div class="contact-info">\n\n.*\n\n\s*.*?\n.*?'
    r'</div>\n\n</div>\n\n\n\n\s*</div>',
    flags=re.DOTALL
)

vzorec_podjetja = re.compile(
    r'<head>.*?\n\n\s(?P<ime>.*?)- TIS\n.*',
    flags=re.DOTALL
)

vzorec_imen = re.compile(
    r'<div class="contact-info">\n\n.*\n\n\s*(?P<ime>.*?)\n',
    flags=re.DOTALL
)

vzorec_telefonskih_stevilk = re.compile(
    r'<div class="caption">Telefon</div>\n\n\s*?<div class="nr">(?P<telefonska>.*?)<',
    flags=re.DOTALL
)

vzorec_mailov = re.compile(
    r'href="mailto:(?P<mail>.*?)"',
    flags=re.DOTALL
)

vzorec_spletnih_strani = re.compile(
    r'title="Spletna stran podjetja.*?>(?P<spletna_stran>.*?)<',
    flags=re.DOTALL
)

vzorec_piksla = re.compile(
    r'Facebook Pixel',
    flags=re.DOTALL
)

vzorec_google_tag_manager = re.compile(
    r'Google Tag Manager',
    flags=re.DOTALL
)

vzorec_google_analytisc = re.compile(
    r'Google Analytics',
    flags=re.DOTALL
)


def izloci_podatke(blok):
    podjetje = vzorec_podjetja.search(blok).groupdict()
    telefonska = vzorec_telefonskih_stevilk.search(blok)
    if telefonska:
        podjetje['telefonska'] = telefonska['telefonska']
    else:
        podjetje['telefonska'] = None
    mail = vzorec_mailov.search(blok)
    if mail:
        podjetje['mail'] = mail['mail']
    else:
        podjetje['mail'] = None
    spletna_stran = vzorec_spletnih_strani.search(blok)
    if spletna_stran:
        podjetje['spletna_stran'] = spletna_stran['spletna_stran']
    else:
        podjetje['spletna_stran'] = None        
    return podjetje

def nalozi_stran(url):
    print(f'Nalagam {url}...')
    odziv = requests.get(url)
    return odziv.text

naslovi = []

for stran in range(stevilo_strani):
    stran += 1
    url = f"https://www.itis.si/dejavnost/{dejavnost}/stran-{stran}"
    vsebina = nalozi_stran(url)
    with open(f'{dejavnost}-stran-{stran}.html', 'w') as f:
        f.write(vsebina)

    with open(f'{dejavnost}-stran-{stran}.html') as f:
        vsebina = f.read()

        for zadetek in re.finditer(vzorec, vsebina):
            naslovi.append(zadetek.groupdict())     

def podjetja_na_strani():
    count = 0
    for naslov in naslovi:
        for a in naslov:
            url1 = (naslov[a])
            url = f"https://www.itis.si{url1}"
            count +=1
            ime_datoteke = '{}-{}.html'.format(dejavnost,count)
            orodja.shrani_spletno_stran(url, ime_datoteke)
            vsebina = orodja.vsebina_datoteke(ime_datoteke)
            for blok in vzorec_podjetja.finditer(vsebina):
                yield izloci_podatke(blok.group(0))


podjetja = []
for podjetje in podjetja_na_strani():
        podjetja.append(podjetje)

#stevec = 0
#for podjetje in podjetja:
#    if stevec < 3000:
#        if podjetje['spletna_stran']:
#            stevec += 1
#            stran = podjetje['spletna_stran']
#            datoteka = f'{stevec}.html'
#            orodja.shrani_spletno_stran(stran,datoteka)
#            vsebina = orodja.vsebina_datoteke(datoteka)
#            piksel = vzorec_piksla.search(vsebina)
#            google_tag = vzorec_google_tag_manager.search(vsebina)
#            google_analytics = vzorec_google_analytisc.search(vsebina)
#            if piksel:
#                podjetje['piksel'] = 'ja'
#            elif google_tag:
#                podjetje['piksel'] = 'ja(google tag manager)'
#            else:
#                podjetje['piksel'] = 'ne'   
#            if google_analytics:
#                podjetje['google analytics'] = 'ja'
#            else:
#                podjetje['google analytics'] = 'ne'           
#        else:
#            podjetje['piksel'] = 'ne'
#    else:
#        podjetje['piksel'] = 'ne'                    

orodja.zapisi_json(podjetja, 'obdelani-podatki.json')
orodja.zapisi_csv(
    podjetja,
    ['ime', 'telefonska', 'mail', 'spletna_stran'], 'obdelani-podatki.csv'
)

