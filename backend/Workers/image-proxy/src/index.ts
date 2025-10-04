addEventListener('fetch', (event: FetchEvent) => {
    const url = new URL(event.request.url);
    if (url.pathname === '/api/v1/image/external') {
        event.respondWith(handleRequest(event.request));
    } else {
        event.respondWith(returnErrorResponse('not an endpoint', 404));
    }
});

function returnErrorResponse(message: string, code: number): Response {
    return new Response(JSON.stringify({message, code}), {
        status: code,
        headers: {'Content-Type': 'application/json'}
    });
}

function logMsg(message: string, request: Request, parsedImageURL: URL): void {
    console.log({'ip': request.headers.get('CF-Connecting-IP'), 'url': parsedImageURL.href, 'message': message});
}

function logErrorMsg(message: string, request: Request, parsedImageURL: URL): void {
    console.log({'ip': request.headers.get('CF-Connecting-IP'), 'url': parsedImageURL.href, 'message': message});
}

async function handleRequest(request: Request): Promise<Response> {
    const allowedOrigin = 'char-archive.example.com';
    const requestOrigin = new URL(request.url).origin;
    if (requestOrigin !== `https://${allowedOrigin}`) {
        return returnErrorResponse('Unauthorized', 403);
    }

    const url = new URL(request.url);
    const imageURLRaw = url.searchParams.get('url');
    if (!imageURLRaw) {
        return returnErrorResponse('Missing URL query parameter', 400);
    }

    let x: URL
    try {
        x = new URL(decodeURIComponent(decodeURIComponent(imageURLRaw)));
    } catch (err) {
        return returnErrorResponse('Invalid URL in the query parameter', 400);
    }
    const imageURL: URL = x

    // Validate and parse the image URL
    let parsedImageURL: URL;
    try {
        parsedImageURL = new URL(imageURL);
    } catch (err) {
        return returnErrorResponse('Invalid URL', 400);
    }

    // Ensure the protocol is HTTP or HTTPS
    if (!['http:', 'https:'].includes(parsedImageURL.protocol)) {
        return returnErrorResponse('Invalid protocol. Only HTTP and HTTPS are allowed', 400);
    }

    const cfImageOptions: any = {};

    // Handle limiting image dimensions to a specific value
    const maxParam = url.searchParams.get('max');
    if (maxParam) {
        const maxValue = parseInt(maxParam, 10);
        if (isNaN(maxValue) || maxValue <= 0) {
            return returnErrorResponse('"max" must be a positive number', 400);
        }
        cfImageOptions.width = maxValue;
        cfImageOptions.height = maxValue;
        cfImageOptions.fit = 'scale-down';
    }

    // Handle resizing while preserving aspect ratio
    const widthParam = url.searchParams.get('width');
    const heightParam = url.searchParams.get('height');
    if (widthParam && heightParam) {
        return returnErrorResponse('Specify either "width" or "height", not both', 400);
    }
    if (widthParam || heightParam) {
        let dimension: 'width' | 'height';
        let dimensionValue: number;
        if (widthParam) {
            dimension = 'width';
            dimensionValue = parseInt(widthParam, 10);
        } else {
            dimension = 'height';
            dimensionValue = parseInt(heightParam, 10);
        }
        if (isNaN(dimensionValue) || dimensionValue <= 0) {
            return returnErrorResponse(`"${dimension}" must be a positive number.`, 400);
        }
        cfImageOptions[dimension] = dimensionValue;
        cfImageOptions.fit = 'contain';
    }

    if ((widthParam || heightParam) && maxParam) {
        return returnErrorResponse('Cannot specify "width" or "height" with "max"', 400);
    }

    // Handle format conversion
    const formatParam = url.searchParams.get('format');
    if (formatParam) {
        const format = formatParam.toLowerCase();
        if (['png', 'jpg', 'jpeg'].includes(format)) {
            cfImageOptions.format = format === 'jpeg' ? 'jpg' : format;
        } else {
            return returnErrorResponse('Invalid "format" parameter. Allowed values: png, jpg, jpeg', 400);
        }
    }

    cfImageOptions.quality = 80;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        controller.abort();
    }, 5000);

    try {
        const response = await fetch(imageURL, {
            cf: {
                image: cfImageOptions
            },
            headers: {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            },
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            return returnErrorResponse(`Failed to fetch the image from the source: ${response.status} - ${response.statusText}`, 502);
        }

        // Validate the Content-Type header to ensure it's an image
        const contentType = response.headers.get('Content-Type') || '';
        if (!contentType.startsWith('image/')) {
            return returnErrorResponse('The fetched resource is not an image', 400);
        }

        const newHeaders = new Headers(response.headers);
        newHeaders.set('Cache-Control', 'public, max-age=2628000'); // One month
        newHeaders.set('X-Content-Type-Options', 'nosniff');
        newHeaders.set("Content-Security-Policy", "default-src 'self' char-archive.example.com mato.example.com; script-src 'self' 'unsafe-inline' char-archive.example.com mato.example.com; style-src 'self' 'unsafe-inline' char-archive.example.com; img-src 'self' char-archive.example.com mato.example.com; font-src 'self' char-archive.example.com; connect-src 'self' char-archive.example.com mato.example.com; media-src 'self' char-archive.example.com data:; object-src 'self' char-archive.example.com; frame-src 'self' char-archive.example.com; worker-src 'self' char-archive.example.com; manifest-src 'self' char-archive.example.com; form-action 'self' char-archive.example.com; base-uri 'self' char-archive.example.com");

        logMsg('request', request, parsedImageURL);

        return new Response(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers: newHeaders
        });

    } catch (err) {
        clearTimeout(timeoutId);
        if (err.name === 'AbortError') {
            return returnErrorResponse('Image fetch timed out after 5 seconds', 504);
        }
        logErrorMsg(`Error fetching the image: ${err}`, request, parsedImageURL);
        return returnErrorResponse('An internal server error occurred while fetching the image', 500);
    }
}