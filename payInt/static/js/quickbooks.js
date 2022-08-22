// JavaScript Document

$(document).ready(function(){
	
	//////////////////////////////////////////////////////////////////////////////////////////////
	//
	// js for log in page
	//
		$('.password-reset').click(function() {
			$('.form-content').html('<form id="reset-pass-form" name="resetPass" action="" method="post"><input id="email1" type="text" name="email1" value="" maxlength="255" placeholder="Enter Account Email"/><input id="email2" type="text" name="email2" placeholder="Re-enter Email" maxlength="255"/><input type="submit" name="submit" value="Send Reset Password Email"/></form>');
			$('#form-container h3').html('Reset Password');
			$('.error-msg').fadeOut(500);
			$('#reset-div').slideToggle(500);
		});
		$('.exit').click(function() {
			$('#form-container h3').html('Log in');
			$('#reset-div').slideToggle(500);
		});
		
		$('.form-content').on('submit','#reset-pass-form',function(event) {
			
			var email1 = $('#email1').val();
			var email2 = $('#email2').val();
			
			var atpos_1 = email1.indexOf("@");
			var dotpos_1 = email1.lastIndexOf(".");
			var atpos_2 = email2.indexOf("@");
			var dotpos_2 = email2.lastIndexOf(".");
			
			if (atpos_1 < 1 || dotpos_1 < atpos_1+2 || dotpos_1+2 >= email1.length) {
				//Not a valid email address
				event.preventDefault();
				alert('Whoops. Both fields need valid email addresses. Try again.');
			} else if (atpos_2 < 1 || dotpos_2 < atpos_2+2 || dotpos_2+2 >= email2.length) {
				// Not a valid email address
				event.preventDefault();
				alert('Whoops. Both fields need valid email addresses. Try again.');
			} else {
				if (email1 != email2) { // make sure emails match
					event.preventDefault();
					alert('Whoops, looks like these emails don\'t match.');
				} else { // emails are equal
				
					// start spinner
					$(this).append('<img class="spinner" src="resources/images/spinner_square.gif">');
					
					// make ajax call to reset pass in database and send email with reset link
					data = $('#reset-pass-form').serialize();
					$.ajax({
						url: 'resources/interface-scripts/reset_email_handler.php',
						type: 'POST',
						data: data,
						dataType: 'json',
						async: false,
						success: function(data) {
							//stop spinner
							$('.spinner').hide(500);
							
								event.preventDefault();
								if (data[1] === true) {
									$('.error-msg').html(data[0]).fadeIn(500);
								} else {
									$('.error-msg').fadeOut(500);
									$('.form-content').html(data[0]);
								}
							},
						error: function(jqXHR, textStatus, errorThrown) {
							event.preventDefault();
							//stop spinner
							$('.spinner').hide(500);
							}
					});
				}
			}
		});
	//
	// END log in page
	//
	/////////////////////////////////////////////////////////////////////////////////////////////////////////////

		$('#software-interface').on('click', '.check-files', function(event){ // checks for presence of all three files. allows to proceed.
			event.preventDefault();
			$.ajax({
					url: 'resources/interface-scripts/check_files_exist.php',
					type: 'POST',
					data: 'check',
					async: false,
					dataType: 'json',
					success: function(data) {
						// success: allow submission of form
							if (data[0] === true && data[1] === true && data[2] === true) {
								$('#progress-form-next').submit();	
							} else {
								if(data[0] === true) { timerlist = ''; } else { timerlist = 'Timer Lists,'; }
								if(data[1] === true) { payroll = ''; } else { payroll = 'Payroll Items,'; }
								if(data[2] === true) { employee = ''; } else { employee = 'Employee List'; }
								msg = "You need to upload the following: "
								+ timerlist + " "
								+ payroll + " "
								+ employee;
								alert(msg);
							}
						},
					error: function(jqXHR, textStatus, errorThrown) {
						}
					});
		})

		$('#software-interface').on('click', '#save', function(event){ // moves through the set-up process
					event.preventDefault();
					
					if ($('#next').hasClass('dim')) {
						$('#next').removeClass('dim')
						$('#save').removeClass('confirm_changes');
					}
					
					$(this).after('<img class="spinner" src="resources/images/spinner_square.gif">');
					
					// if this form attr payroll-items then else... change the data var and url var
					
					var testvar = $(this).attr('form');
					if ( testvar == 'match-employee-names-form' ) {
						data = $('#match-employee-names-form').serialize();;
						url = 'resources/interface-scripts/match_names_script.php';
					} else {
						data = $('#payroll-items-form').serialize();
						url = 'resources/interface-scripts/pitems_array_script.php';
					}
					
					$.ajax({
					url: url,
					type: 'POST',
					data: data,
					dataType: 'json',
					success: function(data) {
							// call stop spinner function
							if ( testvar == 'match-employee-names-form' ) {
								
								if ( data == "submit" ) {
									$('#progress-form-next').append('<input type="hidden" name="db-update" value="name-matching" />');
									$('#progress-form-next').submit();
								}
								else
								{
									$('#post-self').append('<input type="hidden" name="db-update" value="name-matching" />');
									$('#post-self').submit();
								}
							} else {
								$('#progress-form-next').append('<input type="hidden" name="db-update" value="payroll-items" />');
								$('#next').removeClass('halt');
							}
							$('.spinner').hide(500);
						},
					error: function(jqXHR, textStatus, errorThrown) {
							// call stop spinner function
							$('.spinner').hide(500);
						}
					});
			});
			
			$('#software-interface').on('click', '#next', function(event){ // accounts for IE not allowing buttons outside of form
				// Need to account for all the things that is supposed to keep this from firing
				var test = $(this).hasClass('halt');
				if (test) {
					event.preventDefault();
				} else {
					$('#progress-form-next').submit();	
				}
			})
			
			$('#software-interface').on('click', '#back', function(event){ // accounts for IE not allowing buttons outside of form
			
				$('#progress-form-back').submit();
			})
			
			$('#software-interface').on('click', '#files', function(event){ // accounts for IE not allowing buttons outside of form
			
				$('#progress-form-files').submit();
			})
			
			$('#software-interface').on('click', '#items', function(event){ // accounts for IE not allowing buttons outside of form
			
				$('#progress-form-items').submit();
			})
			
			$('#software-interface').on('click', '#names', function(event){ // accounts for IE not allowing buttons outside of form
			
				$('#progress-form-names').submit();
			})

			
			$('#software-interface').on('change', '.action-hook', function(event) { // ajax upload and validate files
				
				files = event.target.files;
				var ref = $(this);
				// GIF SPINNER START
				$(this).before('<img class="spinner" src="resources/images/spinner_square.gif">');
				
				// upload files
				
				var fileType = $(this).attr('name');
				var data = new FormData();
				$.each(files, function(key, value)
				{
					data.append(key, value);
				});
				
				$.ajax({
					url: 'resources/interface-scripts/file_upload.php?files&filetype=' + fileType,
					type: 'POST',
					data: data,
					cache: false,
					dataType: 'json',
					processData: false,
					contentType: false, 
					success: function(data) {
							if (data != 'success') {
								alert(data);
								$(ref).parent('li').children('.msg').addClass('error-msg')
								.removeClass('success-msg')
								.html('failed');
							} else {
								$(ref).parent('li').children('.msg').addClass('success-msg')
								.removeClass('error-msg')
								.html('success');
							}
							// call stop spinner function
							$('.spinner').hide(500);
						},
					error: function(jqXHR, textStatus, errorThrown) {
							// call stop spinner function
							alert(jqXHR + ' | ' + textStatus + ' | ' + errorThrown);
							$('.spinner').hide(500);
						}
				});
				
			});
			
			$('#software-interface').on('change', '#extract', function(event) { // ajax upload and validate files
					upload = event.target.files;
					
					// upload files
					var data = new FormData();
					$.each(upload, function(key, value)
					{
						data.append(key, value);
					});
					
					// *******************************************************************************************
					// step 1 - validate/save file ***************************************************************
						$.ajax({
						url: 'resources/interface-scripts/validate_extract.php?upload',
						type: 'POST',
						data: data,
						cache: false,
						dataType: 'json',
						async: false,
						processData: false,
						contentType: false, 
						success: function(data) {
								if (data['error'] == '') {
									$('#uploaded-file-name').html("Uploaded: " + data['name'] + "<br>" + data['date']);
									
										$('#validation-msg').text(data['validate_msg']);
										
										// call stop spinner function
										$('.spinner').hide(500);
										
										// if need to match employee names
										if (data['flag_name_matching'] === true) {
											$('#progress-form-names').submit();
										} else {
											// add message to box
											$('#match-names-msg').text(data['matching_msg']);
											$('#download-import').addClass('disabled');
											$('#download-import').attr('disabled', 'disabled');	
										}
										
										if (data["status"] === true && data['flag_name_matching'] === false) {
											// allow generation of report
											$('#create-import').removeClass('disabled').addClass('glow');
											$('#create-import').removeAttr('disabled');	
										}
								}
								else
								{
									alert(data['error']);	
								}
							},
						error: function(jqXHR, textStatus, errorThrown) {
								// call stop spinner function
								$('.spinner').hide(500);
							}
						});
						
					// *******************************************************************************************
					// END
			});
			
			$('#software-interface').on('click', '#create-import', function(event) {
				event.preventDefault(); // stop form from submitting
			
					// GIF SPINNER START
					$(this).after('<img class="spinner" src="resources/images/spinner_square.gif">');
					
					data = "run";
					
					$.ajax({
						url: 'resources/interface-scripts/qb_script.php',
						type: 'POST',
						data: data,
						cache: false,
						dataType: 'json',
						async: false,
						processData: false,
						contentType: false, 
						success: function(data) {
							if (data[2] == '') {
								$('#download-import').removeClass('disabled').addClass('glow');
								$('#download-import').removeAttr('disabled');
								$('#create-import').removeClass('glow')
								$('#download-form').attr('action',data[0]);
							} else {
								// show msg box and require matching of payroll items
								$('.msg-container-div').prepend(data[2]);
								$('#msg-box, .msg-container-div').fadeIn("slow");
								$('#confirm-btn').attr('value','payrollitems');
							}
								// call stop spinner function
								$('.spinner').hide(500);
							},
						error: function(jqXHR, textStatus, errorThrown) {
								// call stop spinner function
								$('.spinner').hide(500);
							}
					});
			});
			
			/***********************************************************************************
			/*
			/**/
			
			$('#software-interface').on('click', '#helper-link-1', function(event) {
				event.preventDefault();
				$('#helper-div-1').fadeToggle(1000);
			});
			$('#software-interface').on('click', '.close-btn', function(event) {
				event.preventDefault();
				$('#helper-div-1').fadeToggle(1000);
			});
			
			/*
			/*
			*//////////////////////////////////////////////////////////////////////////////////
			
			$('#software-interface').on('click', '#confirm-btn', function() {
			
				if ($('#confirm-btn').val() == "payrollitems") {
					$('#msg-box, .msg-container-div').fadeOut("slow");
					$('#progress-form-items').submit();
					
				} else if ($('#confirm-btn').val() == "choose-software") {
					
					var software = $('input[name=software]:checked').val();
					
					if (software == 'QuickBooks' || software == 'ADP' || software == 'Paychex' || software == 'Sage') {
//						if (software == 'QuickBooks') {
//							$.ajax({
//							})
//						}
						$('#msg-box, .msg-container-div, #grey-filter').fadeOut("slow");
						$('#choose-software-form').submit();
					}
				} else if ($('#confirm-btn').val() == "update-setup-complete") {
					 $.ajax({
						
						url: 'resources/interface-scripts/setup_complete_script',
						data: {"data":"update"},
						method: 'post',
						dataType: "json",
						success: function(data) {},
						failure: function() {},
						
					 })
					 $('#msg-box, .msg-container-div, #grey-filter').fadeOut("slow");
				}
				else {
					$('#msg-box, .msg-container-div, #grey-filter').fadeOut("slow");	
				}
			})
			
			$('#software-interface').on('click', 'input[name=software]', function() {
				
				var software = $(this).val();
				var manual_link = '';
				var target = '';
				switch (software) {
					case "QuickBooks":
						manual_link = 'http://www.timeclick.com/payroll/manuals/TimeClick-QuickBooks Integration Manual.pdf';
						software_link = 'quickbooks-integration';
						target = '#label-qb';
						break;
					case "ADP":
						manual_link = 'http://www.timeclick.com/payroll/manuals/TimeClick-ADP Integration Manual.pdf';
						software_link = 'adp-integration';
						target = '#label-adp';
						break;
					case "Paychex":
						manual_link = 'http://www.timeclick.com/payroll/manuals/TimeClick-Paychex Integration Manual.pdf';
						software_link = 'paychex-integration';
						target = '#label-paychex';
						break;
					case "Sage":
						manual_link = 'http://www.timeclick.com/payroll/manuals/TimeClick-Sage Integration Manual.pdf';
						software_link = 'sage-integration';
						target = '#label-sage';
						break;
					default:
						break;	
				}
				
				$('.software-options').removeClass('radio-selection');
				$(target).addClass('radio-selection');
				$('#choose-software-form').attr('action',software_link);
				$('#manual-link').attr('href',manual_link);
				$('#manual-link').hide(300).show(300);
				
			})
			
			$('#software-interface').on('change', 'select', function() {
				$('#save').addClass('confirm_changes');
				$('#next').addClass('dim');
			})
}) // END $(document).ready(function(){
	
	
function setupComplete() {
	
	// display message box on completion of part 1 and part 2 of the setup
	$('.msg-container-div #notification-msg').html('Ok! You have now completed the preliminary setup. From now on when you log in you will arrive here. <br><br> Next step: Upload your TimeClick Payroll Report.');
	$('#grey-filter').fadeIn("fast");
	$('#msg-box, .msg-container-div').fadeIn("slow");
}

function firstTimeUser() {
	// display message box on completion of part 1 and part 2 of the setup
	$('.msg-container-div #notification-msg').html('<span>Welcome! Choose your payroll software.</span> <form id="choose-software-form" action="" method="post"><input type="radio" id="radio-qb" name="software" value="QuickBooks"><label for="radio-qb" id="label-qb" class="software-options">QuickBooks</label><!--input type="radio" id="radio-adp" name="software" value="ADP"><label for="radio-adp" id="label-adp" class="software-options">ADP</label><input type="radio" id="radio-paychex" name="software" value="Paychex"><label for="radio-paychex" id="label-paychex" class="software-options">Paychex</label><input type="radio" id="radio-sage" name="software" value="Sage"><label for="radio-sage" id="label-sage" class="software-options">Sage</label--><br><br><a href="#" id="manual-link" target="blank">PDF manual to guide you through set up.</a></form>');
	$('#grey-filter').fadeIn("fast");
	$('#msg-box, .msg-container-div').fadeIn("slow");
}