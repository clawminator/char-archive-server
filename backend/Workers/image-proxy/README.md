# image-proxy

A worker to proxy remote images so that they originate from `char-archive.example.com`. This lets us restrict CSP and CORS
to the site and also prevents crawlers from seeing us linking to any bad sites.

Used for images in item descriptions and helps to keep retards from embedding enormous images for no reason.
