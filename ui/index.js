import tippy from 'tippy.js';


var popovers = document.querySelectorAll('a.popover');
popovers.forEach((element) => {
    console.log(element.children);
    var popoverContent;
    var i = 0;
    while (i < element.children.length && !popoverContent) {
        var childElement = element.children.item(i);
        if(childElement.tagName.toLowerCase() == 'span') {
            popoverContent = childElement.innerHTML;
        }
        i++
    }
    if(popoverContent) {
        tippy(element, {
            content: popoverContent,
            allowHTML: true
        });
    }
});

tippy('.example',{
    content: 'example'
});
