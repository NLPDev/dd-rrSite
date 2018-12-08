$(function() {

    $('.tag_filter li a').click(function(e) {
        e.preventDefault();
        // set active class on this li element
        $(this).parents('.tag_filter').find('li').removeClass('active');
        $(this).parent('li').addClass('active');
        // hide and show announcements from tag_id
        var tag_id = $(this).parent('li').attr('tag_id');
        if(tag_id == 'all') {
            $('.section-copy div.can_tag_filter').slideDown();
        } else {
            $('.section-copy div.can_tag_filter').each(function () {
                if ($(this).hasClass('tag_' + tag_id)) {
                    $(this).slideDown();
                } else {
                    $(this).slideUp();
                }
            });
        }
    });


});