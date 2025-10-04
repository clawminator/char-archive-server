export function doubleEncodeUrlParam(param: string) {
    return encodeURIComponent(encodeURIComponent(param))
}

export function doubleDecodeUrlParam(param: string) {
    return decodeURIComponent(decodeURIComponent(param))
}

export function generateDisabledMsg(title: string, message: string) {
    return `<h2 class="text-2xl font-bold mb-2 text-center">${title}</h2>
<p>${message}`
}

export function limitString(name: string, limit: number) {
    return name.length > limit ? name.substring(0, limit) + "..." : name;
}

export function capitalizeFirstLetter(string: string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

export function toTitleCase(str) {
    return str.replace(
        /\w\S*/g,
        text => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase()
    );
}

export function parseUntrustedHTML(htmlStr: string) {
    // Cloak external images and links so that we aren't caught linking to a terrible site by crawlers.
    // Also helps keep authors from embedding enormous images.
    const imagePrefix = "https://char-archive.example.com/api/v1/image/external?url=";
    const linkPrefix = "https://char-archive.example.com/external-link?url=";

    // Replace src attributes
    htmlStr = htmlStr.replace(/src="([^"]+)"/g, (match, url) => {
        const encodedUrl = doubleEncodeUrlParam(url);
        return `src="${imagePrefix}${encodedUrl}&max=700"`;
    });

    // Replace href attributes
    htmlStr = htmlStr.replace(/href="([^"]+)"/g, (match, url) => {
        const encodedUrl = doubleEncodeUrlParam(url);
        return `href="${linkPrefix}${encodedUrl}"`;
    });

    return htmlStr;
}

export function convertSnakeCaseToKebabCase(obj: Record<string, any>): Record<string, any> {
    const convertedObj: Record<string, any> = {}
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            const kebabKey = key.replace(/_/g, '-')
            convertedObj[kebabKey] = obj[key]
        }
    }
    return convertedObj
}
