import {initializeHandler} from "@/assets/js/source-handler/initialize";

export function resolveCardLink(card) {
    if (card.placeholder !== undefined) {
        return
    }
    const handler = initializeHandler(card.source, card.sourceSpecific)
    return handler.resolveCardLink(card)
}

export function resolveCardAuthor(card) {
    const handler = initializeHandler(card.source, card.sourceSpecific)
    return handler.resolveCardAuthorLink(card)
}

export function resolveCardAvatarURL(card, showImages) {
    const handler = initializeHandler(card.source, card.sourceSpecific)
    return handler.resolveCardAvatarURL(card, !showImages, true, (showImages ? 200 : 40))
}

export function resolveCardPrettyName(card) {
    const handler = initializeHandler(card.source, card.sourceSpecific)
    return handler.prettyName
}

export function resolveCardColor(card) {
    const handler = initializeHandler(card.source, card.sourceSpecific)
    return handler.cardColor
}
