function fetchPokemonMaster() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.clear();
  sheet.appendRow(['Language', 'Set Name', 'Card Name', 'Number', 'Finish']);

  const categories = [
    { id: '3', lang: 'English' },
    { id: '85', lang: 'Japanese' }
  ];

  let batch = [];

  for (const cat of categories) {
    const groupsCsv = UrlFetchApp.fetch(`https://tcgcsv.com{cat.id}/Groups.csv`).getContentText();
    const groups = Utilities.parseCsv(groupsCsv);

    // Start at row 1 to skip header
    for (let i = 1; i < groups.length; i++) {
      const groupId = groups[i][0];
      const setName = groups[i][1];
      if (!groupId) continue;

      try {
        const prodCsv = UrlFetchApp.fetch(`https://tcgcsv.com{cat.id}/${groupId}/ProductsAndPrices.csv`).getContentText();
        const rows = Utilities.parseCsv(prodCsv);
        const headers = rows[0];
        
        const nameIdx = headers.indexOf('name');
        const numIdx = headers.indexOf('extNumber');
        const finishIdx = headers.indexOf('subTypeName');

        for (let r = 1; r < rows.length; r++) {
          const num = (rows[r][numIdx] || '').trim();
          if (!num) continue; // Skip sealed products

          batch.push([
            cat.lang,
            setName,
            (rows[r][nameIdx] || '').trim(),
            "'" + num, // Apostrophe keeps leading zeros like 001/198 intact
            (rows[r][finishIdx] || 'Normal').trim()
          ]);
        }

        // Write in chunks of 5,000 rows so it stays fast
        if (batch.length >= 5000) {
          sheet.getRange(sheet.getLastRow() + 1, 1, batch.length, 5).setValues(batch);
          batch = [];
        }
      } catch (e) {
        Logger.log(`Skipped ${setName}: ${e}`);
      }
      Utilities.sleep(100);
    }
  }

  if (batch.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, batch.length, 5).setValues(batch);
  }
}
