<%inherit file="/base.mako"/>\


<%def name="title()">Images</%def>


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


<%def name="js()">
$('.imageDelete').click(function() {
    var imageID = /\d+/.exec(this.id)[0];
    var imageObject = $('#image' + imageID);
    $.post("${h.url_for('image_delete')}", {
        'imageID': imageID
    }, function(data) {
        if (data.isOk) {
            imageObject.hide();
        } else {
            alert(data.message);
        }
    }, 'json');
});
</%def>


<%def name="listImages()">
% if c.images:
<table class=maximumWidth>
    <tr>
        <td>Image name</td>
        <td>Multispectral</td>
        <td>Panchromatic</td>
        <td></td>
    </tr>
    % for image in c.images:
    <tr id=image${image.id}>
        <td>${image.name}</td>
        <td></td>
        <td></td>
        <td>
        % if h.isPerson():
            <input type=button value=Delete class=imageDelete id=imageDelete${image.id}>
        % endif
        </td>
    </tr>
    % endfor
</table>
<br>
% endif
<div id="addImage" class="tabOFF">Add a new image</div>

<div id="addImage_" class="tab_">
<form action="${h.url_for('image_add', url=h.encodeURL(request.path))}" enctype="multipart/form-data" method="post" onsubmit="return validateForm();">
<table>
    <tr>
        <td>Image name</td>
        <td><input name=imageName></td>
    </tr>
    <tr>
        <td>Multispectral</td>
        <td><input name=imageMultispectral type=file></td>
    </tr>
    <tr>
        <td>Panchromatic</td>
        <td><input name=imagePanchromatic type=file></td>
    </tr>
    <tr>
        <td><input type=submit value=Add></td>
    </tr>
</table>
</form>
</div>
</%def>


${listImages()}
