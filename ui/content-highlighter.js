
function debounce(fn) {
    var timeout;
    return function() {
        if(timeout) clearTimeout(timeout);
        timeout = setTimeout(fn, 150);
    }
}

export class ContentHighlighter {

    #CSRF_TOKEN;

    constructor(csrfToken) {
        this.#CSRF_TOKEN = csrfToken;


        document.addEventListener('selectionchange', debounce(() => {
            this.selectionChange()
        }));
    }

    selectionChange() {
        if(this.highlightButton) this.highlightButton.remove();
        
        var selection = document.getSelection();
        var range = selection.getRangeAt(selection.rangeCount-1);    
        if (range.collapsed) return;
        
        if (!this.getNodeContentId(range.commonAncestorContainer)) return;

        this.highlightButton = this.createHighlightButton(range);
        this.highlightButton.addEventListener('click', () => {
            selection.collapseToEnd();
            this.createHighlight(range);
        });
    }

    getNodeContentId(node) {
        if(node.nodeName == '#text') {
            node = node.parentElement;
        }
        var content_container = this.getHighlightContentNode(node);
        if (content_container) {
            return content_container.getAttribute('content-id');
        } else {
            return false;
        }
    }

    getHighlightContentNode(highlightNode) {
        var content_container = highlightNode.closest('[content-id]');
        if (content_container) {
            return content_container;
        } else {
            return false;
        }
    }

    createHighlightButton(range) {
        var highlightButton = document.createElement('button');
        highlightButton.innerText = 'Make a highlight';
        var boundingCoords = range.getBoundingClientRect();
        highlightButton.style = 'position:fixed;top:'+boundingCoords.top+'px;left:'+boundingCoords.right+'px;';
        var body = document.querySelector('body');
        body.appendChild(highlightButton);
        return highlightButton
    }

    createHighlight(range) {
        var request = new XMLHttpRequest()
        request.responseType = 'json';
        request.addEventListener("loadend", () => {
            if(request.response) {
                var highlightId = request.response['id'];
                this.highlightRangeAs(range, highlightId);
                this.updateHighlightContent(highlightId);
            }
        })
        request.open("POST", "/highlights");
        request.setRequestHeader('Content-type', 'application/json');
        request.setRequestHeader('X-CSRFToken', this.#CSRF_TOKEN);
        request.send();
    }

    updateHighlightContent(highlightId) {
        var highlight = document.querySelector(`[highlight-id="${highlightId}"]`);
        var content_container = this.getHighlightContentNode(highlight);
        
        if (!highlight || !content_container) return;

        var request = new XMLHttpRequest();
        request.responseType = 'json';
        request.open("POST", `/highlights/${highlightId}`);
        request.setRequestHeader('content-type', 'application/json');
        request.setRequestHeader('X-CSRFToken', this.#CSRF_TOKEN);
        request.send(JSON.stringify({
            'text': highlight.innerText,
            'contentId': content_container.getAttribute('content-id'),
            'content': content_container.innerHTML
        }));
    }

    remove_highlight(highlightId) {
        document.querySelectorAll(`[highlight-id="${highlightId}"]`).forEach(function(element){
            element.childNodes.forEach(function(childElement) {
                element.before(childElement);
            });
            element.remove();
        });
    }

    highlightRangeAs(range, highlightId) {
        var highlight = document.createElement('span');
        highlight.classList.add('highlight');
        highlight.setAttribute('highlight-id',highlightId);
        highlight.addEventListener("click", function(event) {
            event.preventDefault();
            remove_highlight(highlightId);
        });
        range.surroundContents(highlight);
    }

}
