import csv
import io
import time
import urllib.request

HEADERS = {'User-Agent': 'PokemonMasterSheetBuilder/1.0'}

CATEGORIES = [
    ('3', 'English'),
    ('85', 'Japanese'),
]

OUTPUT_FILE = 'pokemon_all_cards_master.csv'


def fetch_csv(url):
  req = urllib.request.Request(url, headers=HEADERS)
  with urllib.request.urlopen(req) as resp:
    text = resp.read().decode('utf-8-sig')
    return list(csv.DictReader(io.StringIO(text)))


with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
  writer = csv.writer(f)
  writer.writerow(['Language', 'Set Name', 'Card Name', 'Number', 'Finish'])

  for cat_id, lang in CATEGORIES:
    groups = fetch_csv(f'https://tcgcsv.com{cat_id}/Groups.csv')
    print(f'Fetching {len(groups)} {lang} sets...')

    for i, g in enumerate(groups, 1):
      gid = g['groupId']
      set_name = g['name']
      try:
        rows = fetch_csv(
            f'https://tcgcsv.com{cat_id}/{gid}/ProductsAndPrices.csv'
        )
        card_count = 0
        for r in rows:
          number = r.get('extNumber', '').strip()
          if not number:
            continue
          writer.writerow([
              lang,
              set_name,
              r.get('name', '').strip(),
              number,
              r.get('subTypeName', 'Normal').strip(),
          ])
          card_count += 1
        print(f'[{lang} {i}/{len(groups)}] {set_name}: {card_count} variants')
      except Exception as e:
        print(f'[{lang} {i}/{len(groups)}] Skipped {set_name}: {e}')
      time.sleep(0.15)

print(f'\nComplete! Saved all cards to {OUTPUT_FILE}')
