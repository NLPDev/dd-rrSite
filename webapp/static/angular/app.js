
var realclearApp = angular.module('realclear', ['ui.bootstrap', 'ngRoute', 'ngCookies', 'realclearControllers']);

// this allows our ajax requests to work with django by providing the security token
realclearApp.run(function($http, $cookies) {
    window.CSRF = $cookies.csrftoken;
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
});

// this allows us to insert html into the modal template
realclearApp.filter('unsafe', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
});

// when forms are loaded into the modal, this compiles them so we can access their values
realclearApp.directive('compileTemplate', function($compile, $parse){
    return {
        link: function(scope, element, attr){
            var parsed = $parse(attr.ngBindHtml);
            function getStringValue() { return (parsed(scope) || '').toString(); }
            //Recompile if the template changes
            scope.$watch(getStringValue, function() {
                $compile(element, null, -9999)(scope);  //The -9999 makes it skip directives so that we do not recompile ourselves
            });
        }
    }
});

// creates a jquery datepicker on any <div datepicker></div>
// stores value in a hidden input called #datepicker_value
realclearApp.directive('datepicker', function() {
   return function(scope, element, attrs) {
       element.datepicker({
           inline: true,
           dateFormat: 'yy-mm-dd',
           dayNamesMin: [ "S", "M", "T", "W", "T", "F", "S" ],
           minDate: 0, // cannot pick dates before today
           onSelect: function(dateText) {
               $(this).find('.datepicker_value').val(dateText);
               scope.refresh_times(dateText);
               scope.$apply();
           }
       });
       element.append('<input type="hidden" class="datepicker_value" name="datepicker_value" value="' + $.datepicker.formatDate('yy-mm-dd', new Date()) + '" />');
   }
});

// creates a calendar on any <div calendar></div>
realclearApp.directive('calendar', function($http, $timeout) {
   return function(scope, element, attrs) {
       element.datepicker({
           inline: true,
           dateFormat: 'yy-mm-dd',
           dayNamesMin: [ "S", "M", "T", "W", "T", "F", "S" ],
           onSelect: function(dateText, obj) {
               // ajax load the bottom section with the given day's events
               var calendar_details = $(this).find('.calendar_details').first();
               if($.inArray(dateText, scope.days_with_items) > -1) {
                   show_loading_icon_calendar(calendar_details);
                   $http.post(scope.item_details_url + dateText + '/').success(function (data) {
                       calendar_details.html(data);
                   }).error(function(data, status) {
                       calendar_details.html('Internal Server Error ' + status);
                   });
               } else {
                   calendar_details.html('');
               }
               scope.$apply();
           },
           beforeShowDay: function(date) {
               if(typeof scope.days_with_items == "undefined") {
                   return [true, '', ''];
               }
               // parse the dates
               var event_days = [];
               for(var i = 0; i < scope.days_with_items.length; i++) {
                   event_days.push( parseDate(scope.days_with_items[i]) );
               }
               // add classes to dates with items
               for(var i = 0; i < event_days.length; i++ ) {
                   if (date.getTime() == event_days[i].getTime()) {
                       return [true, 'has_event', ''];
                   }
               }
               return [true, '', ''];
           }
       });
       element.append('<div class="calendar_details"></div>');
       // this initializes the calendar to load today's details
       refresh_calendar($timeout);
   }
});

// opens the modal popup with parameters defined in the scope.
// scope can be populated with content (body html), defaults (for title, button text, and content)
// and key (of any kind, usually a primary or foreign key). all are optional
function open_modal($scope, $modal, controller) {

    var modalInstance = $modal.open({
        templateUrl: '/static/angular/modal.html',
        controller: controller,
        resolve: {
            defaults: function () {
                return $scope.defaults;
            },
            content: function () {
                return $scope.content;
            },
            key: function () {
                return $scope.key;
            }
        }
    });

    return modalInstance;
}


// opens a modal popup with an image filling the whole thing
function open_image_modal($scope, $modal) {

    var modalInstance = $modal.open({
        templateUrl: '/static/angular/image_modal.html',
        controller: 'ImageModalCtrl',
        windowClass: 'image-modal-window',
        resolve: {
            image_url: function () {
                return $scope.image_url;
            },
            image_list: function () {
                return $('#content-wrapper a.image-popup');
            }
        }
    });

    return modalInstance;
}

// fills in the modal template with its starting values
// and defines any functions needed by all modals
function init_modal($scope, $modalInstance, $http, $timeout, defaults, content) {

    $scope.title = 'Alert';
    $scope.button = 'OK';
    $scope.content = '';
    if(typeof defaults != "undefined") {
        if (typeof defaults.modal_title != "undefined") {
            $scope.title = defaults.modal_title;
        }
        if (typeof defaults.modal_button != "undefined") {
            $scope.button = defaults.modal_button;
        }
        if(typeof defaults.modal_content != "undefined") {
            $scope.content = defaults.modal_content;
        }
        if (typeof defaults.modal_title_position != "undefined") {
            $scope.title_position = defaults.modal_title_position;
        }
        if (typeof defaults.modal_button_position != "undefined") {
            $scope.button_position = defaults.modal_button_position;
        }
        if (typeof defaults.modal_text_position != "undefined") {
            $scope.text_position = defaults.modal_text_position;
        }
    }
    if(typeof content != "undefined"){
        $scope.content = content;
    }

    $scope.step = 0;
    $scope.sequence = [];

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.finish = function () {
        $modalInstance.close();
    };

    // main processor for all steps in the modal sequence
    $scope.ok = function () {
        if($scope.step < $scope.sequence.length) {

            // are we displaying a form, or processing a form, or showing a message?
            var form = $('.modal-body form:first');
            if(form.length > 0) {
                // we have a form, lets process it.
                // make extra sure to prevent double submissions
                if(form.data('submitted') !== true) {
                    form.data('submitted', true);
                    // if successful, will move the step forward. otherwise will display form with errors
                    $scope.process(form.serializeArray(), form, $timeout);
                }
            } else {
                // we need something to load, either a form or a message
                show_loading_icon($scope);
                $http.post($scope.sequence[$scope.step]).success(function (data) {
                    // allow steps to be optional
                    if (typeof data['skip_step'] != "undefined" && data['skip_step'] == true) {
                        $scope.step++;
                        $scope.ok();
                    }
                    // we have a form to display
                    else if (typeof data['form'] != "undefined") {
                        $scope.content = data['form'];
                    }
                    // we have a sophisticated message to display
                    else if (typeof data['content'] != "undefined") {
                        $scope.step++;
                        $scope.content = data['content'];
                        if (typeof data['title'] != "undefined") {
                            $scope.title = data['title'];
                        }
                        if (typeof data['button'] != "undefined") {
                            $scope.button = data['button'];
                        }
                        if (typeof data['title_position'] != "undefined") {
                            $scope.title_position = data['title_position'];
                        }
                        if (typeof data['button_position'] != "undefined") {
                            $scope.button_position = data['button_position'];
                        }
                        if (typeof data['text_position'] != "undefined") {
                            $scope.text_position = data['text_position'];
                        }
                    // we have a simple message to display
                    } else {
                        $scope.step++;
                        $scope.content = data;
                    }

                    $timeout(function() {
                        $('select').chosen({enable_split_word_search: true, search_contains: true});
                    }, 0, false);
                }).error(function(data, status) {
                    $scope.content = 'Internal Server Error ' + status;
                    $scope.sequence = []; // this will make the continue button close the modal
                });

            }
        } else {
            $scope.finish();
        }
    };

    // processes form submissions
    //  form_data should be serialized
    //  form is optional, should be a form DOM element. only needed in multi-step processes
    //  $timeout is optional. only needed when processing a form that contains a datepicker
    $scope.process = function (form_data, form, $timeout) {

        show_loading_icon($scope);
        var show_button_position = $scope.button_position;
        $scope.button_position = 'hide';

        // capture any image file this form might have. currently only one image per form is supported.
        var image_files = false;
        if (typeof form != "undefined") {
            image_file_inputs = form.find('input[name=image_file]');
            if (typeof image_file_inputs != "undefined") {
                image_files = [];
                image_file_inputs.each(function(i, elem){
                    var image_file = elem.files[0];
                    image_files.push(image_file);
                });
            }
        }

        //prepare multiselect fields to be merged correctly by toJson
        if($scope.has_multiselect) {
            form_data = $scope.multiselect_prep(form_data);
        }

        $http({
            method: 'POST',
            url: $scope.sequence[$scope.step],
            //IMPORTANT!!! You might think this should be set to 'multipart/form-data'
            // but this is not true because when we are sending up files the request
            // needs to include a 'boundary' parameter which identifies the boundary
            // name between parts in this multi-part request and setting the Content-type
            // manually will not set this boundary parameter. For whatever reason,
            // setting the Content-type to 'false' will force the request to automatically
            // populate the headers properly including the boundary parameter.
            headers: { 'Content-Type': undefined },
            //This method will allow us to change how the data is sent up to the server
            // for which we'll need to encapsulate the model data in 'FormData'
            transformRequest: function (data) {
                var formData = new FormData();
                //need to convert our json object to a string version of json otherwise
                // the browser will do a 'toString()' on the object which will result
                // in the value '[Object object]' on the server.
                formData.append("form_data", angular.toJson(data.form_data));
                //now add the assigned files
                if(data.photos) {
                    $.each(data.photos, function(i, elem){
                        var fieldname = "photo";
                        if(i > 0) {
                            fieldname += (i+1).toString();
                        }
                        // don't include the last, empty input
                        if(typeof elem != "undefined") {
                            formData.append(fieldname, elem);
                        }
                    });
                }
                return formData;
            },
            //Create an object that contains the model and files which will be transformed
            // in the above transformRequest method
            data: { form_data: form_data, photos: image_files }
        }).success(function (data) {
            // re-enable the modal continue button
            $scope.button_position = show_button_position;
            // all successful responses will have a success value set to true
            if(data['success']) {
                // it processed, go to the next step
                if (typeof form != "undefined") {
                    form.remove(); // important to make sure we don't process the form twice
                }
                $scope.step++;
                $scope.ok();
            } else {
                if(data['form'] != '') {
                    // errors in the form, redisplay it
                    $scope.content = data['form'];
                }
                else {
                    // if we aren't given back a form, display the errors in the modal
                    $scope.content = data['errors'];
                    $scope.sequence = []; // this will make the continue button close the modal
                }
                // datepicker refill
                if (typeof data['datepicker_refill'] != "undefined" && typeof $timeout != "undefined") {
                    datepicker_goto($scope, $timeout, data['datepicker_refill']);
                }
                // chosen rebinding
                if(typeof $timeout != "undefined") {
                    $timeout(function () {
                        $('select').chosen({enable_split_word_search: true, search_contains: true});
                    }, 0, false);
                }
            }
        }).error(function(data, status) {
            $scope.content = 'Internal Server Error ' + status;
            $scope.sequence = []; // this will make the continue button close the modal
        });
    };

    // redefine this in your modal controller if you need to do something when a date is clicked
    $scope.refresh_times = function (dateText) {}

}

function show_loading_icon($scope) {
    $scope.content = '<img src="/static/images/ajax-loader.gif" alt="loading.." />';
}

function show_loading_icon_calendar(div) {
    div.html('<img src="/static/images/ajax-loader.gif" alt="loading.." />');
}

// parse a date in yyyy-mm-dd format
function parseDate(input) {
  var parts = input.split('-');
  // new Date(year, month [, day [, hours[, minutes[, seconds[, ms]]]]])
  return new Date(parts[0], parts[1]-1, parts[2]); // Note: months are 0-based
}

// this updates the calendar after a data change. must be put inside timeout to avoid scope.$apply() errors
function refresh_calendar($timeout) {
    $timeout(function() {
        $('.hasDatepicker .ui-datepicker-current-day').click();
    }, 0, false);
}

function datepicker_goto($scope, $timeout, date_str) {
    $timeout(function() {
        $scope.$apply();
        $('div[datepicker]').datepicker("setDate", date_str);
        $('div[datepicker] input[name=datepicker_value]').val(date_str);
    }, 0, false);
}

realclearApp.factory('getCalendarItems', function($http) {
   return {
        getDays: function(ajax_url) {
             //return the promise directly.
             return $http.post(ajax_url)
                       .then(function(result) {
                            //resolve the promise as the data
                            return result.data;
                        });
        }
   }
});

// photo upload support functions
function triggerUpload(obj) {
    $(obj).parent().find('input[type=file]:first').click();
    return false;
}

function previewFile(obj) {
    if(obj.files && obj.files[0]) {

        // display filename
        var file = obj.value;
        var fileName = file.split("\\");
        $(obj).parent().find('.file-input').val(fileName[fileName.length - 1]);

        // display preview image
        var reader = new FileReader();
        reader.onload = function(e) {
            $(obj).parents('.image_upload').find('.image_preview').html('<img src="' + e.target.result + '" />').css('background-color', 'transparent');
        };
        reader.readAsDataURL(obj.files[0]);
    }
}

function addAnotherImageUpload(obj) {
    var last_upload_row = $(obj).parents('form:first').find('div.image_upload:last');
    var new_row = last_upload_row.clone(false);
    // remove any error messages from the new row
    new_row.find('ul.errorlist').remove();
    last_upload_row.after(new_row);
}


// properties managment
$(document).ready(function () {
    var removePropertyModal = $('#remove-property-modal');
    var removeModalCommunity = $('#modal-community');
    var infoModal = $('#info-modal');
    var removeModalLot = $('#modal-lot');
    var property_to_remove;
    var mail_regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;

    $('.rp-item .remove-btn').on('click', function (e) {
        var data = $(this).closest('.rp-item').data();
        removeModalCommunity.text(data.community);
        removeModalLot.text(data.lot);
        property_to_remove = data.id;
        removePropertyModal.modal('show');
    });

    removePropertyModal.find('button.confirm').on('click', function () {
        removeProperty(property_to_remove);
    });

    $('.rp-item .edit-btn').on('click', function (e) {
        var self = $(this);
        self.attr('disabled', true);
        var parent = self.closest('.rp-item');
        updatePropertyContact(
            parent.data().id, parent.find('input[type="text"]').val()
        );
    });
    $('.rp-item input[type="text"]').on('keyup', function (e) {
        if (mail_regex.test(this.value)) var disabled = false;
        else var disabled = true;
        $(this).closest('.rp-item').find('.edit-btn').attr('disabled', disabled);
    });

    function removeProperty(id) {
        $.ajax({
            url: '/account/ajax-release-property/',
            method: 'post',
            dataType: 'json',
            headers: {'X-CSRFToken': CSRF},
            data: { id: id }
        }).done(function (response) {
            console.log('property removed ', response);
            $('.rp-item[data-id="' + response.property + '"]').remove();
            removePropertyModal.modal('hide');
        });
    }

    function updatePropertyContact(id, contact) {
        $.ajax({
            url: '/account/ajax-update-property/',
            method: 'post',
            headers: {'X-CSRFToken': CSRF},
            dataType: 'json',
            data: { id: id, contact: contact }
        }).done(function (response) {
            infoModal.find('h4').text('Contact have been updated');
            infoModal.find('.modal-body').html(
                '<div>Lot number: ' + response.lot_number + '</div>' +
                '<div>New contact: ' + response.contact + '</div>'
            )
            infoModal.modal('show');
        });
    }
});
