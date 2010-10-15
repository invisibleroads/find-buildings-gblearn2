<%inherit file="/base.mako"/>\


<%def name="title()">Regions</%def>


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

<div id="addRegion" class="tabOFF">Add a new region</div>

<div id="addRegion_" class="tab_">
<form action="${h.url_for('region_add', url=h.encodeURL(request.path))}" enctype="multipart/form-data" method="post" onsubmit="return validateForm();">
<table>
    <tr>
        <td class=fieldName>What name do you want to give to the region?</td>
        <td><input name=regionName></td>
    </tr>
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
        <td>What fraction of each region should be reserved for test samples?</td>
        <td><input name=testFractionPerRegion value="0.2"></td>
    </tr>
    <tr>
        <td>How do you want to define the region?</td>
        <td>
            <select id=regionMethod name=regionMethod>
                <option value=viaCoverageFraction>Via coverage fraction</option>
                <option value=viaRectangles>Via rectangles</option>
                <option value=viaShapefile>Via shapefile</option>
            </select>
        </td>
    </tr>


    <tbody id=viaCoverageFraction class=regionMethod>
        <tr>
            <td>How long should each window be in meters?</td>
            <td><input name=windowLengthInMeters value=20></td>
        </tr>
        <tr>
            <td>How long should each region be in windows?</td>
            <td><input name=regionLengthInWindows value=6></td>
        </tr>
        <tr>
            <td>What fraction of the image should be covered by regions?</td>
            <td><input name=coverageFraction value="0.5"></td>
        </tr>
        <tr>
            <td>What offset for the regions should be included in the coverage?</td>
            <td><input name=coverageOffset value=0></td>
        </tr>
    </tbody>


    <tbody id=viaRectangles class=regionMethod>
        <tr>
            <td>Please specify rectangles in pixel coordinates relative to the multispectral image</td>
            <td><textarea name=multispectralRegionFrames>800 3600 1000 4100
2500 3600 2700 4100
1000 2000 1500 2500
2000 2000 2500 2500
1000 4000 2500 4500</textarea></td>
        </tr>
    </tbody>


    <tbody id=viaShapefile class=regionMethod>
        <tr>
            <td>Please upload a shapefile containing your regions of interest</td>
            <td><input name=region type=file></td>
        </tr>
    </tbody>


    <tr>
        <td><input type=submit value=Add></td>
    </tr>
</table>
</form>
</div>
</%def>


${listRegions()}
