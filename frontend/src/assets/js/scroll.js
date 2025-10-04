export function ScrollToDataPathElement(dataPath) {
    // Remove the highlight from existing elements.
    const highlightedElements = document.getElementsByClassName('highlighted-file');
    while (highlightedElements.length > 0) {
        highlightedElements[0].classList.remove('highlighted-file');
    }

    const element = document.querySelector(`[data-path='${dataPath}']`);
    const offset = 42; // navbar height
    if (element) {
        const elementPosition = element.getBoundingClientRect().top + window.scrollY;
        window.scrollTo({top: elementPosition - offset - 25, behavior: 'smooth'});
        element.classList.add("highlighted-file");
    } else {
        console.warn(`Failed to find element to scroll to: ${dataPath}`)
    }
}