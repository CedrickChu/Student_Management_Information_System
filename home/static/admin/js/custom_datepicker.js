document.addEventListener('DOMContentLoaded', function() {
    (function($) {
        $(function() {
            $('.vDateField').datepicker({
                format: 'yyyy-mm-dd',
                autoclose: true,
                todayHighlight: true,
                orientation: "bottom auto",
                startView: 2,
                maxViewMode: 2,
                clearBtn: true
            });
        });
    })(django.jQuery);
});
