
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


window.addEventListener('DOMContentLoaded', () => {

    registerPopovers();

});


