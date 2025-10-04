async function loadDef(cardSource, cardType, cardPath) {
    const url = `https://char-archive.example.com/api/archive/v1/${cardSource}/def/${cardType}/${cardPath}`
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const cardDataDef = await response.json();
        const highlight = hljs.highlight(
            JSON.stringify(cardDataDef, null, 2),
            {language: 'json'}
        ).value
        return [cardDataDef, highlight]
    } catch (err) {
        console.error("Error while fetching:", err);
    }
}