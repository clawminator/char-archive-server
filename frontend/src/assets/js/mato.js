export function matoPush(category, action, name) {
    _paq.push(["trackEvent", category, action, name]);
}

export function matoPushDl(downloadedUrl) {
    _paq.push(['trackLink', downloadedUrl, 'download'])
}