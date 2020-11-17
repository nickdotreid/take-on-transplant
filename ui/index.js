
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

window.addEventListener('DOMContentLoaded', () => {
    registerCollapsibleContent();
    registerPopovers();

});


