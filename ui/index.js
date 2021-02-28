import tippy, {followCursor, hideAll} from 'tippy.js';
import Sortable from 'sortablejs';
import {ContentHighlighter} from './content-highlighter.js'

function registerPopovers() {
    document.querySelectorAll('[data-toggle="popover"]').forEach((element) => {
        let content = element.getAttribute('data-content');
        if (content) {
            const _tippy = tippy(element, {
                allowHTML: true,
                appendTo: document.body,
                content: content,
                interactive: true,
                trigger: 'mouseenter focus click',
                followCursor: 'initial',
                plugins: [followCursor],
                onShow: (instance) => {
                    hideAll({exclude: instance});
                }
            });
            element.addEventListener('click', (event) => {
                event.preventDefault();
                _tippy.show();
            });
        }
    });
}

function setupActiveLinks() {

    const navLinks = document.querySelectorAll('.sidebar a');

    function update() {
        navLinks.forEach((link) => {
            if (!link.hash || link.hash=='') return;
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

function makeSortableLists() {
    document.querySelectorAll('.sortable').forEach(function(element) {
        new Sortable(element);
    });
}

window.addEventListener('DOMContentLoaded', () => {
    registerPopovers();
    setupActiveLinks();
    makeSortableLists();

    if(document.querySelector("input[name='csrfmiddlewaretoken']")) {
        var csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
        new ContentHighlighter(csrfToken);
    }

});
