
import $ from 'jquery';
import 'bootstrap/js/src/collapse';
import 'bootstrap/js/src/popover';

$('[data-toggle="popover"]').popover({
    position: 'top',
    trigger: 'click hover'
});
