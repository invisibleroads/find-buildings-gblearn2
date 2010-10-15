<%inherit file="/base.mako"/>\


<%def name="title()">Analyze image</%def>


<%def name="js()">
$('#addImage_button').click(function() {
});
</%def>


<%def name="toolbar()">
Analyze image
</%def>


<div id="chooseImage" class="tabOFF"> 
<b>Choose image for analysis</b>
</div>

<div id="chooseImage_" class="tab_">
</div>


<hr>


<div id="classifier" class="tabOFF"> 
<b>Choose classifier</b><br>
</div>

<div id="classifier_" class="tab_">

<table>
    <tr>
        <td>&nbsp;</td>
        <td>Classifier Name</td>
    </tr>
% for classifier in c.classifiers: 
<tr>
<td>
<input name="classifier" type="radio"></td>
<td>${classifier.name}</td>
</tr>
% endfor
</table>

<br>

<div id="trainClassifier" class="tabOFF">
Train a New Classifier
</div>

<div id="trainClassifier_" class="tab_">
<b>New classifier name</b><br>
<input value="New Classifier 1"><p>

<b>Pick a dataset for training and testing the classifier</b><br>
<input type=radio name=datasetID value=0> Ruhiira 2003 roofs
<br>
<input type=radio name=datasetID value=1> Ruhiira 2007 roads
<br>
<input type=radio name=datasetID value=2> Koraro 2006 roofs
<br>
<input type=radio name=datasetID value=3> Koraro 2007 roads
<br>

<div id="buildDataSet" class="tabOFF">
Build a new dataset
</div>

<div id="buildDataSet_" class="tab_">
<b>Pick an image</b><br>
<input type=button value="Add a new image">
<br>
<br>
<b>Select a region of the image</b><br>
<input type=button value="Add a new region">
<br>
<br>
<div id="paramDataSet" class="tabOFF">
<b>Set parameters for building the dataset</b>
</div>

<div id="paramDataSet_" class="tab_">
<table>
    <tr>
        <td>Example count per region</td>
        <td><input value="10"></td>
    </tr>
    <tr>
        <td>Shift count</td>
        <td><input value="1"></td>
    </tr>
    <tr>
        <td>Multispectral pixel shift value</td>
        <td><input value="2"></td>
    </tr>
    <tr>
        <td>Training size</td>
        <td><input value="50000"></td>
    </tr>
    <tr>
        <td>Test size</td>
        <td><input value="10000"></td>
    </tr>
    <tr>
        <td>Positive ratio</td>
        <td><input value="0.5"></td>
    </tr>
</table>
</div>
</div>


<br>
<br>
<b>Choose a training algorithm</b><br>
<select>
    <option>Convolutional neural network</option>
    <option>Convolutional neural network with boosting</option>
</select>
<br>
<br>
<div id="paramClassifier" class="tabOFF">
<b>Set parameters for training the classifier</b>
</div>

<div id="paramClassifier_" class="tab_">
<table>
    <tr>
        <td>Ratio range</td>
        <td><input value="2 3"></td>
    </tr>
    <tr>
        <td>Kernel range</td>
        <td><input value="10 9 8 7 6 5 4 3 2"></td>
    </tr>
    <tr>
        <td>Which layer combination</td>
        <td><input value="0"></td>
    </tr>
    <tr>
        <td>Hidden count</td>
        <td><input value="20"></td>
    </tr>
    <tr>
        <td>Iteration count</td>
        <td><input value="3"></td>
    </tr>
    <tr>
        <td>Dataset name</td>
        <td><input value="ruhiira 2003"></td>
    </tr>
    <tr>
        <td>Feature class name</td>
        <td><input value="NormalizedGrayscaleFeatureSet"></td>
    </tr>
    <tr>
        <td>Connection table0 path</td>
        <td><input value="files/GrayscaleFeatureSet0.map"></td>
    </tr>
    <tr>
        <td>Connection table1 path</td>
        <td><input value="files/GrayscaleFeatureSet1.map"></td>
    </tr>
</table>
</div>

</div>

</div>

<hr>


<div id="results" class="tabOFF">
<b>Configure post-processing</b><br>
</div>

<div id="results_" class="tab_">
<table>
<tr>
<td>
<input name="results" type="radio"></td>
<td>Option 1</td>
</tr>
<tr>
<td>
<input name="results" type="radio"></td>
<td>Option 2</td>
</tr>
</table>
</div>

<hr>
<input value="Go" type="submit">
</div>
