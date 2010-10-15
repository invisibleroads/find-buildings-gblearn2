<%inherit file="/base.mako"/>\


<%def name="title()">Scans</%def>


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
$('#regionMethod').change(function() {
    var regionMethods = $('.regionMethod');
    var regionMethodCount = regionMethods.length;
    for (var i=0; i<regionMethodCount; i++) {
        var regionMethod = regionMethods[i];
        if (regionMethod.id == this.value) {
            $(regionMethod).show();
        } else {
            $(regionMethod).hide();
        }
    }
}).change();
$('.regionDelete').click(function() {
    var regionID = /\d+/.exec(this.id)[0];
    var regionObject = $('#region' + regionID);
    $.post("${h.url_for('region_delete')}", {
        'regionID': regionID
    }, function(data) {
        if (data.isOk) {
            regionObject.hide();
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


<%def name="listRegions()">
% if c.regions:
<h1>Regions</h1>
<table class=maximumWidth>
    <tr>
        <td>Region name</td>
        <td></td>
    </tr>
    % for region in c.regions:
    <tr id=region${region.id}>
        <td>${region.name}</td>
        <td>
        % if h.isPerson():
            <input type=button value=Delete class=regionDelete id=regionDelete${region.id}>
        % endif
        </td>
    </tr>
    % endfor
</table>
<br>
% endif

% if c.region_jobs:
<h1>Regions Queued</h1>
<table class=maximumWidth>
    <tr>
        <td>Region name</td>
        <td></td>
    </tr>
    % for job in c.region_jobs:
    <%
        jobInput = job.getInput()
    %>
    <tr id=job${job.id}>
        <td>${jobInput['regionName']}</td>
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

<div id="addScan" class="tabOFF">Add a new scan</div>

<div id="addScan_" class="tab_">
<form action="${h.url_for('scan_add', url=h.encodeURL(request.path))}" enctype="multipart/form-data" method="post" onsubmit="return validateForm();">
<table>
    <tr>
        <td class=fieldName>What name do you want to give to the scan?</td>
        <td><input name=scanName></td>
    </tr>
    <tr>
        <td>Do you want to scan by Regions or Images?</td>
        <td>
            <select id=scanMethod name=scanMethod>
                <option value=viaRegions>Via Regions</option>
                <option value=viaImages>Via Images</option>
            </select>
        </td>
    </tr>

    <tbody id=viaRegions class=scanMethod>
        <tr>
            <td>Which region are we covering?</td>
            <td>
                <select name=imageID>
                % for region in c.regions:
                    <option value=${region.id}>${region.name}</option>
                % endfor
                </select>
            </td>
        </tr>
        <tr>
            <td>What scan ratio should be?</td>
            <td><input name=scanRatio value=2></td>
        </tr>
        <tr>
            <td>What classifier should we choose?</td>
            <td>
                <select name=imageID>
                % for region in c.regions:
                    <option value=${region.id}>${region.name}</option>
                % endfor
                </select>
            </td>
        </tr>
    </tbody>


    <tbody id=viaImages class=scanMethod>
        <tr>
            <td>Please specify rectangles in pixel coordinates relative to the multispectral image</td>
            <td><textarea name=multispectralRegionFrames>800 3600 1000 4100
2500 3600 2700 4100
1000 2000 1500 2500
2000 2000 2500 2500
1000 4000 2500 4500</textarea></td>
        </tr>
    </tbody>

    <tr>
        <td>Which image are we covering?</td>
        <td>
            <select name=imageID>
            % for image in c.images:
                <option value=${image.id}>${image.name}</option>
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


${listRegions()}
