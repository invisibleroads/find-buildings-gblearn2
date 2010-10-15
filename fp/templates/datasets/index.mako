<%inherit file="/base.mako"/>\


<%def name="title()">Datasets</%def>


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
$('.datasetDelete').click(function() {
    var datasetID = /\d+/.exec(this.id)[0];
    var datasetObject = $('#dataset' + datasetID);
    $.post("${h.url_for('dataset_delete')}", {
        'datasetID': datasetID
    }, function(data) {
        if (data.isOk) {
            datasetObject.hide();
        } else {
            alert(data.message);
        }
    }, 'json');
});
</%def>


<%def name="listDatasets()">
<script>    

function deleteARow(r){
    alert(r.parentNode.parentNode.parentNode.parentNode.id);
    var i=r.rowIndex;
    var delRow = r.parentNode.parentNode;
    var tbl = delRow.parentNode.parentNode;
    var rIndex = delRow.sectionRowIndex;
    //var rowArray = new Array(delRow);
    //deleteRows(rowArray);
    //var rIndex = rowObjArray[i].sectionRowIndex;
    delRow.parentNode.deleteRow(rIndex);
    //reorderRows(tbl, rIndex);
}

var lastButtonIDDuck=0;
var lastButtonIDMonkey=0; 
var RowBaseDuck=1;
var RowBaseMonkdy=1;

function insertFile(button, tblId){
    
    // Insert Row
    var tbl = document.getElementById(tblId);
    var row = tbl.insertRow(tbl.rows.length);

    // select cell
    var cellSel = row.insertCell(0);
    var sel = document.createElement('select');
    // render options into select
    % for windowIndex, window in enumerate(c.windows):
        sel.options[windowIndex] = new Option(${window.name}, ${window.id});
    % endfor
    cellSel.appendChild(sel);
    
    // delete cell
    var cellDel = row.insertCell(1);    
    var btnEl = document.createElement('input');
    btnEl.setAttribute('type', 'button');
    btnEl.setAttribute('value', 'Delete');
    btnEl.onclick = function () {deleteARow(this)};
    cellDel.appendChild(btnEl);
}
    
</script>
% if c.datasets:
<table class=maximumWidth>
    <tr>
        <td>Dataset name</td>
        <td>Multispectral</td>
        <td>Panchromatic</td>
        <td></td>
    </tr>
    % for dataset in c.datasets:
    <tr id=dataset${dataset.id}>
        <td>${dataset.name}</td>
        <td></td>
        <td></td>
        <td>
        % if h.isPerson():
            <input type=button value=Delete class=datasetDelete id=datasetDelete${dataset.id}>
        % endif
        </td>
    </tr>
    % endfor
</table>
<br>
% endif
<div id="addDataset" class="tabOFF">Add a new dataset</div>

<div id="addDataset_" class="tab_">
<form action="${h.url_for('dataset_add', url=h.encodeURL(request.path))}" enctype="multipart/form-data" method="post" onsubmit="return validateForm();">
<table>
    <tr>
        <td>Dataset name</td>
        <td><input name=datasetName></td>
    </tr>
    <tr>
        <td>training size</td>
        <td><input name=trainingSize value=500></td>
    </tr>
    <tr>
        <td>test size</td>
        <td><input name=testSize value=100></td>
    </tr>
    <tr>
        <td>positive ratio</td>
        <td><input name=positiveRatio value=0.5></td>
    </tr>
</table>
<table id="windowFile">
    <td><input type=button id=duck value="Add a Window" onclick="insertFile(this,'windowFile')" name=duck></td>
</table>
<table id="pathFile">
    <td><input type=button id=monkey value="Attach Patch File" onclick="insertFile(this,'pathFile')" name=monkey></td>
</table>
    <tr>
        <td><input type=submit value=Add></td>
    </tr>
</form>
</div>
</%def>


${listDatasets()}
