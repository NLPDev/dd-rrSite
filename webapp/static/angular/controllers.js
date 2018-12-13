
var realclearControllers = angular.module('realclearControllers', []);

/* GENERAL IMAGE POPUP */

realclearControllers.controller('ImageModalCtrl', ['$scope', '$modalInstance', 'image_url', 'image_list', function ($scope, $modalInstance, image_url, image_list) {

    $scope.modalImageUrl = image_url;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.next = function(){
        next_image = '';
        image_list.each(function(i, elem) {
            var path = $scope.get_clean_path( $(elem).attr('ng-click') );
            if(next_image == '' && i >= image_list.length - 1) {
                next_image = $scope.get_clean_path( $(image_list[0]).attr('ng-click') );
            }
            else if(path == $scope.modalImageUrl) {
                next_image = $scope.get_clean_path( $(image_list[i+1]).attr('ng-click') );
            }
        });
        $scope.modalImageUrl = next_image;
    };

    $scope.get_clean_path = function(href) {
        href = href.replace("open('", "");
        href = href.replace("')", "");
        return href;
    }

}]);

/* COMMON AREAS RESERVATIONS */

realclearControllers.controller('ReservationCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.open = function(key){
        $scope.key = key;
        $scope.defaults = {modal_title: 'Reserve Common Area', modal_button: 'Continue'};
        open_modal($scope, $modal, 'ReservationModalCtrl');
    };

}]);

realclearControllers.controller('ReservationModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', 'key', function ($scope, $modalInstance, $http, $timeout, defaults, content, key) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // the ajax urls for each step in the process
    $scope.sequence = ['/common-areas/ajax-related-services/' + key + '/',
        '/common-areas/ajax-reservation-form/' + key + '/',
        '/common-areas/ajax-reservation-payment/',
        '/common-areas/ajax-reservation-success/'];

    // load the first step
    $scope.ok();

    // after success, reload the page so their new reservations show
    $scope.finish = function () {
        location.reload();
        $modalInstance.close();
    };

    $scope.refresh_times = function (dateText) {

        var time_fields = ['start_time', 'end_time'];

        time_fields.forEach(function (field, i) {

            $('label[for=id_'+field+']').after('<img src="/static/images/ajax-loader.gif" class="time_loading_icon" alt="loading.." style="margin:0 0 5px 10px;" />');

            $http({
                method: 'POST',
                url: '/common-areas/ajax-datepicker-times/',
                data: {services:$('#reservation_form #services_str').val(), field:field, date:dateText}
            }).success(function (data) {

                var select_html = $.parseHTML(data.select_html);
                var select_elem = $('#reservation_form #id_'+field);
                select_elem.empty();
                $(select_html).find('option').each(function(i, elem){
                    select_elem.append(elem);
                });
                select_elem.trigger("chosen:updated");

                $('img.time_loading_icon').remove();

            }).error(function(data, status) {
                $scope.content = 'Internal Server Error ' + status;
                $scope.sequence = []; // this will make the continue button close the modal
                $('img.time_loading_icon').remove();
            });

        });
    }

}]);

realclearControllers.controller('CommonAreaScheduleCtrl', ['$scope', '$timeout', 'getCalendarItems', function ($scope, $timeout, getCalendarItems) {

    getCalendarItems.getDays('/common-areas/ajax-calendar-days/').then(function(days) {
        $scope.days_with_items = days;
        // this updates the calendar once the days data is loaded
        refresh_calendar($timeout);
    });

    $scope.item_details_url = '/common-areas/ajax-calendar-items/';

}]);

/* VIOLATIONS */

realclearControllers.controller('ViolationCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.process = function(){
        $scope.defaults = {modal_title: 'Report Violation', modal_button: 'Continue'};
        open_modal($scope, $modal, 'ViolationModalCtrl');
    };

}]);

realclearControllers.controller('ViolationModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', function ($scope, $modalInstance, $http, $timeout, defaults, content) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // the ajax urls for each step in the process
    $scope.sequence = ['/violations/ajax-report/',
        '/violations/ajax-report-success/'];

    // process the data in the form
    var form = $('#ng-app form:first');
    // prevent double submissions
    if(form.data('submitted') !== true) {
        form.data('submitted', true);
        $scope.process(form.serializeArray());
    } else {
        $scope.content = 'Warning: double submission prevented.';
        $scope.sequence = [];
    }

    // after success, clear out the form
    $scope.finish = function () {
        form.data('submitted', false);
        if($scope.sequence.length > 0) {
            $('#violation_form input, #violation_form select, #violation_form textarea').val('').trigger("chosen:updated");
            $('#violation_form input[type=checkbox]').attr('checked', false);
        }
        $modalInstance.close();
    };

}]);

/* COMMUNITY CALENDAR OF EVENTS */

realclearControllers.controller('CommunityCalendarCtrl', ['$scope', '$modal', '$timeout', 'getCalendarItems', function ($scope, $modal, $timeout, getCalendarItems) {

    $scope.open = function(){
        $scope.defaults = {modal_title: 'Add Event', modal_button: 'Add Event'};
        open_modal($scope, $modal, 'CommunityCalendarModalCtrl');
    };

    getCalendarItems.getDays('/community/ajax-calendar-days/').then(function(days) {
        $scope.days_with_items = days;
        // this updates the calendar once the days data is loaded
        refresh_calendar($timeout);
    });

    $scope.item_details_url = '/community/ajax-calendar-items/';

}]);

realclearControllers.controller('CommunityCalendarModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', function ($scope, $modalInstance, $http, $timeout, defaults, content) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // the ajax urls for each step in the process
    $scope.sequence = ['/community/ajax-add-calendar-event/',
        '/community/ajax-calendar-event-success/'];

    // load the first step
    $scope.ok();

}]);

realclearControllers.controller('CalendarEventDetailsCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.open = function(image_url){
        $scope.image_url = image_url;
        open_image_modal($scope, $modal);
    };

}]);

/* ANNOUNCEMENTS */

realclearControllers.controller('AnnouncementCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.open = function(){
        $scope.defaults = {modal_title: 'Add Announcement', modal_button: 'Add Announcement'};
        open_modal($scope, $modal, 'AnnouncementModalCtrl');
    };

}]);

realclearControllers.controller('AnnouncementModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', function ($scope, $modalInstance, $http, $timeout, defaults, content) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // the ajax urls for each step in the process
    $scope.sequence = ['/announcements/ajax-add-announcement/',
        '/announcements/ajax-announcement-success/'];

    // load the first step
    $scope.ok();

}]);

realclearControllers.controller('AnnouncementListCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.open = function(image_url){
        $scope.image_url = image_url;
        open_image_modal($scope, $modal);
    };

}]);

realclearControllers.controller('AnnouncementDetailsCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.open = function(image_url){
        $scope.image_url = image_url;
        open_image_modal($scope, $modal);
    };

}]);

/* SERVICE PROVIDERS */

realclearControllers.controller('ServiceProviderCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.open = function(){
        $scope.defaults = {modal_title: 'Add Service', modal_button: 'Add Service'};
        open_modal($scope, $modal, 'ServiceProviderModalCtrl');
    };

}]);

realclearControllers.controller('ServiceProviderModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', function ($scope, $modalInstance, $http, $timeout, defaults, content) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // the ajax urls for each step in the process
    $scope.sequence = ['/service-providers/ajax-add-provider/',
        '/service-providers/ajax-add-provider-success/'];

    // load the first step
    $scope.ok();

}]);


/* PAYMENTS */

realclearControllers.controller('PaymentCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.process = function(){
        $scope.defaults = {modal_title: 'Make Payment', modal_button: 'Continue'};
        open_modal($scope, $modal, 'PaymentModalCtrl');
    };

}]);

realclearControllers.controller('PaymentModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', function ($scope, $modalInstance, $http, $timeout, defaults, content) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // this is used to convert our multiple choice - multiple objects into a single combined object.
    // became required once transformRequest was implemented for image uploads.
    $scope.multiselect_prep = function (form_data) {
        var dues_merged_data = [];
        var violations_merged_data = [];
        for(var i = 0; i < form_data.length; i++) {
            var obj = form_data[i];
            if(obj.name == 'dues') {
                dues_merged_data.push(obj.value);
                form_data.splice(i, 1);
                i--;
            }
            if(obj.name == 'violations') {
                violations_merged_data.push(obj.value);
                form_data.splice(i, 1);
                i--;
            }
        }
        if(dues_merged_data.length > 0) {
            form_data.push({'name':'dues', 'value':dues_merged_data});
        }
        if(violations_merged_data.length > 0) {
            form_data.push({'name':'violations', 'value':violations_merged_data});
        }

        return form_data;
    };

    // the ajax urls for each step in the process
    $scope.sequence = ['/account/ajax-payment/',
        '/account/ajax-payment-success/'];

    // process the data in the form
    var form = $('#payments_form');
    $scope.has_multiselect = true;
    // prevent double submissions
    if(form.data('submitted') !== true) {
        form.data('submitted', true);
        $scope.process(form.serializeArray());
    } else {
        $scope.content = 'Warning: double submission prevented.';
        $scope.sequence = [];
    }

    // after success, redirect to account page
    $scope.finish = function () {
        form.data('submitted', false);
        if($scope.sequence.length > 0) {
            document.location = '/account/';
        }
        $modalInstance.close();
    };

}]);


/* MANAGE ACCOUNT */

realclearControllers.controller('AccountCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.process = function(){
        $scope.defaults = {modal_title: 'Manage Account', modal_button: 'Continue'};
        open_modal($scope, $modal, 'AccountModalCtrl');
    };

}]);

realclearControllers.controller('AccountModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', function ($scope, $modalInstance, $http, $timeout, defaults, content) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // the ajax urls for each step in the process
    $scope.sequence = ['/account/ajax-manage-account/',
        '/account/ajax-manage-account-success/'];

    // process the data in the form
    var form = $('#ng-app form:first');
    // prevent double submissions
    if(form.data('submitted') !== true) {
        form.data('submitted', true);
        $scope.process(form.serializeArray());
    } else {
        $scope.content = 'Warning: double submission prevented.';
        $scope.sequence = [];
    }


    $scope.finish = function () {
        form.data('submitted', false);
        $modalInstance.close();
    };

}]);

realclearControllers.controller('AccountItemsCtrl', ['$scope', '$modal', function ($scope, $modal) {

    $scope.cancel = function(model, id){
        $scope.key = model + '_' + id;
        $scope.defaults = {modal_title: 'Cancel ' + model, modal_button: 'Confirm'};
        open_modal($scope, $modal, 'AccountItemsModalCtrl');
    };

}]);

realclearControllers.controller('AccountItemsModalCtrl', ['$scope', '$modalInstance', '$http', '$timeout', 'defaults', 'content', 'key', function ($scope, $modalInstance, $http, $timeout, defaults, content, key) {

    init_modal($scope, $modalInstance, $http, $timeout, defaults, content);

    // the ajax urls for each step in the process
    $scope.sequence = ['/account/ajax-cancel-item/'+key+'/',
        '/account/ajax-cancel-item-success/'];

    // load the first step
    $scope.ok();

    // after success, reload the page so their cancelled items are removed
    $scope.finish = function () {
        location.reload();
        $modalInstance.close();
    };

}]);