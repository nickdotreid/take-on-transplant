import Sticky from 'sticky-js'
import tippy from 'tippy.js';

function registerPopovers() {
    document.querySelectorAll('[data-toggle="popover"]').forEach((element) => {
        const content = element.getAttribute('data-content');
        if (content) {
            tippy(element, {
                content: content
            });
        }
    });

    document.querySelectorAll('.popover-links a').forEach((element) => {
        const content = element.text;
        if (content) {
            tippy(element, {
                content: content,
                placement: 'right'
            });
        }
    });
}

function registerCollapsibleContent() {
    document.querySelectorAll('.collapsible-content').forEach((element) => {
        const title = element.querySelector('.title');
        if (title) {
            title.addEventListener('click', () => {
                element.classList.toggle('open');
            });
        }
    });
}

function setupActiveLinks() {

    const navLinks = document.querySelectorAll('.sidebar a');

    function update() {
        console.log('update active links');
        navLinks.forEach((link) => {
            let section = document.querySelector(link.hash);
            const topPassed = section.offsetTop <= window.scrollY;
            const bottomPassed = section.offsetTop + section.offsetHeight <= window.scrollY;
            if (topPassed && !bottomPassed) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    let timeout;
    window.addEventListener("scroll", () => {
        if (timeout) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(update, 250);
    });
}

function setupStickyElements() {

    new Sticky('.is-sticky', {
        wrap: true,
        stickyClass: 'is-stuck'
    });

    // const stickyElements = [];
    // document.querySelectorAll('.is-sticky').forEach((element) => {
    //     stickyElements.push({
    //         'element': element,
    //         'top': element.offsetTop,
    //         'height': element.offsetHeight,
    //         'width': element.offsetWidth,
    //         'fillerElement': document.createElement('span')
    //     });
    // });
    // function update() {
    //     console.log(stickyElements);
    //     stickyElements.forEach((_element) => {
    //         const element = _element.element;
    //         const fillerElement = _element.fillerElement;
    //         const bottomPassed = _element.bottom + _element.height <= window.scrollY
    //         if(bottomPassed) {
    //             element.classList.add('is-stuck');
    //             fillerElement.setAttribute('style', `disply:block; width: ${_element.width}px; height: ${_element.height}`);
    //             element.after(fillerElement);
    //         } else {
    //             element.classList.remove('is-stuck');
    //         }
    //     })
    // }

    // let timeout;
    // window.addEventListener("scroll", () => {
    //     if (timeout) {
    //         clearTimeout(timeout);
    //     }
    //     timeout = setTimeout(update, 150);
    // });
}

window.addEventListener('DOMContentLoaded', () => {
    registerCollapsibleContent();
    registerPopovers();
    setupActiveLinks();
    setupStickyElements();
});
