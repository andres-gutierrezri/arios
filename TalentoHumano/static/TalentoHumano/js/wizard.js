'use strict';

$(document).ready(function()
            {

                // Smart Wizard
                $('#smartwizard').smartWizard(
                {
                    selected: 0, // Initial selected step, 0 = first step
                    keyNavigation: true, // Enable/Disable keyboard navigation(left and right keys are used if enabled)
                    autoAdjustHeight: false, // Automatically adjust content height
                    cycleSteps: false, // Allows to cycle the navigation of steps
                    backButtonSupport: true, // Enable the back button support
                    useURLhash: false, // Enable selection of the step based on url hash
                    showStepURLhash: false,
                    lang:
                    { // Language variables
                        next: 'Siguiente',
                        previous: 'Anterior'
                    },
                    toolbarSettings:
                    {
                        toolbarPosition: 'bottom', // none, top, bottom, both
                        toolbarButtonPosition: 'right', // left, right
                        showNextButton: true, // show/hide a Next button
                        showPreviousButton: true, // show/hide a Previous button
                        /*toolbarExtraButtons: [
				$('<button></button>').text('Finish')
							  .addClass('btn btn-info')
							  .on('click', function(){
							alert('Finsih button click');
							  }),
				$('<button></button>').text('Cancel')
							  .addClass('btn btn-danger')
							  .on('click', function(){
							alert('Cancel button click');
							  })
						  ]*/
                    },
                    anchorSettings:
                    {
                        anchorClickable: true, // Enable/Disable anchor navigation
                        enableAllAnchors: false, // Activates all anchors clickable all times
                        markDoneStep: true, // add done css
                        enableAnchorOnDoneStep: true // Enable/Disable the done steps navigation
                    },
                    contentURL: null, // content url, Enables Ajax content loading. can set as data data-content-url on anchor
                    contentCache: true, //ajax content
                    disabledSteps: [], // Array Steps disabled
                    errorSteps: [], // Highlight step with errors
                    theme: 'default', //dots, default, circles
                    transitionEffect: 'slide', // Effect on navigation, none/slide/fade
                    transitionSpeed: '400'
                });




            });