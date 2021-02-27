
function save_highlight_content(highlightId) {
    console.log("Now save the content object that the highlight is a part of...", highlightId);
}

function remove_highlight(highlightId) {
    document.querySelectorAll(`[highlight-id="${highlightId}"]`).forEach(function(element){
        element.childNodes.forEach(function(childElement) {
            element.before(childElement);
        });
        element.remove();
    });
}

function highlight_text_as(highlightId, range) {
    var highlight = document.createElement('span');
    highlight.classList.add('highlight');
    highlight.setAttribute('highlight-id',highlightId);
    highlight.addEventListener("click", function(event) {
        event.preventDefault();
        remove_highlight(highlightId);
    });
    range.surroundContents(highlight);
}

function make_highlight(range) {
    var request = new XMLHttpRequest()
    request.responseType = 'json';
    var csrf_token = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    request.addEventListener("loadend", function(event) {
        console.log(request.responseType, request.response);
        if(request.response) {
            var highlightId = request.response['id'];
            highlight_text_as(highlightId, range);
            save_highlight_content(highlightId);
        }
    })
    request.open("POST", "/highlights");
    request.setRequestHeader('Content-type', 'application/json');
    request.setRequestHeader('X-CSRFToken', csrf_token);
    request.send();
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

    var highlightButton = document.createElement('button')
    highlightButton.innerText = 'Make a highlight'
    var boundingCoords = range.getBoundingClientRect();
    highlightButton.style = 'position:fixed;top:'+boundingCoords.top+'px;left:'+boundingCoords.right+'px;';
    var body = document.querySelector('body');
    body.appendChild(highlightButton);
    highlightButton.addEventListener('click', function() {
        highlightButton.remove();
        selection.collapseToEnd();
        make_highlight(range);
    });
}

export function setupHighligher() {
    document.addEventListener('selectionchange', debounceSelectionChange);
    document.addEventListener('keydown', function(event) {
        if (event.code.includes('Shift')) {
            selectionEnabled = true;
        } else {
            selectionEnabled = false;
        }
    });
    document.addEventListener('keyup', function(event) {
        selectionEnabled = false;
    });
}
