import Sticky from 'sticky-js'
import tippy, {followCursor, hideAll} from 'tippy.js';

function registerPopovers() {
    document.querySelectorAll('[data-toggle="popover"]').forEach((element) => {
        let content = element.getAttribute('data-content');
        let resource;
        const resource_id = element.getAttribute('resource-id');
        if(resource_id) {
            resource = document.getElementById(`resource-${resource_id}`);
            if (resource) {
                content = resource.innerHTML;
            }
        }
        if (content) {
            const popover_target = document.createElement('span');
            popover_target.classList.add('popover-target');
            element.appendChild(popover_target);
            const _tippy = tippy(popover_target, {
                allowHTML: true,
                appendTo: document.body,
                content: content,
                interactive: true,
                trigger: 'mouseenter focus click',
                plugins: [followCursor],
                onShow: (instance) => {
                    hideAll({exclude: instance});
                },
                onShown: (instance) => {
                    const popper = instance.popper;
                    const resourceContent = popper.querySelector('.resource-content');
                    const tippyContent = popper.querySelector('.tippy-content');
                    const popoverReadMore = popper.querySelector('.popover-read-more');
                    if (!popoverReadMore && resourceContent.offsetHeight > tippyContent.offsetHeight) {
                        const readMoreLink = document.createElement('a');
                        readMoreLink.text = 'Read more';
                        readMoreLink.classList.add('popover-read-more');
                        readMoreLink.setAttribute('href', '#resource-'+resource_id);
                        tippyContent.appendChild(readMoreLink);
                    }
                }
            });
            element.addEventListener('click', (event) => {
                event.preventDefault();
                _tippy.show();
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

function addResourceModal(resource_id) {
    hideAll();
    const resource = document.getElementById('resource-' + resource_id);
    const modal = document.createElement('div');
    modal.classList.add('modal');
    const modal_close = document.createElement('a');
    modal_close.classList.add('modal-close');
    modal_close.setAttribute('href', '#');
    modal_close.text = 'Close';
    // modal_close.click((event) => {
    //     event.preventDefault();
    //     modal.remove();
    // });
    modal.appendChild(modal_close);
    const modal_content = document.createElement('div');
    modal_content.classList.add('modal-content');
    modal_content.innerHTML = resource.innerHTML;
    modal.appendChild(modal_content);
    document.body.appendChild(modal);
}

function updateFromHash() {
    document.querySelectorAll('.modal').forEach((element) => {
        element.remove();
    });
    const hash = location.hash.toLocaleLowerCase();
    if(hash.includes('resource-')) {
        const resource_id = hash.split('resource-')[1];
        addResourceModal(resource_id);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    registerCollapsibleContent();
    registerPopovers();
    setupStickyElements();
    setupActiveLinks();
    window.addEventListener('hashchange', function(event) {
        event.preventDefault();
        updateFromHash();
    });
    updateFromHash();
});
