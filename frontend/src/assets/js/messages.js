import {generateDisabledMsg} from "@/assets/js/strings";

export const siteLockedHTML = generateDisabledMsg("Failed to reach the backend server :(", `Sorry, but we're offline. Maybe check the <a href="/#/about.html">about page</a>, the <a href="https://status.example.com/status/chub-archive">status page</a>, or try reloading?`)


export const siteScanningHTML = generateDisabledMsg("Initial scan running", `<p>Please wait for the initial scan to finish. This may take 5 minutes.</p><p>The server caches the directory structure in memory to make serving files faster, meaning it must first crawl through the directory to fill its cache.</p><p>When the scan finishes, make sure to clear your browser's cache for this site with Ctrl + F5.</p><p>Maybe check the <a href="/#/about.html">about page</a>?`)

export const scanMsg = "The backend server is currently scanning. Results may be incomplete until it's finished and the CDN cache is cleared. Clear your browser's cache for this site with Ctrl + F5."



