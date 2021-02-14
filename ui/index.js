import Sticky from 'sticky-js'
import tippy, {followCursor, hideAll} from 'tippy.js';
import Sortable from 'sortablejs';

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

}

var selectionChangeDebounced;
function debounceSelectionChange() {
    if (selectionChangeDebounced) {
        clearTimeout(selectionChangeDebounced);
    }
    selectionChangeDebounced = setTimeout(selectionChange, 1000);
}

var selectionEnabled = false;
function selectionChange() {
    var selection = document.getSelection();
    console.log(selection.rangeCount);
    var range = selection.getRangeAt(selection.rangeCount-1);

    if (range.collapsed || !selectionEnabled) {
        return;
    }
    selection.collapseToEnd();

    if (range.startContainer == range.endContainer) {
        console.log('same container');
        var previous_text = range.startContainer.textContent.slice(0, range.startOffset);
        var selected_text = range.startContainer.textContent.slice(range.startOffset, range.endOffset);
        var after_text = range.startContainer.textContent.slice(range.endOffset);
        
        selection = document.createElement('span');
        selection.style="font-weight:bold;"
        selection.textContent = selected_text;
        
        range.startContainer.textContent = previous_text;
        range.startContainer.after(selection);

        if (after_text !== "") {
            selection.after(after_text);
        }
    } else {
        // split start element
        var previous_text = range.startContainer.textContent.slice(0, range.startOffset);
        var selected_text = range.startContainer.textContent.slice(range.startOffset);
        range.startContainer.textContent = previous_text;
        var selection_element = document.createElement('span');
        selection_element.textContent = selected_text;
        selection_element.style="font-weight:bold;"
        range.startContainer.after(selection_element);
        // split end element
        selected_text = range.endContainer.textContent.slice(0,range.endOffset);
        after_text = range.endContainer.textContent.slice(range.endOffset);
        selection_element = document.createElement('span');
        
        selection_element.textContent = selected_text;
        selection_element.style="font-weight: bold;";
        range.endContainer.before(selection_element);
        range.endContainer.textContent = after_text;
    }
}

function setupTexthighligher() {
    document.addEventListener('selectionchange', debounceSelectionChange);
    document.addEventListener('keydown', function(event) {
        console.log(event.code);
        if (event.code.includes('Shift')) {
            console.log("shift down?")
            selectionEnabled = true;
        } else {
            console.log("not down;");
            selectionEnabled = false;
        }
    });
    document.addEventListener('keyup', function(event) {
        selectionEnabled = false;
    });
}

function makeSortableLists() {
    console.log('hi')
    document.querySelectorAll('.sortable').forEach(function(element) {
        new Sortable(element);
        console.log('sort me!');
    })
}

window.addEventListener('DOMContentLoaded', () => {
    registerPopovers();
    // setupStickyElements();
    setupActiveLinks();
    setupTexthighligher();
    makeSortableLists();
});
