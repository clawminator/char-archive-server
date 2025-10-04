export function generatePlaceholderCards() {
    let result = []
    for (let i = 0; i < 5; i++) {
        result.push({name: "", id: i * Math.random(), placeholder: true, source: "placeholder"})
    }
    return result
}

export function checkCardForked(card) {
    return !!(card.source === "chub" && card.chub.forked.forked)
}
