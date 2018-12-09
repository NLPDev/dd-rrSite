$(function() {

    $('input.payment_choices_checkbox').change(function() {

        var subtotal = 0.00;
        var due_date = '';

        $('input.payment_choices_checkbox:checked').each(function() {

            subtotal += parseFloat( $(this).parent().find('input.payment_choices_cost').val() );

            if(due_date == '' || $(this).parent().find('.payment_choices_due').html() < due_date) {
                due_date = $(this).parent().find('.payment_choices_due').html();
            }

        });

        $('#preview_subtotal').html(subtotal.toFixed(2));
        $('#preview_amount_due').html(subtotal.toFixed(2));
        $('#preview_due_by').html(due_date);

    });

    $('input.payment_choices_checkbox:first').change();

});