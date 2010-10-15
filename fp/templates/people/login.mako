<%inherit file="/base.mako"/>

<%def name="title()">Login</%def>

<%def name="head()">
<script src="http://api.recaptcha.net/js/recaptcha_ajax.js"></script>
</%def>

<%def name="js()">
// Prepare login form
var rejection_count = 0;
function ajax_login() {
    // Validate
    var errorCount = 0;
    errorCount = errorCount + isEmpty('username');
    errorCount = errorCount + isEmpty('password');
    if (errorCount) return;
    // Initialize
    var login_data = {
        'username': $('#username').val(),
        'password': $('#password').val(),
        'offset_in_minutes': new Date().getTimezoneOffset()
    }
    // Get recaptcha
    if ($('#recaptcha_challenge_field').length) {
        login_data['recaptcha_challenge_field'] = $('#recaptcha_challenge_field').val();
        login_data['recaptcha_response_field'] = $('#recaptcha_response_field').val();
    }
    // Attempt login
    $.post("${h.url_for('person_login_')}", login_data, function(data) {
        if (data.isOk) {
            window.location = "${c.url}";
        } else {
            $('#m_username').html('Invalid login');
            rejection_count = rejection_count + 1;
            if (rejection_count >= ${h.REJECTION_LIMIT}) {
                Recaptcha.create("${c.publicKey}", "recaptcha", {
                    theme: "red",
                    callback: Recaptcha.focus_response_field
                });
            }
        }
    }, 'json');
}
$('#login_button').click(ajax_login);
function isEmpty(inputID) {
    var input = $('#' + inputID);
    var output = $('#m_' + inputID);
    if (input.val() == '') {
        output.text('You must provide a ' + inputID);
        return 1;
    } else {
        output.text('');
        return 0;
    }
}
$('#password').keydown(function(e) {
    if (e.keyCode == 13) ajax_login();
});


// Prepare reset form
$('#reset_form').hide();
$('#reset_link').click(function() {
    $('#reset_link').hide();
    $('#reset_form').show();
    $('#reset_email').keydown(function(e) {
        if (e.keyCode == 13) ajax_reset();
    }).focus();
});
$('#reset_button').click(ajax_reset);
function ajax_reset() {
    // Check that the email is not empty
    var email = $.trim($('#reset_email').val());
    if (!email) return;
    // Post
    $('.lockOnReset').attr('disabled', true);
    $.post("${h.url_for('person_reset')}", {
        'email': email
    }, function(data) {
        if (data.isOk) {
            $('#m_reset').html('Please check your email');
        } else {
            $('#m_reset').html('Email not found');
            $('.lockOnReset').removeAttr('disabled');
        }
    }, 'json');
}


// Focus
$('#username').focus();
</%def>


<%def name="toolbar()">
<a class=linkOFF href="${h.url_for('person_register')}" id=register>Register for an account</a>
</%def>


<%def name="support()">
<a href="${h.url_for('person_index')}" class=linkOFF>People</a>
&nbsp;
</%def>


<%def name="board()">
<a id=reset_link class=linkOFF>Forgot your password?</a>
<table id=reset_form>
    <tr>
        <td><label for=reset_email>Email</label></td>
        <td><input class=lockOnReset id=reset_email></td>
        <td><input class=lockOnReset id=reset_button type=button value=Reset></td>
        <td id=m_reset></td>
    </tr>
</table>
</%def>


<%
messageByCode = { 
    'updated': 'Account updated',
    'created': 'Account created',
    'expired': 'Ticket expired',
}
%>

<table>
    <tr>
        <td><label for=username>Username</label></td>
        <td><input id=username></td>
        <td id=m_username>${messageByCode.get(c.messageCode, '')}</td>
    </tr>
    <tr>
        <td><label for=password>Password</label></td>
        <td><input id=password type=password></td>
        <td id=m_password></td>
    </tr>
</table>

<div id=recaptcha>
</div>

<input id=login_button type=button value=Login>
