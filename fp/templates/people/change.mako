<%inherit file="/base.mako"/>

<%def name="title()">Profile ${c.title}</%def>

<%def name="css()">
.field {
    width: 15em;
}
td {
    padding-right: 1em;
}
</%def>

<%def name="js()">
function getMessageObj(id) { return $('#m_' + id); }
var ids = ['nickname', 'username', 'password', 'password2', 'email', 'email_sms', 'status'];
var defaultByID = {};
for (var i=0; i<ids.length; i++) {
    var id = ids[i];
    defaultByID[id] = getMessageObj(id).html();
}
function showFeedback(messageByID) {
    for (var i=0; i<ids.length; i++) {
        var id = ids[i];
        var o = getMessageObj(id);
        if (messageByID[id]) {
            o.html('<b>' + messageByID[id] + '</b>');
        } else {
            o.html(defaultByID[id]);
        }
    }
}
$('#button_save').click(function() {
    // Get
    var username = $('#username').val(),
        password = $('#password').val(), 
        password2 = $('#password2').val(), 
        nickname = $('#nickname').val(), 
        email = $('#email').val(), 
        email_sms = $('#email_sms').val();
    // Validate password
    var messageByID = {}, hasError = false;
    if (password != password2) {
        messageByID['password'] = 'Passwords must match';
        messageByID['password2'] = 'Passwords must match';
        hasError = true;
    }
    // Send feedback
    if (hasError) {
        showFeedback(messageByID);
    } else {
        // Lock
        $('.lockOnSave').attr('disabled', 'disabled');
        // Post
        $.post("${h.url_for(c.save_url_name)}", {
            username: username,
            password: password,
            nickname: nickname,
            email: email,
            email_sms: email_sms
        }, function(data) {
            // If there are no errors,
            if (data.isOk) {
                messageByID['status'] = "${c.success_message}";
            }
            // If there are errors,
            else {
                // Fill
                messageByID = data.errorByID;
                // Unlock
                $('.lockOnSave').removeAttr('disabled');
            }
            showFeedback(messageByID);
        }, 'json');
    }
});
$('#username').focus();
</%def>

<%def name="toolbar()">
% if request.path.startswith('/people/register'):
    Register for an account
% else:
    Configure your account
% endif
</%def>


<table>
    <tr>
        <td class=label><label for=username>Username</label></td>
        <td class=field><input id=username name=username class="lockOnSave maximumWidth" autocomplete=off></td>
        <td id=m_username>What you use to login</td>
    </tr>
    <tr>
        <td class=label><label for=password>Password</label></td>
        <td class=field><input id=password name=password class="lockOnSave maximumWidth" type=password autocomplete=off></td>
        <td id=m_password>So you have some privacy</td>
    </tr>
    <tr>
        <td class=label><label for=password2>Password again</label></td>
        <td class=field><input id=password2 name=password2 class="lockOnSave maximumWidth" type=password autocomplete=off></td>
        <td id=m_password2>To make sure you typed it right</td>
    </tr>
    <tr>
        <td class=label><label for=nickname>Nickname</label></td>
        <td class=field><input id=nickname name=nickname class="lockOnSave maximumWidth" autocomplete=off></td>
        <td id=m_nickname>How others see you</td>
    </tr>
    <tr>
        <td class=label><label for=email>Email</label></td>
        <td class=field><input id=email name=email class="lockOnSave maximumWidth" autocomplete=off></td>
        <td id=m_email>To confirm changes to your account</td>
    </tr>
    <tr>
        <td class=label><label for=email_sms>SMS email</label></td>
        <td class=field><input id=email_sms name=email_sms class="lockOnSave maximumWidth" autocomplete=off></td>
        <td id=m_email_sms>How you can receive text message alerts for urgent scheduled goals (optional)</td>
    </tr>
    <tr><td><input id=button_save class=lockOnSave type=button value="${c.button_label}"></td></tr>
</table>

<span id=m_status></span>
