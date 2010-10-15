<%inherit file="/base.mako"/>\


<%def name="title()">Windows</%def>


<%def name="head()">
<script>
function validateForm() {
    % if h.isPerson():

    % else:
        window.location = "${h.url_for('person_login', url=h.encodeURL(request.path))}";
        return false;
    % endif
}
</script>
</%def>


<%def name="css()">
.fieldName {
    width: 30em;
}
</%def>


<%def name="js()">
$('#windowMethod').change(function() {
    var windowMethods = $('.windowMethod');
    var windowMethodCount = windowMethods.length;
    for (var i=0; i<windowMethodCount; i++) {
        var windowMethod = windowMethods[i];
        if (windowMethod.id == this.value) {
            $(windowMethod).show();
        } else {
            $(windowMethod).hide();
        }
    }
}).change();
$('.windowDelete').click(function() {
    var windowID = /\d+/.exec(this.id)[0];
    var windowObject = $('#window' + windowID);
    $.post("${h.url_for('window_delete')}", {
        'windowID': windowID
    }, function(data) {
        if (data.isOk) {
            windowObject.hide();
        } else {
            alert(data.message);
        }
    }, 'json');
});
$('.jobDelete').click(function() {
    var jobID = /\d+/.exec(this.id)[0];
    var jobObject = $('#job' + jobID);
    $.post("${h.url_for('job_delete')}", {
        'jobID': jobID
    }, function(data) {
        if (data.isOk) {
            jobObject.hide();
        } else {
            alert(data.message);
        }
    }, 'json');
});
</%def>


<%def name="listWindows()">
% if c.windows:
<h1>Windows</h1>
<table class=maximumWidth>
    <tr>
        <td>Window name</td>
        <td></td>
    </tr>
    % for window in c.windows:
    <tr id=window${window.id}>
        <td>${window.name}</td>
        <td>
        % if h.isPerson():
            <input type=button value=Delete class=windowDelete id=windowDelete${window.id}>
        % endif
        </td>
    </tr>
    % endfor
</table>
<br>
% endif

% if c.window_jobs:
<h1>Windows Queued</h1>
<table class=maximumWidth>
    <tr>
        <td>Window name</td>
        <td></td>
    </tr>
    % for job in c.window_jobs:
    <%
        jobInput = job.getInput()
    %>
    <tr id=job${job.id}>
        <td>${jobInput.get('windowName')}</td>
        <td>
        % if h.isPerson():
            <input type=button value=Delete class=jobDelete id=jobDelete${job.id}>
        % endif
        </td>
    </tr>
    % endfor
</table>
<br>
% endif

<div id="addWindow" class="tabOFF">Add a new window</div>

<div id="addWindow_" class="tab_">
<form action="${h.url_for('window_add', url=h.encodeURL(request.path))}" enctype="multipart/form-data" method="post" onsubmit="return validateForm();">
<table>
    <tr>
        <td class=fieldName>What name do you want to give to the window?</td>
        <td><input name=windowName></td>
    </tr>

    <tr>
        <td class=fieldName>example count per region</td>
        <td><input name=exampleCountPerRegion value="10"></td>
    </tr>

    <tr>
        <td class=fieldName>multispectral pixel shift value</td>
        <td><input name=multispectralPixelShiftValue value="2"></td>
    </tr>

    <tr>
        <td class=fieldName>shift count</td>
        <td><input name=shiftCount value="1"></td>
    </tr>

    <tr>
        <td class=fieldName>Which region are we sampling?</td>
        <td>
            <select name=regionID>
            % for region in c.regions:
                <option value=${region.id}>${region.name}</option>
            % endfor
            </select>
        </td>
    </tr>

    <tr>
        <td><input type=submit value=Add></td>
    </tr>
</table>
</form>
</div>
</%def>


${listWindows()}
